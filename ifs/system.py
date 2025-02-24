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
        try:
            if relationship.source_id not in self.parts:
                raise ValueError(f"Source part {relationship.source_id} not found")
            if relationship.target_id not in self.parts:
                raise ValueError(f"Target part {relationship.target_id} not found")
            
            # Check if relationship already exists
            for existing_rel in self.relationships.values():
                if (existing_rel.source_id == relationship.source_id and 
                    existing_rel.target_id == relationship.target_id and
                    existing_rel.relationship_type == relationship.relationship_type):
                    raise ValueError("Similar relationship already exists")
            
            self.relationships[relationship.id] = relationship
            return relationship.id
        except Exception as e:
            print(f"Error in add_relationship: {str(e)}")
            raise
    
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

# This file now serves as a utility file for system operations
# The IFSSystem model is defined in models.py

def generate_system_graph(system):
    """Generate a NetworkX graph from the system data"""
    G = nx.DiGraph()
    
    # Add nodes (parts)
    for part in system.parts:
        G.add_node(part.id, label=part.name, role=part.role or "Unknown")
    
    # Add edges (relationships)
    for rel in system.relationships:
        G.add_edge(
            rel.source_id, 
            rel.target_id, 
            type=rel.relationship_type,
            description=rel.description
        )
    
    return G

def plot_system_graph(system, filename=None):
    """Plot the system graph and save it to a file if specified"""
    G = generate_system_graph(system)
    
    # Get node positions using spring layout
    pos = nx.spring_layout(G, seed=42)
    
    # Create figure and axis
    plt.figure(figsize=(12, 10))
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_size=700, node_color='lightblue')
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, arrowsize=15, width=1.5)
    
    # Draw node labels
    node_labels = {node: G.nodes[node]['label'] for node in G.nodes}
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=10)
    
    # Draw edge labels
    edge_labels = {(u, v): G.edges[u, v]['type'] for u, v in G.edges}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
    
    # Set title and remove axis
    plt.title("Internal Family System")
    plt.axis('off')
    
    # Save or show
    if filename:
        plt.savefig(filename)
        plt.close()
        return filename
    else:
        plt.tight_layout()
        plt.show()
        
def export_system_json(system):
    """Export the system to a JSON file"""
    return json.dumps(system.to_dict(), indent=2)

def import_system_json(json_data, user_id):
    """Import a system from JSON data"""
    from .models import db, IFSSystem, Part, Relationship, Journal
    
    data = json.loads(json_data)
    
    # Create new system
    system = IFSSystem(user_id=user_id)
    db.session.add(system)
    db.session.flush()  # Get the system ID
    
    # Add parts
    parts_map = {}  # Map old IDs to new parts
    for part_id, part_data in data.get('parts', {}).items():
        part = Part(
            name=part_data['name'],
            system_id=system.id,
            role=part_data.get('role'),
            description=part_data.get('description', '')
        )
        part.feelings = json.dumps(part_data.get('feelings', []))
        part.beliefs = json.dumps(part_data.get('beliefs', []))
        part.triggers = json.dumps(part_data.get('triggers', []))
        part.needs = json.dumps(part_data.get('needs', []))
        part.created_at = part_data.get('created_at', datetime.datetime.now().isoformat())
        part.updated_at = part_data.get('updated_at', datetime.datetime.now().isoformat())
        
        db.session.add(part)
        parts_map[part_id] = part
    
    db.session.flush()  # Get part IDs
    
    # Add relationships
    for rel_id, rel_data in data.get('relationships', {}).items():
        source_id = parts_map[rel_data['source_id']].id
        target_id = parts_map[rel_data['target_id']].id
        
        relationship = Relationship(
            source_id=source_id,
            target_id=target_id,
            relationship_type=rel_data['relationship_type'],
            description=rel_data.get('description', ''),
            system_id=system.id
        )
        relationship.created_at = rel_data.get('created_at', datetime.datetime.now().isoformat())
        
        db.session.add(relationship)
    
    # Add journals
    for journal_id, journal_data in data.get('journals', {}).items():
        # Find the new part ID if part_id is present
        part_id = None
        if journal_data.get('part_id') and journal_data['part_id'] in parts_map:
            part_id = parts_map[journal_data['part_id']].id
            
        journal = Journal(
            title=journal_data.get('title', 'Imported Journal'),
            content=journal_data.get('content', ''),
            part_id=part_id,
            system_id=system.id
        )
        journal.date = journal_data.get('date', datetime.datetime.now().isoformat())
        
        db.session.add(journal)
    
    db.session.commit()
    return system 