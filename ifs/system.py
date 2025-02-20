import json
import networkx as nx
import matplotlib.pyplot as plt
from typing import Dict, Any, Optional
from .models import Part, Relationship, Journal
import datetime

class IFSSystem:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.parts = {}  # Dict[part_id, Part]
        self.relationships = {}  # Dict[relationship_id, Relationship]
        self.journals = {}  # Dict[journal_id, Journal]
        self.created_at = datetime.datetime.now().isoformat()
        self.abstraction_level = "mixed"  # "abstract", "concrete", "mixed"
        
        # Initialize with Self part
        self_part = Part(name="Self", role="Self", 
                        description="The compassionate core consciousness that can observe and interact with other parts")
        self.parts[self_part.id] = self_part
    
    def add_part(self, part: Part) -> str:
        """Add a new part to the system and return its ID"""
        self.parts[part.id] = part
        return part.id
    
    def update_part(self, part_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing part with new information"""
        if part_id not in self.parts:
            return False
        
        part = self.parts[part_id]
        for key, value in updates.items():
            if hasattr(part, key):
                setattr(part, key, value)
        
        part.updated_at = datetime.datetime.now().isoformat()
        return True
    
    def add_relationship(self, relationship: Relationship) -> str:
        """Add a new relationship between parts and return its ID"""
        if relationship.source_id not in self.parts or relationship.target_id not in self.parts:
            raise ValueError("Both source and target parts must exist in the system")
        
        self.relationships[relationship.id] = relationship
        return relationship.id
    
    def add_journal(self, journal: Journal) -> str:
        """Add a new journal entry and return its ID"""
        self.journals[journal.id] = journal
        return journal.id
    
    def get_part_by_name(self, name: str) -> Optional[Part]:
        """Find a part by name (case-insensitive)"""
        for part in self.parts.values():
            if part.name.lower() == name.lower():
                return part
        return None
    
    def to_dict(self):
        return {
            "user_id": self.user_id,
            "parts": {id: part.to_dict() for id, part in self.parts.items()},
            "relationships": {id: rel.to_dict() for id, rel in self.relationships.items()},
            "journals": {id: journal.to_dict() for id, journal in self.journals.items()},
            "created_at": self.created_at,
            "abstraction_level": self.abstraction_level
        }
    
    @classmethod
    def from_dict(cls, data):
        system = cls(user_id=data["user_id"])
        system.created_at = data["created_at"]
        system.abstraction_level = data.get("abstraction_level", "mixed")
        
        # Load parts
        system.parts = {}
        for part_id, part_data in data["parts"].items():
            system.parts[part_id] = Part.from_dict(part_data)
        
        # Load relationships
        system.relationships = {}
        for rel_id, rel_data in data["relationships"].items():
            system.relationships[rel_id] = Relationship.from_dict(rel_data)
        
        # Load journals
        system.journals = {}
        for journal_id, journal_data in data["journals"].items():
            system.journals[journal_id] = Journal.from_dict(journal_data)
        
        return system 