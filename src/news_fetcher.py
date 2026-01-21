import feedparser
from datetime import datetime, timedelta


'''def fetch_google_news(
    query: str,
    days_back: int = 3,
    max_items: int = 10
):
    """
    Fetch recent Google News headlines for a query.
    """

    query = query.replace(" ", "+")
    url = f"https://news.google.com/rss/search?q={query}"

    feed = feedparser.parse(url)

    headlines = []
    cutoff_date = datetime.utcnow() - timedelta(days=days_back)

    for entry in feed.entries:
        if len(headlines) >= max_items:
            break

        if hasattr(entry, "published_parsed"):
            published = datetime(*entry.published_parsed[:6])
            if published < cutoff_date:
                continue

        headlines.append(entry.title)

    return headlines
'''

def fetch_google_news(
    query: str,
    reference_date: str,
    window_days: int = 3,
    max_items: int = 10
):
    """
    Fetch Google News headlines strictly around a reference date.
    """
    ref_date = datetime.strptime(reference_date, "%Y-%m-%d")
    start_date = ref_date - timedelta(days=window_days)
    end_date = ref_date + timedelta(days=1)

    query = query.replace(" ", "+")
    url = f"https://news.google.com/rss/search?q={query}"

    feed = feedparser.parse(url)

    headlines = []

    for entry in feed.entries:
        if len(headlines) >= max_items:
            break

        if not hasattr(entry, "published_parsed"):
            continue

        published = datetime(*entry.published_parsed[:6])

        if start_date <= published <= end_date:
            headlines.append(entry.title)

    return headlines
