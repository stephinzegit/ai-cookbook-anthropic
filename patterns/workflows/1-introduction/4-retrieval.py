import json

import anthropic
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()
client = anthropic.Anthropic()

"""
docs: https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview
"""

# --------------------------------------------------------------
# Define the knowledge base retrieval tool
# --------------------------------------------------------------


def search_kb(question: str):
    """
    Load the whole knowledge base from the JSON file.
    (This is a mock function for demonstration purposes, we don't search)
    """
    with open("kb.json", "r") as f:
        return json.load(f)


# --------------------------------------------------------------
# Step 1: Call model with search_kb tool defined
# --------------------------------------------------------------
tools = [
    {
        "name": "search_kb",
        "description": (
            "Search the store's knowledge base. Covers the return policy, "
            "international shipping and payment methods. "
            "Do not use for questions unrelated to the store."
        ),
        "strict": True,
        "input_schema": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "The user's question",
                },
            },
            "required": ["question"],
            "additionalProperties": False,
        },
    }
]

system_prompt = "You are a helpful assistant that answers questions from the knowledge base about our e-commerce store."

messages = [
    {"role": "user", "content": "What is the return policy?"},
]

response = client.messages.create(
    model="claude-sonnet-5-5",
    max_tokens=1024,
    system=system_prompt,
    tools=tools,
    tool_choice={"type": "auto"},
    messages=messages,
)

# --------------------------------------------------------------
# Step 2: Model decides to call function(s)
# --------------------------------------------------------------

response.model_dump()  # Inspect the raw response: it contains the tool call(s)

# Print each requested tool call
for block in response.content:
    if block.type == "tool_use":
        print(f"Claude called {block.name} with {json.dumps(block.input)}")


# --------------------------------------------------------------
# Step 3: Execute search_kb function
# --------------------------------------------------------------

# Append the assistant message once, before looping over the tool calls
messages += [{"role": "assistant", "content": response.content}]


def call_function(name, args):
    if name == "search_kb":
        return search_kb(**args)


tool_content = []
for block in response.content:
    if block.type == "tool_use":
        name = block.name
        args = block.input

        result = call_function(name, args)
        tool_content.append(
            {
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": json.dumps(result),
            }
        )


# If Claude answers without calling the tool, tool_content is empty and the API
# rejects this empty user message.
messages += [{"role": "user", "content": tool_content}]


# --------------------------------------------------------------
# Step 4: Supply result and call model again
# --------------------------------------------------------------


class KBResponse(BaseModel):
    answer: str = Field(description="The answer to the user's question.")
    source: int = Field(description="The record id of the answer.")


response_2 = client.messages.parse(
    model="claude-sonnet-5-5",
    max_tokens=1024,
    system=system_prompt,
    tools=tools,
    tool_choice={"type": "auto"},
    messages=messages,
    output_format=KBResponse,
)


# --------------------------------------------------------------
# Step 5: Check model response
# --------------------------------------------------------------

final = response_2.parsed_output
print(final.answer)
print(final.source)


# --------------------------------------------------------------
# Question that doesn't trigger the tool
# --------------------------------------------------------------

messages = [
    {"role": "user", "content": "What is the weather in Tokyo?"},
]

response_3 = client.messages.create(
    model="claude-sonnet-5-5",
    max_tokens=1024,
    system=system_prompt,
    tools=tools,
    tool_choice={"type": "auto"},
    messages=messages,
)

response_3.model_dump()

for block in response_3.content:
    if block.type == "text":
        print(block.text)
