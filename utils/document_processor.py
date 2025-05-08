import os
import logging
import tempfile
import re
from typing import List, Optional
import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from utils.web_scraper import get_website_text_content

logger = logging.getLogger(__name__)

def read_pdf_file(file_path: str) -> str:
    """Extract text from a PDF file."""
    logger.info(f"Reading PDF file: {file_path}")
    text = ""
    try:
        with open(file_path, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        logger.error(f"Error reading PDF file: {str(e)}")
        raise e
    return text

def read_text_file(file_path: str) -> str:
    """Read a text file."""
    logger.info(f"Reading text file: {file_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        # Try different encoding if utf-8 fails
        with open(file_path, "r", encoding="latin-1") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading text file: {str(e)}")
        raise e

def chunk_text(text: str, filename: str) -> List[Document]:
    """Split text into manageable chunks."""
    logger.info(f"Chunking text from {filename}")
    
    # Create text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    
    # Split text into chunks
    chunks = text_splitter.create_documents([text], metadatas=[{"source": filename}])
    logger.info(f"Created {len(chunks)} chunks from {filename}")
    
    return chunks

def is_valid_url(url: str) -> bool:
    """Check if a string is a valid URL."""
    # Simple URL validation regex
    url_pattern = re.compile(
        r'^(https?://)?' # http:// or https:// (optional)
        r'((([a-z\d]([a-z\d-]*[a-z\d])*)\.)+[a-z]{2,}|' # domain...
        r'((\d{1,3}\.){3}\d{1,3})|' # ...or ipv4
        r'localhost)' # or localhost
        r'(:\d+)?' # optional port
        r'(/[-a-z\d%_.~+]*)*' # path
        r'(\?[;&a-z\d%_.~+=-]*)?' # query string
        r'(\#[-a-z\d_]*)?$', # fragment locator
        re.IGNORECASE
    )
    return bool(url_pattern.match(url))

def process_url(url: str) -> Optional[List[Document]]:
    """Process a website URL into document chunks."""
    logger.info(f"Processing URL: {url}")
    
    try:
        # Ensure URL starts with http:// or https://
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Get text content from the URL
        text = get_website_text_content(url)
        
        if text is None or not text.strip():
            logger.error(f"Failed to extract content from URL: {url}")
            return None
        
        # Create chunks from the text
        chunks = chunk_text(text, url)
        return chunks
    
    except Exception as e:
        logger.error(f"Error processing URL: {str(e)}")
        return None

def process_document(file_path: str, original_filename: str) -> List[Document]:
    """Process a document file (PDF or TXT) into chunks."""
    logger.info(f"Processing document: {original_filename}")
    
    try:
        # Read the file based on extension
        if original_filename.endswith('.pdf'):
            text = read_pdf_file(file_path)
        elif original_filename.endswith('.txt'):
            text = read_text_file(file_path)
        else:
            raise ValueError(f"Unsupported file type: {original_filename}")
        
        # Create chunks from the text
        chunks = chunk_text(text, original_filename)
        return chunks
    
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise e
