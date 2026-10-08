import anthropic
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()
client = anthropic.Anthropic()

# --------------------------------------------------------------
# Step 1: Define the response format in a Pydantic model
# --------------------------------------------------------------


class CalendarEvent(BaseModel):
    name: str
    date: str
    participants: list[str]


# --------------------------------------------------------------
# Step 2: Call the model
# --------------------------------------------------------------


response = client.messages.parse(
    model="claude-sonnet-5-5",
    max_tokens=1024,
    system="Extract the event information.",
    messages=[
        {
            "role": "user",
            "content": ("Alice and Bob are going to a science fair on Friday."),
        }
    ],
    output_format=CalendarEvent,
)


# --------------------------------------------------------------
# Step 3: Parse the response
# --------------------------------------------------------------

event = response.parsed_output
print(event.name)
print(event.date)
print(event.participants)
