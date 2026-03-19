#!/usr/bin/env python3
"""下载视频到 ~/Downloads/claw_video/video/"""

import sys
import subprocess
from pathlib import Path

def download_video(url):
    output_dir = Path.home() / "Downloads" / "claw_video" / "video"
    output_dir.mkdir(parents=True, exist_ok=True)

    # 使用 yt-dlp 下载最佳质量视频
    cmd = [
        "yt-dlp",
        "-f", "bestvideo[ext=mkv]+bestaudio[ext=m4a]/best[ext=mkv]/best",
        "--output", str(output_dir / "%(title)s.%(ext)s"),
        url
    ]

    print(f"下载视频到: {output_dir}")
    result = subprocess.run(cmd, capture_output=False)
    sys.exit(result.returncode)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python download_video.py <视频URL>")
        sys.exit(1)
    download_video(sys.argv[1])
