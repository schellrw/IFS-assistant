"""
Utilities for generating and managing text embeddings.
"""
import os
import logging
from typing import List, Dict, Any, Union, Optional
import json

# Conditionally import numpy, which may not be available during migrations
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("Warning: numpy not available, vector operations will be limited")

# Conditionally import sentence-transformers
try:
    from sentence_transformers import SentenceTransformer
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("Warning: sentence-transformers not available, embedding generation will be disabled")

# Configure logging
logger = logging.getLogger(__name__)

class EmbeddingManager:
    """Class for managing text embeddings using sentence-transformers models."""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """Initialize the embedding manager.
        
        Args:
            model_name: Name of the sentence-transformers model to use.
                Default is 'all-MiniLM-L6-v2'.
        """
        self.model_name = model_name
        self._model = None
        self.embedding_dim = 384  # Default for all-MiniLM-L6-v2
    
    @property
    def model(self) -> Any:
        """Lazy-loaded sentence transformer model.
        
        Returns:
            The sentence transformer model.
        """
        if not TRANSFORMERS_AVAILABLE:
            logger.error("sentence-transformers library is not available")
            return None
            
        if self._model is None:
            try:
                self._model = SentenceTransformer(self.model_name)
                logger.info(f"Loaded embedding model: {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                raise RuntimeError(f"Failed to load embedding model: {e}")
        return self._model
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate an embedding for a single text.
        
        Args:
            text: The text to generate an embedding for.
            
        Returns:
            The embedding as a list of floats.
        """
        if not TRANSFORMERS_AVAILABLE:
            logger.warning("Cannot generate embeddings: sentence-transformers not available")
            return [0.0] * self.embedding_dim  # Return zero vector
            
        try:
            embedding = self.model.encode(text)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise RuntimeError(f"Error generating embedding: {e}")
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to generate embeddings for.
            
        Returns:
            List of embeddings, each as a list of floats.
        """
        if not TRANSFORMERS_AVAILABLE:
            logger.warning("Cannot generate embeddings: sentence-transformers not available")
            return [[0.0] * self.embedding_dim for _ in texts]  # Return zero vectors
            
        try:
            embeddings = self.model.encode(texts)
            return [emb.tolist() for emb in embeddings]
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise RuntimeError(f"Error generating embeddings: {e}")
    
    def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Compute the cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding.
            embedding2: Second embedding.
            
        Returns:
            The cosine similarity between the embeddings.
        """
        if not NUMPY_AVAILABLE:
            logger.warning("Cannot compute similarity: numpy not available")
            return 0.0
            
        e1 = np.array(embedding1)
        e2 = np.array(embedding2)
        
        # Compute cosine similarity
        return float(np.dot(e1, e2) / (np.linalg.norm(e1) * np.linalg.norm(e2)))
    
    def get_part_embedding(self, part: Dict[str, Any]) -> List[float]:
        """Generate an embedding for a part based on its attributes.
        
        Args:
            part: Dictionary representation of a part.
            
        Returns:
            The embedding as a list of floats.
        """
        if not TRANSFORMERS_AVAILABLE:
            logger.warning("Cannot generate part embedding: sentence-transformers not available")
            return [0.0] * self.embedding_dim  # Return zero vector
            
        # Construct a descriptive text from the part's attributes
        text_elements = [
            f"Name: {part.get('name', '')}",
            f"Role: {part.get('role', '')}",
            f"Description: {part.get('description', '')}"
        ]
        
        # Add feelings, beliefs, etc. if available
        if part.get('feelings'):
            text_elements.append(f"Feelings: {', '.join(part.get('feelings', []))}")
        if part.get('beliefs'):
            text_elements.append(f"Beliefs: {', '.join(part.get('beliefs', []))}")
        if part.get('triggers'):
            text_elements.append(f"Triggers: {', '.join(part.get('triggers', []))}")
        if part.get('needs'):
            text_elements.append(f"Needs: {', '.join(part.get('needs', []))}")
        
        # Combine into a single text
        part_text = " ".join(text_elements)
        
        # Generate and return the embedding
        return self.generate_embedding(part_text)


# Create a singleton instance
embedding_manager = EmbeddingManager() 