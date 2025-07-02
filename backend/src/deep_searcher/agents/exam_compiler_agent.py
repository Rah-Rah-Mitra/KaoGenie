# src/deep_searcher/agents/exam_compiler_agent.py
import json
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnablePassthrough
from langchain_openai import ChatOpenAI

from config.settings import settings
from src.deep_searcher.utils.file_utils import load_prompt
from src.deep_searcher.models.exam_models import CompiledExam

class ExamCompilerAgent:
    """An agent that formats questions and solutions into final exam documents."""
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.DEFAULT_LLM_MODEL,
            temperature=0.0,
            openai_api_key=settings.OPENAI_API_KEY
        )
        self.prompt_template = load_prompt("prompts/exam_compiler_agent/system.prompt")
        self.parser = JsonOutputParser(pydantic_object=CompiledExam)

        self.chain: Runnable = (
            RunnablePassthrough.assign(
                exam_questions_json=lambda x: json.dumps([q.model_dump() for q in x["exam_questions"]], indent=2)
            )
            | ChatPromptTemplate.from_template(self.prompt_template)
            | self.llm
            | self.parser
        )