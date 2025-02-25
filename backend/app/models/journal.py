"""
Journal model for user reflections and notes.
"""
from uuid import uuid4
from typing import Dict, Any, Optional

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from . import db

class Journal(db.Model):
    """Model for journal entries in an IFS system."""
    __tablename__ = 'journals'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String(200), nullable=False)
    content = Column(Text)
    date = Column(DateTime, default=func.now())
    
    # Relationships
    part_id = Column(UUID(as_uuid=True), ForeignKey('parts.id'), nullable=True)
    system_id = Column(UUID(as_uuid=True), ForeignKey('systems.id'), nullable=False)
    
    # Relationship to part (optional)
    part = relationship('Part', back_populates='journals', lazy=True)
    
    def __init__(self, title: str, system_id: str, content: str = "", 
                 part_id: Optional[str] = None):
        """Initialize a journal entry.
        
        Args:
            title: Title of the journal entry.
            system_id: UUID of the system this journal belongs to.
            content: Content of the journal entry.
            part_id: Optional UUID of the part this journal is associated with.
        """
        self.title = title
        self.content = content
        self.part_id = part_id
        self.system_id = system_id
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert journal to dictionary representation.
        
        Returns:
            Dictionary representation of the journal.
        """
        return {
            "id": str(self.id),
            "title": self.title,
            "content": self.content,
            "date": self.date.isoformat() if self.date else None,
            "part_id": str(self.part_id) if self.part_id else None
        }
    
    def __repr__(self) -> str:
        return f"<Journal {self.title}>" 