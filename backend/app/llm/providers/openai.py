import json
import time
from typing import List, Optional, Any, AsyncGenerator
import httpx
from app.llm.base import BaseLLMProvider, LLMMessage, LLMResponse, LLMStreamChunk
from app.config.settings import settings


class OpenAIProvider(BaseLLMProvider):
    provider_name: str = "openai"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.base_url = "https://api.openai.com/v1"

    async def generate(
        self,
        messages: List[LLMMessage],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> LLMResponse:
        target_model = model or "gpt-4o-mini"
        if not self.api_key:
            return LLMResponse(
                content="[OpenAI Provider (Offline Mode)]: OPENAI_API_KEY is not set. Configure it in .env.",
                model=target_model,
                provider=self.provider_name,
                input_tokens=10,
                output_tokens=15,
                estimated_cost_usd=0.0,
                latency_ms=10.0,
            )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        formatted_messages = [{"role": m.role, "content": m.content} for m in messages]
        payload = {
            "model": target_model,
            "messages": formatted_messages,
            "temperature": temperature,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens

        start_time = time.perf_counter()
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

        latency_ms = (time.perf_counter() - start_time) * 1000.0
        choice = data["choices"][0]
        content = choice["message"]["content"]
        usage = data.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        cost = self.calculate_cost(target_model, prompt_tokens, completion_tokens)

        return LLMResponse(
            content=content,
            model=target_model,
            provider=self.provider_name,
            input_tokens=prompt_tokens,
            output_tokens=completion_tokens,
            estimated_cost_usd=cost,
            latency_ms=latency_ms,
        )

    async def stream(
        self,
        messages: List[LLMMessage],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> AsyncGenerator[LLMStreamChunk, None]:
        target_model = model or "gpt-4o-mini"
        if not self.api_key:
            yield LLMStreamChunk(
                delta="[OpenAI Provider (Offline Mode)]: OPENAI_API_KEY is not set. Configure it in .env.",
                model=target_model,
                provider=self.provider_name,
                is_finished=True
            )
            return

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        formatted_messages = [{"role": m.role, "content": m.content} for m in messages]
        payload = {
            "model": target_model,
            "messages": formatted_messages,
            "temperature": temperature,
            "stream": True,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens

        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", f"{self.base_url}/chat/completions", headers=headers, json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line or not line.startswith("data:"):
                        continue
                    data_str = line[len("data:"):].strip()
                    if data_str == "[DONE]":
                        yield LLMStreamChunk(
                            delta="",
                            model=target_model,
                            provider=self.provider_name,
                            is_finished=True
                        )
                        break
                    try:
                        chunk_json = json.loads(data_str)
                        choices = chunk_json.get("choices", [])
                        if choices:
                            delta_text = choices[0].get("delta", {}).get("content", "")
                            finish_reason = choices[0].get("finish_reason")
                            yield LLMStreamChunk(
                                delta=delta_text,
                                model=target_model,
                                provider=self.provider_name,
                                is_finished=finish_reason is not None,
                            )
                    except Exception:
                        continue

    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        # GPT-4o-mini: $0.15/1M in, $0.60/1M out
        return (input_tokens * 0.00000015) + (output_tokens * 0.00000060)
