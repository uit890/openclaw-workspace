#!/usr/bin/env python3
"""
AI 资讯抓取 + SQLite 去重存储
数据文件：/Users/liufeng/work/dev/chuyunxiyi-ai/ai_news.db
"""

import sqlite3
import hashlib
import re
import logging
import concurrent.futures
from datetime import datetime, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# ─── 配置 ───────────────────────────────────────────────
DB_PATH = Path("/Users/liufeng/work/dev/chuyunxiyi-ai/ai_news.db")
LOG_FILE = Path("/Users/liufeng/work/dev/chuyunxiyi-ai/ai_news.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# ─── 数据库 ─────────────────────────────────────────────
def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS ai_news (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                source          TEXT NOT NULL,
                title           TEXT NOT NULL,
                url             TEXT NOT NULL,
                summary         TEXT,
                star_count      TEXT,
                published_at    DATETIME,
                fetched_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
                title_hash      TEXT NOT NULL
            )
        """)
        c.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_source_title
            ON ai_news(source, title_hash)
        """)
        c.execute("CREATE INDEX IF NOT EXISTS idx_published_at ON ai_news(published_at)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_fetched_at ON ai_news(fetched_at)")
        conn.commit()
    log.info("✅ 数据库初始化完成: %s", DB_PATH)

def title_hash(title: str) -> str:
    return hashlib.md5(title.strip().lower().encode()).hexdigest()

def is_duplicate(source: str, title: str) -> bool:
    h = title_hash(title)
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("SELECT 1 FROM ai_news WHERE source=? AND title_hash=? LIMIT 1", (source, h))
        return c.fetchone() is not None

def insert_news(source: str, title: str, url: str, summary=None,
                published_at=None, star_count=None) -> bool:
    h = title_hash(title)
    now_utc = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    with get_conn() as conn:
        try:
            c = conn.cursor()
            c.execute("""
                INSERT INTO ai_news (source, title, url, summary, published_at, star_count, title_hash, fetched_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (source, title, url, summary, published_at, star_count, h, now_utc))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

def clean_old_data(hours: int = 48):
    cutoff = datetime.now() - timedelta(hours=hours)
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM ai_news WHERE fetched_at < ?", (cutoff,))
        conn.commit()
        deleted = c.rowcount
    log.info("🗑️  清理了 %s 条 %s 小时前的旧数据", deleted, hours)
    return deleted

# ─── 时间解析 ───────────────────────────────────────────
def parse_relative_time(time_str: str):
    """解析"N分钟前/N小时前/N天前"等相对时间"""
    if not time_str:
        return None
    time_str = time_str.strip()
    m = re.search(r"(\d+)\s*秒", time_str)
    if m:
        return datetime.now() - timedelta(seconds=int(m.group(1)))
    m = re.search(r"(\d+)\s*分钟", time_str)
    if m:
        return datetime.now() - timedelta(minutes=int(m.group(1)))
    m = re.search(r"(\d+)\s*小时", time_str)
    if m:
        return datetime.now() - timedelta(hours=int(m.group(1)))
    m = re.search(r"(\d+)\s*天", time_str)
    if m:
        return datetime.now() - timedelta(days=int(m.group(1)))
    return None

# ─── 各数据源解析 ────────────────────────────────────────

def fetch_36kr():
    """36氪 AI 资讯"""
    url = "https://www.36kr.com/information/AI/"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        items = soup.select("div.kr-shadow-content")
        results = []
        for item in items[:10]:
            title_tag = item.select_one("a.article-item-title")
            time_tag = item.select_one("span")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            link = title_tag.get("href", "")
            if link and not link.startswith("http"):
                link = "https://www.36kr.com" + link
            time_str = time_tag.get_text(strip=True) if time_tag else None
            published = parse_relative_time(time_str)
            results.append({
                "source": "36kr",
                "title": title,
                "url": link,
                "published_at": published,
            })
        log.info("✅ 36kr: 抓取到 %s 条", len(results))
        return results
    except Exception as e:
        log.warning("❌ 36kr 抓取失败: %s", e)
        return []


def fetch_github():
    """GitHub Trending"""
    url = "https://github.com/trending"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        articles = soup.select("article.Box-row")
        results = []
        for item in articles[:10]:
            title_tag = item.select_one("h2 a")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            link = "https://github.com" + title_tag.get("href", "")
            desc_tag = item.select_one("p.col-9")
            summary = desc_tag.get_text(strip=True) if desc_tag else None
            # 星标信息：从 span.d-inline-block.float-sm-right 取 "X stars today"
            meta_tag = item.select_one("div.f6")
            star_count = None
            if meta_tag:
                spans = meta_tag.select("span.d-inline-block.float-sm-right")
                if spans:
                    text = spans[-1].get_text(strip=True)
                    # 格式: "1,038 stars today"
                    m = re.match(r"([\d,]+)\s+stars today", text)
                    if m:
                        star_count = m.group(1).replace(",", "")
            published = datetime.now()  # GitHub trending 不显示时间，用抓取时间
            results.append({
                "source": "github",
                "title": title,
                "url": link,
                "summary": summary,
                "star_count": star_count,
                "published_at": published,
            })
        log.info("✅ github: 抓取到 %s 条", len(results))
        return results
    except Exception as e:
        log.warning("❌ github 抓取失败: %s", e)
        return []


def fetch_huxiu():
    """虎嗅网"""
    url = "https://www.huxiu.com"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        # 找所有文章链接，按 href 去重
        seen_urls = set()
        article_map = {}  # url -> {title, published_at}
        all_links = soup.find_all("a", href=True)

        for a in all_links:
            href = a.get("href", "")
            # 匹配 https://www.huxiu.com/article/数字.html
            if not re.match(r"https://www\.huxiu\.com/article/\d+\.html", href):
                continue
            if href in seen_urls:
                continue
            seen_urls.add(href)

            text = a.get_text(strip=True)
            # 标题特征：文本长度 > 10 且不是纯数字
            if not text or len(text) < 10:
                continue
            try:
                int(text)
                continue  # 跳过纯数字（如评论数）
            except ValueError:
                pass

            title = text
            # 找时间：往前找同级兄弟元素中的时间
            time_str = None
            parent = a.find_parent("div", class_="huxiu_info_item")
            if parent:
                time_tag = parent.select_one(".huxiu_time")
                if time_tag:
                    time_str = time_tag.get_text(strip=True)

            published = parse_relative_time(time_str)
            article_map[href] = {
                "title": title,
                "url": href,
                "published_at": published,
            }

        results = [
            {"source": "huxiu", **v}
            for v in article_map.values()
        ]
        log.info("✅ huxiu: 抓取到 %s 条", len(results))
        return results
    except Exception as e:
        log.warning("❌ huxiu 抓取失败: %s", e)
        return []


def fetch_tmtpost():
    """钛媒体"""
    url = "https://www.tmtpost.com"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        seen_urls = set()
        results = []
        all_links = soup.find_all("a", href=True)

        for a in all_links:
            href = a.get("href", "")
            # 匹配 tmtpost 文章 URL
            if not re.match(r"https://www\.tmtpost\.com/\d+\.html", href):
                continue
            if href in seen_urls:
                continue
            seen_urls.add(href)

            text = a.get_text(strip=True)
            if not text or len(text) < 10:
                continue

            title = text
            # 尝试找时间
            time_str = None
            parent = a.find_parent("li")
            if parent:
                time_tag = parent.select_one(".time")
                if time_tag:
                    time_str = time_tag.get_text(strip=True)

            published = parse_relative_time(time_str)
            results.append({
                "source": "tmtpost",
                "title": title,
                "url": href,
                "published_at": published,
            })

        log.info("✅ tmtpost: 抓取到 %s 条", len(results))
        return results
    except Exception as e:
        log.warning("❌ tmtpost 抓取失败: %s", e)
        return []


def fetch_techcrunch():
    """TechCrunch"""
    url = "https://techcrunch.com"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        seen_urls = set()
        results = []
        all_links = soup.find_all("a", href=True)

        for a in all_links:
            href = a.get("href", "")
            # 匹配 2026 年的文章页（结尾是 / 不是 .html）
            if not re.match(r"https://techcrunch\.com/2026/\d+/\d+/.+", href):
                continue
            if href in seen_urls:
                continue
            seen_urls.add(href)

            text = a.get_text(strip=True)
            if not text or len(text) < 15:
                continue

            title = text
            # TechCrunch 文章时间通常在 parent 的 time 标签
            time_tag = a.find_next("time")
            time_str = time_tag.get("datetime") if time_tag else None
            published = None
            if time_str:
                try:
                    published = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
                except ValueError:
                    published = parse_relative_time(time_str)
            else:
                published = datetime.now()

            results.append({
                "source": "techcrunch",
                "title": title,
                "url": href,
                "published_at": published,
            })

        log.info("✅ techcrunch: 抓取到 %s 条", len(results))
        return results
    except Exception as e:
        log.warning("❌ techcrunch 抓取失败: %s", e)
        return []


def fetch_theverge():
    """The Verge - 尝试从 HTML 中提取"""
    url = "https://www.theverge.com"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        seen_urls = set()
        results = []
        all_links = soup.find_all("a", href=True)

        for a in all_links:
            href = a.get("href", "")
            # 匹配 theverge 文章 URL: /ai-artificial-intelligence/894587/slug
            if not re.match(r"/[a-z][\w-]+/\d+/\S+", href):
                continue
            if href in seen_urls:
                continue
            seen_urls.add(href)

            text = a.get_text(strip=True)
            if not text or len(text) < 10:
                continue

            full_url = "https://www.theverge.com" + href
            results.append({
                "source": "theverge",
                "title": text,
                "url": full_url,
                "published_at": datetime.now(),
            })

        log.info("✅ theverge: 抓取到 %s 条", len(results))
        return results
    except Exception as e:
        log.warning("❌ theverge 抓取失败: %s", e)
        return []


# ─── 主流程 ─────────────────────────────────────────────
FETCHERS = {
    "36kr": fetch_36kr,
    "github": fetch_github,
    "huxiu": fetch_huxiu,
    "tmtpost": fetch_tmtpost,
    "techcrunch": fetch_techcrunch,
    "theverge": fetch_theverge,
}

def fetch_all_sources():
    all_items = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(fn): name for name, fn in FETCHERS.items()}
        for future in concurrent.futures.as_completed(futures):
            name = futures[future]
            try:
                items = future.result()
                all_items.extend(items)
            except Exception as e:
                log.warning("❌ %s 执行异常: %s", name, e)
    return all_items

def run():
    log.info("🚀 开始执行 AI 资讯抓取任务")
    init_db()
    clean_old_data(hours=48)

    items = fetch_all_sources()
    new_count = 0
    dup_count = 0
    for item in items:
        ok = insert_news(
            source=item["source"],
            title=item["title"],
            url=item["url"],
            summary=item.get("summary"),
            published_at=item.get("published_at"),
            star_count=item.get("star_count"),
        )
        if ok:
            new_count += 1
        else:
            dup_count += 1

    log.info("📊 插入完成: 新增 %s 条, 重复 %s 条", new_count, dup_count)
    return new_count, dup_count


def get_recent_news(hours: int = 24, limit: int = 100):
    """获取最近 N 小时的资讯，按来源分组。优先按发布时间降序，保证各来源都有数据。"""
    cutoff = datetime.now() - timedelta(hours=hours)
    with get_conn() as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("""
            SELECT source, title, url, summary, star_count, published_at, fetched_at
            FROM ai_news
            WHERE fetched_at >= ?
            ORDER BY published_at DESC NULLS LAST, fetched_at DESC
            LIMIT ?
        """, (cutoff, limit))
        rows = c.fetchall()

    sections = {}
    for row in rows:
        src = row["source"]
        if src not in sections:
            sections[src] = []
        sections[src].append(row)

    return sections


def format_for_feishu_card(sections: dict) -> dict:
    """
    将分区数据格式化为飞书 Card Table JSON
    - 第一列：来源媒体（纵向合并单元格 rowspan）
    - 第二列：摘要（可点击超链接）
    - 每来源最多 5 条
    - 英文标题翻译为中文
    """
    from deep_translator import GoogleTranslator

    _translator = GoogleTranslator(source="en", target="zh-CN")
    _trans_cache = {}

    def translate(text: str) -> str:
        if not text:
            return text
        if text in _trans_cache:
            return _trans_cache[text]
        try:
            result = _translator.translate(text)
            _trans_cache[text] = result
            return result
        except Exception:
            return text

    source_order = ["github", "36kr", "huxiu", "tmtpost", "techcrunch", "theverge"]
    source_names = {
        "github":     "⭐ GitHub",
        "36kr":      "📱 36氪",
        "huxiu":     "🐯 虎嗅",
        "tmtpost":   "🔬 钛媒体",
        "techcrunch":"🌐 TechCrunch",
        "theverge":  "🌍 The Verge",
    }

    MAX_PER_SOURCE = 5

    # 构建 table rows
    # Feishu Card table: 每个 cell 是一个 {tag: "cell", ...} 对象
    # 合并单元格：起点 cell 设 rowspan，非起点设 rowspan=0, colspan=0
    rows = []
    for src in source_order:
        if src not in sections:
            continue
        items = sections[src][:MAX_PER_SOURCE]

        seen_titles = set()
        for i, item in enumerate(items):
            title = item["title"].strip()
            if title in seen_titles:
                continue
            seen_titles.add(title)
            url = item["url"].strip()

            # 英文标题翻译
            is_english = all(ord(c) < 128 for c in title)
            if is_english and len(title) > 10:
                title_cn = translate(title)
                display_title = title_cn if title_cn and title_cn != title else title
            else:
                display_title = title

            # 转义 title 中的 ] 避免破坏飞书链接格式
            safe_title = display_title.replace("]", "』")
            star = f" ⭐{int(item['star_count']):,}" if item.get("star_count") else ""

            # 飞书卡片 cell 格式：
            # - 合并行：起点 cell 有 rowspan 字段，其余被合并的 cell rowspan=0 colspan=0
            is_first_in_group = (i == 0)
            group_size = len(items) if is_first_in_group else 0

            # 第一列 cell（来源媒体）
            if is_first_in_group:
                src_cell = {
                    "tag": "cell",
                    "text": source_names.get(src, src),
                    "rowspan": group_size,
                    "colspan": 1,
                }
            else:
                src_cell = {
                    "tag": "cell",
                    "text": "",
                    "rowspan": 0,
                    "colspan": 0,
                }

            # 第二列 cell（摘要链接）
            summary_cell = {
                "tag": "cell",
                "text": f'[{safe_title}]({url}){star}',
                "markdown": True,
                "rowspan": 1 if not is_first_in_group else group_size,
                "colspan": 1,
            }

            rows.append([src_cell, summary_cell])

    card = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": "🤖 AI 科技资讯"},
                "template": "blue",
            },
            "elements": [
                {
                    "tag": "table",
                    "columns": [
                        {"title": {"tag": "plain_text", "content": "来源媒体"}, "width": 120},
                        {"title": {"tag": "plain_text", "content": "摘要"}, "width": 520},
                    ],
                    "rows": rows,
                },
                {"tag": "hr"},
                {
                    "tag": "note",
                    "elements": [
                        {"tag": "plain_text", "content": "由 AI News Fetcher 自动抓取 · "},
                        {"tag": "plain_text", "content": datetime.now().strftime("%Y-%m-%d %H:%M")},
                    ],
                },
            ],
        },
    }
    return card


# 兼容旧接口
def format_for_push(sections: dict) -> str:
    """兼容旧调用，透传到 format_for_feishu_card，取 card.elements[0].rows 渲染为文本"""
    card = format_for_feishu_card(sections)
    # 提取出链接文本用于旧场景（飞书卡片模式直接发 card JSON）
    return str(card)


if __name__ == "__main__":
    run()
