# src/deep_searcher/agents/question_spec_generator_agent.py
import logging
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI

from config.settings import settings
from src.deep_searcher.utils.file_utils import load_prompt
from src.deep_searcher.models.exam_models import GeneratedQuestionSpecs

logger = logging.getLogger(__name__)

class QuestionSpecGeneratorAgent:
    """An agent that generates question specifications based on document context."""
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.DEFAULT_LLM_MODEL,
            temperature=0.2, # Low temp for deterministic structure
            openai_api_key=settings.OPENAI_API_KEY
        )
        self.prompt_template = load_prompt("prompts/question_spec_generator/system.prompt")
        self.parser = JsonOutputParser(pydantic_object=GeneratedQuestionSpecs)

        self.chain: Runnable = (
            ChatPromptTemplate.from_template(self.prompt_template)
            | self.llm
            | self.parser
        )