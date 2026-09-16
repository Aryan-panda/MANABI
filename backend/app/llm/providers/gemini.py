import time
from typing import List, Optional, Any, AsyncGenerator
import httpx
from app.llm.base import BaseLLMProvider, LLMMessage, LLMResponse, LLMStreamChunk
from app.config.settings import settings


class GeminiProvider(BaseLLMProvider):
    provider_name: str = "gemini"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

    async def generate(
        self,
        messages: List[LLMMessage],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> LLMResponse:
        target_model = model or settings.LLM_MODEL or "gemini-1.5-flash"
        if not self.api_key:
            # Fallback mock for offline development when API key is missing
            return LLMResponse(
                content="[Gemini Provider (Offline Mode)]: Real API key not configured. Configure GEMINI_API_KEY in .env.",
                model=target_model,
                provider=self.provider_name,
                input_tokens=10,
                output_tokens=15,
                estimated_cost_usd=0.0,
                latency_ms=10.0,
            )

        system_instruction = None
        contents = []
        for m in messages:
            if m.role == "system":
                system_instruction = {"parts": [{"text": m.content}]}
            else:
                role = "model" if m.role == "assistant" else "user"
                contents.append({"role": role, "parts": [{"text": m.content}]})

        payload: dict = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
            }
        }
        if max_tokens:
            payload["generationConfig"]["maxOutputTokens"] = max_tokens
        if system_instruction:
            payload["systemInstruction"] = system_instruction

        start_time = time.perf_counter()
        endpoint = f"{self.base_url}/models/{target_model}:generateContent?key={self.api_key}"
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(endpoint, json=payload)
            resp.raise_for_status()
            data = resp.json()

        latency_ms = (time.perf_counter() - start_time) * 1000.0
        candidates = data.get("candidates", [])
        content = ""
        if candidates and "content" in candidates[0]:
            parts = candidates[0]["content"].get("parts", [])
            content = "".join(p.get("text", "") for p in parts)

        usage = data.get("usageMetadata", {})
        prompt_tokens = usage.get("promptTokenCount", 0)
        candidates_tokens = usage.get("candidatesTokenCount", 0)
        cost = self.calculate_cost(target_model, prompt_tokens, candidates_tokens)

        return LLMResponse(
            content=content,
            model=target_model,
            provider=self.provider_name,
            input_tokens=prompt_tokens,
            output_tokens=candidates_tokens,
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
        target_model = model or settings.LLM_MODEL or "gemini-1.5-flash"
        if not self.api_key:
            yield LLMStreamChunk(
                delta="[Gemini Provider (Offline Mode)]: GEMINI_API_KEY is not set. Configure it in .env to stream live tokens.",
                model=target_model,
                provider=self.provider_name,
                is_finished=True
            )
            return

        system_instruction = None
        contents = []
        for m in messages:
            if m.role == "system":
                system_instruction = {"parts": [{"text": m.content}]}
            else:
                role = "model" if m.role == "assistant" else "user"
                contents.append({"role": role, "parts": [{"text": m.content}]})

        payload: dict = {
            "contents": contents,
            "generationConfig": {"temperature": temperature}
        }
        if max_tokens:
            payload["generationConfig"]["maxOutputTokens"] = max_tokens
        if system_instruction:
            payload["systemInstruction"] = system_instruction

        endpoint = f"{self.base_url}/models/{target_model}:streamGenerateContent?alt=sse&key={self.api_key}"
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", endpoint, json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line or not line.startswith("data:"):
                        continue
                    data_str = line[len("data:"):].strip()
                    if not data_str:
                        continue
                    try:
                        import json
                        chunk_json = json.loads(data_str)
                        candidates = chunk_json.get("candidates", [])
                        if candidates and "content" in candidates[0]:
                            parts = candidates[0]["content"].get("parts", [])
                            text_delta = "".join(p.get("text", "") for p in parts)
                            finish_reason = candidates[0].get("finishReason")
                            is_finished = finish_reason is not None and finish_reason != ""
                            yield LLMStreamChunk(
                                delta=text_delta,
                                model=target_model,
                                provider=self.provider_name,
                                is_finished=is_finished,
                            )
                    except Exception:
                        continue

    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        # Gemini 1.5 Flash rates: $0.075 / 1M in, $0.30 / 1M out
        return (input_tokens * 0.000000075) + (output_tokens * 0.00000030)
