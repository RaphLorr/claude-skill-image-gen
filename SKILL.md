---
name: image-gen
description: >-
  Generate an image from a text prompt using OpenAI gpt-image-2 through the
  local codex CLI — uses the user's ChatGPT plan quota, requires NO
  OPENAI_API_KEY. Use whenever the user asks to generate, create, draw, render,
  paint, or make an image, picture, illustration, logo, icon, banner, avatar,
  or artwork.
---

# Image generation (gpt-image-2 via codex CLI)

Generate a real AI image by running the wrapper, which shells out to the
official `codex` binary (it already holds the ChatGPT auth) and saves a PNG:

```bash
python3 ~/.claude/skills/image-gen/scripts/generate.py "<detailed prompt>" \
  --out <path/to/image.png> [--quality <q>] [--size <s>] [--ref <image>]
```

The script prints the saved file path on stdout. Show or embed it in your reply
(e.g. `![result](path)`) so the user can view it.

## Writing the prompt
Always expand the user's request into a rich, specific prompt: subject, style,
composition, lighting, colours, mood. gpt-image-2 rewards specificity.

## Choosing `--out`
Always pass a descriptive path under the current project (e.g.
`assets/hero-banner.png`) so successive images don't overwrite each other.

## Choosing `--quality` (default: `auto`)
- `high` — user asks for "detailed", "photorealistic", "high-res", "print",
  "polished", a hero image, or final artwork.
- `low` — user asks for a "quick", "draft", "rough", or "placeholder" image.
- `medium` — explicitly asked for medium, or a balance of speed and detail.
- omit (auto) — no quality signal in the request.

Higher quality costs more quota and time; don't default to `high`.

## Choosing `--size` (default: `auto`)
Pick from the user's intent; pass an aspect keyword, a ratio, or exact pixels:
- `landscape` / `16:9` / `wide` — banners, headers, scenery, desktop wallpaper.
- `portrait` / `2:3` / `tall` — posters, phone wallpaper, full-body subjects.
- `square` / `1:1` — avatars, icons, app art, social posts.
- `WIDTHxHEIGHT` (e.g. `1024x1024`) — when the user gives exact dimensions.
- omit (auto) — let the model choose.

## Reference image — `--ref <path>` (image-to-image)
Pass an existing image with `--ref <path>` (repeatable). There is **no mode flag**
— the **prompt decides** how the reference is used, so always make the intent
explicit in the prompt you write:
- **Style transfer (new subject):** "in the style of the attached image, draw a
  NEW …" — e.g. a cat logo styled like a reference fox logo.
- **Edit / keep the subject:** "edit the attached photo, KEEP the same
  person/subject, change only …" — e.g. turn a snapshot into a studio portrait.

Examples
- "make a cat logo in the same style as this fox" →
  `… "a flat geometric cat-head logo, new subject: a cat, in the style of the attached image" --ref fox.png --size square`
- "turn my photo into an editorial studio portrait" →
  `… "edit the attached photo, keep the same person; elevated editorial studio portrait, soft directional light, complementing background" --ref me.jpg --size portrait --quality high`

## Examples
- "draw a detailed watercolor cat for my wall" →
  `… "a highly detailed watercolor painting of a fluffy cat, soft light" --quality high --size portrait`
- "quick square robot avatar" →
  `… "a friendly cartoon robot mascot, flat vector, white background" --quality low --size square`
- "a wide banner of a mountain sunrise" →
  `… "a serene mountain sunrise, golden light, layered peaks, mist" --size 16:9`

## Requirements & behaviour
- Requires `codex login` to have been run once (`~/.codex/auth.json`). This
  wrapper never reads that file — only the official `codex` binary does.
- Consumes the user's **ChatGPT plan quota**, ~**3–5× the tokens** of a text
  turn. Don't batch-generate casually.
- **Proxy (this machine):** routes through `127.0.0.1:10808` by default — you do
  NOT need to pass `--proxy`. If generation fails with a "Connection reset" or
  timeout error, the proxy is off: run `proxy_on` first, then retry. Override the
  route with `--proxy host:port` / `IMAGE_GEN_PROXY`, or disable with `--proxy none`.
- Generation takes ~30–90s; the script retries once if the connection stalls.
