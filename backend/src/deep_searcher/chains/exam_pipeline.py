# src/deep_searcher/chains/exam_pipeline.py
import asyncio
import uuid
import logging
from typing import List, Dict, Tuple

from src.deep_searcher.models.exam_models import QuestionSpec, ExamQuestion, CompiledExam
from src.deep_searcher.agents.question_generator_agent import QuestionGeneratorAgent
from src.deep_searcher.agents.math_solver_agent import MathSolverAgent
from src.deep_searcher.agents.general_solver_agent import GeneralSolverAgent
from src.deep_searcher.agents.exam_compiler_agent import ExamCompilerAgent
from src.deep_searcher.vector_store.manager import VectorStoreManager
from src.deep_searcher.utils.streaming_utils import StreamCallbackHandler

logger = logging.getLogger(__name__)


async def run_exam_generation_pipeline(
    subject: str,
    grade_level: str,
    question_specs: List[QuestionSpec],
    vsm: VectorStoreManager,
    callback: StreamCallbackHandler,
) -> Tuple[CompiledExam, List[ExamQuestion]]:
    """Orchestrates the parallel generation of an exam, sending progress updates."""
    
    # 1. Prepare retrievers
    text_retriever = vsm.create_retriever(topic_name=subject, collection_type="text")
    image_retriever = vsm.create_retriever(topic_name=subject, collection_type="images")

    # 2. Instantiate agents
    question_agent = QuestionGeneratorAgent(retriever=text_retriever, image_retriever=image_retriever)
    math_solver = MathSolverAgent()
    general_solver = GeneralSolverAgent()
    compiler = ExamCompilerAgent()

    # 3. Generate all questions in parallel
    total_questions_to_generate = sum(spec.count for spec in question_specs)
    log_msg = f"Generating {total_questions_to_generate} questions across {len(question_specs)} specifications..."
    logger.info(log_msg)
    await callback.send_update("progress", {"step": "question_generation", "status": log_msg})

    question_gen_tasks = []
    for spec in question_specs:
        task = question_agent.chain.ainvoke({
            "subject": subject,
            "grade_level": grade_level,
            "question_type": spec.question_type,
            "count": spec.count,
            "user_prompt": spec.prompt or "None"
        })
        question_gen_tasks.append((task, spec.question_type))
    
    question_results_with_type = await asyncio.gather(*(t for t, _ in question_gen_tasks))
    
    all_generated_questions = []
    for i, result in enumerate(question_results_with_type):
        q_type = question_gen_tasks[i][1]
        for q_data in result.get('questions', []):
            all_generated_questions.append((q_data, q_type))

    log_msg = f"--- Generated a total of {len(all_generated_questions)} questions ---"
    logger.info(log_msg)
    await callback.send_update("log", {"message": log_msg})

    # 4. Solve all questions in parallel
    log_msg = f"Starting parallel solution generation for {len(all_generated_questions)} questions..."
    logger.info(log_msg)
    await callback.send_update("progress", {"step": "solution_generation", "status": log_msg})

    solution_gen_tasks = []
    for q_data, q_type in all_generated_questions:
        if q_type == "Math Problem":
            task = math_solver.chain.ainvoke({"question_text": q_data['question_text']})
        else:
            task = general_solver.chain.ainvoke({
                "question_type": q_type,
                "question_text": q_data['question_text'],
                "options": q_data.get('options')
            })
        solution_gen_tasks.append(task)

    solutions = await asyncio.gather(*solution_gen_tasks)
    log_msg = "--- Completed solution generation ---"
    logger.info(log_msg)
    await callback.send_update("log", {"message": log_msg})

    # 5. Combine questions and solutions into structured objects
    exam_questions: List[ExamQuestion] = []
    for (q_data, q_type), sol_data in zip(all_generated_questions, solutions):
        exam_q = ExamQuestion(
            id=f"q-{uuid.uuid4().hex[:8]}",
            question_type=q_type,
            question_text=q_data['question_text'],
            options=q_data.get('options'),
            image_url=q_data.get('image_url'),
            solution=sol_data
        )
        exam_questions.append(exam_q)
    
    # 6. Compile final exam and answer key
    log_msg = "--- Compiling final exam documents ---"
    logger.info(log_msg)
    await callback.send_update("progress", {"step": "compilation", "status": "Compiling final exam documents..."})
    
    compiled_result = await compiler.chain.ainvoke({"exam_questions": exam_questions})
    
    log_msg = "--- Exam compilation complete ---"
    logger.info(log_msg)
    await callback.send_update("log", {"message": log_msg})

    return compiled_result, exam_questions