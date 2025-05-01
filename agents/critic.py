"""Return a patched *user_code.py* file – text only, no execution."""

from agents.llm_backends import get_model

SYSTEM_PROMPT = (
    "You are CodeCritic.  Given failing test output and current code, "
    "return a *complete replacement* for user_code.py that fixes the bug. "
    "Add explanations only as inline comments."
)


class _SimpleWriter:
    def __init__(self):
        self.model = get_model()
        self.callable = callable(self.model)

    def run(self, prompt: str) -> str:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": prompt},
        ]
        if self.callable:
            response = self.model(messages)
            return response.content.strip()

        # Fallback path (OpenAI SDK)
        return self._openai_complete(prompt)


def make_critic() -> _SimpleWriter:
    return _SimpleWriter()