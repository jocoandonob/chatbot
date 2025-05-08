import os
import tempfile
import logging
from typing import List
from flask import Flask, request, jsonify, render_template, redirect, url_for, g
from werkzeug.utils import secure_filename

from utils.document_processor import process_document, process_url, is_valid_url
from utils.vector_store import VectorStore
from utils.openai_utils import get_answer_from_chunks
from utils.request_limiter import RequestLimiter
from models import db, VisitorCount

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the database
db.init_app(app)

# Initialize vector store
vector_store = VectorStore()

# Create database tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    # Increment visitor count
    visitor_count = VisitorCount.increment()
    return render_template('index.html', visitor_count=visitor_count)

@app.route('/visitor-count')
def get_visitor_count():
    # Get current visitor count
    count = VisitorCount.get_count()
    return jsonify({"count": count})

@app.route('/upload', methods=['POST'])
def upload_file():
    logger.info("Received upload request")
    
    if 'file' not in request.files:
        return jsonify({"status": "error", "detail": "No file part"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"status": "error", "detail": "No selected file"}), 400
    
    # Check file type
    if file and (file.filename.endswith('.txt') or file.filename.endswith('.pdf')):
        # Create a temporary file to store the uploaded content
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            try:
                # Write the file content to the temp file
                file.save(temp_file.name)
                temp_file.flush()
                
                # Process the document and store embeddings
                chunks = process_document(temp_file.name, secure_filename(file.filename))
                vector_store.add_documents(chunks)
                
                # Generate sample questions based on the actual content
                # First, let's get a summary of the document to generate better questions
                from utils.openai_utils import get_answer_from_chunks
                
                # Create content-specific questions based on document content
                content_summary = get_answer_from_chunks(
                    "Briefly summarize the key topics and concepts in this document", 
                    chunks[:3]  # Using first few chunks to get the main topics
                )
                
                # Now generate relevant questions based on the content
                from utils.openai_utils import generate_content_specific_questions
                sample_questions = generate_content_specific_questions(content_summary)
                
                return jsonify({
                    "status": "success", 
                    "message": f"Successfully processed {file.filename}", 
                    "chunks_count": len(chunks),
                    "sample_questions": sample_questions
                })
            except Exception as e:
                logger.error(f"Error processing file: {str(e)}")
                return jsonify({"status": "error", "detail": f"Error processing file: {str(e)}"}), 500
            finally:
                # Remove the temporary file
                os.unlink(temp_file.name)
    else:
        return jsonify({"status": "error", "detail": "Only .txt and .pdf files are supported"}), 400

@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.get_json()
    
    if not data or 'question' not in data:
        return jsonify({"status": "error", "detail": "No question provided"}), 400
    
    # Check if user has reached their prompt limit
    can_ask, remaining_requests = RequestLimiter.can_make_request(request)
    if not can_ask:
        return jsonify({
            "status": "error", 
            "detail": "You have reached your limit of 5 questions. Please try again later.",
            "limit_reached": True
        }), 429  # Too Many Requests status code
    
    question = data['question']
    logger.info(f"Received question: {question}")
    
    if not vector_store.is_initialized():
        return jsonify({"status": "error", "detail": "Please upload a document first"}), 400
    
    try:
        # Retrieve relevant chunks
        relevant_chunks = vector_store.similarity_search(question, k=3)
        
        if not relevant_chunks:
            return jsonify({
                "answer": "I couldn't find any relevant information in the uploaded documents to answer your question.",
                "remaining_requests": remaining_requests
            })
        
        # Get answer from OpenAI
        answer = get_answer_from_chunks(question, relevant_chunks)
        
        # Return the answer and remaining requests
        return jsonify({
            "answer": answer,
            "remaining_requests": remaining_requests
        })
        
    except Exception as e:
        logger.error(f"Error answering question: {str(e)}")
        return jsonify({"status": "error", "detail": f"Error answering question: {str(e)}"}), 500

@app.route('/process-url', methods=['POST'])
def process_website_url():
    logger.info("Received URL processing request")
    
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({"status": "error", "detail": "No URL provided"}), 400
    
    url = data['url'].strip()
    
    # Validate URL
    if not is_valid_url(url):
        return jsonify({"status": "error", "detail": "Invalid URL format"}), 400
    
    try:
        # Process the URL and get chunks
        chunks = process_url(url)
        
        if not chunks:
            return jsonify({"status": "error", "detail": "Failed to extract content from the URL"}), 400
        
        # Add chunks to vector store
        vector_store.add_documents(chunks)
        
        # Generate sample questions based on the actual content
        content_summary = get_answer_from_chunks(
            "Briefly summarize the key topics and concepts in this document", 
            chunks[:3]  # Using first few chunks to get the main topics
        )
        
        # Generate relevant questions based on the content
        from utils.openai_utils import generate_content_specific_questions
        sample_questions = generate_content_specific_questions(content_summary)
        
        return jsonify({
            "status": "success", 
            "message": f"Successfully processed content from {url}", 
            "chunks_count": len(chunks),
            "sample_questions": sample_questions
        })
        
    except Exception as e:
        logger.error(f"Error processing URL: {str(e)}")
        return jsonify({"status": "error", "detail": f"Error processing URL: {str(e)}"}), 500

@app.route('/remaining-requests')
def remaining_requests():
    """Get the remaining requests for the current user"""
    remaining = RequestLimiter.get_remaining_requests(request)
    return jsonify({"remaining_requests": remaining})

@app.route('/health')
def health_check():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)