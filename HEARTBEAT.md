# HEARTBEAT.md

## AI资讯定时推送任务
每2小时执行一次推送（6点、8点、10点...22点）

---

### 第一步：抓取并存库

```bash
python3 ~/.openclaw/workspace/skills/ai-news/scripts/ai_news_fetcher.py
```

**说明：** 各数据源并行抓取，结果自动写入 `~/work/dev/chuyunxiyi-ai/ai_news.db` 去重（`source + title_hash` 唯一索引），48小时前的旧数据自动清理。

---

### 第二步：读取并推送

```python
import sys
sys.path.insert(0, os.path.expanduser("~/.openclaw/workspace/skills/ai-news/scripts"))
from ai_news_fetcher import get_recent_news, format_for_push

sections = get_recent_news(hours=24, limit=30)
content = format_for_push(sections)
# 发送 content 给用户
```

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
