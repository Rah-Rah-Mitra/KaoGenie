# src/deep_searcher/agents/question_generator_agent.py
import logging
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnablePassthrough
from langchain.schema.retriever import BaseRetriever
from langchain.schema.document import Document
from langchain_openai import ChatOpenAI

from config.settings import settings
from src.deep_searcher.utils.file_utils import load_prompt
from src.deep_searcher.models.exam_models import GeneratedQuestions

logger = logging.getLogger(__name__)

class QuestionGeneratorAgent:
    """An agent that generates questions based on retrieved context."""
    def __init__(self, retriever: BaseRetriever, image_retriever: BaseRetriever):
        self.retriever = retriever
        self.image_retriever = image_retriever
        self.llm = ChatOpenAI(
            model=settings.DEFAULT_LLM_MODEL,
            temperature=0.3,
            openai_api_key=settings.OPENAI_API_KEY
        )
        self.prompt_template = load_prompt("prompts/question_generator/system.prompt")
        self.parser = JsonOutputParser(pydantic_object=GeneratedQuestions)

        self.chain: Runnable = (
            RunnablePassthrough.assign(
                context=lambda x: self._get_combined_context(x["subject"])
            )
            | ChatPromptTemplate.from_template(self.prompt_template)
            | self.llm
            | self.parser
        )

    def _format_docs(self, docs: list[Document]) -> str:
        """Formats retrieved documents into a single string."""
        if not docs:
            return "No documents found."
        
        formatted_docs = []
        for doc in docs:
            source = doc.metadata.get('source', 'N/A')
            content = doc.page_content
            header = f"[Source: {source}]"
            # Add image source directly if content is a description
            if "description of an image" in content.lower() or content.startswith("Image of"):
                 header = f"[Image Source: {source}]"

            formatted_docs.append(f"{header}\n{content}")
            
        return "\n\n---\n\n".join(formatted_docs)

    def _get_combined_context(self, topic: str) -> str:
        """Retrieves and formats both text and image context."""
        logger.info(f"Retrieving context for topic: {topic}")
        text_docs = self.retriever.invoke(topic)
        image_docs = self.image_retriever.invoke(topic)
        
        text_context = self._format_docs(text_docs)
        image_context = self._format_docs(image_docs)

        return f"Textual Content:\n{text_context}\n\nAvailable Images:\n{image_context}"