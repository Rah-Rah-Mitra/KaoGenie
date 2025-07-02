# src/deep_searcher/data_pipeline/crawler.py

import asyncio
import logging
import re
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Set

import aiohttp
from bs4 import BeautifulSoup

from config.settings import settings
from src.deep_searcher.utils.url_utils import normalize_url

logger = logging.getLogger(__name__)

HEADERS = {
    'User-Agent': settings.CRAWLER_USER_AGENT
}

def _is_valid_url(url: str, base_domain: str) -> bool:
    """Checks if a URL is valid and within the same domain."""
    if not url or url.startswith(('#', 'mailto:', 'tel:')):
        return False
    
    try:
        parsed_url = urlparse(url)
        # It's a relative URL, so it's valid for joining
        if not parsed_url.scheme:
            return True
        # It's an absolute URL, check if it's http/https and from the same domain
        if parsed_url.scheme in ['http', 'https'] and parsed_url.netloc == base_domain:
            return True
        return False
    except Exception:
        return False

def _filter_urls(urls: Set[str]) -> Set[str]:
    """Filters a set of URLs against the regex patterns in settings."""
    if not settings.CRAWLER_EXCLUDE_PATTERNS:
        return urls
    
    filtered_urls = set()
    for url in urls:
        if not any(re.search(pattern, url, re.IGNORECASE) for pattern in settings.CRAWLER_EXCLUDE_PATTERNS):
            filtered_urls.add(url)
    return filtered_urls

async def _fetch_and_extract_links(session: aiohttp.ClientSession, url: str) -> Set[str]:
    """Fetches a single URL and extracts all valid, same-domain, absolute links."""
    extracted_links = set()
    try:
        # Reuse downloader timeout setting for individual requests
        timeout = aiohttp.ClientTimeout(total=settings.DOWNLOADER_TIMEOUT)
        async with session.get(url, timeout=timeout, headers=HEADERS, ssl=False) as response:
            if response.status != 200 or 'text/html' not in response.headers.get('Content-Type', ''):
                logger.debug(f"Skipping non-HTML or failed request for {url} (Status: {response.status})")
                return extracted_links

            html = await response.text()
            soup = BeautifulSoup(html, 'lxml')
            base_domain = urlparse(url).netloc

            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                absolute_url = normalize_url(urljoin(url, href.strip()))
                
                if _is_valid_url(absolute_url, base_domain):
                    extracted_links.add(absolute_url)
            
            return extracted_links
    except asyncio.TimeoutError:
        logger.warning(f"Timeout while trying to fetch {url}")
        return extracted_links
    except Exception as e:
        logger.warning(f"Could not fetch or parse {url}. Reason: {e}")
        return extracted_links

async def discover_urls_from_hits(hits: List[Dict]) -> List[str]:
    """
    Takes initial search hits, crawls them to find more links, and returns a
    unified list of relevant URLs, respecting the CRAWLER_MAX_DISCOVERED_URLS limit.
    """
    if not hits:
        return []

    initial_urls = {normalize_url(hit['href']) for hit in hits if hit.get('href')}
    logger.info(f"Step 1: Received {len(initial_urls)} unique initial URLs from search hits.")

    discovered_links = set()
    # Reuse ingestion concurrency setting to limit simultaneous crawl requests
    semaphore = asyncio.Semaphore(settings.INGESTION_CONCURRENT_DOWNLOADS)

    async def crawl_task_wrapper(url, session):
        async with semaphore:
            return await _fetch_and_extract_links(session, url)

    async with aiohttp.ClientSession() as session:
        logger.info(f"Step 2: Starting simple crawl on initial URLs...")
        tasks = [crawl_task_wrapper(url, session) for url in initial_urls]
        results = await asyncio.gather(*tasks)
    
    for link_set in results:
        if link_set:
            discovered_links.update(link_set)
            
    logger.info(f"Step 3: Discovered {len(discovered_links)} new links from crawling.")

    # Combine initial URLs with the newly discovered links
    combined_urls = initial_urls.union(discovered_links)

    # Filter the final list against exclude patterns
    filtered_urls = _filter_urls(combined_urls)
    initial_filtered_count = len(filtered_urls)

    # Apply the new limit from settings
    max_urls = settings.CRAWLER_MAX_DISCOVERED_URLS
    if max_urls > 0 and initial_filtered_count > max_urls:
        logger.warning(
            f"Crawler discovered {initial_filtered_count} URLs, which exceeds the limit of {max_urls}. "
            f"Truncating the list to the first {max_urls} URLs."
        )
        final_urls_list = sorted(list(filtered_urls))[:max_urls]
    else:
        final_urls_list = sorted(list(filtered_urls))
    
    limit_info = f"limit is {max_urls}" if max_urls > 0 else "limit is disabled"
    logger.info(f"Discovery complete. Returning {len(final_urls_list)} unique and filtered URLs ({limit_info}).")
    return final_urls_list