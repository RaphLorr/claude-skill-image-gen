#!/usr/bin/env python3
"""Generate an image with OpenAI gpt-image-2 via the local `codex` CLI.

Uses your ChatGPT subscription quota — no OPENAI_API_KEY required.

How it works: it asks codex to call its built-in image_generation tool, then
reads the resulting image straight out of codex's session log and decodes it
itself. This is deterministic — it never relies on the agent to save the file
(which is unreliable and can emit the wrong image).

Trust note: only the official `codex` binary ever reads ~/.codex/auth.json.
This wrapper never opens that file or handles your tokens — it just shells out
to `codex`, exactly like running codex yourself.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

# Optional proxy for region-blocked networks. Local default points at this
# machine's proxy; override with IMAGE_GEN_PROXY env or --proxy ('none' disables).
DEFAULT_PROXY = os.environ.get("IMAGE_GEN_PROXY", "127.0.0.1:10808").strip()
SESSIONS_DIR = Path.home() / ".codex" / "sessions"
SESSION_ID_RE = re.compile(r"session id:\s*([0-9a-fA-F-]{16,})")
IMAGE_MAGIC = (b"\x89PNG\r\n\x1a\n", b"\xff\xd8\xff", b"GIF8", b"RIFF")

QUALITY_CHOICES = ("auto", "low", "medium", "high")

# gpt-image-2 renders best at these native sizes; aspect keywords map onto them.
PIXELS_RE = re.compile(r"^\d{3,4}x\d{3,4}$")
SIZE_ALIASES = {
    "auto": None,
    "square": "1024x1024", "1:1": "1024x1024",
    "portrait": "1024x1536", "2:3": "1024x1536", "3:4": "1024x1536",
    "tall": "1024x1536", "9:16": "1024x1536",
    "landscape": "1536x1024", "3:2": "1536x1024", "4:3": "1536x1024",
    "wide": "1536x1024", "16:9": "1536x1024",
}


def log(msg: str) -> None:
    print(msg, file=sys.stderr)


def resolve_size(size: str) -> str | None:
    """Map a --size value (alias, ratio, or WxH) to explicit pixels, or None for auto."""
    key = size.strip().lower()
    if key in SIZE_ALIASES:
        return SIZE_ALIASES[key]
    if PIXELS_RE.match(key):
        return key
    raise ValueError(
        f"invalid --size '{size}'. Use one of {sorted(SIZE_ALIASES)} or WIDTHxHEIGHT."
    )


def build_proxy_env(proxy: str) -> dict[str, str]:
    """Return os.environ plus proxy vars (codex's Rust client reads these)."""
    env = dict(os.environ)
    if proxy and proxy.lower() != "none":
        http = f"http://{proxy}"
        env.update(
            HTTP_PROXY=http, HTTPS_PROXY=http,
            http_proxy=http, https_proxy=http,
            ALL_PROXY=f"socks5://{proxy}",
        )
    return env


def build_prompt(user_prompt: str, size_px: str | None, quality: str) -> str:
    specs = []
    if size_px:
        specs.append(f"Output exactly {size_px} pixels.")
    if quality != "auto":
        specs.append(f"Use {quality} rendering quality.")
    spec_line = (" ".join(specs) + "\n\n") if specs else ""
    return (
        "$imagegen Generate the following image using your built-in image "
        "generation tool (gpt-image-2). Do NOT save any file, do NOT run shell "
        "commands, and do NOT write code — just call the image generation tool "
        "once. The image will be retrieved automatically.\n\n"
        f"{spec_line}"
        f"Image to generate: {user_prompt}"
    )


def run_codex(prompt: str, workdir: Path, proxy: str, timeout: int) -> subprocess.CompletedProcess:
    cmd = [
        "codex", "exec",
        "--skip-git-repo-check",
        "-s", "workspace-write",
        "-c", "model_reasoning_effort=low",  # image gen needs no deep reasoning; saves quota
        "-C", str(workdir),
        prompt,
    ]
    log(f"[image-gen] gpt-image-2 via codex{f' (proxy: {proxy})' if proxy else ''} …")
    try:
        return subprocess.run(
            cmd, env=build_proxy_env(proxy),
            capture_output=True, text=True, timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"codex timed out after {timeout}s (network stall or proxy down)")


def find_rollout(codex_output: str, since: float) -> Path:
    """Locate the session jsonl codex just wrote — by session id, else newest."""
    match = SESSION_ID_RE.search(codex_output)
    if match:
        hits = list(SESSIONS_DIR.rglob(f"*{match.group(1)}*.jsonl"))
        if hits:
            return hits[0]
    candidates = [p for p in SESSIONS_DIR.rglob("rollout-*.jsonl") if p.stat().st_mtime >= since - 1]
    if not candidates:
        raise RuntimeError("could not locate the codex session log for this run")
    return max(candidates, key=lambda p: p.stat().st_mtime)


def extract_image_b64(rollout: Path) -> str:
    """Return the last image_generation result (base64) from a rollout jsonl."""
    result = None
    for line in rollout.read_text(errors="replace").splitlines():
        try:
            payload = json.loads(line).get("payload", {})
        except Exception:
            continue
        if str(payload.get("type", "")).startswith("image_generation") and isinstance(payload.get("result"), str):
            result = payload["result"]  # keep the last one if several
    if not result:
        raise RuntimeError("no image was generated (the image_generation tool did not run)")
    return result


def attempt_once(prompt: str, out_dir: Path, proxy: str, timeout: int) -> bytes:
    started = time.time()
    proc = run_codex(prompt, out_dir, proxy, timeout)
    rollout = find_rollout(f"{proc.stdout}\n{proc.stderr}", started)
    data = base64.b64decode(extract_image_b64(rollout))
    if not data.startswith(IMAGE_MAGIC):
        raise RuntimeError(f"decoded session data was not a valid image; stderr:\n{proc.stderr[-800:]}")
    return data


def generate(prompt: str, out_path: Path, *, size: str, quality: str,
             proxy: str, timeout: int, attempts: int = 2) -> Path:
    out_path = out_path.expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if shutil.which("codex") is None:
        raise RuntimeError("`codex` CLI not found on PATH. Install: npm i -g @openai/codex")
    if not (Path.home() / ".codex" / "auth.json").exists():
        raise RuntimeError("Not logged in to codex. Run: codex login")

    full_prompt = build_prompt(prompt, resolve_size(size), quality)

    # The connection occasionally stalls before the first token (common when
    # region-blocked); one retry rides over it. A stall costs no image quota.
    last_error: RuntimeError | None = None
    for n in range(1, attempts + 1):
        try:
            data = attempt_once(full_prompt, out_path.parent, proxy, timeout)
            out_path.write_bytes(data)
            return out_path
        except RuntimeError as error:
            last_error = error
            log(f"[image-gen] attempt {n}/{attempts} failed: {error}")
            if n < attempts:
                log("[image-gen] retrying …")
                time.sleep(3)
    raise last_error


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate an image with gpt-image-2 via codex (ChatGPT quota, no API key)."
    )
    parser.add_argument("prompt", help="Detailed description of the image to generate.")
    parser.add_argument("-o", "--out", default="assets/generated/image.png", help="Output image path.")
    parser.add_argument("-q", "--quality", choices=QUALITY_CHOICES, default="auto",
                        help="Render quality (default: auto).")
    parser.add_argument("-s", "--size", default="auto",
                        help="auto | WIDTHxHEIGHT | square|portrait|landscape|wide|tall | 1:1|2:3|3:2|16:9|9:16.")
    parser.add_argument("--proxy", default=DEFAULT_PROXY,
                        help="host:port proxy for region-blocked networks, or 'none'.")
    parser.add_argument("--timeout", type=int, default=240, help="Seconds per attempt before giving up.")
    args = parser.parse_args()

    try:
        path = generate(
            args.prompt, Path(args.out),
            size=args.size, quality=args.quality,
            proxy=args.proxy, timeout=args.timeout,
        )
    except (RuntimeError, ValueError) as error:
        log(f"[image-gen] ERROR: {error}")
        return 1

    print(path)  # stdout = the saved file path, for the caller to use
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
