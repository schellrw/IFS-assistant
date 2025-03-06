"""
Check conversations in the database to verify our test.
"""
from backend.app import create_app
from backend.app.models import db
from backend.app.models.conversation import PartConversation, ConversationMessage
import sys

app = create_app()

with app.app_context():
    try:
        # Check conversations
        conversations = PartConversation.query.all()
        print(f"Total conversations in database: {len(conversations)}")
        
        for idx, conv in enumerate(conversations, 1):
            print(f"\n=== Conversation {idx}: {conv.title} ===")
            print(f"ID: {conv.id}")
            print(f"Part ID: {conv.part_id}")
            print(f"Created: {conv.created_at}")
            
            # Get messages
            messages = ConversationMessage.query.filter_by(conversation_id=conv.id).order_by(ConversationMessage.timestamp).all()
            print(f"Number of messages: {len(messages)}")
            
            if messages:
                print("\n--- Messages ---")
                for msg_idx, msg in enumerate(messages, 1):
                    print(f"{msg_idx}. {msg.role.upper()}: {msg.content[:150]}...")
                    print(f"   Timestamp: {msg.timestamp}")
                    if msg.embedding:
                        print(f"   Embedding: [Exists - {len(msg.embedding)} dimensions]")
                    else:
                        print("   Embedding: None")
                    print("")
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr) 