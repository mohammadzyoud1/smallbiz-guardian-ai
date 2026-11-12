import re
NUMBER = re.compile(r"-?\d[\d,]*\.?\d*")
SKIP = re.compile(
    r"\b\d+\s*-?\s*weeks?\b|\bweeks?\s+\d+\b|\b\d+\s*k\b|\b\d+\s+(?:practical\s+)?(?:options|scenarios|flags)\b",
    re.IGNORECASE,
)
def collect_values(data, out=None):
    out = [] if out is None else out
    if isinstance(data, dict):
        for value in data.values():
            collect_values(value, out)
    elif isinstance(data, (list, tuple)):
        for value in data:
            collect_values(value, out)
    elif isinstance(data, (int, float)) and not isinstance(data, bool):
        out.append(float(data))
    return out


def check_answer(answer, tool_outputs, tolerance=1.0):
    allowed = collect_values(tool_outputs)
    unsupported = []
    for number in numbers_in(answer):
        if not any(
            abs(abs(number) - abs(value)) <= tolerance or abs(abs(number) - abs(value) * 100) <= tolerance
            for value in allowed
        ):      
            unsupported.append(number)
    return {"faithful": not unsupported, "unsupported_numbers": unsupported}

def numbers_in(text):
    text = text.replace("–", "-").replace("−", "-").replace("—", "-").replace("‑", "-")
    text = re.sub(r"-\s*\$", "-", text)
    text = SKIP.sub(" ", text)
    found = []
    for match in NUMBER.findall(text):
        cleaned = match.replace(",", "").rstrip(".")
        if cleaned and cleaned != "-":
            try:
                found.append(float(cleaned))
            except ValueError:
                pass
    return found