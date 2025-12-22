from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import asyncio
import nest_asyncio

nest_asyncio.apply()

BASE_URL =  {
    "site.muet.edu.pk",
    "www.muet.edu.pk",
    "muet.edu.pk",
    "http://exam.muet.edu.pk"
}
MAX_PAGES = 2000

visited = set()

all_links = set()  # Store unique links

def is_internal(url):
    """Check if URL belongs to MUET domain"""
    base_domain = urlparse(BASE_URL).netloc
    url_domain = urlparse(url).netloc
    return url_domain == base_domain or url_domain == ""

def clean_url(url):
    """Remove fragments and normalize URL"""
    parsed = urlparse(url)
    # Remove fragment (#section) and rebuild URL
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}{'?' + parsed.query if parsed.query else ''}"

async def crawl():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120"
        )
        page = await context.new_page()

        while to_visit and len(visited) < MAX_PAGES:
            url = to_visit

            if url in visited:
                continue

            print(f"Crawling ({len(visited)+1}/{MAX_PAGES}): {url}")

            try:
                await page.goto(url, timeout=60000, wait_until="domcontentloaded")
                await page.wait_for_timeout(2000)  # Wait for dynamic content
                html = await page.content()
            except Exception as e:
                print(f"❌ Failed: {url} - {str(e)[:50]}")
                visited.add(url)
                continue

            visited.add(url)

            # Parse HTML and extract links
            soup = BeautifulSoup(html, "html.parser")

            for a in soup.find_all("a", href=True):
                raw_link = a["href"]

                # Convert relative URLs to absolute
                absolute_link = urljoin(BASE_URL, raw_link)

                # Clean and normalize
                clean_link = clean_url(absolute_link)

                # Only process internal MUET links
                if is_internal(clean_link):
                    all_links.add(clean_link)

                    # Add to crawl queue if not visited
                    if clean_link not in visited and clean_link not in to_visit:
                        to_visit.append(clean_link)

        await browser.close()

# Run the crawler
to_visits = [
    "https://site.muet.edu.pk/",
    "https://www.muet.edu.pk/",
    "http://exam.muet.edu.pk"
]
for i in range(len(to_visits)):
    to_visit = to_visits[i]
    asyncio.run(crawl())


# Display results
print("\n" + "="*80)
print(f"✅ Crawling Complete!")
print(f"📊 Total pages visited: {len(visited)}")
print(f"🔗 Total unique links found: {len(all_links)}")
print("="*80)

# Print all links
print("\n📋 All MUET Website Links:\n")
for i, link in enumerate(sorted(all_links), 1):
    print(f"{i}. {link}")

# Optional: Save to file
with open("muet_links.txt", "w", encoding="utf-8") as f:
    f.write(f"Total Links: {len(all_links)}\n")
    f.write("="*80 + "\n\n")
    for link in sorted(all_links):
        f.write(f"{link}\n")

print(f"\n💾 Links saved to 'muet_links.txt'")