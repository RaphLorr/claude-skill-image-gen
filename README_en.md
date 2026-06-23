# image-gen

**Generate AI images on your existing ChatGPT plan — right inside Claude Code. No API key, no browser, no copy-paste.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
&nbsp;·&nbsp; **English** | [中文](README.md)

---

## The pain this solves

You're a heavy **Claude Code** user. Mid-build — an HTML landing page, a slide deck, a README — you suddenly need a nice image. Today the loop looks like this:

1. Ask Claude (or ChatGPT) to **write an image prompt**
2. Open **chatgpt.com** in the browser
3. **Paste** the prompt → wait → generate
4. **Download** the PNG
5. **Copy / move** the file back into your project repo
6. Wire it into your HTML / PPT

Every single image yanks you out of the terminal and breaks your flow.

## The fix

If you **already pay for ChatGPT**, you already have the official **`codex` CLI**, and codex can call **`gpt-image-2`** on your subscription — **no `OPENAI_API_KEY`, no per-image fee.** This skill lets **Claude Code call it directly:**

> *"draw a wide hero banner for this landing page"* → the image is generated and **saved straight into `assets/`** — no browser, no copy-paste, no download.

Claude writes the rich prompt, generates the image on **your ChatGPT quota**, and drops the file exactly where you need it.

```
Before:  Claude Code → write prompt → 🌐 chatgpt.com → generate → download → drag into repo
After:   Claude Code → image-gen skill → codex → gpt-image-2 → ✅ saved in your repo
```

## How it works (and why it's safe)

It **shells out to the official OpenAI `codex` binary** — the one that already holds your ChatGPT auth. The wrapper **never opens `~/.codex/auth.json`** and never touches your tokens; it runs `codex` exactly like you would.

| Approach | Who reads your `~/.codex/auth.json` |
|---|---|
| Read the token & call OpenAI's backend yourself | a **third-party script** holds your non-expiring `refresh_token` |
| **This skill** — shell out to official `codex` | **only OpenAI's own binary** (which already has it) |

The image comes back as base64 inside codex's local session log; the wrapper reads `image_generation_call.result` from the newest `~/.codex/sessions/**/rollout-*.jsonl` and decodes it — **deterministic**, never trusting the agent to "save the file."

## Requirements

- **[OpenAI Codex CLI](https://developers.openai.com/codex/cli)** — `npm i -g @openai/codex`
- A **ChatGPT plan** (Plus / Pro / Team / Enterprise), logged in via `codex login`
- **Python 3.10+** (standard library only — nothing to `pip install`)

> Built-in image generation runs on your plan's usage limits and uses them ~3–5× faster than text-only turns.

## Install

Personal Claude Code skills live in `~/.claude/skills/`:

```bash
git clone https://github.com/RaphLorr/claude-skill-image-gen ~/.claude/skills/image-gen
```

Then just ask Claude Code for an image — the skill auto-triggers. Or run the script directly.

## Usage

Once installed, just **ask Claude Code in plain language** — the skill auto-triggers and you don't memorize any commands:

> 💬 "draw a wide hero banner for this landing page, techy feel"
> 💬 "a flat square robot avatar — draft quality is fine"
> 💬 "generate a detailed watercolor cat for my README, portrait"
> 💬 "in the style of this image, draw a matching cat logo" (image-to-image)
> 💬 "turn this photo into an editorial studio portrait, keep the person" (image edit)

Claude does the rest: **writes a rich prompt → picks quality / size / effort → calls the skill → saves the image straight into your project**, then tells you the path.

How the options get chosen is driven by the rules in `SKILL.md`; Claude maps your wording automatically:

| When you say… | Claude picks |
|---|---|
| "detailed / photorealistic / hi-res / for print" | `--quality high` |
| "quick / draft / placeholder" | `--quality low` |
| "banner / header / scenery / wide" | `--size landscape` |
| "poster / phone wallpaper / tall" | `--size portrait` |
| "avatar / icon / square" | `--size square` |
| "complex scene / text in the image / careful edit" | `--effort high` |

<details>
<summary><b>Advanced: direct CLI (optional)</b></summary>

You can also run the script yourself, without the agent:

```bash
python3 scripts/generate.py "<prompt>" [options]
```

| Option | Default | Description |
|---|---|---|
| `-o, --out PATH` | `assets/generated/image.png` | Output PNG path |
| `-q, --quality` | `auto` | `auto` \| `low` \| `medium` \| `high` |
| `-s, --size` | `auto` | `auto` \| `WIDTHxHEIGHT` \| `square`/`portrait`/`landscape`/`wide`/`tall` \| `1:1`/`2:3`/`3:2`/`16:9`/`9:16` |
| `-r, --ref PATH` | _(none)_ | Reference image (repeatable); image-to-image — the prompt decides style-vs-edit |
| `-e, --effort` | `low` | `low` \| `medium` \| `high` \| `xhigh` — model reasoning before the render (prompt planning, not pixel quality). Raise for complex prompts/in-image text/`--ref` edits |
| `--proxy HOST:PORT` | _(none)_ | Proxy for region-blocked networks (or `none`) |
| `--timeout N` | auto | Seconds per attempt; auto-scales with size (300s, up to 600s for 2K/4K) |

The saved file path is printed to stdout.
</details>

### Behind a firewall? (e.g. mainland China)

If OpenAI's backend is unreachable from your network, route codex through a local proxy:

```bash
export IMAGE_GEN_PROXY="127.0.0.1:7890"   # your local proxy host:port
# or per call:  --proxy 127.0.0.1:7890
```

A `Connection reset by peer` error means there's no working route to OpenAI.

## Caveats

- Consumes your ChatGPT plan quota; not exempt from usage limits.
- Reads codex's local session-log format to extract the image — a future codex release could change that.
- Not affiliated with or endorsed by OpenAI. "ChatGPT", "Codex", and "gpt-image" are trademarks of OpenAI.

## License

MIT — see [LICENSE](LICENSE).
