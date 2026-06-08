import json
import httpx
from ..config import Config
from ..utils import get_logger

log = get_logger("planner")

_SYSTEM = """You are Nunabot's task planner. Convert a user's plain-language request into a
single JSON object describing the GPU task to run. Respond with ONLY JSON, no prose.

Schema:
{
  "task_key": "<one of: inference, generation, analysis, automation, market>",
  "units_multiple": <number, 1.0 = a standard job; larger = heavier>,
  "intent": "<short restatement of what the user wants>"
}

Pick the closest task_key. Use units_multiple to scale heavier or lighter jobs.
"""


class TaskPlanner:
    """LLM bot agent: natural language -> structured task spec -> priced quote."""

    def __init__(self, job_engine, config=Config):
        self.jobs = job_engine
        self.config = config

    def plan(self, message: str) -> dict:
        spec = self._llm_spec(message)
        quote = self.jobs.quote(spec["task_key"], spec["units_multiple"])
        return {"request": spec, "quote": quote.to_dict()}

    def _llm_spec(self, message: str) -> dict:
        if not self.config.LLM_API_KEY:
            raise ValueError("NUNA_LLM_API_KEY not configured")
        if self.config.LLM_PROVIDER == "anthropic":
            return self._anthropic(message)
        return self._openai_compatible(message)

    def _anthropic(self, message: str) -> dict:
        r = httpx.post(
            f"{self.config.LLM_BASE_URL}/messages",
            headers={
                "x-api-key": self.config.LLM_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": self.config.LLM_MODEL,
                "max_tokens": 400,
                "system": _SYSTEM,
                "messages": [{"role": "user", "content": message}],
            },
            timeout=30.0,
        )
        r.raise_for_status()
        return self._parse(r.json()["content"][0]["text"])

    def _openai_compatible(self, message: str) -> dict:
        r = httpx.post(
            f"{self.config.LLM_BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {self.config.LLM_API_KEY}"},
            json={
                "model": self.config.LLM_MODEL,
                "max_tokens": 400,
                "messages": [
                    {"role": "system", "content": _SYSTEM},
                    {"role": "user", "content": message},
                ],
            },
            timeout=30.0,
        )
        r.raise_for_status()
        return self._parse(r.json()["choices"][0]["message"]["content"])

    def _parse(self, text: str) -> dict:
        text = text.strip()
        if text.startswith("```"):
            text = text.split("```")[1].lstrip("json").strip()
        spec = json.loads(text)
        spec["units_multiple"] = float(spec.get("units_multiple", 1.0))
        return spec
