import os
import tempfile
import logging
from typing import List
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.requests import Request

from utils.document_processor import process_document
from utils.vector_store import VectorStore
from utils.openai_utils import get_answer_from_chunks

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Document Q&A Chatbot")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure the app is correctly exposed for Gunicorn WSGI
from starlette.middleware.wsgi import WSGIMiddleware

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Initialize vector store
vector_store = VectorStore()

# Pydantic models
class QuestionRequest(BaseModel):
    question: str

class AnswerResponse(BaseModel):
    answer: str
    source_chunks: List[str]

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    logger.info(f"Received file: {file.filename}")
    
    # Check file type
    if file.filename.endswith(('.txt', '.pdf')):
        # Create a temporary file to store the uploaded content
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            try:
                # Write the file content to the temp file
                content = await file.read()
                temp_file.write(content)
                temp_file.flush()
                
                # Process the document and store embeddings
                chunks = process_document(temp_file.name, file.filename)
                vector_store.add_documents(chunks)
                
                # Generate sample questions based on content
                sample_questions = [
                    "What is the main topic of this document?",
                    "Can you summarize this document?",
                    "What are the key points from this document?"
                ]
                
                return {
                    "status": "success", 
                    "message": f"Successfully processed {file.filename}", 
                    "chunks_count": len(chunks),
                    "sample_questions": sample_questions
                }
            except Exception as e:
                logger.error(f"Error processing file: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
            finally:
                # Remove the temporary file
                os.unlink(temp_file.name)
    else:
        raise HTTPException(status_code=400, detail="Only .txt and .pdf files are supported")

@app.post("/ask", response_model=AnswerResponse)
async def ask_question(question_request: QuestionRequest):
    logger.info(f"Received question: {question_request.question}")
    
    if not vector_store.is_initialized():
        raise HTTPException(status_code=400, detail="Please upload a document first")
    
    try:
        # Retrieve relevant chunks
        relevant_chunks = vector_store.similarity_search(question_request.question, k=3)
        
        if not relevant_chunks:
            return AnswerResponse(
                answer="I couldn't find any relevant information in the uploaded documents to answer your question.",
                source_chunks=[]
            )
        
        # Get answer from OpenAI
        answer = get_answer_from_chunks(question_request.question, relevant_chunks)
        
        # Format source chunks for display
        formatted_chunks = [chunk.page_content[:200] + "..." for chunk in relevant_chunks]
        
        return AnswerResponse(answer=answer, source_chunks=formatted_chunks)
        
    except Exception as e:
        logger.error(f"Error answering question: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error answering question: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "ok"}
