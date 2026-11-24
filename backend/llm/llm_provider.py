import json
import os
import time


# Base Provider Interface
class Provider:
    """What the agent needs from any language model."""

    def chat(self, messages, tools):
        # Each provider must implement its own chat method
        raise NotImplementedError

# Groq Provider
class GroqProvider(Provider):
    # Initialize the Groq client and select the language model
    def __init__(self, model="openai/gpt-oss-120b"):
        from groq import Groq
        # Read the API key securely from the environment variables
        self.client = Groq(api_key=os.environ["GROQ_API_KEY"])
        self.model = model

    # Send messages and optional tools to the Groq model
    def chat(self, messages, tools):
        import groq

         # Prepare the API request

        arguments = {"model": self.model, "messages": messages}

        # Include tool definitions only when tools are provided

        if tools:
            arguments["tools"] = tools

        response = None

        # Retry the request if rate limits or certain request errors occur

        for attempt in range(5):
            try:
                response = self.client.chat.completions.create(**arguments)
                break

            # Wait before retrying when the API rate limit is reached

            except groq.RateLimitError:
                time.sleep(20)

            # Retry certain bad requests, then raise the error

            except groq.BadRequestError:
                if attempt >= 2:
                    raise
        # Raise an error if no response was received after the retries

        if response is None:
            raise RuntimeError("The model did not answer after several tries.")

        # Extract the assistant's response message

        message = response.choices[0].message

         # Extract tool calls requested by the model

        calls = []
        for call in message.tool_calls or []:
            calls.append({
                "id": call.id,
                "name": call.function.name,
                "arguments": json.loads(call.function.arguments),
            })

        # Return a standardized response for the application

        return {
            "text": message.content or "",
            "tool_calls": calls,
            "tokens": response.usage.total_tokens,
        }

# Fake Provider for Testing

class FakeProvider(Provider):
    """Replays scripted replies, so tests need no API key."""

    def __init__(self, replies):
        self.replies = list(replies)

    def chat(self, messages, tools):
        # Retrieve and remove the next reply from the list
        
        reply = self.replies.pop(0)
        return {
            "text": reply.get("text", ""),
            "tool_calls": reply.get("tool_calls", []),
            "tokens": reply.get("tokens", 0),          
        }