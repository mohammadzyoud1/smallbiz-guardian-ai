import json
import os


class Provider:
    """What the agent needs from any language model."""

    def chat(self, messages, tools):
        raise NotImplementedError


class GroqProvider(Provider):
    def __init__(self, model="openai/gpt-oss-20b"):
        from groq import Groq

        self.client = Groq(api_key=os.environ["GROQ_API_KEY"])
        self.model = model

    def chat(self, messages, tools):
        import groq

        arguments = {"model": self.model, "messages": messages}
        if tools:
            arguments["tools"] = tools

        response = None
        for attempt in range(3):
            try:
                response = self.client.chat.completions.create(**arguments)
                break
            except groq.BadRequestError:
                if attempt == 2:
                    raise

        message = response.choices[0].message
        calls = []
        for call in message.tool_calls or []:
            calls.append({
                "id": call.id,
                "name": call.function.name,
                "arguments": json.loads(call.function.arguments),
            })
        return {
            "text": message.content or "",
            "tool_calls": calls,
            "tokens": response.usage.total_tokens,
        }

class FakeProvider(Provider):
    """Replays scripted replies, so tests need no API key."""

    def __init__(self, replies):
        self.replies = list(replies)

    def chat(self, messages, tools):
        reply = self.replies.pop(0)
        return {
            "text": reply.get("text", ""),
            "tool_calls": reply.get("tool_calls", []),
            "tokens": reply.get("tokens", 0),          
        }