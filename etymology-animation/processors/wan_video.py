#!/usr/bin/env python3
"""
阿里云百炼 Wan2.7 图生视频模块

使用 wan2.7-i2v-2026-04-25 模型，支持：
  - 首帧生视频（传入首帧PNG + prompt）
  - 首尾帧生视频（传入首帧PNG + 尾帧PNG + prompt）

依赖：pip install requests
环境变量：DASHSCOPE_API_KEY（已在 .env 中配置）
"""

import argparse
import base64
import json
import logging
import os
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

API_BASE = "https://dashscope.aliyuncs.com/api/v1"
CREATE_URL = f"{API_BASE}/services/aigc/video-generation/video-synthesis"
TASK_URL = f"{API_BASE}/tasks"
MODEL = "wan2.7-i2v-2026-04-25"

POLL_INTERVAL = 15  # 秒
MAX_POLL_TIME = 600  # 最长等待10分钟


def _get_api_key() -> str:
    key = os.getenv("DASHSCOPE_API_KEY")
    if not key:
        raise ValueError("请设置 DASHSCOPE_API_KEY 环境变量（见 .env 文件）")
    return key


def _image_to_data_url(path: str) -> str:
    """将本地图片转为 base64 data URL，供 API 直接使用。"""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"图片不存在: {path}")
    suffix = p.suffix.lower()
    mime_map = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                ".webp": "image/webp", ".bmp": "image/bmp"}
    mime = mime_map.get(suffix, "application/octet-stream")
    data = p.read_bytes()
    b64 = base64.b64encode(data).decode()
    return f"data:{mime};base64,{b64}"


def _resolve_url(source: str) -> str:
    """如果是本地文件路径，转 base64；否则原样返回（公网 URL）。"""
    parsed = urlparse(source)
    if parsed.scheme in ("http", "https", "oss"):
        return source
    return _image_to_data_url(source)


def create_task(
    prompt: str,
    first_frame: str,
    last_frame: str | None = None,
    resolution: str = "720P",
    duration: int = 5,
    prompt_extend: bool = True,
    negative_prompt: str | None = None,
    seed: int | None = None,
) -> str:
    """提交视频生成任务，返回 task_id。"""
    import requests

    api_key = _get_api_key()

    media = [{"type": "first_frame", "url": _resolve_url(first_frame)}]
    if last_frame:
        media.append({"type": "last_frame", "url": _resolve_url(last_frame)})

    body: dict = {
        "model": MODEL,
        "input": {
            "prompt": prompt,
            "media": media,
        },
        "parameters": {
            "resolution": resolution,
            "duration": duration,
            "prompt_extend": prompt_extend,
        },
    }
    if negative_prompt:
        body["input"]["negative_prompt"] = negative_prompt
    if seed is not None:
        body["parameters"]["seed"] = seed

    headers = {
        "Authorization": f"Bearer {api_key}",
        "X-DashScope-Async": "enable",
        "Content-Type": "application/json",
    }

    logger.info(f"提交视频生成任务: model={MODEL}, resolution={resolution}, duration={duration}s")
    logger.info(f"首帧: {first_frame}" + (f", 尾帧: {last_frame}" if last_frame else ""))

    resp = requests.post(CREATE_URL, headers=headers, json=body, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    if "code" in data:
        raise RuntimeError(f"API 错误: {data['code']} - {data.get('message', '')}")

    task_id = data["output"]["task_id"]
    logger.info(f"任务已提交, task_id: {task_id}")
    return task_id


def poll_result(task_id: str, output_dir: str | None = None) -> dict:
    """轮询任务状态，直到完成或失败。返回完整响应。"""
    import requests

    api_key = _get_api_key()
    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"{TASK_URL}/{task_id}"

    logger.info(f"轮询任务结果 (每 {POLL_INTERVAL}s 查询一次)...")
    start = time.time()

    while True:
        if time.time() - start > MAX_POLL_TIME:
            raise TimeoutError(f"任务 {task_id} 超时 (>{MAX_POLL_TIME}s)")

        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        status = data["output"]["task_status"]

        if status == "SUCCEEDED":
            logger.info("视频生成成功!")
            return data
        elif status in ("FAILED", "CANCELED"):
            code = data["output"].get("code", "")
            msg = data["output"].get("message", "")
            raise RuntimeError(f"任务失败 [{status}]: {code} {msg}")
        else:
            elapsed = int(time.time() - start)
            logger.info(f"  状态: {status} (已等待 {elapsed}s)")
            time.sleep(POLL_INTERVAL)


def download_video(url: str, output_path: str) -> str:
    """下载视频到本地。"""
    import requests

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    logger.info(f"下载视频: {output_path}")

    resp = requests.get(url, timeout=120, stream=True)
    resp.raise_for_status()
    with open(output_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)

    size_mb = Path(output_path).stat().st_size / (1024 * 1024)
    logger.info(f"下载完成: {output_path} ({size_mb:.1f} MB)")
    return output_path


def generate_video(
    prompt: str,
    first_frame: str,
    last_frame: str | None = None,
    output: str = "output.mp4",
    resolution: str = "720P",
    duration: int = 5,
    prompt_extend: bool = True,
    negative_prompt: str | None = None,
    seed: int | None = None,
) -> str:
    """完整流程：提交任务 → 轮询 → 下载视频。返回输出文件路径。"""
    task_id = create_task(
        prompt=prompt,
        first_frame=first_frame,
        last_frame=last_frame,
        resolution=resolution,
        duration=duration,
        prompt_extend=prompt_extend,
        negative_prompt=negative_prompt,
        seed=seed,
    )
    result = poll_result(task_id)
    video_url = result["output"]["video_url"]
    return download_video(video_url, output)


def main():
    parser = argparse.ArgumentParser(
        description="Wan2.7 图生视频工具（阿里云百炼）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
示例:
  # 首帧生视频
  python -m processors.wan_video --first data/png/取/jiaguwen.png --prompt "白底黑字..." -o data/video/取/jiaguwen.mp4

  # 首尾帧生视频
  python -m processors.wan_video --first data/png/取/jiaguwen.png --last data/png/取/jinwen.png --prompt "..." -o output.mp4
""",
    )
    parser.add_argument("--first", required=True, help="首帧图片路径（PNG/JPG）或公网URL")
    parser.add_argument("--last", default=None, help="尾帧图片路径（PNG/JPG）或公网URL（可选）")
    parser.add_argument("--prompt", required=True, help="视频描述 prompt")
    parser.add_argument("--negative-prompt", default=None, help="反向提示词")
    parser.add_argument("-o", "--output", default="output.mp4", help="输出视频路径")
    parser.add_argument("--resolution", default="720P", choices=["720P", "1080P"], help="分辨率档位")
    parser.add_argument("--duration", type=int, default=5, help="视频时长秒数 [2-15]")
    parser.add_argument("--no-prompt-extend", action="store_true", help="禁用 prompt 智能改写")
    parser.add_argument("--seed", type=int, default=None, help="随机种子（可选，用于复现）")
    parser.add_argument("--poll-only", default=None, help="仅轮询已有 task_id 的结果")

    args = parser.parse_args()

    # 仅轮询模式：跳过创建任务，直接查结果
    if args.poll_only:
        result = poll_result(args.poll_only)
        video_url = result["output"]["video_url"]
        download_video(video_url, args.output)
        print(f"视频已保存: {args.output}")
        return 0

    if args.duration < 2 or args.duration > 15:
        print("错误: duration 必须在 2-15 秒之间")
        return 1

    try:
        path = generate_video(
            prompt=args.prompt,
            first_frame=args.first,
            last_frame=args.last,
            output=args.output,
            resolution=args.resolution,
            duration=args.duration,
            prompt_extend=not args.no_prompt_extend,
            negative_prompt=args.negative_prompt,
            seed=args.seed,
        )
        print(f"视频已保存: {path}")
        return 0
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
