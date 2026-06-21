# image-gen

**Generate AI images on your existing ChatGPT plan — right inside Claude Code. No API key, no browser, no copy-paste.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
&nbsp;·&nbsp; **English** | [中文](#中文)

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

```bash
python3 scripts/generate.py "<prompt>" [options]
```

| Option | Default | Description |
|---|---|---|
| `-o, --out PATH` | `assets/generated/image.png` | Output PNG path |
| `-q, --quality` | `auto` | `auto` \| `low` \| `medium` \| `high` |
| `-s, --size` | `auto` | `auto` \| `WIDTHxHEIGHT` \| `square`/`portrait`/`landscape`/`wide`/`tall` \| `1:1`/`2:3`/`3:2`/`16:9`/`9:16` |
| `--proxy HOST:PORT` | _(none)_ | Proxy for region-blocked networks (or `none`) |
| `--timeout N` | `240` | Seconds per attempt |

The saved file path is printed to stdout. When invoked as a skill, `SKILL.md` tells Claude how to map your wording to `--quality` / `--size` automatically.

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

---

# 中文

**用你现有的 ChatGPT 订阅额度生成 AI 图片 —— 直接在 Claude Code 里完成。无需 API key，无需开浏览器，无需复制粘贴。**

[English](#image-gen) | **中文**

## 这个仓库要解决的痛点

你是个重度 **Claude Code** 用户。写代码写到一半 —— 一个 HTML 落地页、一份 PPT、一个 README —— 突然需要一张好看的图。以前的流程是这样的：

1. 让 Claude（或 ChatGPT）**写一段生成图片的 prompt**
2. 打开浏览器进 **chatgpt.com**
3. 把 prompt **复制粘贴**进去 → 等待 → 生成
4. **下载** PNG
5. 再把图片文件 **拷回** 本地项目仓库
6. 接进你的 HTML / PPT 里

每生成一张图，都要跳出终端、来回复制粘贴，彻底打断心流。

## 解决方案

如果你 **已经是 ChatGPT 订阅用户**，那你本地的官方 **`codex` CLI** 就能用你的订阅额度直接调用 **`gpt-image-2`** —— **不需要 `OPENAI_API_KEY`，也不按张收费。** 这个 skill 让 **Claude Code 直接调用它：**

> *"给这个落地页画一张宽幅 banner"* → 图片直接生成并 **保存到 `assets/`** —— 不开浏览器、不复制粘贴、不用下载。

Claude 负责写出丰富的 prompt，用 **你的 ChatGPT 额度** 生成图片，并把文件直接放到你需要的位置。

```
以前：  Claude Code → 写 prompt → 🌐 chatgpt.com → 生成 → 下载 → 拖回仓库
现在：  Claude Code → image-gen skill → codex → gpt-image-2 → ✅ 直接存进你的仓库
```

## 工作原理（以及为什么安全）

它通过 **调用官方的 OpenAI `codex` 二进制** 来工作 —— 也就是那个本来就持有你 ChatGPT 登录凭证的程序。本封装 **从不打开 `~/.codex/auth.json`**，也不碰你的 token；它运行 `codex` 的方式和你自己手敲完全一样。

| 做法 | 谁会读你的 `~/.codex/auth.json` |
|---|---|
| 自己读取 token 再去调 OpenAI 后端 | **第三方脚本** 拿到了你永不过期的 `refresh_token` |
| **本 skill** —— 调用官方 `codex` | **只有 OpenAI 自己的二进制**（它本来就有） |

图片以 base64 形式回传，存在 codex 本地的会话日志里；封装脚本从最新的 `~/.codex/sessions/**/rollout-*.jsonl` 中读取 `image_generation_call.result` 并解码 —— **确定性提取**，绝不依赖 agent 去"自己保存文件"。

## 环境要求

- **[OpenAI Codex CLI](https://developers.openai.com/codex/cli)** —— `npm i -g @openai/codex`
- 一个 **ChatGPT 订阅**（Plus / Pro / Team / Enterprise），并已 `codex login` 登录
- **Python 3.10+**（仅用标准库，无需 `pip install`）

> 内置图片生成会占用你订阅套餐的用量额度，消耗速度约为纯文本回合的 3–5 倍。

## 安装

Claude Code 的个人 skill 放在 `~/.claude/skills/`：

```bash
git clone https://github.com/RaphLorr/claude-skill-image-gen ~/.claude/skills/image-gen
```

之后在 Claude Code 里直接说"画张图"即可自动触发；也可以直接命令行运行脚本。

## 用法

```bash
python3 scripts/generate.py "<提示词>" [选项]
```

| 选项 | 默认值 | 说明 |
|---|---|---|
| `-o, --out PATH` | `assets/generated/image.png` | 输出 PNG 路径 |
| `-q, --quality` | `auto` | `auto` \| `low` \| `medium` \| `high` |
| `-s, --size` | `auto` | `auto` \| `宽x高` \| `square`/`portrait`/`landscape`/`wide`/`tall` \| `1:1`/`2:3`/`3:2`/`16:9`/`9:16` |
| `--proxy HOST:PORT` | _（无）_ | 受限网络下的代理（或 `none`） |
| `--timeout N` | `240` | 每次尝试的超时秒数 |

保存路径会打印到 stdout。作为 skill 调用时，`SKILL.md` 会指导 Claude 自动把你的措辞映射到 `--quality` / `--size`。

### 在防火墙后面？（如中国大陆）

如果你的网络无法直连 OpenAI 后端，让 codex 走本地代理：

```bash
export IMAGE_GEN_PROXY="127.0.0.1:7890"   # 你的本地代理 host:port
# 或单次调用：  --proxy 127.0.0.1:7890
```

出现 `Connection reset by peer` 错误，说明当前没有可用的 OpenAI 路由。

## 注意事项

- 会消耗你的 ChatGPT 套餐额度，并不豁免用量限制。
- 依赖 codex 本地会话日志的格式来提取图片 —— 未来 codex 版本可能改变该格式。
- 本项目与 OpenAI 无任何关联，亦未获其背书。"ChatGPT"、"Codex"、"gpt-image" 均为 OpenAI 的商标。

## 许可证

MIT —— 见 [LICENSE](LICENSE)。
