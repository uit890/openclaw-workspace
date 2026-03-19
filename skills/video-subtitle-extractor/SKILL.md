---
name: video-subtitle-extractor
description: |
  视频字幕提取与分析工具，支持从视频 URL 下载、Whisper 转录及 AI 智能总结。

  **触发条件（当用户有以下需求时使用此 Skill）**：
  (1) 用户想要知道某个视频网站某个视频的主要内容
  (2) 用户说"视频内容总结"、"这个视频讲了什么"、"视频说了什么"
  (3) 用户提供一个视频链接，要求提取字幕或总结内容
  (4) 用户提到"视频字幕"、"提取字幕"、"转录视频"
  (5) 用户发送了一个视频链接并询问视频相关问题
---

## 适配说明

- 视频存放目录：`~/Downloads/claw_video`
- 字幕目录：`~/Downloads/claw_video/subtitle/`
- 总结内容：**直接发送给用户**，不保存文件

## 前置要求

```bash
pip install yt-dlp openai-whisper
brew install ffmpeg
```

## 使用方式

用户提供视频 URL，我自动完成：下载 → 转录 → AI 总结 → 直接发送总结内容给用户。

## 执行流程

### Step 1: 下载视频

```bash
python ~/.openclaw/workspace/skills/video-subtitle-extractor/scripts/download_video.py <视频URL>
```

输出：`~/Downloads/claw_video/video/xxx.mkv`

### Step 2: Whisper 转录

```bash
python ~/.openclaw/workspace/skills/video-subtitle-extractor/scripts/transcribe.py <视频文件>
```

输出：`~/Downloads/claw_video/subtitle/xxx.txt` + `xxx.json`

### Step 3: AI 总结

读取字幕文件，AI 分析并生成详细总结，**直接发送给用户**。

#### 总结内容要求

1. **内容大纲（按时间区间）**
   - 时间区间 + 章节主题 + 关键内容摘要

2. **关键知识点**
   - 核心技术点/概念
   - 重要事实和数据
   - 作者强调的重点
   - 操作步骤或方法论

3. **AI 分析**
   - 内容的价值和适用场景
   - 逻辑结构和层次
   - 深度和难度评估
   - 亮点或创新点

4. **错误指出**
   - 具体时间点 + 错误内容 + 正确说法

**输出格式：** 发送给用户的 Markdown 消息
