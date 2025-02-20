import json
import datetime
import networkx as nx
import matplotlib.pyplot as plt
from uuid import uuid4
from typing import List, Dict, Any, Optional

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
    
    def visualize_system(self, filename="ifs_system_graph.png"):
        """Generate a visualization of the internal system as a network graph"""
        G = nx.DiGraph()
        
        # Add nodes for parts
        for part_id, part in self.parts.items():
            G.add_node(part_id, label=part.name, role=part.role or "Undefined")
        
        # Add edges for relationships
        for rel_id, rel in self.relationships.items():
            G.add_edge(rel.source_id, rel.target_id, 
                       label=rel.relationship_type, 
                       description=rel.description)
        
        # Generate positions using layout algorithm
        pos = nx.spring_layout(G)
        
        # Create figure
        plt.figure(figsize=(12, 10))
        
        # Draw nodes with different colors based on role
        role_colors = {
            "Self": "green",
            "Protector": "blue",
            "Manager": "purple",
            "Firefighter": "red",
            "Exile": "orange",
            "Undefined": "gray"
        }
        
        for role in role_colors:
            role_nodes = [n for n, attrs in G.nodes(data=True) if attrs.get('role') == role]
            nx.draw_networkx_nodes(G, pos, nodelist=role_nodes, 
                                 node_color=role_colors[role], 
                                 node_size=700,
                                 alpha=0.8)
        
        # Draw edges
        nx.draw_networkx_edges(G, pos, width=1.5, alpha=0.7, arrows=True)
        
        # Draw labels
        nx.draw_networkx_labels(G, pos, labels={n: G.nodes[n]['label'] for n in G.nodes()})
        
        # Add edge labels
        edge_labels = {(u, v): G.edges[u, v]['label'] for u, v in G.edges()}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
        
        # Add legend
        legend_elements = [plt.Line2D([0], [0], marker='o', color='w', 
                                    markerfacecolor=color, markersize=10, label=role)
                         for role, color in role_colors.items()]
        plt.legend(handles=legend_elements, loc='upper right')
        
        plt.title("IFS Internal System Map")
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(filename)
        plt.close()
        
        return filename


class IFSAssistant:
    """Main interface for interacting with the IFS system"""
    
    def __init__(self, system: IFSSystem = None, user_id: str = None):
        if system:
            self.system = system
        elif user_id:
            self.system = IFSSystem(user_id=user_id)
        else:
            raise ValueError("Either system or user_id must be provided")
            
        # Simple IFS knowledge base for guidance
        self.ifs_concepts = {
            "Self": "The compassionate core consciousness that can observe and interact with all parts.",
            "Exile": "Young parts that carry pain, trauma, or fear and are often protected by other parts.",
            "Manager": "Proactive protector parts that try to keep the system functioning and prevent exile pain.",
            "Firefighter": "Reactive protector parts that activate when exiles are triggered, often using extreme behaviors.",
            "Protector": "Parts that shield exiles from being overwhelmed by difficult emotions.",
            "Blending": "When a part's feelings and beliefs become so strong that they take over your perspective.",
            "Unburdening": "The process of releasing the extreme beliefs and emotions carried by parts.",
            "Self-leadership": "When the Self is in charge of the system rather than parts."
        }
        
    def save_to_file(self, filename: str):
        """Save the current system state to a JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.system.to_dict(), f, indent=2)
            
    @classmethod
    def load_from_file(cls, filename: str):
        """Load a system from a JSON file"""
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            system = IFSSystem.from_dict(data)
            return cls(system=system)
    
    def create_part_dialog(self, abstract_concrete_spectrum: float = 0.5):
        """
        Interactive dialog to create a new part, with customized prompts based on where the 
        user falls on the abstract-concrete spectrum (0 = very abstract, 1 = very concrete)
        
        Note: This would be replaced with a GUI dialog in a real application
        """
        if abstract_concrete_spectrum < 0.3:
            # More abstract approach
            name = input("What would you call this aspect of yourself? ")
            description = input("How would you describe what this aspect represents? ")
            role = input("If you had to categorize this aspect (Manager, Firefighter, Exile, etc), what might fit? ")
            
        elif abstract_concrete_spectrum > 0.7:
            # More concrete approach
            name = input("What is this part's name? ")
            description = input("What does this part look like? How does it feel in your body? ")
            print("\nIFS roles:")
            print("- Manager: Proactive protector that keeps system functioning")
            print("- Firefighter: Reactive protector that activates when triggered")
            print("- Exile: Carries pain, trauma, or vulnerability")
            print("- Self: Your core compassionate consciousness")
            role = input("Which role does this part have? ")
            
        else:
            # Balanced approach
            name = input("What would you like to call this part? ")
            description = input("Tell me about this part - what it feels like, what it cares about: ")
            role = input("What role might this part have (Manager, Firefighter, Exile, Self, other)? ")
        
        feelings = input("What emotions does this part carry? (comma-separated) ").split(",")
        feelings = [f.strip() for f in feelings if f.strip()]
        
        # Create the part
        part = Part(name=name, role=role, description=description, feelings=feelings)
        self.system.add_part(part)
        
        return part.id
    
    def suggest_reflective_prompts(self, part_id: str = None):
        """Generate reflective prompts based on the current system state"""
        prompts = []
        
        if part_id and part_id in self.system.parts:
            part = self.system.parts[part_id]
            prompts.extend([
                f"What does {part.name} need from you right now?",
                f"What is {part.name} trying to protect you from?",
                f"How does it feel in your body when {part.name} is present?",
                f"What would happen if {part.name} didn't have to carry this burden?",
                f"What would {part.name} like to tell the Self directly?"
            ])
        else:
            # System-wide prompts
            if len(self.system.parts) > 1:  # More than just Self
                prompts.extend([
                    "Which part do you feel most strongly right now?",
                    "Are there any parts that feel in conflict with each other?",
                    "Which part would benefit most from some attention today?",
                    "Is there a part that's been trying to get your attention recently?"
                ])
            else:
                prompts.extend([
                    "What aspects of yourself have you noticed protecting you?",
                    "When you feel strong emotions, can you identify any patterns?",
                    "Are there emotions or reactions that feel automatic or out of your control?",
                    "What part of yourself would you like to understand better?"
                ])
                
        return prompts
    
    def explain_ifs_concept(self, concept: str):
        """Provide a simple explanation of an IFS concept"""
        concept_lower = concept.lower()
        
        for key, description in self.ifs_concepts.items():
            if key.lower() == concept_lower:
                return f"{key}: {description}"
        
        # If no exact match, look for partial matches
        matches = [key for key in self.ifs_concepts if concept_lower in key.lower()]
        if matches:
            results = []
            for match in matches:
                results.append(f"{match}: {self.ifs_concepts[match]}")
            return "\n\n".join(results)
        
        return f"I don't have specific information about '{concept}' in IFS terminology. Would you like to explore a related concept?"
    
    def analyze_journal_entry(self, content: str):
        """
        Analyze a journal entry to identify potential parts and emotions
        
        Note: In a real implementation, this would use an LLM for more sophisticated analysis
        """
        analysis = {
            "identified_emotions": [],
            "potential_parts": [],
            "insights": []
        }
        
        # Simple keyword-based emotion detection
        common_emotions = [
            "angry", "sad", "happy", "afraid", "ashamed", "disgusted", 
            "surprised", "anxious", "peaceful", "excited", "frustrated"
        ]
        
        for emotion in common_emotions:
            if emotion in content.lower():
                analysis["identified_emotions"].append(emotion)
        
        # Identify potential parts based on existing parts' names
        for part_id, part in self.system.parts.items():
            if part.name.lower() in content.lower() and part.name.lower() != "self":
                analysis["potential_parts"].append(part_id)
        
        # Simple pattern matching for potential new parts
        patterns = [
            "part of me feels", "I feel like", "a voice inside says",
            "something in me wants", "I notice myself"
        ]
        
        for pattern in patterns:
            if pattern in content.lower():
                start_idx = content.lower().find(pattern) + len(pattern)
                excerpt = content[start_idx:start_idx + 50].strip()
                analysis["insights"].append(f"Potential part identified: \"{excerpt}...\"")
        
        return analysis
