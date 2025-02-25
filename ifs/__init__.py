# Initialize the empty package
# We'll import these items at the module level to avoid circular imports
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

# Import models and other modules after db is defined
# These will be imported when needed

__all__ = [
    'User', 'Part', 'Relationship', 'Journal', 'IFSSystem', 'db',
    'generate_system_graph', 'plot_system_graph', 'export_system_json', 'import_system_json'
]

def get_models():
    from ifs.models import User, Part, Relationship, Journal, IFSSystem
    return User, Part, Relationship, Journal, IFSSystem

def get_system_utils():
    from ifs.system import generate_system_graph, plot_system_graph, export_system_json, import_system_json
    return generate_system_graph, plot_system_graph, export_system_json, import_system_json 