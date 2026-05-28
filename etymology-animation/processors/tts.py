#!/usr/bin/env python3
"""
火山引擎TTS (文字转语音) 模块

用于为汉字教学视频生成旁白配音。
依赖：pip install websockets python-dotenv
"""

import argparse
import json
import logging
import uuid
import os
from pathlib import Path
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_cluster(voice: str) -> str:
    if voice.startswith("S_"):
        return "volcano_icl"
    return "volcano_tts"


class VolcEngineTTS:
    def __init__(self, appid=None, access_token=None):
        self.appid = appid or os.getenv("VOLC_APPID")
        self.access_token = access_token or os.getenv("VOLC_ACCESS_KEY_ID")

        if not self.appid or not self.access_token:
            raise ValueError("请设置 VOLC_APPID 和 VOLC_ACCESS_KEY_ID 环境变量")

    async def synthesize(self, text, output_file="output.wav", voice_type="zh_female_qingxin",
                       encoding="wav", endpoint="wss://openspeech.bytedance.com/api/v1/tts/ws_binary",
                       cluster=None):

        import websockets
        from processors.protocols import MsgType, full_client_request, receive_message

        cluster = cluster or get_cluster(voice_type)

        headers = {
            "Authorization": f"Bearer;{self.access_token}",
        }

        logger.info(f"Connecting to {endpoint} with headers: {headers}")
        websocket = await websockets.connect(
            endpoint, additional_headers=headers, max_size=10 * 1024 * 1024
        )
        logger.info(
            f"Connected to WebSocket server, Logid: {websocket.response.headers['x-tt-logid']}",
        )

        try:
            request = {
                "app": {
                    "appid": self.appid,
                    "token": self.access_token,
                    "cluster": cluster,
                },
                "user": {
                    "uid": str(uuid.uuid4()),
                },
                "audio": {
                    "voice_type": voice_type,
                    "encoding": encoding,
                },
                "request": {
                    "reqid": str(uuid.uuid4()),
                    "text": text,
                    "operation": "submit",
                    "with_timestamp": "1",
                    "extra_param": json.dumps(
                        {
                            "disable_markdown_filter": False,
                        }
                    ),
                },
            }

            await full_client_request(websocket, json.dumps(request).encode())

            audio_data = bytearray()
            while True:
                msg = await receive_message(websocket)

                if msg.type == MsgType.FrontEndResultServer:
                    continue
                elif msg.type == MsgType.AudioOnlyServer:
                    audio_data.extend(msg.payload)
                    if msg.sequence < 0:
                        break
                else:
                    raise RuntimeError(f"TTS conversion failed: {msg}")

            if not audio_data:
                raise RuntimeError("No audio data received")

            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, "wb") as f:
                f.write(audio_data)
            logger.info(f"Audio received: {len(audio_data)}, saved to {output_file}")
            return True, f"音频已保存到 {output_file}"

        finally:
            await websocket.close()
            logger.info("Connection closed")


def main():
    if "--install-deps" in sys.argv:
        import subprocess
        print("正在安装依赖...")
        subprocess.run([sys.executable, "-m", "pip", "install", "websockets", "python-dotenv"], check=True)
        print("依赖安装完成！")
        return 0

    import asyncio
    parser = argparse.ArgumentParser(description="火山引擎TTS文字转语音工具")
    parser.add_argument("--appid", help="APP ID (也可通过环境变量 VOLC_APPID 设置)")
    parser.add_argument("--access_token", help="Access Token (也可通过环境变量 VOLC_ACCESS_KEY_ID 设置)")
    parser.add_argument("--voice_type", default="BV700_V2_streaming", help="Voice type (默认: BV700_V2_streaming)")
    parser.add_argument("--cluster", default="", help="Cluster name (默认自动识别)")
    parser.add_argument("--text", required=True, help="Text to convert")
    parser.add_argument("--encoding", default="wav", help="Output file encoding (默认: wav)")
    parser.add_argument("-o", "--output", default="output.wav", help="Output file path (默认: output.wav)")
    parser.add_argument(
        "--endpoint",
        default="wss://openspeech.bytedance.com/api/v1/tts/ws_binary",
        help="WebSocket endpoint URL",
    )

    args = parser.parse_args()

    try:
        tts = VolcEngineTTS(
            appid=args.appid,
            access_token=args.access_token
        )

        success, message = asyncio.run(tts.synthesize(
            text=args.text,
            output_file=args.output,
            voice_type=args.voice_type,
            encoding=args.encoding,
            endpoint=args.endpoint,
            cluster=args.cluster if args.cluster else None
        ))

        print(message)
        return 0 if success else 1

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
