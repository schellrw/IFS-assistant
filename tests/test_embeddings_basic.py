"""
Simplified test script for embedding functionality without pgvector.
This script will:
1. Generate embeddings for sample text
2. Compare embeddings using cosine similarity
3. Retrieve messages and calculate similarity manually
"""
import numpy as np
from backend.app import create_app
from backend.app.models import db
from backend.app.models.part import Part
from backend.app.models.conversation import ConversationMessage, PartPersonalityVector
from backend.app.utils.embeddings import embedding_manager
import sys
from typing import List, Dict, Any, Tuple

# Create Flask app context
app = create_app()

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    if not vec1 or not vec2:
        return 0.0
        
    # Convert to numpy arrays for efficient calculation
    a = np.array(vec1)
    b = np.array(vec2)
    
    # Calculate similarity
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def manual_similarity_search(query_text: str, messages: List[ConversationMessage], limit: int = 3) -> List[Tuple[ConversationMessage, float]]:
    """Manually calculate similarity between query and messages."""
    # Generate embedding for query
    query_embedding = embedding_manager.generate_embedding(query_text)
    
    # Calculate similarity for each message
    similarities = []
    for message in messages:
        if message.embedding:
            similarity = cosine_similarity(query_embedding, message.embedding)
            similarities.append((message, similarity))
    
    # Sort by similarity (highest first)
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    # Return top results
    return similarities[:limit]

def test_basic_embeddings():
    """Test basic embedding functionality without pgvector."""
    with app.app_context():
        try:
            print("Testing basic embedding functionality...")
            
            # 1. Basic embedding generation test
            sample_texts = [
                "Hello, how are you today?",
                "What's your role in the system?",
                "I'm feeling anxious about this situation.",
                "Tell me more about your beliefs."
            ]
            
            print("\n1. Basic Embedding Generation:")
            for i, text in enumerate(sample_texts, 1):
                embedding = embedding_manager.generate_embedding(text)
                print(f"Text {i}: Generated embedding with {len(embedding)} dimensions")
            
            # 2. Embedding similarity test
            print("\n2. Embedding Similarity Test:")
            embedding1 = embedding_manager.generate_embedding("I feel anxious and worried")
            embedding2 = embedding_manager.generate_embedding("I'm experiencing anxiety")
            embedding3 = embedding_manager.generate_embedding("Tell me about your purpose")
            
            sim1_2 = cosine_similarity(embedding1, embedding2)
            sim1_3 = cosine_similarity(embedding1, embedding3)
            sim2_3 = cosine_similarity(embedding2, embedding3)
            
            print(f"Similarity between 'anxious' texts: {sim1_2:.4f}")
            print(f"Similarity between 'anxious' and 'purpose': {sim1_3:.4f}")
            print(f"Similarity between 'anxiety' and 'purpose': {sim2_3:.4f}")
            
            # 3. Retrieve message embeddings from database
            messages = ConversationMessage.query.all()
            messages_with_embeddings = [m for m in messages if m.embedding is not None]
            
            if messages_with_embeddings:
                print(f"\n3. Database Messages with Embeddings: {len(messages_with_embeddings)}")
                
                # Test search with a few queries
                test_queries = [
                    "Tell me about yourself",
                    "What's your role in the system?",
                    "How do you feel about that?"
                ]
                
                for query in test_queries:
                    print(f"\nSearch Query: '{query}'")
                    results = manual_similarity_search(query, messages_with_embeddings)
                    
                    for i, (message, similarity) in enumerate(results, 1):
                        print(f"{i}. {message.role.upper()}: {message.content[:100]}...")
                        print(f"   Similarity: {similarity:.4f}")
            else:
                print("\n3. No messages with embeddings found in database")
            
            # 4. Check personality vectors
            personality_vectors = PartPersonalityVector.query.all()
            if personality_vectors:
                print(f"\n4. Personality Vectors: {len(personality_vectors)}")
                for i, vector in enumerate(personality_vectors, 1):
                    part = Part.query.get(vector.part_id)
                    print(f"Vector {i}: Part: {part.name}, Aspect: {vector.aspect}, Dimensions: {len(vector.embedding)}")
            else:
                print("\n4. No personality vectors found in database")
            
            return True
                
        except Exception as e:
            print(f"Error in basic embedding test: {e}", file=sys.stderr)
            return False

if __name__ == "__main__":
    success = test_basic_embeddings()
    if success:
        print("\nBasic embedding test completed successfully!")
    else:
        print("\nBasic embedding test failed.") 