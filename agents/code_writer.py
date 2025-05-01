"""
A very small writer that just asks the LLM for code text.
No sandbox execution → nothing gets ‘stuck’.
Works with smolagents-1.14 because we treat the model as *callable*.
"""

from agents.llm_backends import get_model


SYSTEM_PROMPT = (
    "You are CodeWriter, an expert Python engineer. "
    "Return the *full contents* of a single .py module that fulfils the spec. "
    "Do NOT write tests or call open(); just output the code text."
)


class _SimpleWriter:
    """Mimics the `.run()` interface the orchestrator expects."""

    def __init__(self):
        self.model = get_model() # LiteLLMModel
        self.is_callable = callable(self.model)

    def run(self, prompt: str) -> str:
        """
        `prompt` is the string the orchestrator gives us
        (it already contains SYSTEM_PROMPT + spec).
        """
        if self.is_callable:
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt},
            ]
            response = self.model(messages)
            return response.content.strip()

        # Fallback path (OpenAI SDK)
        return self._openai_complete(prompt)


def make_code_writer() -> _SimpleWriter:
    return _SimpleWriter()