# src/deep_searcher/agents/query_generator_agent.py
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI

from config.settings import settings
from src.deep_searcher.utils.file_utils import load_prompt
from src.deep_searcher.models.exam_models import GeneratedQueries

class SearchQueryGeneratorAgent:
    """An agent that generates a list of search queries based on a subject and grade level."""
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.DEFAULT_LLM_MODEL,
            temperature=0.2,
            openai_api_key=settings.OPENAI_API_KEY
        )
        self.prompt_template = load_prompt("prompts/query_generator/system.prompt")
        self.parser = JsonOutputParser(pydantic_object=GeneratedQueries)

        self.chain: Runnable = (
            ChatPromptTemplate.from_template(self.prompt_template)
            | self.llm
            | self.parser
        )