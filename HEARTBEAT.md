# HEARTBEAT.md

## AI资讯定时推送任务
每2小时执行一次推送（6点、8点、10点...22点）

---

### 第一步：抓取并存库（调用 ai-news-fetcher skill）

```bash
cd /Users/liufeng/work/dev/chuyunxiyi-ai && python3 ai_news_fetcher.py
```

**说明：** 各数据源并行抓取，结果自动写入 `ai_news.db` 去重（`source + title_hash` 唯一索引），48小时前的旧数据自动清理。

---

### 第二步：从 SQLite 读取最新数据

```python
import sys
sys.path.insert(0, "/Users/liufeng/work/dev/chuyunxiyi-ai")
from ai_news_fetcher import get_recent_news, format_for_push

sections = get_recent_news(hours=24, limit=30)
content = format_for_push(sections)
# content 即为格式化后的推送文本
```

---

### 第三步：发送推送

将 `content` 发送给用户（峰哥），推送格式示例：

```
📱 36氪
────────────────────
• 标题内容
  https://...

⭐ GitHub
────────────────────
• repo/project ⭐1234
  https://github.com/...
```

**注意：** SQLite 中同一标题（相同 source）只保留一条，故 SQLite 出库 = 已去重。可直接推送。

---

### 数据源
| 来源 | 地址 |
|------|------|
| 36kr | https://www.36kr.com/information/AI/ |
| GitHub | https://github.com/trending |
| 虎嗅 | https://www.huxiu.com |
| 钛媒体 | https://www.tmtpost.com |
| TechCrunch | https://techcrunch.com |
| The Verge | https://www.theverge.com |
