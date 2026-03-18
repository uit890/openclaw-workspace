#!/usr/bin/env python3
"""
语音转文字脚本 - 使用 faster-whisper 本地模型
用法: python3 whisper_transcribe.py <音频文件路径> [输出txt路径]
"""

import sys
import warnings
from faster_whisper import WhisperModel

# 忽略 numpy 警告
warnings.filterwarnings("ignore", category=RuntimeWarning)

MODEL_SIZE = "base"
AUDIO_PATH = sys.argv[1] if len(sys.argv) > 1 else "input.ogg"
OUTPUT_PATH = sys.argv[2] if len(sys.argv) > 2 else "output.txt"

print("加载模型: " + MODEL_SIZE + " ...")
model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")

print("转录中: " + AUDIO_PATH + " ...")
segments, info = model.transcribe(AUDIO_PATH, language="zh")

print("语言: " + info.language + "，时长: " + str(round(info.duration, 1)) + "s")
print("-" * 40)

text_lines = []
for segment in segments:
    line = segment.text.strip()
    start = round(segment.start, 1)
    end = round(segment.end, 1)
    print("[" + str(start) + "s -> " + str(end) + "s] " + line)
    text_lines.append(line)

full_text = "".join(text_lines)

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(full_text)

print("-" * 40)
print("保存到: " + OUTPUT_PATH)
print("最终文字: " + full_text)
