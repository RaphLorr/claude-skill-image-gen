# image-gen

**用你现有的 ChatGPT 订阅额度生成 AI 图片 —— 直接在 Claude Code 里完成。无需 API key，无需开浏览器，无需复制粘贴。**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
&nbsp;·&nbsp; [English](README_en.md) | **中文**

---

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

装好后，在 Claude Code 里 **直接用自然语言提需求** 即可 —— skill 会自动触发，你不用记任何命令：

> 💬 "给这个落地页画一张宽幅 banner，科技感一点"
> 💬 "画个扁平风格的方形机器人头像，草图质量就行"
> 💬 "给 README 生成一张精致的水彩猫，竖版"
> 💬 "参考这张图的风格，画一个同款的猫 logo"（图生图）
> 💬 "把这张照片改成杂志写真风，保留人物"（图生图·改图）

Claude 会自动完成：**写出丰富的 prompt → 选好质量/尺寸 → 调用 skill → 把图片直接存进你的项目**，然后把保存路径告诉你。

参数怎么选由 `SKILL.md` 里的规则驱动，Claude 按你的措辞自动映射：

| 你怎么说 | Claude 自动选择 |
|---|---|
| "精致 / 写实 / 高清 / 用于打印" | `--quality high` |
| "草图 / 快速 / 占位图" | `--quality low` |
| "banner / 头图 / 风景 / 宽幅" | `--size landscape` |
| "海报 / 手机壁纸 / 竖版" | `--size portrait` |
| "头像 / 图标 / 方形" | `--size square` |

<details>
<summary><b>进阶：直接命令行调用（可选）</b></summary>

不依赖 agent，也可以自己跑脚本：

```bash
python3 scripts/generate.py "<提示词>" [选项]
```

| 选项 | 默认值 | 说明 |
|---|---|---|
| `-o, --out PATH` | `assets/generated/image.png` | 输出 PNG 路径 |
| `-q, --quality` | `auto` | `auto` \| `low` \| `medium` \| `high` |
| `-s, --size` | `auto` | `auto` \| `宽x高` \| `square`/`portrait`/`landscape`/`wide`/`tall` \| `1:1`/`2:3`/`3:2`/`16:9`/`9:16` |
| `-r, --ref PATH` | _（无）_ | 参考图，可重复；图生图（借风格 / 改图保留主体，由 prompt 决定） |
| `-e, --effort` | `low` | `low` \| `medium` \| `high` \| `xhigh` — 出图前模型的推理强度（只影响对 prompt 的理解规划，不改像素质量）。复杂指令 / 图内文字 / `--ref` 编辑时可调高 |
| `--proxy HOST:PORT` | _（无）_ | 受限网络下的代理（或 `none`） |
| `--timeout N` | 自动 | 每次尝试的超时秒数；随尺寸自动调整（默认 300s，2K/4K 最多 600s） |

保存路径会打印到 stdout。
</details>

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
