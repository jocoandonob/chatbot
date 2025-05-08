import logging
import numpy as np
from typing import List, Optional
import faiss
from langchain.schema import Document
from .openai_utils import get_embeddings

logger = logging.getLogger(__name__)

class VectorStore:
    """In-memory vector store using FAISS."""
    
    def __init__(self):
        self.documents = []
        self.index = None
        self.dimension = 1536  # OpenAI ada-002 embedding dimension
    
    def is_initialized(self) -> bool:
        """Check if the vector store is initialized with documents."""
        return self.index is not None and len(self.documents) > 0
    
    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to the vector store."""
        logger.info(f"Adding {len(documents)} documents to vector store")
        
        if not documents:
            logger.warning("No documents to add")
            return
        
        # Store the documents
        self.documents.extend(documents)
        
        # Create embeddings for the documents
        embeddings = []
        for doc in documents:
            embedding = get_embeddings(doc.page_content)
            embeddings.append(embedding)
        
        # Convert to numpy array
        embeddings_np = np.array(embeddings, dtype=np.float32)
        
        # Create or update the index
        if self.index is None:
            # Create a new index
            self.index = faiss.IndexFlatL2(self.dimension)
            self.index.add(embeddings_np)
        else:
            # Add to existing index
            self.index.add(embeddings_np)
        
        logger.info(f"Vector store now contains {len(self.documents)} documents")
    
    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """Search for similar documents based on the query."""
        logger.info(f"Performing similarity search for query: {query}")
        
        if not self.is_initialized():
            logger.warning("Vector store is not initialized")
            return []
        
        # Get embedding for the query
        query_embedding = get_embeddings(query)
        query_embedding_np = np.array([query_embedding], dtype=np.float32)
        
        # Search the index
        distances, indices = self.index.search(query_embedding_np, k=min(k, len(self.documents)))
        
        # Get the documents for the indices
        results = [self.documents[idx] for idx in indices[0]]
        
        logger.info(f"Found {len(results)} relevant documents")
        return results
