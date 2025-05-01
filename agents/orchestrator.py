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