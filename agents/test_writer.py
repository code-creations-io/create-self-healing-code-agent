"""Return PyTest code as plain text – no execution inside the agent sandbox."""

from agents.llm_backends import get_model

SYSTEM_PROMPT = (
    "You are TestWriter.  Write *PyTest* unit tests for the code-under-test. "
    "Use assert statements only—no print.  "
    "Place the tests in a file named test_user_code.py. "
    "Import the code under test via  `from user_code import *`."
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


def make_test_writer() -> _SimpleWriter:
    return _SimpleWriter()