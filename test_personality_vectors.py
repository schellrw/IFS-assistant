"""
Test script for generating personality vectors for parts.
This script will:
1. Get a part from the database
2. Generate personality vectors for the part
3. Verify the vectors are stored correctly
"""
from backend.app import create_app
from backend.app.models import db
from backend.app.models.part import Part
from backend.app.models.conversation import PartPersonalityVector
from backend.app.utils.embeddings import embedding_manager
import sys
from datetime import datetime

# Create Flask app context
app = create_app()

def test_personality_vectors():
    """Generate and test personality vectors for a part."""
    with app.app_context():
        try:
            # Get a part to generate vectors for
            part = Part.query.first()
            if not part:
                print("No parts found in the database. Cannot test personality vectors.")
                return
            
            print(f"Using part: {part.name} (ID: {part.id})")
            print(f"Role: {part.role}")
            print(f"Description: {part.description[:100]}..." if part.description else "No description")
            
            # Check if part already has personality vectors
            existing_vector = PartPersonalityVector.query.filter_by(
                part_id=part.id, aspect="personality").first()
            
            if existing_vector:
                print(f"Part already has personality vectors with {len(existing_vector.embedding)} dimensions.")
                print(f"Last updated: {existing_vector.updated_at}")
                
                # Option to regenerate
                existing_vector.embedding = embedding_manager.get_part_embedding(part.to_dict())
                existing_vector.updated_at = datetime.now()
                db.session.commit()
                print("Personality vectors updated.")
            else:
                # Generate personality vectors
                print("Generating new personality vectors...")
                personality_embedding = embedding_manager.get_part_embedding(part.to_dict())
                
                # Create new personality vector
                new_vector = PartPersonalityVector(
                    part_id=part.id,
                    aspect="personality",
                    embedding=personality_embedding,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                
                db.session.add(new_vector)
                db.session.commit()
                print(f"New personality vectors created with {len(personality_embedding)} dimensions.")
            
            # Verify vectors in database
            all_vectors = PartPersonalityVector.query.filter_by(part_id=part.id).all()
            print(f"\nTotal vectors for part {part.name}: {len(all_vectors)}")
            
            for i, vector in enumerate(all_vectors, 1):
                print(f"Vector {i}: Aspect: {vector.aspect}, Dimensions: {len(vector.embedding)}")
                # Print first few values of embedding to verify content
                print(f"Sample values: {vector.embedding[:5]}...")
            
            return True
                
        except Exception as e:
            print(f"Error in personality vector test: {e}", file=sys.stderr)
            db.session.rollback()
            return False

if __name__ == "__main__":
    print("Testing personality vectors generation...")
    success = test_personality_vectors()
    if success:
        print("\nPersonality vectors test completed successfully!")
    else:
        print("\nPersonality vectors test failed.") 