# create-self-healing-code-agent

- Created at: 2025-04-30
- Created by: `🐢 Arun Godwin Patel @ Code Creations`

## Table of contents

- [Setup](#setup)
  - [System](#system)
  - [Installation](#installation)
- [Walkthrough](#walkthrough)
  - [Code Structure](#code-structure)
  - [Tech stack](#tech-stack)
  - [Build from scratch](#build-from-scratch)
    - [1. Create a virtual environment](#1-create-a-virtual-environment)
    - [2. Activate the virtual environment](#2-activate-the-virtual-environment)
    - [3. Write the backend](#3-write-the-backend)
    - [4. Create the agents](#4-create-the-agents)
    - [5. Construct the orchestrator](#5-construct-the-orchestrator)
    - [6. Setup the config files](#6-setup-the-config-files)
    - [7. Create the Python module](#7-create-the-python-module)
    - [8. Run the agent](#8-run-the-agent)

## Setup

### System

This code repository was tested on the following computers:

- Windows 11

At the time of creation, this code was built using `Python 3.11.0`

### Installation

1. Install `virtualenv`

```bash
# 1. Open a CMD terminal
# 2. Install virtualenv globally
pip install virtualenv
```

2. Create a virtual environment

```bash
python -m venv venv
```

3. Activate the virtual environment

```bash
# Windows
.\venv\Scripts\activate
# Mac
source venv/bin/activate
```

4. Install the required packages

```bash
pip install -r requirements.txt
```

5. Run the module

```bash
python main.py
```

## Walkthrough

### Code Structure

The code directory structure is as follows:

```plaintext
build-langchain-web-browsing-agent-with-mcp
└───agents
|   └──code_writer.py
|   └──critic.py
|   └──llm_backends.py
|   └──orchestrator.py
|   └──test_writer.py
│   .env
│   .gitignore
│   main.py
│   README.md
│   requirements.txt
```

The `main.py` file is the entry point of the self healing code generation agent.

The `agents/` folder contains functions that manage the construction of the multi-agent architecture.

The `.env` file contains the environment variables used by the application.

The `.gitignore` file specifies the files and directories that should be ignored by Git.

The `requirements.txt` file lists the Python packages required by the application.

### Tech stack

**AI**

- LLM: `OpenAI`
- Agentic framework: `Smolagents`

**Testing**

- Python: `pytest`

### Build from scratch

This project was built using Python, Smolagents and the OpenAI LLM. A simple text prompt is provided to the module which in turn generates an approriate code file, which is then reviewed and self healed by the multi agent framework until all tests pass.

#### 1. Create a virtual environment

```bash
python -m venv venv
```

#### 2. Activate the virtual environment

```bash
# Windows
.\venv\Scripts\activate
# Mac
source venv/bin/activate
```

#### 3. Install the required packages

```bash
pip install -r requirements.txt
```

#### 4. Write the backend

The backend is written in Python and uses the Smolagents framework to create a multi-agent architecture. The `agents/` folder contains the code for the agents, including the code writer, critic, and orchestrator.

First, we will create the `llm_backends.py` file in the `agents/` folder. This file contains the code for the LLM backends that will be used by the agents.

```python
# agents/llm_backends.py
from __future__ import annotations
import os
from smolagents import LiteLLMModel

def get_model():
    if os.getenv("OPENAI_API_KEY"):
        return LiteLLMModel(model_id="gpt-4o")
    raise RuntimeError("No LLM credentials found (OPENAI_API_KEY)")
```

##### 5. Create the agents

Next, we will create the `code_writer.py` file in the `agents/` folder. This code writer agent is responsible for generating code based on the provided prompt.

```python
# agents/code_writer.py
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
```

Next, we will create the `critic.py` file in the `agents/` folder. This critic agent is responsible for reviewing the generated code and providing feedback.

```python
# agents/critic.py
# agents/critic.py
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
```

Next, we will create the `test_writer.py` file in the `agents/` folder. This test writer agent is responsible for generating tests for the code.

```python
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
```

##### 6. Construct the orchestrator

Next, we will create the `orchestrator.py` file in the `agents/` folder. This orchestrator is responsible for managing the interactions between the agents.

````python
import re, subprocess, shutil
from pathlib import Path
from rich import print
from agents.code_writer import make_code_writer, SYSTEM_PROMPT as CW_PROMPT
from agents.test_writer import make_test_writer, SYSTEM_PROMPT as TW_PROMPT
from agents.critic import make_critic, SYSTEM_PROMPT as CR_PROMPT

WORK_DIR = Path(__file__).resolve().parents[1] / "work_dir"
CODE_FILE = WORK_DIR / "user_code.py"
TEST_FILE = WORK_DIR / "test_user_code.py"
_CODE_RE = re.compile(r"```(?:python)?\s*\n(.*?)```", re.S)

####################
# Helper functions #
####################

def _extract(src: str) -> str:
    m = _CODE_RE.search(src)
    return m.group(1) if m else src

def _run_pytest() -> tuple[bool, str]:
    "returns (all_passed, pytest_output)"
    result = subprocess.run(
        ["pytest", "-q"], cwd=WORK_DIR, capture_output=True, text=True
    )
    return result.returncode == 0, result.stdout + result.stderr

########################
# Self-correcting loop #
########################

def self_correcting_loop(spec: str, max_rounds: int = 5) -> str:
    if WORK_DIR.exists(): shutil.rmtree(WORK_DIR)
    WORK_DIR.mkdir(parents=True)

    cw = make_code_writer()
    tw = make_test_writer()
    crt = make_critic()

    # 1️⃣ draft code
    raw_code = cw.run(CW_PROMPT + "\n\n" + spec)
    CODE_FILE.write_text(_extract(raw_code).strip() + "\n")

    # 2️⃣ draft tests
    tests_task = (
        TW_PROMPT
        + "\n\nWrite tests for the following code:\n"
        + CODE_FILE.read_text()
    )
    raw_tests = tw.run(tests_task)
    TEST_FILE.write_text(_extract(raw_tests).strip() + "\n")

    for i in range(1, max_rounds + 1):
        passed, out = _run_pytest()
        print(f"[bold yellow]Round {i}[/]  –  tests pass? {passed}")
        if passed:
            return CODE_FILE.read_text()

        # 3️⃣ critic patches
        critic_task = (
            CR_PROMPT
            + "\n\nTests output:\n```\n"
            + out
            + "\n```\nCurrent code:\n```python\n"
            + CODE_FILE.read_text()
            + "\n```"
        )
        patch = crt.run(critic_task)
        CODE_FILE.write_text(_extract(patch).strip() + "\n")

    raise RuntimeError(f"Failed after {max_rounds} rounds")
````

##### 7. Setup the config files

The only config file that we need is the `.env` file. This file contains the environment variables used by the application. Create a file called `.env` in the root directory and add the following content:

```plaintext
OPENAI_API_KEY=your_openai_api_key
```

If you're running on Windows and you find issues related to `utf encoding`, running the following command in the terminal should fix it:

```bash
export PYTHONUTF8=1
```

##### 8. Create the Python module

Next, we will create the `main.py` file in the root directory. This file is the entry point of the application and is responsible for running the self-correcting loop.

```python
import sys, dotenv
from agents.orchestrator import self_correcting_loop

dotenv.load_dotenv() # loads .env into environment

if __name__ == "__main__":
    spec = sys.argv[1] if len(sys.argv) > 1 else "Write fibonacci(n)"
    final_code = self_correcting_loop(spec)
    print("\n✅  ALL TESTS PASS.  Final code ↓\n")
    print(final_code)
```

This completes the setup of our self healing code generation multi-agent!

Here are some example prompts you can use to test the module:

```python
python main.py "Implement quicksort(arr: list[int]) -> list[int] that returns a new sorted list. Do not use Python's built-in sort."
```

```python
python main.py "Implement slugify(text: str) -> str that lowercases, ascii-folds, replaces spaces with dashes and strips punctuation."
```

```python
python main.py "Write is_valid_sudoku(board: list[list[int]]) -> bool that returns True when a 9×9 board satisfies Sudoku rules. Zero denotes an empty cell."
```

## Happy coding! 🚀

```bash
🐢 Arun Godwin Patel @ Code Creations
```
