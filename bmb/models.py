"""固定模型抽象:测试用 FakeModel(零 API、确定性),运行时用 OpenAI 兼容客户端接开源模型。"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Callable


class FixedModel(ABC):
    """测量仪器:对所有架构同一把尺。作答 temp=0;判分可 temp>0。"""

    @abstractmethod
    def generate(self, prompt: str, temperature: float = 0.0, seed: int = 0) -> str:
        ...


class FakeModel(FixedModel):
    """确定性假模型,供测试。responder: prompt -> 回复字符串。"""

    def __init__(self, responder: Callable[[str], str] | None = None) -> None:
        self._responder = responder or (lambda p: f"[fake] {p[:32]}")

    def generate(self, prompt: str, temperature: float = 0.0, seed: int = 0) -> str:
        return self._responder(prompt)


class OpenAICompatibleModel(FixedModel):
    """运行时:接任意 OpenAI 兼容开源模型端点(vLLM/Ollama/远程)。openai 惰性导入。"""

    def __init__(self, base_url: str, api_key: str, model: str) -> None:
        self.base_url = base_url
        self.api_key = api_key
        self.model = model

    def generate(self, prompt: str, temperature: float = 0.0, seed: int = 0) -> str:
        from openai import OpenAI  # 惰性:测试不需要装/配
        client = OpenAI(base_url=self.base_url, api_key=self.api_key)
        resp = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            seed=seed,
        )
        return resp.choices[0].message.content or ""


def count_tokens(text: str, model: str = "default") -> int:
    """v1 启发式估计;部署时可换真 tokenizer。全链路一致即可。"""
    return max(1, len(text) // 4)
