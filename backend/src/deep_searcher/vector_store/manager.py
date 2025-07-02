# src/deep_searcher/vector_store/manager.py
import logging
import uuid
from typing import List

import chromadb
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema.document import Document
from langchain_community.vectorstores.utils import filter_complex_metadata
from langchain.schema.retriever import BaseRetriever
from langchain.text_splitter import RecursiveCharacterTextSplitter

from config.settings import settings
from src.deep_searcher.utils.sanitizers import sanitize_for_collection_name

logger = logging.getLogger(__name__)

class VectorStoreManager:
    """Manages all interactions with the ChromaDB vector store."""

    def __init__(self):
        self.embedding_function = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=settings.OPENAI_API_KEY
        )
        self.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
        logger.info(f"VectorStoreManager initialized with ChromaDB client at '{settings.CHROMA_PERSIST_DIR}'")

    def get_sanitized_name(self, name: str) -> str:
        return sanitize_for_collection_name(name)

    def get_collection_name(self, topic_name: str, collection_type: str) -> str:
        sanitized_topic = self.get_sanitized_name(topic_name)
        return f"{sanitized_topic}_{collection_type}"

    def reset_collections(self, topic_name: str):
        sanitized_topic = self.get_sanitized_name(topic_name)
        logger.warning(f"Resetting all collections for topic: '{topic_name}' (sanitized: '{sanitized_topic}')...")
        all_collections = self.client.list_collections()
        collections_to_delete = [c.name for c in all_collections if c.name.startswith(f"{sanitized_topic}_")]
        if not collections_to_delete:
            logger.info(f"No collections found for topic '{topic_name}' to delete.")
            return
        for collection_name in collections_to_delete:
            try:
                self.client.delete_collection(name=collection_name)
                logger.info(f"  - Successfully deleted collection: {collection_name}")
            except Exception as e:
                logger.error(f"  - Error deleting collection {collection_name}: {e}")

    def add_documents(self, collection_name: str, documents: List[Document]) -> int:
        if not documents:
            logger.warning(f"No documents provided to add to collection '{collection_name}'.")
            return 0

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
        )
        chunked_docs = text_splitter.split_documents(documents)
        
        filtered_docs = filter_complex_metadata(chunked_docs)
        total_docs = len(filtered_docs)
        if total_docs == 0:
            logger.warning(f"No processable chunks were generated for collection '{collection_name}'.")
            return 0

        logger.info(f"Adding {total_docs} document chunks to '{collection_name}' in batches of {settings.CHROMA_BATCH_SIZE}...")
        vector_store = Chroma(
            client=self.client,
            collection_name=collection_name,
            embedding_function=self.embedding_function
        )

        for i in range(0, total_docs, settings.CHROMA_BATCH_SIZE):
            batch = filtered_docs[i:i + settings.CHROMA_BATCH_SIZE]
            try:
                vector_store.add_documents(batch)
            except Exception as e:
                logger.error(f"Failed to ingest batch for collection {collection_name}: {e}")
        
        logger.info(f"Successfully added {total_docs} chunks to collection '{collection_name}'.")
        return total_docs

    def get_collection_sources(self, collection_name: str) -> List[str]:
        try:
            collection = self.client.get_collection(name=collection_name)
            results = collection.get(include=["metadatas"])
            metadatas = results.get("metadatas", [])
            if not metadatas: return []
            unique_sources = {meta['source'] for meta in metadatas if 'source' in meta}
            return sorted(list(unique_sources))
        except Exception:
            return []

    def create_retriever(self, topic_name: str, collection_type: str = "text") -> BaseRetriever:
        collection_name = self.get_collection_name(topic_name, collection_type)
        k = settings.IMAGE_RETRIEVER_TOP_K if collection_type == "images" else settings.RETRIEVER_TOP_K
        logger.info(f"Creating retriever with k={k} for collection: {collection_name}")
        
        try:
            self.client.get_collection(name=collection_name)
            store = Chroma(
                client=self.client,
                collection_name=collection_name,
                embedding_function=self.embedding_function,
            )
            return store.as_retriever(search_kwargs={"k": k})
        except Exception:
            logger.warning(f"Collection '{collection_name}' not found. Retrieval for this type will yield no results.")
            dummy_store = Chroma(
                client=self.client,
                collection_name=f"dummy_{uuid.uuid4().hex}",
                embedding_function=self.embedding_function,
            )
            return dummy_store.as_retriever(search_kwargs={"k": k})