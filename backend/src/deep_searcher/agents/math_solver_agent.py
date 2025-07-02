# src/deep_searcher/agents/math_solver_agent.py
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnablePassthrough
from langchain_openai import ChatOpenAI

from config.settings import settings
from src.deep_searcher.utils.file_utils import load_prompt
from src.deep_searcher.models.exam_models import GeneratedSolution

class MathSolverAgent:
    """A specialized agent for solving math problems using DeepSeek-Math."""
    def __init__(self):
        self.llm = ChatOpenAI(
            # model=settings.MATH_LLM_MODEL,
            model=settings.DEFAULT_LLM_MODEL,
            temperature=0.0,
            openai_api_key=settings.OPENAI_API_KEY
            #api_key=settings.DEEPSEEK_API_KEY,
            #base_url=settings.DEEPSEEK_API_URL
        )
        self.prompt_template = load_prompt("prompts/math_solver_agent/system.prompt")
        # Switch to the more robust PydanticOutputParser
        self.parser = PydanticOutputParser(pydantic_object=GeneratedSolution)

        # Update the chain to dynamically insert formatting instructions
        self.chain: Runnable = (
            RunnablePassthrough.assign(
                format_instructions=lambda x: self.parser.get_format_instructions()
            )
            | ChatPromptTemplate.from_template(self.prompt_template)
            | self.llm
            | self.parser
        )