import datetime
import uuid
from uuid import uuid4
from typing import List, Dict, Any, Optional
from passlib.hash import bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ARRAY
import json

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.String(50), default=lambda: datetime.datetime.now().isoformat())
    
    systems = db.relationship('IFSSystem', backref='user', lazy=True)
    
    def __init__(self, username: str, email: str, password: str):
        self.id = str(uuid4())
        self.username = username
        self.email = email
        self.password_hash = bcrypt.hash(password)
        self.created_at = datetime.datetime.now().isoformat()
    
    def verify_password(self, password: str) -> bool:
        return bcrypt.verify(password, self.password_hash)
    
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at
        }

class Part(db.Model):
    __tablename__ = 'parts'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50))
    description = db.Column(db.Text)
    feelings = db.Column(db.Text, default='[]')  # JSON list stored as text
    beliefs = db.Column(db.Text, default='[]')   # JSON list stored as text
    triggers = db.Column(db.Text, default='[]')  # JSON list stored as text
    needs = db.Column(db.Text, default='[]')     # JSON list stored as text
    created_at = db.Column(db.String(50), default=lambda: datetime.datetime.now().isoformat())
    updated_at = db.Column(db.String(50), default=lambda: datetime.datetime.now().isoformat())
    system_id = db.Column(db.String(36), db.ForeignKey('systems.id'), nullable=False)
    
    def __init__(self, name: str, system_id: str, role: Optional[str] = None, description: str = "", feelings: List[str] = None):
        self.id = str(uuid4())
        self.name = name
        self.role = role
        self.description = description
        self.feelings = json.dumps(feelings or [])
        self.created_at = datetime.datetime.now().isoformat()
        self.updated_at = self.created_at
        self.beliefs = json.dumps([])
        self.triggers = json.dumps([])
        self.needs = json.dumps([])
        self.system_id = system_id
        
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "description": self.description,
            "feelings": json.loads(self.feelings),
            "beliefs": json.loads(self.beliefs),
            "triggers": json.loads(self.triggers),
            "needs": json.loads(self.needs),
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data, system_id):
        part = cls(
            name=data["name"], 
            system_id=system_id,
            role=data.get("role"), 
            description=data.get("description", "")
        )
        part.id = data["id"]
        part.feelings = json.dumps(data.get("feelings", []))
        part.beliefs = json.dumps(data.get("beliefs", []))
        part.triggers = json.dumps(data.get("triggers", []))
        part.needs = json.dumps(data.get("needs", []))
        part.created_at = data["created_at"]
        part.updated_at = data["updated_at"]
        return part

class Relationship(db.Model):
    __tablename__ = 'relationships'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    source_id = db.Column(db.String(36), db.ForeignKey('parts.id'), nullable=False)
    target_id = db.Column(db.String(36), db.ForeignKey('parts.id'), nullable=False)
    relationship_type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.String(50), default=lambda: datetime.datetime.now().isoformat())
    system_id = db.Column(db.String(36), db.ForeignKey('systems.id'), nullable=False)
    
    source = db.relationship('Part', foreign_keys=[source_id], backref=db.backref('source_relationships', lazy=True))
    target = db.relationship('Part', foreign_keys=[target_id], backref=db.backref('target_relationships', lazy=True))
    
    def __init__(self, source_id: str, target_id: str, relationship_type: str, system_id: str, description: str = ""):
        self.id = str(uuid4())
        self.source_id = source_id
        self.target_id = target_id
        self.relationship_type = relationship_type
        self.description = description
        self.created_at = datetime.datetime.now().isoformat()
        self.system_id = system_id
        
    def to_dict(self):
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relationship_type": self.relationship_type,
            "description": self.description,
            "created_at": self.created_at
        }

class Journal(db.Model):
    __tablename__ = 'journals'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    date = db.Column(db.String(50), default=lambda: datetime.datetime.now().isoformat())
    part_id = db.Column(db.String(36), db.ForeignKey('parts.id'))
    system_id = db.Column(db.String(36), db.ForeignKey('systems.id'), nullable=False)
    
    part = db.relationship('Part', backref=db.backref('journals', lazy=True))
    
    def __init__(self, title: str, system_id: str, content: str = "", part_id: Optional[str] = None):
        self.id = str(uuid4())
        self.title = title
        self.content = content
        self.date = datetime.datetime.now().isoformat()
        self.part_id = part_id
        self.system_id = system_id
        
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "date": self.date,
            "part_id": self.part_id
        }

class IFSSystem(db.Model):
    __tablename__ = 'systems'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.String(50), default=lambda: datetime.datetime.now().isoformat())
    abstraction_level = db.Column(db.String(50), default="mixed")
    
    parts = db.relationship('Part', backref='system', lazy=True, cascade='all, delete-orphan')
    relationships = db.relationship('Relationship', backref='system', lazy=True, cascade='all, delete-orphan')
    journals = db.relationship('Journal', backref='system', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, user_id: str):
        self.id = str(uuid4())
        self.user_id = user_id
        self.created_at = datetime.datetime.now().isoformat()
        self.abstraction_level = "mixed"
        
    def to_dict(self):
        parts_dict = {}
        for part in self.parts:
            parts_dict[part.id] = part.to_dict()
            
        relationships_dict = {}
        for rel in self.relationships:
            relationships_dict[rel.id] = rel.to_dict()
            
        journals_dict = {}
        for journal in self.journals:
            journals_dict[journal.id] = journal.to_dict()
            
        return {
            "id": self.id,
            "user_id": self.user_id,
            "parts": parts_dict,
            "relationships": relationships_dict,
            "journals": journals_dict,
            "created_at": self.created_at,
            "abstraction_level": self.abstraction_level
        } 