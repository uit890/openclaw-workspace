---
name: ai-news-fetcher
description: "获取AI/科技热点资讯，支持6个数据源并行抓取+SQLite去重，格式化后推送飞书卡片。当用户提到AI资讯、科技新闻、热点资讯、今日科技、最近AI有什么大新闻、刷一下科技资讯、整理今天的AI资讯，或者设置定时推送任务时，务必使用此 skill。定时触发使用 CronCreate 工具。"
---

# AI News Fetcher Skill

从 6 个主流科技/AI 数据源并行抓取热点资讯，自动去重后以飞书卡片表格格式返回。

## 快速开始

用户触发后，完整执行以下步骤：

```
1. 并行抓取 6 个数据源
2. SQLite 去重写入
3. 查询最近 24 小时数据
4. 格式化为飞书卡片 table 输出
```

## 核心脚本

- **抓取脚本**：`~/.openclaw/workspace/skills/ai-news/scripts/ai_news_fetcher.py`
- **数据库**：`~/work/dev/chuyunxiyi-ai/ai_news.db`（SQLite，本地文件）

## 数据源

| 来源 | 类型 | 地址 |
|------|------|------|
| 36kr | AI/科技 | https://www.36kr.com/information/AI/ |
| GitHub | 开源项目 | https://github.com/trending |
| 虎嗅 | 科技商业 | https://www.huxiu.com |
| 钛媒体 | 科技AGI | https://www.tmtpost.com |
| TechCrunch | 全球科技 | https://techcrunch.com |
| The Verge | 科技评论 | https://www.theverge.com |

## 完整执行流程

### Step 1 — 抓取并存库

```bash
python3 ~/.openclaw/workspace/skills/ai-news/scripts/ai_news_fetcher.py
```

- 6 个数据源**并行请求**，各自独立 try-catch（单源失败不影响其他）
- 标题 MD5 去重，已存在的数据跳过
- 写入 `ai_news.db`，入库前自动清理 48 小时前的旧数据

### Step 2 — 查询并格式化

```python
import sys
sys.path.insert(0, "~/.openclaw/workspace/skills/ai-news/scripts")
from ai_news_fetcher import get_recent_news, format_for_feishu_card

sections = get_recent_news(hours=24, limit=50)
card = format_for_feishu_card(sections)
# card 是一个 Feishu Card JSON，可直接用于飞书机器人发送
```

### Step 3 — 发送给飞书（用户配置）

根据用户的飞书机器人/飞书插件配置发送 `card` JSON。通常是 POST 到一个 Webhook 地址或调用 Feishu API。

> 如果用户没有配置发送方式，**必须先询问**飞书机器人 Webhook URL 或发送方式，再执行发送。不要在没有出口的情况下尝试发送。

## 飞书卡片表格输出格式

`format_for_feishu_card()` 输出为飞书 Card Table 格式：

- **第一列（来源媒体）**：纵向合并单元格，每组连续相同来源的条目合并为一个大单元格
- **第二列（摘要）**：可点击的超链接，格式为 `[标题](URL)`
- 来源顺序：GitHub > 36kr > 虎嗅 > 钛媒体 > TechCrunch > The Verge
- 每来源最多展示 **5 条**
- 英文标题自动翻译为中文

**示例表格结构**：

| 来源媒体 | 摘要 |
|----------|------|
| ⭐ GitHub（合并3格） | [AutoGPT-Next：下一代自动化AI代理](https://github.com/...) ⭐1.2k |
|  | [GPT-5代码解释器开源版发布](https://github.com/...) ⭐892 |
|  | [LLM推理优化新方法](https://github.com/...) ⭐654 |
| 📱 36氪（合并2格） | [OpenAI发布新模型GPT-4.5](https://36kr.com/...) |
|  | [Anthropic发布Claude 3.5](https://36kr.com/...) |
| ... | ... |

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
| title_hash | 标题MD5（用于去重） |

## 定时任务

用户要求定时推送时，使用 CronCreate 工具：

```
cron: "0 9 * * *"（每天早上9点）
prompt: 帮我执行 ai-news-fetcher skill，完成抓取、格式化，并将结果发送到飞书
recurring: true
```

定时任务的 prompt 应引导重新执行 Skill 的完整流程。

## 错误处理

- **部分数据源失败**：继续处理其他数据源，最终输出时标注失败的源
- **所有数据源失败**：返回错误信息，提示用户检查网络或数据源状态
- **去重后无新数据**：输出"最近24小时暂无新资讯"并退出
- **数据库不存在**：自动创建（init_db 在 run() 中自动调用）
