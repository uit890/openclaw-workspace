---
name: ai-news-fetcher
description: "获取AI/科技热点资讯，支持6个数据源并行抓取+SQLite去重。触发词：AI资讯、科技新闻、热点资讯、今日科技。"
---

# AI News Fetcher Skill

从 6 个主流科技/AI 数据源并行抓取热点资讯，自动去重后返回结构化结果。

## 核心脚本

脚本位置：`~/.openclaw/workspace/skills/ai-news/scripts/ai_news_fetcher.py`

数据文件：`~/work/dev/chuyunxiyi-ai/ai_news.db`（SQLite）

## 数据源

| 来源 | 类型 | 地址 |
|------|------|------|
| 36kr | AI/科技 | https://www.36kr.com/information/AI/ |
| GitHub | 开源项目 | https://github.com/trending |
| 虎嗅 | 科技商业 | https://www.huxiu.com |
| 钛媒体 | 科技AGI | https://www.tmtpost.com |
| TechCrunch | 全球科技 | https://techcrunch.com |
| The Verge | 科技评论 | https://www.theverge.com |

## 使用方式

### 抓取并存库

```bash
python3 ~/.openclaw/workspace/skills/ai-news/scripts/ai_news_fetcher.py
```

### 获取最近资讯（格式化推送文本）

```python
import sys
sys.path.insert(0, "~/.openclaw/workspace/skills/ai-news/scripts")
from ai_news_fetcher import get_recent_news, format_for_push

sections = get_recent_news(hours=24, limit=30)
content = format_for_push(sections)
```

### 数据库字段

| 字段 | 说明 |
|------|------|
| source | 来源平台 |
| title | 资讯标题 |
| url | 原文链接 |
| summary | 摘要/GitHub项目描述 |
| star_count | GitHub星标数 |
| published_at | 发布时间 |
| fetched_at | 入库时间 |


## 执行流程

1. 并行请求 6 个数据源（各自独立 try-catch）
2. 解析各站页面，提取标题/链接/时间
3. 对标题做 MD5，与 SQLite 已有数据去重
4. 新数据写入 `ai_news.db`（`source + title_hash` 唯一索引）
5. 48小时前的旧数据自动清理
