from backend.app import create_app
from backend.app.models.part import Part
from backend.app.models.conversation import PartConversation, ConversationMessage
import sys

app = create_app()

with app.app_context():
    try:
        # Check parts
        parts_count = Part.query.count()
        print(f"Parts in database: {parts_count}")
        
        if parts_count > 0:
            # Display first part
            first_part = Part.query.first()
            print(f"Sample part: {first_part.name} (ID: {first_part.id})")
            
            # Check conversations
            conversations_count = PartConversation.query.count()
            print(f"Conversations in database: {conversations_count}")
            
            if conversations_count > 0:
                # Display first conversation
                first_conv = PartConversation.query.first()
                print(f"Sample conversation: {first_conv.title} (ID: {first_conv.id})")
                
                # Check messages
                msg_count = ConversationMessage.query.count()
                print(f"Messages in database: {msg_count}")
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr) 