import asyncio
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator
from app.llm.base import BaseLLMProvider, LLMMessage, LLMResponse, LLMStreamChunk
from app.llm.providers.gemini import GeminiProvider
from app.llm.providers.openai import OpenAIProvider
from app.llm.providers.ollama import OllamaProvider
from app.config.settings import settings

logger = logging.getLogger("manabi.llm.gateway")


class ModelGateway:
    def __init__(self):
        self._providers: Dict[str, BaseLLMProvider] = {
            "gemini": GeminiProvider(),
            "openai": OpenAIProvider(),
            "ollama": OllamaProvider(),
        }

    def get_provider(self, provider_name: Optional[str] = None) -> BaseLLMProvider:
        name = (provider_name or settings.LLM_PROVIDER).lower()
        provider = self._providers.get(name)
        if not provider:
            logger.warning(f"Unknown provider '{name}'. Falling back to Gemini.")
            return self._providers["gemini"]
        return provider

    async def generate(
        self,
        messages: List[LLMMessage],
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        max_retries: int = 3,
        **kwargs: Any
    ) -> LLMResponse:
        llm_provider = self.get_provider(provider)
        backoff = 1.0

        for attempt in range(1, max_retries + 1):
            try:
                response = await llm_provider.generate(
                    messages=messages,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )
                logger.info(
                    f"LLM Generation Succeeded | Provider: {response.provider} | Model: {response.model} | "
                    f"Tokens: {response.input_tokens}in/{response.output_tokens}out | Latency: {response.latency_ms:.2f}ms"
                )
                return response
            except Exception as exc:
                logger.warning(
                    f"LLM Generation Attempt {attempt}/{max_retries} failed for {llm_provider.provider_name}: {exc}"
                )
                if attempt == max_retries:
                    # Optional fallback to external ollama or gemini
                    if llm_provider.provider_name != "ollama":
                        try:
                            logger.info("Attempting fallback to Ollama provider...")
                            fallback_provider = self._providers["ollama"]
                            return await fallback_provider.generate(
                                messages=messages,
                                temperature=temperature,
                                max_tokens=max_tokens,
                                **kwargs
                            )
                        except Exception as fb_exc:
                            logger.error(f"Fallback provider also failed: {fb_exc}")
                    raise
                await asyncio.sleep(backoff)
                backoff *= 2.0

        raise RuntimeError("LLM generation exhausted retries")

    async def stream(
        self,
        messages: List[LLMMessage],
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> AsyncGenerator[LLMStreamChunk, None]:
        llm_provider = self.get_provider(provider)
        try:
            async for chunk in llm_provider.stream(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            ):
                yield chunk
        except Exception as exc:
            logger.error(f"Streaming failed for {llm_provider.provider_name}: {exc}")
            yield LLMStreamChunk(
                delta=f"\n\n[Error during token streaming: {str(exc)}]",
                provider=llm_provider.provider_name,
                is_finished=True
            )


model_gateway = ModelGateway()
