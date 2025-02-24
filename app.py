from flask import Flask, jsonify, request, g
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from ifs import IFSSystem, Part, Relationship, Journal, User
import datetime
import os

app = Flask(__name__)
# Set a secret key for JWT
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'dev-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)
# During development, allow all origins
CORS(app, supports_credentials=True)  # We'll make this more restrictive when deploying

jwt = JWTManager(app)

# In-memory user store (replace with database in production)
users = {}
# In-memory system store (replace with database in production)
systems = {}

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not username or not email or not password:
        return jsonify({"error": "All fields are required"}), 400
        
    if username in [user.username for user in users.values()]:
        return jsonify({"error": "Username already exists"}), 400
        
    user = User(username=username, email=email, password=password)
    users[user.id] = user
    
    # Create a new system for the user
    system = IFSSystem(user_id=user.id)
    systems[user.id] = system
    
    # Create access token
    access_token = create_access_token(identity=user.id)
    
    return jsonify({
        "message": "User registered successfully",
        "access_token": access_token,
        "user": user.to_dict()
    }), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    
    user = next((u for u in users.values() if u.username == username), None)
    
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
        user_id = get_jwt_identity()
        g.current_user_id = user_id
        g.current_system = systems.get(user_id)
    except:
        pass

@app.route('/api/system', methods=['GET'])
@jwt_required()
def get_system():
    user_id = get_jwt_identity()
    system = systems.get(user_id)
    if not system:
        return jsonify({"error": "System not found"}), 404
    return jsonify(system.to_dict())

@app.route('/api/parts', methods=['GET', 'POST'])
@jwt_required()
def handle_parts():
    user_id = get_jwt_identity()
    system = systems.get(user_id)
    
    if request.method == 'GET':
        return jsonify({id: part.to_dict() for id, part in system.parts.items()})
    
    if request.method == 'POST':
        data = request.json
        new_part = Part(
            name=data['name'],
            role=data.get('role'),
            description=data.get('description', ''),
            feelings=data.get('feelings', [])
        )
        new_part.beliefs = data.get('beliefs', [])
        new_part.triggers = data.get('triggers', [])
        new_part.needs = data.get('needs', [])
        
        part_id = system.add_part(new_part)
        return jsonify({"id": part_id, "part": new_part.to_dict()})

@app.route('/api/parts/<part_id>', methods=['GET', 'PUT'])
@jwt_required()
def handle_part(part_id):
    user_id = get_jwt_identity()
    system = systems.get(user_id)
    if not system:
        return jsonify({"error": "System not found"}), 404
    
    part = system.parts.get(part_id)
    if request.method == 'GET':
        return jsonify(part.to_dict()) if part else ('', 404)
    
    if request.method == 'PUT':
        success = system.update_part(part_id, request.json)
        return jsonify({"success": success})

@app.route('/api/test', methods=['GET'])
def test_connection():
    return jsonify({
        "status": "success",
        "message": "Backend is connected!",
        "timestamp": datetime.datetime.now().isoformat()
    })

@app.route('/api/journals', methods=['POST'])
@jwt_required()
def add_journal():
    user_id = get_jwt_identity()
    system = systems.get(user_id)
    if not system:
        return jsonify({"error": "System not found"}), 404
    
    data = request.json
    journal = Journal(
        content=data['content'],
        parts_present=data.get('parts_present', []),
        emotions=data.get('emotions', [])
    )
    journal_id = system.add_journal(journal)
    return jsonify({"id": journal_id, "journal": journal.to_dict()})

@app.route('/api/relationships', methods=['POST'])
@jwt_required()
def add_relationship():
    user_id = get_jwt_identity()
    system = systems.get(user_id)
    if not system:
        return jsonify({"error": "System not found"}), 404
    
    data = request.json
    print("Received relationship data:", data)  # Debug print
    
    try:
        relationship = Relationship(
            source_id=data['source_id'],
            target_id=data['target_id'],
            relationship_type=data['relationship_type'],
            description=data.get('description', '')
        )
        
        # Validate that both parts exist
        if relationship.source_id not in system.parts:
            return jsonify({"error": f"Source part {relationship.source_id} not found"}), 400
        if relationship.target_id not in system.parts:
            return jsonify({"error": f"Target part {relationship.target_id} not found"}), 400
        
        relationship_id = system.add_relationship(relationship)
        print("Created relationship with ID:", relationship_id)  # Debug print
        
        return jsonify({
            "id": relationship_id,
            "relationship": relationship.to_dict()
        })
    except Exception as e:
        print("Error creating relationship:", str(e))  # Debug print
        return jsonify({"error": str(e)}), 500

@app.route('/api/relationships/<relationship_id>', methods=['PUT', 'DELETE'])
@jwt_required()
def handle_relationship(relationship_id):
    user_id = get_jwt_identity()
    system = systems.get(user_id)
    if not system or relationship_id not in system.relationships:
        return jsonify({"error": "Relationship not found"}), 404
    
    if request.method == 'PUT':
        data = request.json
        relationship = system.relationships[relationship_id]
        
        if 'relationship_type' in data:
            relationship.relationship_type = data['relationship_type']
        if 'description' in data:
            relationship.description = data['description']
        
        return jsonify({
            "success": True,
            "relationship": relationship.to_dict()
        })
    
    if request.method == 'DELETE':
        del system.relationships[relationship_id]
        return jsonify({"success": True})

if __name__ == '__main__':
    app.run(debug=True, port=5000) 