# ============================================================
# MUET News & Events Web Crawler (Crawl4AI)
# ============================================================

import re
import asyncio
from crawl4ai import AsyncWebCrawler

BASE_URL = "https://www.muet.edu.pk"


# ------------------------------------------------------------
# Extract article links from listing pages
# ------------------------------------------------------------
def extract_article_links(markdown: str) -> list[str]:
    """
    Extracts valid MUET news article URLs from markdown
    """
    links = re.findall(
        r'\((https://www\.muet\.edu\.pk/news-events/[^\s)]+)\)',
        markdown
    )

    # Remove duplicates and fragments (#top etc.)
    return list(set(link.split("#")[0] for link in links))


# ------------------------------------------------------------
# Clean useless sections from article content
# ------------------------------------------------------------
def clean_article_text(text: str) -> str:
    """
    Extracts article content between Search and Explore sections.
    """
    start_marker = r'\[ Search\s+\]\(https://www\.muet\.edu\.pk/search\)'
    end_marker = r'\[ Explore \]\(https://www\.muet\.edu\.pk/about "Explore"\)'

    pattern = start_marker + r'([\s\S]*?)' + end_marker

    match = re.search(pattern, text, flags=re.DOTALL)

    if not match:
        return None

    return match.group(1).strip()


# ------------------------------------------------------------
# Crawl a single URL
# ------------------------------------------------------------
async def crawl(url: str) -> str | None:
    try:
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(
                url=url,
                excluded_tags=['header', 'footer', 'nav', 'aside'],
                exclude_external_links=True,
            )
            return result.markdown
    except Exception as e:
        print(f"❌ Failed to crawl {url}: {e}")
        return None


# ------------------------------------------------------------
# Fetch ALL article URLs from paginated listing
# ------------------------------------------------------------
async def fetch_all_article_links() -> list[str]:
    page = 0
    all_links = set()

    while True:
        url = f"{BASE_URL}/about/news-events?page={page}"
        print(f"📄 Crawling listing page: {page}")

        markdown = await crawl(url)
        if not markdown or "No results" in markdown:
            break

        links = extract_article_links(markdown)
        if not links:
            break

        all_links.update(links)
        page += 1

    print(f"✅ Total article links found: {len(all_links)}")
    return list(all_links)


# ------------------------------------------------------------
# Fetch & clean all articles
# ------------------------------------------------------------
async def fetch_all_articles() -> list[dict]:
    article_links = await fetch_all_article_links()
    articles = []

    for i, link in enumerate(article_links, start=0):
        print(f"📰 Fetching article {i}/{len(article_links)}")

        markdown = await crawl(link)
        if not markdown:
            continue

        cleaned_text = clean_article_text(markdown)

        articles.append({
            "url": link,
            "content": cleaned_text
        })

    print(f"✅ Successfully extracted {len(articles)} articles")
    return articles


# ------------------------------------------------------------
# SAVE TO FILE (Optional)
# ------------------------------------------------------------
def save_articles(articles, filename="muet_news_data.txt"):
    filename=f"data/website_documents/{filename}"
    with open(filename, "w", encoding="utf-8") as f:
        for article in articles:
            f.write(f"URL: {article['url']}\n")
            f.write(article['content'])
            f.write("\n\n" + "=" * 80 + "\n\n")

    print(f"📁 Data saved to {filename}")


# ============================================================
# RUN (Jupyter / Script Compatible)
# ============================================================

async def main(path):
    articles = await fetch_all_articles()
    save_articles(articles,path)
    return articles


# ---- JUPYTER ----
# articles = await main()

# ---- SCRIPT ----
# asyncio.run(main()) 
