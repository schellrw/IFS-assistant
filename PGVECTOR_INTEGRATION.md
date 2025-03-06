# pgvector Integration Documentation

This document explains how pgvector is integrated with the IFS Assistant application for efficient vector similarity search.

## Overview

The IFS Assistant uses pgvector, a PostgreSQL extension that enables efficient vector operations and similarity searches. This is essential for:

- Semantic search of conversation messages
- Finding similar parts based on personality vectors
- Implementing memory and context-aware AI interactions

## Database Schema

The application uses two main tables with vector columns:

1. **conversation_messages**
   - `embedding`: Vector(384) - Stores embeddings of message content
   - Used for semantic search across conversation history

2. **part_personality_vectors**
   - `embedding`: Vector(384) - Stores embeddings of part personality aspects
   - Used for finding parts with similar characteristics or responses

## Vector Generation

Embeddings are generated using the SentenceTransformer model 'all-MiniLM-L6-v2', which produces vectors with 384 dimensions.

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
embedding = model.encode("Your text here")  # Returns a vector with 384 dimensions
```

The EmbeddingManager class in `backend/app/utils/embeddings.py` handles this functionality.

## Vector Storage and Retrieval

### Storing Vectors

When storing vectors in the database, convert NumPy arrays to lists:

```python
# Example: Storing an embedding in a ConversationMessage
message = ConversationMessage(
    role="user",
    content="Hello, how are you?",
    conversation_id=conversation_id,
    embedding=embedding.tolist()  # Convert numpy array to list for storage
)
db.session.add(message)
db.session.commit()
```

### Vector Similarity Search

For similarity search, use the vector operators provided by pgvector:

- `<->`: Euclidean distance (smaller = more similar)
- `<=>`: Cosine distance (smaller = more similar)
- `<#>`: Inner product (larger = more similar)

Example query using SQLAlchemy:

```python
from sqlalchemy import text

# Example: Finding similar messages
query_embedding = embedding_manager.generate_embedding("How are you feeling today?")

sql = text("""
    SELECT id, content, role, 
           embedding <-> :query_embedding AS distance
    FROM conversation_messages
    WHERE embedding IS NOT NULL
    ORDER BY embedding <-> :query_embedding
    LIMIT :limit
""")

result = db.session.execute(
    sql, 
    {"query_embedding": query_embedding, "limit": 5}
)
```

## Vector Indexes

The application uses vector indexes to accelerate similarity searches:

```sql
CREATE INDEX idx_conversation_messages_embedding 
ON conversation_messages USING ivfflat (embedding vector_l2_ops);

CREATE INDEX idx_part_personality_vectors_embedding 
ON part_personality_vectors USING ivfflat (embedding vector_l2_ops);
```

These indexes use the IVFFLAT algorithm which speeds up approximate nearest neighbor searches.

## Tips for Working with Vectors

1. **Dimensionality Matters**: Always ensure vectors have 384 dimensions to match the model.

2. **Vector Normalization**: For cosine similarity, normalize vectors before storing:
   ```python
   from numpy.linalg import norm
   normalized_vector = embedding / norm(embedding)
   ```

3. **Batch Processing**: When generating multiple embeddings, use batch processing:
   ```python
   texts = ["Text 1", "Text 2", "Text 3"]
   embeddings = model.encode(texts)  # More efficient than encoding individually
   ```

4. **Error Handling**: Handle potential dimension mismatches when copying data:
   ```sql
   -- Safe conversion with explicit dimensions
   UPDATE table SET new_column = old_column::vector(384)
   ```

## Maintenance

Regularly monitor vector indexes, especially as the database grows:

1. **Reindex if necessary**:
   ```sql
   REINDEX INDEX idx_conversation_messages_embedding;
   ```

2. **Check index usage**:
   ```sql
   SELECT indexrelname, idx_scan, idx_tup_read, idx_tup_fetch
   FROM pg_stat_user_indexes
   WHERE indexrelname LIKE '%embedding%';
   ```

3. **Vacuum analyze after bulk operations**:
   ```sql
   VACUUM ANALYZE conversation_messages;
   VACUUM ANALYZE part_personality_vectors;
   ```

## Troubleshooting

1. **"Column does not have dimensions"**: Ensure the vector columns are created with explicit dimensions:
   ```sql
   ALTER TABLE table_name ADD COLUMN embedding vector(384);
   ```

2. **Performance issues**: Check if indexes are being used:
   ```sql
   EXPLAIN ANALYZE SELECT * FROM conversation_messages 
   ORDER BY embedding <-> '[...]'::vector(384) LIMIT 5;
   ```

3. **Data type errors**: Ensure vectors are properly cast when comparing:
   ```sql
   -- Explicitly cast the query vector
   ORDER BY embedding <-> :query_embedding::vector(384)
   ``` 