import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_prompt import SYSTEM_PROMPT
from dotenv import load_dotenv
from llm.llm_provider import GroqProvider

load_dotenv()
messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": "My cash is 9,500 and I pay 3,000 rent next week. Should I take a loan?"},
]
print(GroqProvider().chat(messages, tools=[])["text"])