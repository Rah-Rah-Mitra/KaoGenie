# main.py
import asyncio
import traceback
import logging
import json
import uuid
import sys
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional, Dict, Coroutine, Tuple, Callable

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from config.logging_config import setup_logging
setup_logging()

from config.settings import settings
from config.exam_presets import PRESETS
from src.deep_searcher.agents.query_generator_agent import SearchQueryGeneratorAgent
from src.deep_searcher.agents.question_spec_generator_agent import QuestionSpecGeneratorAgent
from src.deep_searcher.vector_store.manager import VectorStoreManager
from src.deep_searcher.chains.exam_pipeline import run_exam_generation_pipeline
from src.deep_searcher.models.exam_models import (
    FullExam, 
    IngestionSummary, 
    QuestionSpec, 
    ExamQuestion, 
    ExamFromTopicRequest,
)
from src.deep_searcher.data_pipeline import web_searcher, crawler, url_processor
from src.deep_searcher.utils.streaming_utils import StreamCallbackHandler

logger = logging.getLogger(__name__)

vsm = VectorStoreManager()
query_agent = SearchQueryGeneratorAgent()
spec_agent = QuestionSpecGeneratorAgent()
api_lock = asyncio.Lock()
ACTIVE_EXAMS: Dict[str, FullExam] = {}
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
]

app = FastAPI(
    title="Agentic Exam Generator API",
    description="An API to generate customized exam papers using a multi-agent system. Use `/exam/from-topic` for the best experience.",
    version="2.3.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
router = APIRouter(prefix="/exam")

async def _ingest_data_for_subject(subject: str, grade_level: str, callback: StreamCallbackHandler) -> IngestionSummary:
    log_msg = f"--- Starting data ingestion for subject: '{subject}' at level: '{grade_level}' ---"
    logger.info(log_msg)
    await callback.send_update("progress", {"step": "start_ingestion", "status": "Starting data ingestion..."})

    # Text ingestion
    await callback.send_update("progress", {"step": "text_query_gen", "status": "Generating text search queries..."})
    text_query_result = await query_agent.chain.ainvoke({
        "subject": subject, "grade_level": grade_level, "num_queries": settings.SEARCH_QUERIES_TO_GENERATE, "search_type": "text"
    })
    text_queries = text_query_result.get('queries', [])
    if not text_queries: raise HTTPException(status_code=400, detail="Text query generation failed.")
    await callback.send_update("log", {"message": f"Generated {len(text_queries)} text queries."})

    await callback.send_update("progress", {"step": "web_search", "status": "Searching the web for documents..."})
    with ThreadPoolExecutor() as executor:
        hits = await web_searcher.perform_searches_and_get_hits(queries=text_queries, executor=executor, search_type='web')
    await callback.send_update("log", {"message": f"Initial web search found {len(hits)} potential documents."})

    await callback.send_update("progress", {"step": "crawling", "status": "Discovering more links from search results..."})
    discovered_urls = await crawler.discover_urls_from_hits(hits)
    await callback.send_update("log", {"message": f"Discovered a total of {len(discovered_urls)} URLs for processing."})

    await callback.send_update("progress", {"step": "text_processing", "status": "Downloading and processing text content..."})
    text_docs = await url_processor.process_urls(discovered_urls)
    text_collection_name = vsm.get_collection_name(subject, "text")
    text_chunks_ingested = vsm.add_documents(text_collection_name, text_docs)
    await callback.send_update("log", {"message": f"Processed text content into {text_chunks_ingested} chunks."})

    # Image ingestion
    await callback.send_update("progress", {"step": "image_query_gen", "status": "Generating image search queries..."})
    image_query_result = await query_agent.chain.ainvoke({
        "subject": subject, "grade_level": grade_level, "num_queries": settings.IMAGE_SEARCH_QUERIES_TO_GENERATE, "search_type": "image"
    })
    image_queries = image_query_result.get('queries', [])
    image_chunks_ingested = 0
    image_urls = []
    if image_queries:
        await callback.send_update("log", {"message": f"Generated {len(image_queries)} image queries."})
        await callback.send_update("progress", {"step": "image_search", "status": "Searching for relevant images..."})
        with ThreadPoolExecutor() as executor:
            image_hits = await web_searcher.perform_searches_and_get_hits(queries=image_queries, executor=executor, search_type='image')
            image_urls = [hit['href'] for hit in image_hits if hit.get('href')]
        if image_urls:
            await callback.send_update("log", {"message": f"Found {len(image_urls)} potential images."})
            await callback.send_update("progress", {"step": "image_processing", "status": "Downloading and processing images..."})
            image_docs = await url_processor.process_urls(image_urls)
            images_collection_name = vsm.get_collection_name(subject, "images")
            image_chunks_ingested = vsm.add_documents(images_collection_name, image_docs)
            await callback.send_update("log", {"message": f"Processed images into {image_chunks_ingested} chunks."})

    verified_text_sources = vsm.get_collection_sources(text_collection_name)
    verified_image_sources = vsm.get_collection_sources(vsm.get_collection_name(subject, "images"))
    return IngestionSummary(
        message=f"Ingestion complete for '{subject}'.",
        processed_sources_count=len(discovered_urls) + len(image_urls),
        total_chunks_ingested=text_chunks_ingested + image_chunks_ingested,
        collections_created=[name for name, count in [(text_collection_name, text_chunks_ingested), (vsm.get_collection_name(subject, "images"), image_chunks_ingested)] if count > 0],
        ingested_sources=sorted(list(set(verified_text_sources + verified_image_sources)))
    )

async def _orchestrate_exam_generation(
    subject: str,
    grade_level: str,
    exam_title: str,
    question_specs: List[QuestionSpec],
    ingestion_coroutine_factory: Callable[..., Coroutine],
    callback: StreamCallbackHandler
) -> FullExam:
    exam_id = f"exam-{uuid.uuid4().hex}"
    
    await callback.send_update("log", {"message": f"Preparing environment for subject: '{subject}'."})
    vsm.reset_collections(subject)

    ingestion_coroutine = ingestion_coroutine_factory(subject, grade_level, callback)
    ingestion_summary = await ingestion_coroutine
    
    if ingestion_summary.total_chunks_ingested == 0:
        raise HTTPException(status_code=404, detail="Could not find or process any source material. The file might be empty, corrupted, or of an unsupported format.")
        
    await callback.send_update("log", {"message": "Data ingestion complete. Starting exam generation."})
    compiled_result, exam_questions = await run_exam_generation_pipeline(
        subject=subject, grade_level=grade_level, question_specs=question_specs, vsm=vsm, callback=callback
    )
    final_exam = FullExam(
        exam_id=exam_id,
        ingestion_summary=ingestion_summary,
        exam_title=exam_title,
        exam_paper_markdown=compiled_result['exam_paper'],
        answer_key_markdown=compiled_result['answer_key'],
        questions=exam_questions,
        sources_used=ingestion_summary.ingested_sources
    )
    ACTIVE_EXAMS[exam_id] = final_exam
    return final_exam

@router.post("/from-topic", summary="Generate Exam from Topic (Streaming)")
async def generate_exam_from_topic(request: ExamFromTopicRequest):
    if api_lock.locked():
        raise HTTPException(status_code=429, detail="A process is already running.")
    
    callback = StreamCallbackHandler()

    async def generation_task():
        async with api_lock:
            try:
                final_exam = await _orchestrate_exam_generation(
                    subject=request.subject,
                    grade_level=request.grade_level,
                    exam_title=request.exam_title,
                    question_specs=request.question_specs,
                    ingestion_coroutine_factory=_ingest_data_for_subject,
                    callback=callback
                )
                await callback.send_update("final_result", final_exam.model_dump())
            except Exception as e:
                logger.error(f"Error in /from-topic background task: {e}", exc_info=True)
                detail = str(e) if not isinstance(e, HTTPException) else e.detail
                await callback.send_update("error", {"detail": detail})
            finally:
                await callback.send_update("end_stream", {"message": "Stream ended."})

    asyncio.create_task(generation_task())
    return StreamingResponse(callback.stream_generator(), media_type="text/event-stream")

@router.post("/from-file", summary="Generate Exam from an Uploaded File (Streaming)")
async def generate_exam_from_file(
    exam_title: str = Form(..., description="The title for the generated exam paper.", examples=["Midterm Exam: English Comprehension"]),
    subject: str = Form(..., description="The general subject of the file, e.g., 'English Literature'.", examples=["English Literature"]),
    grade_level: str = Form(..., description="The target grade level for the exam.", examples=["High School Final Year"]),
    example_paper: UploadFile = File(..., description="The source PDF, DOCX, etc., file to be used as context."),
):
    if api_lock.locked():
        raise HTTPException(status_code=429, detail="A process is already running.")
    
    callback = StreamCallbackHandler()
    file_content_bytes = await example_paper.read()
    if not file_content_bytes:
        raise HTTPException(status_code=400, detail="The uploaded file appears to be empty.")

    async def file_generation_task():
        async with api_lock:
            try:
                # 1. Reset collections for a clean run
                await callback.send_update("log", {"message": f"Preparing environment for subject: '{subject}'."})
                vsm.reset_collections(subject)

                # 2. Process file and ingest into vector store
                await callback.send_update("progress", {"step": "file_processing", "status": f"Processing uploaded file: '{example_paper.filename}'..."})
                docs = await url_processor.process_local_file_content(
                    content_bytes=file_content_bytes,
                    filename=example_paper.filename,
                    content_type=example_paper.content_type
                )
                text_collection_name = vsm.get_collection_name(subject, "text")
                chunks_ingested = vsm.add_documents(text_collection_name, docs)
                await callback.send_update("log", {"message": f"Processed file into {chunks_ingested} chunks."})

                ingestion_summary = IngestionSummary(
                    message=f"Ingestion complete from local file '{example_paper.filename}'.",
                    processed_sources_count=1,
                    total_chunks_ingested=chunks_ingested,
                    collections_created=[text_collection_name] if chunks_ingested > 0 else [],
                    ingested_sources=vsm.get_collection_sources(text_collection_name)
                )

                if ingestion_summary.total_chunks_ingested == 0:
                    raise HTTPException(status_code=404, detail="Could not extract any content from the file. It might be corrupted or an unsupported format.")

                # 3. Generate question specifications from the ingested content
                await callback.send_update("progress", {"step": "spec_generation", "status": "AI is analyzing the file to create an exam structure..."})
                full_text = " ".join([doc.page_content for doc in docs])
                context_for_spec_gen = (full_text[:12000] + '...') if len(full_text) > 12000 else full_text
                
                spec_result = await spec_agent.chain.ainvoke({"context": context_for_spec_gen})
                question_specs_dicts = spec_result.get('question_specs', [])
                if not question_specs_dicts:
                    raise HTTPException(status_code=500, detail="AI agent failed to generate question specifications from the document content.")
                
                question_specs = [QuestionSpec.model_validate(s) for s in question_specs_dicts]
                await callback.send_update("log", {"message": f"AI generated exam structure: {len(question_specs)} section(s)."})

                # 4. Run the core exam generation pipeline
                exam_id = f"exam-{uuid.uuid4().hex}"
                compiled_result, exam_questions = await run_exam_generation_pipeline(
                    subject=subject, grade_level=grade_level, question_specs=question_specs, vsm=vsm, callback=callback
                )
                
                # 5. Assemble and send the final response object
                final_exam = FullExam(
                    exam_id=exam_id,
                    ingestion_summary=ingestion_summary,
                    exam_title=exam_title,
                    exam_paper_markdown=compiled_result['exam_paper'],
                    answer_key_markdown=compiled_result['answer_key'],
                    questions=exam_questions,
                    sources_used=ingestion_summary.ingested_sources
                )
                ACTIVE_EXAMS[exam_id] = final_exam
                await callback.send_update("final_result", final_exam.model_dump())

            except Exception as e:
                logger.error(f"Error in /from-file background task: {e}", exc_info=True)
                detail = str(e) if not isinstance(e, HTTPException) else e.detail
                await callback.send_update("error", {"detail": detail})
            finally:
                await callback.send_update("end_stream", {"message": "Stream ended."})

    asyncio.create_task(file_generation_task())
    return StreamingResponse(callback.stream_generator(), media_type="text/event-stream")
            
@router.post("/regenerate-question/{exam_id}/{question_id}", response_model=ExamQuestion, summary="Regenerate a Single Question")
async def regenerate_single_question(exam_id: str, question_id: str):
    if api_lock.locked():
        raise HTTPException(status_code=429, detail="A process is already running.")
    exam = ACTIVE_EXAMS.get(exam_id)
    if not exam: raise HTTPException(status_code=404, detail=f"Exam with ID '{exam_id}' not found.")
    original_question = next((q for q in exam.questions if q.id == question_id), None)
    if not original_question: raise HTTPException(status_code=404, detail=f"Question with ID '{question_id}' not found.")
    
    # This process is fast, so we create a dummy callback for compatibility
    class DummyCallback:
        async def send_update(self, *args, **kwargs): pass
    
    async with api_lock:
        try:
            spec = QuestionSpec(question_type=original_question.question_type, count=1, prompt="Generate a different version.")
            subject = exam.ingestion_summary.message.split("'")[1]
            grade_level = "N/A"
            # We don't have grade_level info here, so this might be suboptimal but will work
            _, new_exam_questions = await run_exam_generation_pipeline(
                subject, grade_level, [spec], vsm, callback=DummyCallback()
            )
            if not new_exam_questions: raise HTTPException(status_code=500, detail="Failed to regenerate.")
            new_question = new_exam_questions[0]
            for i, q in enumerate(exam.questions):
                if q.id == question_id: exam.questions[i] = new_question
            ACTIVE_EXAMS[exam_id] = exam
            return new_question
        except Exception as e:
            logger.error(f"Error during regeneration: {e}")
            raise HTTPException(status_code=500, detail=str(e))

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=1234)