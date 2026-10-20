"""
Tools: Enables agents to execute specific actions in external systems.
This component provides the capability to make API calls, database updates, file operations, and other practical actions.


More info: https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview
"""

import json

import anthropic
import requests


def get_weather(latitude, longitude):
    response = requests.get(
        f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m"
    )
    data = response.json()
    return data["current"]["temperature_2m"]


def call_function(name, args):
    if name == "get_weather":
        return get_weather(**args)
    raise ValueError(f"Unknown function: {name}")


def intelligence_with_tools(prompt: str) -> str:
    client = anthropic.Anthropic()

    tools = [
        {
            "name": "get_weather",
            "description": "Get current temperature for provided coordinates in celsius.",
            "strict": True,
            "input_schema": {
                "type": "object",
                "properties": {
                    "latitude": {
                        "type": "number",
                        "description": "The latitude of the location.",
                    },
                    "longitude": {
                        "type": "number",
                        "description": "The longitude of the location.",
                    },
                },
                "required": ["latitude", "longitude"],
                "additionalProperties": False,
            },
        }
    ]

    input_messages = [{"role": "user", "content": prompt}]

    # Step 1: Call model with tools
    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=1024,
        messages=input_messages,
        tools=tools,
        tool_choice={"type": "auto"},
    )

    # Step 2: Handle function calls
    if response.stop_reason == "tool_use":
        input_messages += [{"role": "assistant", "content": response.content}]
        tool_content = []
        for block in response.content:
            if block.type == "tool_use":
                # Step 3: Execute function
                result = call_function(block.name, block.input)

                # Step 4: Collect tool result
                tool_content.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result),
                    }
                )
        input_messages += [{"role": "user", "content": tool_content}]

        # Step 5: Get final response with function results
        final_response = client.messages.create(
            model="claude-sonnet-5",
            max_tokens=1024,
            messages=input_messages,
            tools=tools,
            tool_choice={"type": "auto"},
        )
    else:
        final_response = response

    return final_response.content[0].text


if __name__ == "__main__":
    result = intelligence_with_tools(prompt="What's the weather like in Paris today?")
    print("Tool Calling Output:")
    print(result)
