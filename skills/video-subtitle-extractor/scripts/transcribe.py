#!/usr/bin/env python3
"""使用 Whisper 将视频/音频转录为带时间戳的字幕"""

import sys
import subprocess
from pathlib import Path
import whisper
import json

def transcribe(video_path, model_name="small"):
    video_path = Path(video_path).expanduser()
    if not video_path.exists():
        print(f"文件不存在: {video_path}")
        sys.exit(1)

    # 输出目录
    output_dir = Path.home() / "Downloads" / "claw_video" / "subtitle"
    output_dir.mkdir(parents=True, exist_ok=True)

    # 加载 Whisper 模型
    print(f"加载 Whisper {model_name} 模型...")
    model = whisper.load_model(model_name)

    # 转录
    print(f"转录中: {video_path.name}")
    result = model.transcribe(str(video_path), language="zh")

    # 保存 JSON 原始数据
    json_path = output_dir / f"{video_path.stem}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # 保存带时间戳的 txt 字幕
    txt_path = output_dir / f"{video_path.stem}.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        for segment in result["segments"]:
            start = segment["start"]
            end = segment["end"]
            text = segment["text"].strip()
            # 格式: [MM:SS.mmm --> MM:SS.mmm] 文字
            start_str = format_timestamp(start)
            end_str = format_timestamp(end)
            f.write(f"[{start_str} --> {end_str}] {text}\n")

    print(f"字幕已保存:")
    print(f"  TXT: {txt_path}")
    print(f"  JSON: {json_path}")
    return txt_path

def format_timestamp(seconds):
    """将秒数转换为 [MM:SS.mmm] 格式"""
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes:02d}:{secs:06.3f}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python transcribe.py <视频文件> [模型: tiny/base/small/medium/large]")
        sys.exit(1)

    video_path = sys.argv[1]
    model_name = sys.argv[2] if len(sys.argv) > 2 else "small"
    transcribe(video_path, model_name)
