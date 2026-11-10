import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv
from llm.llm_provider import GroqProvider

load_dotenv()
provider = GroqProvider()
answer = provider.chat([{"role": "user", "content": "Reply with one short sentence: what is cash flow?"}], tools=[])
print(answer)