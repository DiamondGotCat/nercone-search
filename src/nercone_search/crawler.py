# ┌─────────────────────────────────────────┐
# │ crawler.py on Nercone Search            │
# │ Copyright (c) 2026 DiamondGotCat        │
# │ Made by Nercone / MIT License           │
# └─────────────────────────────────────────┘

import requests
import urllib.parse
import urllib.robotparser
from bs4 import BeautifulSoup
from markitdown import MarkItDown
from cachetools import TTLCache, cached
from .embed import embed
from .database import append
from .config import CrawlerName, CrawlerVersion, CrawlerAdditionalInformations, CrawlerRobotsCacheTTL, CrawlerRobotsCacheSize

md = MarkItDown()
robots_cache = TTLCache(maxsize=CrawlerRobotsCacheSize, ttl=CrawlerRobotsCacheTTL)

@cached(robots_cache)
def fetch_robots(url: str) -> str:
    response = requests.get(url, headers={"User-Agent": f"{CrawlerName}/{CrawlerVersion} ({', '.join(CrawlerAdditionalInformations)})"}, allow_redirects=True)
    if str(response.status_code).startswith("2"):
        return response.text
    else:
        return "User-agent: *\nDisallow: /"

def can_fetch(url: str) -> bool:
    parsed_url = urllib.parse.urlparse(url)
    robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
    robots_txt = fetch_robots(robots_url)
    parser = urllib.robotparser.RobotFileParser()
    parser.set_url(robots_url)
    parser.parse(robots_txt)
    return parser.can_fetch(f"{CrawlerName}/{CrawlerVersion}", url)

def crawl(url: str, disallow_ok: bool = False):
    if can_fetch(url):
        response = requests.get(url, headers={"User-Agent": f"{CrawlerName}/{CrawlerVersion} ({', '.join(CrawlerAdditionalInformations)})"}, allow_redirects=True)
        if str(response.status_code).startswith("2"):
            if response.headers.get("Content-Type", "unknown").lower().startswith("text/"):
                content = response.text
                content_md = md.convert(response).markdown
                if response.headers.get("Content-Type", "unknown").lower() == "text/html":
                    bs = BeautifulSoup(content, "html.parser")
                    title = bs.title.string.strip() if bs.title and bs.title.string else "No Title"
                    description_tag = bs.find("meta", attrs={"name": "description"})
                    description = description_tag["content"].strip() if description_tag and description_tag.has_attr("content") else "No description."
                    keywords_tag = bs.find("meta", attrs={"name": "keywords"})
                    keywords_text = keywords_tag["content"].strip() if keywords_tag and keywords_tag.has_attr("content") else ""
                    keywords = list(map(str.strip, keywords_text.split(",")))
                    append(url=url, title=title, description=description, markdown=content_md, keywords=keywords, tensor=embed(content_md))
    elif not disallow_ok:
        raise Exception(f"Cannot fetch '{url}' because Disallowed in robots.txt")
