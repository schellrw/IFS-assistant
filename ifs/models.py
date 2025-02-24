import datetime
import uuid
from uuid import uuid4
from typing import List, Dict, Any, Optional
from passlib.hash import bcrypt

class Part:
    def __init__(self, name: str, role: Optional[str] = None, description: str = "", feelings: List[str] = None):
        self.id = str(uuid4())
        self.name = name
        self.role = role  # e.g., "Protector", "Exile", "Manager", "Firefighter", "Self"
        self.description = description
        self.feelings = feelings or []
        self.created_at = datetime.datetime.now().isoformat()
        self.updated_at = self.created_at
        self.beliefs = []
        self.triggers = []
        self.needs = []
        
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "description": self.description,
            "feelings": self.feelings,
            "beliefs": self.beliefs,
            "triggers": self.triggers,
            "needs": self.needs,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data):
        part = cls(name=data["name"], role=data.get("role"), description=data.get("description", ""))
        part.id = data["id"]
        part.feelings = data.get("feelings", [])
        part.beliefs = data.get("beliefs", [])
        part.triggers = data.get("triggers", [])
        part.needs = data.get("needs", [])
        part.created_at = data["created_at"]
        part.updated_at = data["updated_at"]
        return part

class Relationship:
    def __init__(self, source_id: str, target_id: str, relationship_type: str, description: str = ""):
        self.id = str(uuid4())
        self.source_id = source_id
        self.target_id = target_id
        self.relationship_type = relationship_type  # e.g., "protects", "triggered by", "blends with"
        self.description = description
        self.created_at = datetime.datetime.now().isoformat()
    
    def to_dict(self):
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relationship_type": self.relationship_type,
            "description": self.description,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        relationship = cls(
            source_id=data["source_id"],
            target_id=data["target_id"],
            relationship_type=data["relationship_type"],
            description=data.get("description", "")
        )
        relationship.id = data["id"]
        relationship.created_at = data["created_at"]
        return relationship

class Journal:
    def __init__(self, content: str, parts_present: List[str] = None, emotions: List[str] = None):
        self.id = str(uuid4())
        self.content = content
        self.parts_present = parts_present or []  # Part IDs
        self.emotions = emotions or []
        self.created_at = datetime.datetime.now().isoformat()
        self.insights = []
    
    def to_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "parts_present": self.parts_present,
            "emotions": self.emotions,
            "insights": self.insights,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        journal = cls(
            content=data["content"],
            parts_present=data.get("parts_present", []),
            emotions=data.get("emotions", [])
        )
        journal.id = data["id"]
        journal.insights = data.get("insights", [])
        journal.created_at = data["created_at"]
        return journal

class User:
    def __init__(self, username: str, email: str, password: str = None):
        self.id = str(uuid4())
        self.username = username
        self.email = email
        self.password_hash = bcrypt.hash(password) if password else None
        self.created_at = datetime.datetime.now().isoformat()
        self.updated_at = self.created_at
        
    def verify_password(self, password: str) -> bool:
        return bcrypt.verify(password, self.password_hash)
        
    def to_dict(self, include_private=False):
        result = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
        if include_private:
            result["password_hash"] = self.password_hash
        return result
    
    @classmethod
    def from_dict(cls, data):
        user = cls(username=data["username"], email=data["email"])
        user.id = data["id"]
        user.password_hash = data.get("password_hash")
        user.created_at = data["created_at"]
        user.updated_at = data["updated_at"]
        return user 