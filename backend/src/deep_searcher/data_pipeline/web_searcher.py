# src/deep_searcher/data_pipeline/web_searcher.py
import asyncio
import itertools
import logging
from functools import partial
from concurrent.futures import ThreadPoolExecutor

from googleapiclient.discovery import build
from config.settings import settings

logger = logging.getLogger(__name__)

def _execute_single_google_search(query: str, max_results: int, search_type: str) -> list[dict]:
    """(Internal Helper) Performs a single synchronous web or image search using Google."""
    logger.info(f"Executing {search_type.upper()} search for query: '{query}'...")
    try:
        service = build("customsearch", "v1", developerKey=settings.GOOGLE_API_KEY)
        
        # --- FIX: Build a params dictionary for the API call ---
        params = {
            "q": query,
            "cx": settings.GOOGLE_CSE_ID,
            "num": max_results
        }
        if search_type == 'image':
            params['searchType'] = 'image'
        
        # Execute the request with the correct parameters
        res = service.cse().list(**params).execute()
        # --- END OF FIX ---
        
        search_items = res.get("items", [])
        results = [
            {"title": item.get("title", "Untitled"), "href": item.get("link"), "mime": item.get("mime", "application/octet-stream")}
            for item in search_items if item.get("link")
        ]
        logger.info(f"Found {len(results)} {search_type} results for query: '{query}'")
        return results
    except Exception as e:
        logger.error(f"An error occurred during {search_type} search for '{query}': {e}")
        return []

async def perform_searches_and_get_hits(queries: list[str], executor: ThreadPoolExecutor, search_type: str = 'web') -> list[dict]:
    """Asynchronously runs multiple Google searches and returns a de-duplicated list of hits."""
    logger.info(f"\n--- Starting concurrent {search_type.upper()} search for {len(queries)} queries ---")
    loop = asyncio.get_running_loop()
    
    max_results = settings.IMAGE_SEARCH_MAX_RESULTS_PER_QUERY if search_type == 'image' else settings.SEARCH_MAX_RESULTS_PER_QUERY
    
    search_tasks = [partial(_execute_single_google_search, query, max_results, search_type) for query in queries]
    search_coroutines = [loop.run_in_executor(executor, task) for task in search_tasks]
    list_of_hit_lists = await asyncio.gather(*search_coroutines)
    
    unique_hits = {hit['href']: hit for hit in itertools.chain.from_iterable(list_of_hit_lists)}
    
    final_hits = list(unique_hits.values())
    logger.info(f"--- {search_type.upper()} search complete. Found {len(final_hits)} unique items in total. ---")
    return final_hits