---
name: ai-news-fetcher
description: "获取AI/科技热点资讯，支持6个数据源并行抓取+SQLite去重，格式化后推送飞书。当用户提到AI资讯、科技新闻、热点资讯、今日科技、最近AI有什么大新闻时，使用此 Skill。"
---

# AI News Fetcher Skill

从 6 个主流科技/AI 数据源并行抓取热点资讯，自动去重后以**飞书可点击超链接格式**返回。

## 核心文件

- **抓取脚本**：`~/.openclaw/workspace/skills/ai-news/scripts/ai_news_fetcher.py`
- **数据库**：`~/work/dev/chuyunxiyi-ai/ai_news.db`

## 数据源

| 来源 | 地址 |
|------|------|
| ⭐ GitHub | https://github.com/trending |
| 📱 36氪 | https://www.36kr.com/information/AI/ |
| 🐯 虎嗅 | https://www.huxiu.com |
| 🔬 钛媒体 | https://www.tmtpost.com |
| 🌐 TechCrunch | https://techcrunch.com |
| 🌍 The Verge | https://www.theverge.com |

## 完整执行流程

### Step 1 — 抓取并存库

```bash
python3 ~/.openclaw/workspace/skills/ai-news/scripts/ai_news_fetcher.py
```

### Step 2 — 查询并格式化

```python
import sys, os
sys.path.insert(0, os.path.expanduser("~/.openclaw/workspace/skills/ai-news/scripts"))
from ai_news_fetcher import get_recent_news, format_for_push

sections = get_recent_news(hours=24, limit=50)
markdown_text = format_for_push(sections)
# markdown_text 是飞书兼容的 Markdown，包含 [标题](URL) 可点击链接
```

### Step 3 — 发送给用户

`format_for_push()` 返回的是卡片结构（dict），通过 OpenClaw message 工具发送：

```
target: ou_620abe530f4e51e0f6c22fe8f3472055
message: <format_for_push() 返回的 dict>
msg_type: interactive（由 message 内容中的 msg_type 决定）
```

**注意**：发送时 `message` 参数直接传 `format_for_push()` 返回的 dict（Python object），消息类型为 `interactive`，卡片内的链接是原生可点击的，**URL 不会在明文中显示**。

## 输出格式

`format_for_push()` 返回飞书 **Interactive Card**（原生可点击超链接卡片）：

```json
{
  "msg_type": "interactive",
  "card": {
    "config": {"wide_screen_mode": true},
    "elements": [
      {"tag": "markdown", "content": "## 🤖 AI 科技资讯"},
      {"tag": "markdown", "content": "**⭐ GitHub**"},
      {"tag": "markdown", "content": "- [repo-name](https://github.com/...) ⭐1,234"},
      ...
    ]
  }
}
```

**规格：**
- GitHub 优先展示在最前
- 每来源最多 **5 条**
- 英文标题自动翻译为中文
- **标题本身是可点击超链接**，URL 不在明文中展示
- GitHub 项目附带星标数

## 数据库字段

| 字段 | 说明 |
|------|------|
| source | 来源平台 |
| title | 资讯标题 |
| url | 原文链接 |
| summary | 摘要/GitHub项目描述 |
| star_count | GitHub星标数 |
| published_at | 发布时间 |
| fetched_at | 入库时间 |

## 导出 CSV

```python
from ai_news_fetcher import export_csv
path = export_csv(hours=24)  # 输出到 /tmp/openclaw/ai_news_export.csv
```

## 定时推送

使用 CronCreate 工具设置定时任务：

- cron 表达式：`0 0/2 * * *`（每2小时一次）
- sessionTarget: isolated
- prompt：执行 ai-news-fetcher skill 完整流程（抓取→格式化→发送）
