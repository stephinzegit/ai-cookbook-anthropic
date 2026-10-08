import json

import anthropic
import requests
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()
client = anthropic.Anthropic()


# --------------------------------------------------------------
# Define the tool (function) that we want to call
# --------------------------------------------------------------


def get_weather(latitude, longitude):
    """This is a publically available API that returns the weather for a given location."""
    response = requests.get(
        f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
    )
    data = response.json()
    return data["current"]


# --------------------------------------------------------------
# Step 1: Call model with get_weather tool defined
# --------------------------------------------------------------
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

system_prompt = "You are a helpful weather assistant."

messages = [
    {"role": "user", "content": "What's the weather like in Paris and Nice today?"},
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
# Step 3: Execute get_weather function
# --------------------------------------------------------------

# Append the assistant message once, before looping over the tool calls
messages += [{"role": "assistant", "content": response.content}]


def call_function(name, args):
    if name == "get_weather":
        return get_weather(**args)


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


messages += [{"role": "user", "content": tool_content}]

# --------------------------------------------------------------
# Step 4: Supply result and call model again
# --------------------------------------------------------------

# This assumes Claude requests both weather lookups in its first response.
# If it asks for another tool call here, parsed_output is None and step 5 fails.
# A complete solution repeats steps 3 and 4 in a while loop for as long as
# stop_reason is "tool_use": that is the agent loop.
# Kept as two calls to match the original file.


class CityWeather(BaseModel):
    city: str = Field(description="The name of the city.")
    temperature: float = Field(description="The current temperature in celsius.")


class WeatherResponse(BaseModel):
    cities: list[CityWeather] = Field(description="One entry per requested city.")
    response: str = Field(
        description="A natural language response to the user's question."
    )


response_2 = client.messages.parse(
    model="claude-sonnet-5-5",
    max_tokens=1024,
    system=system_prompt,
    tools=tools,
    tool_choice={"type": "auto"},
    messages=messages,
    output_format=WeatherResponse,
)


# --------------------------------------------------------------
# Step 5: Check model response
# --------------------------------------------------------------

final = response_2.parsed_output
for city in final.cities:
    print(f"{city.city}: {city.temperature}°C")

print(final.response)
