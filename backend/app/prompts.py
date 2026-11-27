import json
import re

from app.tasksets import DATA_DIR

_CONFIG = json.loads((DATA_DIR / "conditions.json").read_text(encoding="utf-8"))

SYSTEM_PROMPT: str = _CONFIG["system"]
# analyser_repair is in the pilot config but needs the repair loop, which is not built yet.
SUPPORTED_CONDITIONS = ("baseline", "security_prefix")


def build_prompt(condition: str, task_prompt: str) -> str:
    if condition not in SUPPORTED_CONDITIONS:
        raise ValueError(f"unsupported condition: {condition}")
    return _CONFIG["conditions"][condition]["template"].format(task_prompt=task_prompt)


# Same rule as the pilot script, so counts stay comparable: longest Python block, else everything.
def extract_code(response: str) -> str:
    blocks = re.findall(r"```(?:python|py)?\s*\n(.*?)```", response, re.S)
    return max(blocks, key=len) if blocks else response
