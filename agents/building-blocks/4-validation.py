"""
Validation: Ensures LLM outputs match predefined data schemas.
This component provides schema validation and structured data parsing to guarantee consistent data formats for downstream code.

More info: https://platform.claude.com/docs/en/build-with-claude/structured-outputs
"""

import anthropic
from pydantic import BaseModel


class TaskResult(BaseModel):
    """
    More info: https://docs.pydantic.dev
    """

    task: str
    completed: bool
    priority: int


def structured_intelligence(prompt: str) -> TaskResult:
    client = anthropic.Anthropic()
    response = client.messages.parse(
        model="claude-sonnet-5",
        max_tokens=1024,
        system="Extract task information from the user input.",
        messages=[
            {"role": "user", "content": prompt},
        ],
        output_format=TaskResult,
    )
    return response.parsed_output


if __name__ == "__main__":
    result = structured_intelligence(
        "I need to complete the project presentation by Friday, it's high priority"
    )
    print("Structured Output:")
    print(result.model_dump_json(indent=2))
    print(f"Extracted task: {result.task}")
