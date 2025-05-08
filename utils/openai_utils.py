import os
import logging
from typing import List, Dict, Any
from langchain.schema import Document
from openai import OpenAI

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
MODEL = "gpt-4o"

logger = logging.getLogger(__name__)

# Get API key from environment variable
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
if not OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY not found in environment variables. API calls will fail.")

client = OpenAI(api_key=OPENAI_API_KEY)

def get_embeddings(text: str) -> List[float]:
    """Get embeddings for the provided text."""
    try:
        response = client.embeddings.create(
            input=text,
            model="text-embedding-ada-002",
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Error getting embeddings: {str(e)}")
        raise e

def get_answer_from_chunks(question: str, chunks: List[Document]) -> str:
    """Generate an answer for the question based on the document chunks."""
    try:
        # Combine the chunks
        context = "\n\n".join([chunk.page_content for chunk in chunks])
        
        # Create the prompt
        prompt = f"""Answer the following question based on the provided context only. 
        If you don't know the answer or the answer is not in the context, just say so.
        
        Context:
        {context}
        
        Question: {question}
        
        Answer:"""
        
        # Call OpenAI to generate response
        logger.info(f"Sending prompt to OpenAI: {prompt[:100]}...")
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that provides answers based solely on the provided context."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Lower temperature for more factual responses
            max_tokens=500
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        logger.error(f"Error generating answer: {str(e)}")
        raise e


def generate_content_specific_questions(document_summary: str, num_questions: int = 3) -> List[str]:
    """Generate content-specific questions based on the document summary."""
    try:
        prompt = f"""Based on the following document summary, generate {num_questions} specific, 
        insightful questions that could be asked about this content. Make the questions 
        specific to the unique concepts, ideas, or information in this document:
        
        Document Summary:
        {document_summary}
        
        Create questions that would demonstrate understanding of the key concepts in this specific document.
        Return exactly {num_questions} questions, separated by newlines. 
        Don't prefix with numbers or bullet points."""
        
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates insightful questions based on document content."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,  # Higher temperature for more creative questions
            max_tokens=300
        )
        
        # Parse the response into a list of questions
        questions_text = response.choices[0].message.content.strip()
        questions = [q.strip() for q in questions_text.split('\n') if q.strip()]
        
        # Ensure we have the requested number of questions
        while len(questions) < num_questions:
            questions.append(f"What else can you tell me about this document?")
            
        return questions[:num_questions]  # Limit to exactly num_questions
    
    except Exception as e:
        logger.error(f"Error generating content-specific questions: {str(e)}")
        # Fallback to generic but content-focused questions
        return [
            "What are the main ideas presented in this document?",
            "Can you explain the key concepts mentioned in this document?",
            "What conclusions or insights can be drawn from this document?"
        ]
