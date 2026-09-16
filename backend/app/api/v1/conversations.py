import json
import uuid
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.database.session import get_db
from app.database.models.auth import User
from app.database.models.conversations import Conversation, Message, Feedback
from app.database.models.agents import AgentExecution, LLMUsage
from app.security.deps import get_current_user
from app.agents import get_agent, AGENT_REGISTRY
from app.agents.base import AgentContext
from app.agents.router import intent_router
from app.llm.base import LLMMessage
from app.rag.retrieval.retriever import rag_retriever
from app.rag.citations.engine import citation_engine
from app.memory.manager import memory_manager
from app.database.base import utc_now

router = APIRouter(prefix="/conversations", tags=["Conversations"])


class ConversationCreate(BaseModel):
    agent_id: Optional[str] = "academic"
    title: Optional[str] = "New Conversation"


class MessageCreate(BaseModel):
    content: str
    stream: bool = True
    provider: Optional[str] = None
    model: Optional[str] = None


class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    model: Optional[str] = None
    token_count: int
    created_at: str


class ConversationDetailResponse(BaseModel):
    id: str
    agent_id: str
    title: str
    status: str
    created_at: str
    messages: List[MessageResponse]


class FeedbackRequest(BaseModel):
    message_id: Optional[str] = None
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


@router.post("", response_model=ConversationDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    payload: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    agent_id = payload.agent_id.lower() if payload.agent_id else "academic"
    if agent_id not in AGENT_REGISTRY:
        agent_id = "academic"

    conversation = Conversation(
        user_id=current_user.id,
        agent_id=agent_id,
        title=payload.title or "New Conversation",
        status="active",
    )
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)

    return ConversationDetailResponse(
        id=str(conversation.id),
        agent_id=conversation.agent_id,
        title=conversation.title,
        status=conversation.status,
        created_at=conversation.created_at.isoformat(),
        messages=[],
    )


@router.get("", response_model=List[ConversationDetailResponse])
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc())
    )
    result = await db.execute(stmt)
    conversations = result.scalars().all()

    response = []
    for c in conversations:
        response.append(
            ConversationDetailResponse(
                id=str(c.id),
                agent_id=c.agent_id,
                title=c.title,
                status=c.status,
                created_at=c.created_at.isoformat(),
                messages=[],
            )
        )
    return response


@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    conv_uuid = uuid.UUID(conversation_id)
    stmt = select(Conversation).where(Conversation.id == conv_uuid, Conversation.user_id == current_user.id)
    conversation = (await db.execute(stmt)).scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")

    msg_stmt = select(Message).where(Message.conversation_id == conv_uuid).order_by(Message.created_at.asc())
    messages = (await db.execute(msg_stmt)).scalars().all()

    return ConversationDetailResponse(
        id=str(conversation.id),
        agent_id=conversation.agent_id,
        title=conversation.title,
        status=conversation.status,
        created_at=conversation.created_at.isoformat(),
        messages=[
            MessageResponse(
                id=str(m.id),
                role=m.role,
                content=m.content,
                model=m.model,
                token_count=m.token_count,
                created_at=m.created_at.isoformat(),
            )
            for m in messages
        ],
    )


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    conv_uuid = uuid.UUID(conversation_id)
    stmt = delete(Conversation).where(Conversation.id == conv_uuid, Conversation.user_id == current_user.id)
    result = await db.execute(stmt)
    await db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")
    return {"message": "Conversation deleted successfully."}


@router.post("/{conversation_id}/messages")
async def post_message(
    conversation_id: str,
    payload: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    conv_uuid = uuid.UUID(conversation_id)
    stmt = select(Conversation).where(Conversation.id == conv_uuid, Conversation.user_id == current_user.id)
    conversation = (await db.execute(stmt)).scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")

    # Record User Message
    user_msg = Message(
        conversation_id=conv_uuid,
        role="user",
        content=payload.content,
        token_count=len(payload.content.split()),
    )
    db.add(user_msg)
    await db.commit()

    # Load history
    msg_stmt = select(Message).where(Message.conversation_id == conv_uuid).order_by(Message.created_at.asc())
    all_msgs = (await db.execute(msg_stmt)).scalars().all()
    history = [LLMMessage(role=m.role, content=m.content) for m in all_msgs[:-1]]

    # Agent selection
    agent = get_agent(conversation.agent_id) or AGENT_REGISTRY["academic"]

    # Retrieve relevant RAG evidence if agent has retrieval domain
    rag_docs = []
    if agent.retrieval_domain:
        rag_docs = await rag_retriever.retrieve(db, query=payload.content, domain=agent.retrieval_domain)

    # Fetch relevant user memories
    memories = await memory_manager.get_user_memories(db, current_user.id)
    memory_dicts = [{"key": m.key, "value": m.value, "confidence": m.confidence} for m in memories]

    context = AgentContext(
        user_id=str(current_user.id),
        conversation_id=conversation_id,
        memories=memory_dicts,
        rag_documents=rag_docs,
    )

    if payload.stream:
        # SSE Streaming response
        async def event_generator():
            full_response_parts = []
            yield f"data: {json.dumps({'type': 'start', 'agent': agent.agent_id})}\n\n"
            async for chunk in agent.stream(
                user_message=payload.content,
                history=history,
                context=context,
                provider=payload.provider,
                model=payload.model,
            ):
                if chunk.delta:
                    full_response_parts.append(chunk.delta)
                    yield f"data: {json.dumps({'type': 'token', 'delta': chunk.delta})}\n\n"
                if chunk.is_finished:
                    break

            complete_content = "".join(full_response_parts)
            # Append citations if retrieved
            if rag_docs:
                citations_md = citation_engine.format_citations_markdown(rag_docs)
                complete_content += citations_md
                yield f"data: {json.dumps({'type': 'token', 'delta': citations_md})}\n\n"

            # Save assistant message to database
            assistant_msg = Message(
                conversation_id=conv_uuid,
                role="assistant",
                content=complete_content,
                model=payload.model or "default",
                token_count=len(complete_content.split()),
            )
            db.add(assistant_msg)
            conversation.updated_at = utc_now()
            await db.commit()

            yield f"data: {json.dumps({'type': 'end', 'message_id': str(assistant_msg.id)})}\n\n"

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )
    else:
        # Synchronous execution
        agent_out = await agent.execute(
            user_message=payload.content,
            history=history,
            context=context,
            provider=payload.provider,
            model=payload.model,
        )
        content_to_save = agent_out.content
        if rag_docs:
            content_to_save += citation_engine.format_citations_markdown(rag_docs)

        assistant_msg = Message(
            conversation_id=conv_uuid,
            role="assistant",
            content=content_to_save,
            model=agent_out.model,
            token_count=agent_out.output_tokens,
        )
        db.add(assistant_msg)
        conversation.updated_at = utc_now()
        await db.commit()
        await db.refresh(assistant_msg)

        return MessageResponse(
            id=str(assistant_msg.id),
            role=assistant_msg.role,
            content=assistant_msg.content,
            model=assistant_msg.model,
            token_count=assistant_msg.token_count,
            created_at=assistant_msg.created_at.isoformat(),
        )


@router.post("/{conversation_id}/feedback")
async def post_feedback(
    conversation_id: str,
    payload: FeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    conv_uuid = uuid.UUID(conversation_id)
    msg_uuid = uuid.UUID(payload.message_id) if payload.message_id else None

    feedback = Feedback(
        user_id=current_user.id,
        conversation_id=conv_uuid,
        message_id=msg_uuid,
        rating=payload.rating,
        comment=payload.comment,
    )
    db.add(feedback)
    await db.commit()
    return {"message": "Feedback submitted successfully."}
