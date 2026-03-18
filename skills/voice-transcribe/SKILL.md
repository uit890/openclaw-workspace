---
name: voice-transcribe
description: "语音消息转文字技能。当收到语音消息时，自动下载音频文件，使用 faster-whisper 本地模型转录为文字，并对转录结果进行 AI 纠错，然后基于纠错后的文字完成正常回复。"
---

# Voice Transcribe Skill（语音转文字 + 纠错）

当收到语音消息时，自动完成：下载音频 → Whisper 转录 → AI 纠错 → 正常回复。

## 工作流程

1. **检测语音消息**：从飞书消息事件中提取 `audio` 类型消息的 `message_id`
2. **下载音频**：使用 `feishu_im_bot_image` 工具下载音频文件（格式：ogg/opus）
3. **Whisper 转录**：调用 `faster-whisper` 本地模型（base）转成文字
4. **AI 纠错**：对转录原文进行文字纠错（纠正错别字、标点、口误）
5. **输出结果**：显示纠错后文字 → 执行正常回复流程

## 使用方式

### 脚本

```bash
python3 <Skill Location>/scripts/whisper_transcribe.py <音频文件路径> [输出txt路径]
```

### 代码流程

```
飞书语音消息
    ↓
feishu_im_bot_image 下载 audio ogg 文件
    ↓
whisper_transcribe.py 转录
    ↓
AI 纠错（prompt 引导）
    ↓
基于纠错后文字回复用户
```

## AI 纠错 Prompt

```
你是一个中文语音转文字的纠错专家。以下是一段语音转录的原始文字，可能存在错别字、标点错误、口误等问题。

请对这段文字进行纠错，只输出纠错后的文字，不要解释，不要备注，直接输出修正后的完整文字。

原文：{转录原文}
纠错后：
```

## 转录脚本说明

- **模型**：faster-whisper base（CPU int8，约 140MB）
- **语言**：自动检测（默认中文）
- **音频格式**：支持 ogg、opus、mp3、wav、m4a
- **首次运行**：自动下载模型到 `~/.cache/huggingface/`
- **输出**：带时间戳的逐段文字 + 合并的纯文字文件

## 错误处理

- 音频下载失败 → 提示用户「语音文件下载失败」
- Whisper 转录失败 → 提示用户「语音转文字失败」
- 转录结果为空 → 提示用户「未能识别到语音内容」

## 依赖

```bash
pip3 install faster-whisper
```

模型自动下载，无需手动配置。
