# Building AI Agents in Pure Python: Anthropic SDK version

The code examples from Dave Ebbelaar's video [Building AI Agents in Pure Python - Beginner Course](https://www.youtube.com/watch?v=bZzyPscbtI8), rewritten for the Anthropic Python SDK (Claude) instead of the OpenAI SDK.

The original code is in [patterns/workflows](https://github.com/daveebbelaar/ai-cookbook/tree/main/patterns/workflows) in Dave's ai-cookbook repository. The patterns come from Anthropic's article [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents).

The files keep the names, step headings and examples of the originals, so the two versions can be read side by side. Setup and run instructions are in the [root README](../../README.md).

## Contents

| File | What it shows |
| --- | --- |
| `1-introduction/1-basic.py` | A single call to the model |
| `1-introduction/2-structured.py` | Structured output with a Pydantic model |
| `1-introduction/3-tools.py` | Tool use: the model asks for a function call, the code runs it and sends the result back |
| `1-introduction/4-retrieval.py` | The same mechanism with a knowledge base lookup (`kb.json`) |
| `2-workflow-patterns/1-prompt-chaining.py` | Three chained calls with a gate check in between |
| `2-workflow-patterns/2-routing.py` | One call classifies the request, the code routes it to a handler |
| `2-workflow-patterns/3-parallelization.py` | Two checks run concurrently with `asyncio.gather` |

`4-orchestrator.py` from the original repository is not covered in the video and is not included.

## OpenAI to Anthropic cheat sheet

| OpenAI SDK (original) | Anthropic SDK (this repository) |
| --- | --- |
| `client.chat.completions.create(...)` | `client.messages.create(...)` |
| `client.beta.chat.completions.parse(..., response_format=Model)` | `client.messages.parse(..., output_format=Model)` |
| `completion.choices[0].message.parsed` | `message.parsed_output` |
| System prompt as a `{"role": "system"}` message | `system=` parameter |
| `max_tokens` optional | `max_tokens` required |
| Tool defined as `{"type": "function", "function": {..., "parameters": {...}}}` | Tool defined as `{"name", "description", "input_schema"}` |
| `message.tool_calls`, with arguments as a JSON string | `tool_use` blocks in `message.content`, with `input` already a dict |
| Tool result sent as a `{"role": "tool"}` message | Tool result sent as a `tool_result` block inside a `user` message |
| `AsyncOpenAI` | `AsyncAnthropic` |

## Differences from the original, beyond the SDK

- **`3-tools.py`** asks about two cities, so the model requests two tool calls. The assistant message is appended once, before the loop over the tool calls, and all the results go back in a single `user` message. The output schema returns a list of cities instead of one temperature.
- **`4-retrieval.py`** uses a more specific tool description. With the original one, Claude called the knowledge base tool even for the unrelated weather question at the end of the file.
- **`1-prompt-chaining.py`** sends the event details to the last call with `model_dump_json()`.
- **`1-prompt-chaining.py` and `2-routing.py`** end with a step-by-step block that runs each call on its own, to inspect its output.
- **`3-parallelization.py`** uses `nest_asyncio2` instead of `nest_asyncio`. With the original package, the cell hung in the VS Code interactive window on Python 3.14. The file name is also spelled out in full.
