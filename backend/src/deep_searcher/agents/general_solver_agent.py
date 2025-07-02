# src/deep_searcher/agents/general_solver_agent.py
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI

from config.settings import settings
from src.deep_searcher.utils.file_utils import load_prompt
from src.deep_searcher.models.exam_models import GeneratedSolution

class GeneralSolverAgent:
    """An agent that provides solutions for non-math questions."""
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.DEFAULT_LLM_MODEL,
            temperature=0.0,
            openai_api_key=settings.OPENAI_API_KEY
        )
        self.prompt_template = load_prompt("prompts/general_solver_agent/system.prompt")
        self.parser = JsonOutputParser(pydantic_object=GeneratedSolution)

        self.chain: Runnable = (
            ChatPromptTemplate.from_template(self.prompt_template)
            | self.llm
            | self.parser
        )