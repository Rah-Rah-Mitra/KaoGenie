# config/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    # Load from .env file
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    # --- API Keys ---
    OPENAI_API_KEY: str
    DEEPSEEK_API_KEY: str
    GOOGLE_API_KEY: str
    GOOGLE_CSE_ID: str

    # --- LLM & Search Configuration ---
    DEFAULT_LLM_MODEL: str = "gpt-4.1" # Do not change
    MATH_LLM_MODEL: str = "deepseek-reasoner"
    DEEPSEEK_API_URL: str = "https://api.deepseek.com" # NEW
    SEARCH_QUERIES_TO_GENERATE: int = 2
    SEARCH_MAX_RESULTS_PER_QUERY: int = 10
    IMAGE_SEARCH_QUERIES_TO_GENERATE: int = 2
    IMAGE_SEARCH_MAX_RESULTS_PER_QUERY: int = 10
    RETRIEVER_TOP_K: int = 10
    IMAGE_RETRIEVER_TOP_K: int = 5
    
    # --- Data Ingestion & Exam Generation Configuration ---
    DOWNLOADER_TIMEOUT: int = 15
    INGESTION_CONCURRENT_DOWNLOADS: int = 5
    EXAM_GENERATION_MAX_CONCURRENCY: int = 5
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    CHROMA_BATCH_SIZE: int = 5000
    IMAGE_PARTITIONING_STRATEGY: str = "auto"

    # --- Vector Store Configuration ---
    CHROMA_PERSIST_DIR: str = "./chroma_store"
    
    # --- Web Crawler Configuration ---
    # User agent for your custom crawler's requests.
    CRAWLER_USER_AGENT: str = "ExamGeneratorBot/1.0 (Educational Research; +http://example.com/bot)"

    # Regex patterns to exclude certain URLs from being processed.
    CRAWLER_EXCLUDE_PATTERNS: list[str] = [
        r".*/login.*", r".*/signin.*", r".*/register.*",
        r".*/contact.*", r".*mailto:.*", r".*tel:.*",
        r".*\.(zip|exe|dmg|mp4|mp3)$", # Filter out common file types and images during crawl
        r".*#.*" # Exclude fragment identifiers
    ]
    
    # NEW: The maximum number of URLs to process after discovery. Set to 0 for unlimited.
    CRAWLER_MAX_DISCOVERED_URLS: int = 10


settings = Settings()