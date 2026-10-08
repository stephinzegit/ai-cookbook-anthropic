import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-sonnet-5-5",
    max_tokens=1000,
    system="You're a helpful assistant.",
    messages=[
        {
            "role": "user",
            "content": "Write a limerick about the Python programming language.",
        }
    ],
)

for block in message.content:
    if block.type == "text":
        print(block.text)
