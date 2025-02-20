from flask import Flask, jsonify, request
from flask_cors import CORS
from ifs import IFSSystem, Part, Relationship, Journal
import datetime

app = Flask(__name__)
# During development, allow all origins
CORS(app)  # We'll make this more restrictive when deploying

# Initialize a demo system
demo_system = IFSSystem(user_id="demo_user")

@app.route('/api/system', methods=['GET'])
def get_system():
    return jsonify(demo_system.to_dict())

@app.route('/api/parts', methods=['GET', 'POST'])
def handle_parts():
    if request.method == 'GET':
        return jsonify({id: part.to_dict() for id, part in demo_system.parts.items()})
    
    if request.method == 'POST':
        data = request.json
        new_part = Part(
            name=data['name'],
            role=data.get('role'),
            description=data.get('description', ''),
            feelings=data.get('feelings', [])
        )
        part_id = demo_system.add_part(new_part)
        return jsonify({"id": part_id, "part": new_part.to_dict()})

@app.route('/api/parts/<part_id>', methods=['GET', 'PUT'])
def handle_part(part_id):
    if request.method == 'GET':
        part = demo_system.parts.get(part_id)
        return jsonify(part.to_dict()) if part else ('', 404)
    
    if request.method == 'PUT':
        success = demo_system.update_part(part_id, request.json)
        return jsonify({"success": success})

@app.route('/api/test', methods=['GET'])
def test_connection():
    return jsonify({
        "status": "success",
        "message": "Backend is connected!",
        "timestamp": datetime.datetime.now().isoformat()
    })

@app.route('/api/journals', methods=['POST'])
def add_journal():
    data = request.json
    journal = Journal(
        content=data['content'],
        parts_present=data.get('parts_present', []),
        emotions=data.get('emotions', [])
    )
    journal_id = demo_system.add_journal(journal)
    return jsonify({"id": journal_id, "journal": journal.to_dict()})

if __name__ == '__main__':
    app.run(debug=True, port=5000) 