# src/deep_searcher/data_pipeline/url_processor.py
import asyncio
import logging
from io import BytesIO
from functools import partial
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Tuple, Dict, List

import aiohttp
from fastapi import UploadFile
from unstructured.partition.html import partition_html
from unstructured.partition.pdf import partition_pdf
from unstructured.partition.image import partition_image
from unstructured.partition.docx import partition_docx
from unstructured.documents.elements import Element as UnstructuredElement
from langchain_core.documents import Document

from config.settings import settings
from src.deep_searcher.utils.url_utils import normalize_url

logger = logging.getLogger(__name__)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
}

# We remove PDF from this dispatcher as it will now be handled conditionally.
PARTITION_DISPATCHER: Dict[str, Callable[..., List[UnstructuredElement]]] = {
    "text/html": partial(partition_html, strategy="fast"),
    "image/jpeg": partial(partition_image, strategy=settings.IMAGE_PARTITIONING_STRATEGY),
    "image/png": partial(partition_image, strategy=settings.IMAGE_PARTITIONING_STRATEGY),
    "image/gif": partial(partition_image, strategy=settings.IMAGE_PARTITIONING_STRATEGY),
    "image/webp": partial(partition_image, strategy=settings.IMAGE_PARTITIONING_STRATEGY),
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": partial(partition_docx, strategy="fast"),
}

def _partition_and_convert(content_bytes: bytes, content_type: str, source_name: str, pdf_strategy: str = "fast") -> List[Document]:
    """Partitions content, allowing for a specific PDF strategy."""
    if not content_bytes or not content_type:
        return []

    partition_func = None
    # Special handling for PDFs to allow strategy selection.
    if content_type == "application/pdf":
        logger.debug(f"Partitioning PDF '{source_name}' with strategy: '{pdf_strategy}'")
        partition_func = partial(partition_pdf, strategy=pdf_strategy, extract_images_in_pdf=False)
    else:
        partition_func = PARTITION_DISPATCHER.get(content_type)

    if not partition_func:
        logger.warning(f"Skipping partitioning for unsupported content type: {content_type} from {source_name}")
        return []
            
    try:
        file = BytesIO(content_bytes)
        if content_type.startswith("image/"):
             elements = partition_func(file=file, file_filename=source_name)
        else:
             elements = partition_func(file=file, metadata_filename=source_name)
        
        docs = []
        for el in elements:
            if not el.text:
                if content_type.startswith("image/"):
                    placeholder_text = f"An image from {source_name}"
                    metadata = el.metadata.to_dict()
                    metadata['source'] = metadata.get('filename', source_name)
                    docs.append(Document(page_content=placeholder_text, metadata=metadata))
                continue
            metadata = el.metadata.to_dict()
            metadata['source'] = metadata.get('filename', source_name)
            docs.append(Document(page_content=el.text, metadata=metadata))
        return docs
    except Exception as e:
        logger.error(f"Failed to partition {source_name} ({content_type}): {e}")
        return []

async def process_local_file_content(content_bytes: bytes, filename: str, content_type: str) -> List[Document]:
    """Processes content from a locally uploaded file using 'auto' strategy for PDFs."""
    logger.info(f"Processing local file: {filename} ({content_type})")
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as executor:
        docs = await loop.run_in_executor(
            executor,
            # Use 'auto' strategy for local files to enable full OCR
            partial(_partition_and_convert, content_bytes, content_type, filename, pdf_strategy="auto")
        )
    logger.info(f"Generated {len(docs)} documents from local file {filename}.")
    return docs

async def _download_content(session: aiohttp.ClientSession, url: str) -> Tuple[bytes | None, str | None]:
    try:
        timeout = aiohttp.ClientTimeout(total=settings.DOWNLOADER_TIMEOUT)
        async with session.get(url, timeout=timeout, headers=HEADERS, ssl=False) as resp:
            resp.raise_for_status()
            content_bytes = await resp.read()
            content_type = resp.headers.get("Content-Type", "").split(";")[0]
            return content_bytes, content_type
    except Exception as e:
        logger.warning(f"Failed to download {url}. Reason: {e}")
        return None, None

async def process_urls(urls: List[str]) -> List[Document]:
    """Processes URLs using 'fast' strategy for PDFs to prioritize speed and stability."""
    normalized_urls = {normalize_url(u) for u in urls if u}
    logger.info(f"Processing {len(normalized_urls)} unique, normalized URLs.")
    all_processed_docs: List[Document] = []
    semaphore = asyncio.Semaphore(settings.INGESTION_CONCURRENT_DOWNLOADS)
    
    async def process_single_url(url: str, session: aiohttp.ClientSession, executor: ThreadPoolExecutor, loop):
        async with semaphore:
            content_bytes, content_type = await _download_content(session, url)
            if content_bytes and content_type:
                return await loop.run_in_executor(
                    executor,
                    # Use 'fast' strategy for web URLs
                    partial(_partition_and_convert, content_bytes, content_type, url, pdf_strategy="fast")
                )
        return []

    async with aiohttp.ClientSession() as session:
        with ThreadPoolExecutor() as executor:
            loop = asyncio.get_running_loop()
            tasks = [process_single_url(url, session, executor, loop) for url in normalized_urls if url]
            results = await asyncio.gather(*tasks)
            for doc_list in results:
                if doc_list: all_processed_docs.extend(doc_list)

    logger.info(f"URL processing complete. Generated {len(all_processed_docs)} documents.")
    return all_processed_docs