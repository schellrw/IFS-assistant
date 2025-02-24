from flask import Flask, jsonify, request, g
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from ifs.models import User, Part, Relationship, Journal, IFSSystem, db
import datetime
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'dev-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# During development, allow all origins
CORS(app, supports_credentials=True)  # We'll make this more restrictive when deploying

jwt = JWTManager(app)

# Create all database tables
@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    print(f"Registration attempt for: {username}, {email}")
    
    if not username or not email or not password:
        print(f"Registration failed: Missing fields")
        return jsonify({"error": "All fields are required"}), 400
        
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        print(f"Registration failed: Username {username} already exists")
        return jsonify({"error": "Username already exists"}), 400
    
    try:
        # Create new user
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        
        # Create a new system for the user
        system = IFSSystem(user_id=user.id)
        db.session.add(system)
        
        # Add default "Self" part
        self_part = Part(
            name="Self", 
            system_id=system.id,
            role="Self", 
            description="The compassionate core consciousness that can observe and interact with other parts"
        )
        db.session.add(self_part)
        
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(identity=user.id)
        
        print(f"User {username} registered successfully with ID: {user.id}")
        return jsonify({
            "message": "User registered successfully",
            "access_token": access_token,
            "user": user.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Registration error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    
    user = User.query.filter_by(username=username).first()
    
    if not user or not user.verify_password(password):
        return jsonify({"error": "Invalid username or password"}), 401
    
    # Create access token
    access_token = create_access_token(identity=user.id)
    
    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "user": user.to_dict()
    })

# Middleware to load the current user's system
@app.before_request
def load_system():
    # Skip auth for login and register endpoints
    if request.path in ['/api/login', '/api/register', '/api/test']:
        return
    
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return
    
    try:
        # Get the token
        token = auth_header.split(' ')[1]
        # Set the current user ID
        user_id = get_jwt_identity()
        g.user_id = user_id
        # Load the user's system
        g.system = IFSSystem.query.filter_by(user_id=user_id).first()
    except Exception as e:
        print(f"Error loading system: {str(e)}")
        pass

@app.route('/api/system', methods=['GET'])
@jwt_required()
def get_system():
    user_id = get_jwt_identity()
    system = IFSSystem.query.filter_by(user_id=user_id).first()
    
    if not system:
        return jsonify({"error": "System not found"}), 404
    
    return jsonify(system.to_dict())

@app.route('/api/parts', methods=['GET', 'POST'])
@jwt_required()
def parts():
    user_id = get_jwt_identity()
    system = IFSSystem.query.filter_by(user_id=user_id).first()
    
    if not system:
        return jsonify({"error": "System not found"}), 404
    
    if request.method == 'POST':
        data = request.json
        part = Part(
            name=data['name'],
            system_id=system.id,
            role=data.get('role'),
            description=data.get('description', '')
        )
        # Handle feelings and other arrays
        if 'feelings' in data:
            part.feelings = json.dumps(data['feelings'])
        
        db.session.add(part)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "part": part.to_dict()
        })
    
    # GET method
    parts = Part.query.filter_by(system_id=system.id).all()
    return jsonify([part.to_dict() for part in parts])

@app.route('/api/parts/<part_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def part(part_id):
    user_id = get_jwt_identity()
    system = IFSSystem.query.filter_by(user_id=user_id).first()
    
    if not system:
        return jsonify({"error": "System not found"}), 404
    
    part = Part.query.filter_by(id=part_id, system_id=system.id).first()
    if not part:
        return jsonify({"error": "Part not found"}), 404
    
    if request.method == 'GET':
        return jsonify(part.to_dict())
    
    if request.method == 'PUT':
        data = request.json
        
        if 'name' in data:
            part.name = data['name']
        if 'role' in data:
            part.role = data['role']
        if 'description' in data:
            part.description = data['description']
        if 'feelings' in data:
            part.feelings = json.dumps(data['feelings'])
        if 'beliefs' in data:
            part.beliefs = json.dumps(data['beliefs'])
        if 'triggers' in data:
            part.triggers = json.dumps(data['triggers'])
        if 'needs' in data:
            part.needs = json.dumps(data['needs'])
        
        part.updated_at = datetime.datetime.now().isoformat()
        db.session.commit()
        
        return jsonify({
            "success": True,
            "part": part.to_dict()
        })
    
    if request.method == 'DELETE':
        db.session.delete(part)
        db.session.commit()
        return jsonify({"success": True})

@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({
        "status": "ok",
        "message": "API is working"
    })

@app.route('/api/journals', methods=['POST'])
@jwt_required()
def create_journal():
    user_id = get_jwt_identity()
    system = IFSSystem.query.filter_by(user_id=user_id).first()
    
    if not system:
        return jsonify({"error": "System not found"}), 404
    
    data = request.json
    journal = Journal(
        title=data.get('title', 'Untitled Journal'),
        content=data.get('content', ''),
        part_id=data.get('part_id'),
        system_id=system.id
    )
    
    db.session.add(journal)
    db.session.commit()
    
    return jsonify({
        "success": True,
        "journal": journal.to_dict()
    })

@app.route('/api/relationships', methods=['POST'])
@jwt_required()
def create_relationship():
    user_id = get_jwt_identity()
    system = IFSSystem.query.filter_by(user_id=user_id).first()
    
    if not system:
        return jsonify({"error": "System not found"}), 404
    
    data = request.json
    source_id = data.get('source_id')
    target_id = data.get('target_id')
    
    # Verify that the parts exist in the system
    source_part = Part.query.filter_by(id=source_id, system_id=system.id).first()
    target_part = Part.query.filter_by(id=target_id, system_id=system.id).first()
    
    if not source_part:
        return jsonify({"error": f"Source part {source_id} not found"}), 404
    if not target_part:
        return jsonify({"error": f"Target part {target_id} not found"}), 404
    
    # Check if relationship already exists
    existing_rel = Relationship.query.filter_by(
        source_id=source_id, 
        target_id=target_id,
        system_id=system.id
    ).first()
    
    if existing_rel:
        return jsonify({"error": "Relationship already exists"}), 400
    
    relationship = Relationship(
        source_id=source_id,
        target_id=target_id,
        relationship_type=data.get('relationship_type', 'generic'),
        description=data.get('description', ''),
        system_id=system.id
    )
    
    db.session.add(relationship)
    db.session.commit()
    
    return jsonify({
        "success": True,
        "relationship": relationship.to_dict()
    })

@app.route('/api/relationships/<relationship_id>', methods=['PUT', 'DELETE'])
@jwt_required()
def relationship(relationship_id):
    user_id = get_jwt_identity()
    system = IFSSystem.query.filter_by(user_id=user_id).first()
    
    if not system:
        return jsonify({"error": "System not found"}), 404
        
    relationship = Relationship.query.filter_by(id=relationship_id, system_id=system.id).first()
    if not relationship:
        return jsonify({"error": "Relationship not found"}), 404
    
    if request.method == 'PUT':
        data = request.json
        
        if 'relationship_type' in data:
            relationship.relationship_type = data['relationship_type']
        if 'description' in data:
            relationship.description = data['description']
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "relationship": relationship.to_dict()
        })
    
    if request.method == 'DELETE':
        db.session.delete(relationship)
        db.session.commit()
        return jsonify({"success": True})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables before running the app
    app.run(debug=True, port=5000) 