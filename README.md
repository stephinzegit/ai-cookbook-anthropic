# ai-cookbook: Anthropic SDK version

Examples from Dave Ebbelaar's [ai-cookbook](https://github.com/daveebbelaar/ai-cookbook), rewritten for the Anthropic Python SDK (Claude) instead of the OpenAI SDK.

The folders mirror the original repository, so each file sits at the same path as the one it adapts.

## Sections

| Section | Original material | Files |
| --- | --- | --- |
| [`patterns/workflows`](patterns/workflows) | Video: [Building AI Agents in Pure Python - Beginner Course](https://www.youtube.com/watch?v=bZzyPscbtI8) | 7 |

The other sections of the original repository are not adapted yet.

## Setup

The project uses [uv](https://docs.astral.sh/uv/) and targets Python 3.14 or later. One environment at the root serves every section.

```bash
uv sync
cp .env.example .env
```

Then put your Anthropic API key in `.env`.

## Running the examples

Like the originals, the files are meant to be run step by step in an interactive window, to inspect the variables after each step. In VS Code: "Jupyter: Run Current File in Interactive Window".

They also run from a terminal:

```bash
cd patterns/workflows/1-introduction
uv run 3-tools.py
```

Run each file from inside its own folder: some of them open data files with a relative path.

Every run calls the Claude API and is billed to your API key. The model is set to `claude-sonnet-5-5` in each file.

## License

MIT, like the original repository. See [LICENSE](LICENSE): it keeps the copyright notice of the original repository, as the license requires.
