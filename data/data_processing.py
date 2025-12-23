# # Convert to LangChain Document
# import re
# from crawl4ai import *
# def remove_section(text, start_marker="[Skip to Main Content]", end_marker= "\n\n\n#"):
#     """
#     Removes any text between start_marker and end_marker (inclusive).
#     Works across multiple lines.
#     """
#     pattern = re.escape(start_marker) + r".*?" + re.escape(end_marker)
#     cleaned_text = re.sub(pattern, "", text, flags=re.DOTALL)
#     pattern = re.escape('#') + r".*?" + re.escape(end_marker)
#     cleaned_text = re.sub(pattern, "", cleaned_text, flags=re.DOTALL)
#     pattern = re.escape("[ Skip to main content ]") + r".*?" + re.escape("\n####")
#     text=re.sub(pattern, "", cleaned_text, flags=re.DOTALL)
#     pattern = re.escape("[ Skip to main content ]") + r".*?" + re.escape("[ Return focus to the top of the page ]")
#     cleaned_text = re.sub(pattern, "", cleaned_text , flags=re.DOTALL)
#     return cleaned_text




# async def main(url):
#   try:
#     async with AsyncWebCrawler() as crawler:
#         result = await crawler.arun(
#             url=url,
#             excluded_tags=['header', 'footer', 'nav', 'aside'],
#             exclude_external_links=True,
#         )
#         url=result.url
#         result=remove_section(result.markdown)
#         return result,url
#   except Exception as e:
#     print(f"❌ Failed to load {url}: {e}")
#     return None,None


# # main function function to fetch the data
# def run_data_extraction_whole():
#   with open('muet_links.txt') as f:
#     file_content = f.read()
#   extracted_links = []
#   for line in file_content.split('\n'):
#       line = line.strip()
#       if line.startswith('http://') or line.startswith('https://'):
#           extracted_links.append(line)

#   # In Jupyter/IPython, just await directly
#   list_urls=[]
#   list_result=[]
#   OUTPUT_FILE = "muet_data.txt"
#   for _,links in enumerate(extracted_links):
#     if "muet" not in links:
#       continue
#     if "facebook" in links:
#       continue
#     print('executing no',_)
#     result ,urls= await main(links)
#     list_urls.append(urls)
#     list_result.append(result)

#   with open('muet_data.txt', "w", encoding="utf-8") as f:
#       for data in list_result:
#         if data:
#           f.write(data + "\n\n\n\n")
#         else:
#           print("no link")

#   return list_result, list_urls



















import re
import asyncio
from crawl4ai import AsyncWebCrawler

# ============================================================
# TEXT CLEANING
# ============================================================
def remove_sections(text: str) -> str:
    """
    Removes navigation, skip links, and repeated headers
    """
    if not text:
        return ""

    patterns = [
        r"\[Skip to Main Content\].*?\n{2,}#",
        r"\[ Skip to main content \].*?\n####",
        r"\[ Skip to main content \].*?\[ Return focus to the top of the page \]",
        r"#.*?\n{2,}#",   # repeated markdown headers
        r'!\[Mehran University official Logo\][\s\S]*$'
    ]

    cleaned = text
    for pattern in patterns:
        cleaned = re.sub(
            pattern,
            "",
            cleaned,
            flags=re.DOTALL | re.IGNORECASE
        )

    return cleaned.strip()


# ============================================================
# SINGLE PAGE FETCHER
# ============================================================
async def fetch_page(url: str):
    try:
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(
                url=url,
                excluded_tags=["header", "footer", "nav", "aside"],
                exclude_external_links=True,
            )

            if not result or not result.markdown:
                return None, url

            cleaned_text = remove_sections(result.markdown)
            return cleaned_text, result.url

    except Exception as e:
        print(f"❌ Failed: {url} | {e}")
        return None, url


# ============================================================
# MAIN PIPELINE
# ============================================================
async def run_data_extraction_whole(OUTPUT_FILE):
    INPUT_FILE = "data\muet_links.txt"

    # ----------------------------
    # Load & filter URLs
    # ----------------------------
    with open(INPUT_FILE, encoding="utf-8") as f:
        urls = {
            line.strip()
            for line in f
            if line.startswith("http")
            and "muet.edu.pk" in line
            and "facebook" not in line
        }

    print(f"🔗 Total URLs to crawl: {len(urls)}")

    results = []
    final_urls = []

    # ----------------------------
    # Crawl each page
    # ----------------------------
    for idx, url in enumerate(urls, 1):
        print(f"🚀 ({idx}/{len(urls)}) Crawling: {url}")

        text, final_url = await fetch_page(url)

        if text:
            results.append(text)
            final_urls.append(final_url)

        await asyncio.sleep(0.5)  # polite crawling

    # ----------------------------
    # Save cleaned data
    # ----------------------------
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for content in results:
            f.write(content + "\n\n\n")

    print(f"✅ Saved cleaned data to {OUTPUT_FILE}")
    print(f"📄 Pages processed: {len(results)}")

    return results, final_urls


# ============================================================
# RUN (Jupyter / Script Compatible)
# ============================================================
# results, final_urls = await run_data_extraction_whole()

