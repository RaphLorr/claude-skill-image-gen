# image-gen — a Claude Code skill for AI images on your ChatGPT plan

Generate images with **OpenAI gpt-image-2** from inside Claude Code (or any
agent), using **your ChatGPT subscription quota** — **no `OPENAI_API_KEY`, no
third-party API, no per-image fees.**

It works by shelling out to the **official OpenAI `codex` CLI**, which has a
built-in image generation tool. Just ask Claude *"draw me a logo of a fox"* and
it runs the wrapper and saves a PNG.

```bash
python3 scripts/generate.py "a serene mountain sunrise, golden light, mist" \
  --out sunrise.png --quality high --size 16:9
```

## Why this design (trust model)

There are two ways to use your ChatGPT plan for images:

| Approach | Who reads your `~/.codex/auth.json` |
|---|---|
| Read the token + call OpenAI's backend yourself | **a third-party script** holds your non-expiring `refresh_token` |
| **This skill** — shell out to the official `codex` binary | **only OpenAI's own binary** (which already has it) |

This wrapper **never opens `auth.json`** and never handles your tokens. It only
spawns `codex`, exactly like running it yourself — so there's no third-party
supply-chain surface around your credentials.

The image itself comes back as base64 inside codex's local session log; the
wrapper reads `image_generation_call.result` out of the newest
`~/.codex/sessions/**/rollout-*.jsonl` and decodes it. This is **deterministic**
— it never trusts the agent to "save the file," which is unreliable.

## Requirements

- **[OpenAI Codex CLI](https://developers.openai.com/codex/cli)** — `npm i -g @openai/codex`
- A **ChatGPT plan** (Plus / Pro / Team / Enterprise), logged in via `codex login`
- **Python 3.10+** (standard library only — no pip install)

> Built-in image generation runs on your plan's usage limits and uses them
> ~3–5× faster than text-only turns. See OpenAI's
> [Codex image generation docs](https://developers.openai.com/codex/cli/features).

## Install

**As a Claude Code skill** (personal skills live in `~/.claude/skills/`):

```bash
git clone https://github.com/<you>/claude-skill-image-gen ~/.claude/skills/image-gen
```

Then in Claude Code, just ask for an image — the skill auto-triggers. Or run the
script directly from anywhere.

## Usage

```
python3 scripts/generate.py "<prompt>" [options]
```

| Option | Default | Description |
|---|---|---|
| `-o, --out PATH` | `assets/generated/image.png` | Output PNG path |
| `-q, --quality`  | `auto` | `auto` \| `low` \| `medium` \| `high` |
| `-s, --size`     | `auto` | `auto` \| `WIDTHxHEIGHT` \| `square`/`portrait`/`landscape`/`wide`/`tall` \| `1:1`/`2:3`/`3:2`/`16:9`/`9:16` |
| `--proxy HOST:PORT` | _(none)_ | Proxy for region-blocked networks (or `none`) |
| `--timeout N` | `240` | Seconds per attempt |

The saved file path is printed to stdout.

### Region-blocked networks

If OpenAI's backend is unreachable from your location, route codex through a
local proxy:

```bash
export IMAGE_GEN_PROXY="127.0.0.1:7890"   # your local proxy host:port
# or per-call:  --proxy 127.0.0.1:7890
```

A `Connection reset by peer` error means there's no working route to OpenAI.

## Caveats

- Consumes your ChatGPT plan quota; not free of usage limits.
- Reads codex's local session-log format to extract the image — if a future
  codex release changes that format, the extraction may need updating.
- Not affiliated with or endorsed by OpenAI. "ChatGPT", "Codex" and
  "gpt-image" are trademarks of OpenAI.

## License

MIT — see [LICENSE](LICENSE).
