# AI资讯定时推送任务
每2小时执行一次（cron: `0 */2 * * *`）

---

## 第一步：触发 ai-news-fetcher Skill

本任务**使用 ai-news-fetcher skill** 获取AI/科技资讯，不要直接抓取网页。

请按以下步骤执行：

### Step 1 — 执行抓取

在终端运行：
```bash
python3 ~/.openclaw/workspace/skills/ai-news/scripts/ai_news_fetcher.py
```

说明：6个数据源并行抓取，结果自动写入 `~/work/dev/chuyunxiyi-ai/ai_news.db`（`source + title_hash` 唯一索引去重），入库前自动清理48小时前的旧数据。

### Step 2 — 查询并获取飞书卡片

```python
import sys
sys.path.insert(0, os.path.expanduser("~/.openclaw/workspace/skills/ai-news/scripts"))
from ai_news_fetcher import get_recent_news, format_for_feishu_card

sections = get_recent_news(hours=24, limit=50)
card = format_for_feishu_card(sections)
# card 是飞书 Card JSON dict
```

### Step 3 — 输出结果

将 `card` JSON 以文本形式输出（`json.dumps(card, ensure_ascii=False, indent=2)`），作为本次任务的最终输出。

OpenClaw 会自动通过 Feishu 发送给用户（open_id: ou_620abe530f4e51e0f6c22fe8f3472055）。

### Step 4 — 更新推送记录

将本次推送的**标题列表**（从 card 中提取每个条目的标题和来源）追加写入 `~/.openclaw/workspace/memory/ai-news-push.md`，格式参考该文件的历史记录。

---

## 数据源

| 来源 | 地址 |
|------|------|
| 36kr | https://www.36kr.com/information/AI/ |
| GitHub | https://github.com/trending |
| 虎嗅 | https://www.huxiu.com |
| 钛媒体 | https://www.tmtpost.com |
| TechCrunch | https://techcrunch.com |
| The Verge | https://www.theverge.com |

---

## 推送记录文件

`~/.openclaw/workspace/memory/ai-news-push.md` — 记录每次推送的标题、来源、时间和推送结果（messageId）。
