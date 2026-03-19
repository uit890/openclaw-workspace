---
name: ai-news-fetcher
description: "获取AI/科技热点资讯，支持6个数据源并行抓取+SQLite去重。触发词：AI资讯、科技新闻、热点资讯、今日科技。"
---

# AI News Fetcher Skill

从 6 个主流科技/AI 数据源并行抓取热点资讯，自动去重后返回结构化结果。

## 数据源

| 来源 | 类型 | 地址 |
|------|------|------|
| 36kr | AI/科技 | https://www.36kr.com/information/AI/ |
| GitHub | 开源项目 | https://github.com/trending |
| 虎嗅 | 科技商业 | https://www.huxiu.com |
| 钛媒体 | 科技AGI | https://www.tmtpost.com |
| TechCrunch | 全球科技 | https://techcrunch.com |
| The Verge | 科技评论 | https://www.theverge.com |

## 核心脚本

脚本位置：`/Users/liufeng/work/dev/chuyunxiyi-ai/ai_news_fetcher.py`

## 使用方式

### 抓取并存储（去重）

```bash
cd /Users/liufeng/work/dev/chuyunxiyi-ai && python3 ai_news_fetcher.py
```

### 获取最近入库的资讯（直接从 SQLite 读取）

```bash
sqlite3 /Users/liufeng/work/dev/chuyunxiyi-ai/ai_news.db \
  "SELECT source, title, url, summary, star_count, published_at, fetched_at
   FROM ai_news
   WHERE fetched_at >= datetime('now', '-24 hours')
   ORDER BY fetched_at DESC
   LIMIT 20"
```

### 数据库字段说明

| 字段 | 说明 |
|------|------|
| id | 自增主键 |
| source | 来源平台 |
| title | 资讯标题 |
| url | 原文链接 |
| summary | 摘要/GitHub项目描述 |
| star_count | GitHub星标数 |
| published_at | 发布时间 |
| fetched_at | 入库时间 |
| title_hash | 标题MD5（去重用） |

### 清理旧数据（保留48小时）

```bash
cd /Users/liufeng/work/dev/chuyunxiyi-ai && python3 -c "
from ai_news_fetcher import init_db, clean_old_data
init_db()
clean_old_data(hours=48)
"
```

## 执行流程

1. 并行请求 6 个数据源（各自独立 try-catch）
2. 解析各站页面，提取标题/链接/时间
3. 对标题做 MD5，与 SQLite 已有数据去重
4. 新数据写入 `ai_news.db`（`source + title_hash` 唯一索引）
5. 返回入库记录条数统计

## 返回示例

```
✅ 36kr: 抓取到 10 条
✅ github: 抓取到 6 条
✅ huxiu: 抓取到 36 条
✅ tmtpost: 抓取到 53 条
✅ techcrunch: 抓取到 36 条
✅ theverge: 抓取到 47 条
📊 插入完成: 新增 47 条, 重复 141 条
```
