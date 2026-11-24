import json
import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()
# Select the language model
# Initialize the Groq client using the API key

client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL = "openai/gpt-oss-20b" #model from Groq's docs

# Function that returns the cash forecast for a given week
def get_forecast(week: int) -> dict:
    return {"week": week, "ending_cash": 1234}

# Define the tool that the model is allowed to call
tools = [{
    "type": "function",
    "function": {
        "name": "get_forecast",
        "description": "TODO", # Describe what the tool does
        "parameters": {
            "type": "object",
            "properties": {"week": {"type": "integer"}}, # The week number to forecast
            "required": ["week"],  # The model must provide a week number
        },
    },
}]

# Send the user's question to the model
messages = [{"role": "user", "content": "What is the forecast for week 6?"}]

# 1. First call: the model should ask to use the tool
response = client.chat.completions.create(
    model=MODEL, messages=messages, tools=tools
)
# Extract the assistant's response

msg = response.choices[0].message
# Display any tool calls requested by the model
print("Tool calls:", msg.tool_calls)

# Continue only if the model requested a tool
if msg.tool_calls:
    messages.append(msg)  # Add the assistant's tool request to the conversation history

    for call in msg.tool_calls:
        # Convert the tool arguments from JSON text into a Python dictionary
        args = json.loads(call.function.arguments)  
        # Call the actual Python function using the arguments provided by the model
        result = get_forecast(args["week"]) 
        # Send the tool result back to the conversation                
        messages.append({
            "role": "tool",
            "tool_call_id": call.id,     # Connect the result to the correct tool call                 
            "content": json.dumps(result),  # Convert the result into JSON text
        })
    # Second API Call: Model Generates the Final Answer
    # Send the updated conversation, including the tool result, back to the model
    final = client.chat.completions.create(
        model=MODEL, messages=messages, tools=tools
    )
    # Display the model's final natural-language answer
    print("Answer:", final.choices[0].message.content)