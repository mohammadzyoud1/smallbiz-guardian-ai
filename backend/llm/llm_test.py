import json
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL = "openai/gpt-oss-20b" #model from Groq's docs

def get_forecast(week: int) -> dict:
    return {"week": week, "ending_cash": 1234}

tools = [{
    "type": "function",
    "function": {
        "name": "get_forecast",
        "description": "TODO",
        "parameters": {
            "type": "object",
            "properties": {"week": {"type": "integer"}},
            "required": ["week"],
        },
    },
}]

messages = [{"role": "user", "content": "What is the forecast for week 6?"}]

# 1. First call: the model should ask to use the tool
response = client.chat.completions.create(
    model=MODEL, messages=messages, tools=tools
)
msg = response.choices[0].message
print("Tool calls:", msg.tool_calls)
if msg.tool_calls:
    messages.append(msg)  # the model's own tool request

    for call in msg.tool_calls:
        args = json.loads(call.function.arguments)   # {"week": 6}
        result = get_forecast(args["week"])                  # BLANK 1: pass the week
        messages.append({
            "role": "tool",
            "tool_call_id": call.id,                    # BLANK 2: the call's id
            "content": json.dumps(result),
        })

    final = client.chat.completions.create(
        model=MODEL, messages=messages, tools=tools
    )
    print("Answer:", final.choices[0].message.content)