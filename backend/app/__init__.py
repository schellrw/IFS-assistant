"""
Application factory module.
"""
import os
from typing import Optional, Dict, Any
import logging
from logging.config import dictConfig

# Add dotenv loading at the top level
from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from .models import db, migrate
from .config.config import get_config
from .utils.db_adapter import init_db_adapter

# Set up logging
def configure_logging(app: Flask) -> None:
    """Configure application logging.
    
    Args:
        app: Flask application instance.
    """
    log_level = app.config.get('LOG_LEVEL', 'INFO')
    
    dictConfig({
        'version': 1,
        'formatters': {
            'default': {
                'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout',
                'formatter': 'default'
            },
        },
        'root': {
            'level': log_level,
            'handlers': ['console']
        }
    })

def create_app(test_config: Optional[Dict[str, Any]] = None) -> Flask:
    """Application factory for creating a Flask app instance.
    
    Args:
        test_config: Optional configuration dictionary for testing.
        
    Returns:
        Configured Flask application instance.
    """
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    # Load config
    if test_config is None:
        app.config.from_object(get_config())
    else:
        app.config.from_mapping(test_config)
    
    # Configure logging
    configure_logging(app)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt = JWTManager(app)
    
    # Initialize database adapter
    try:
        init_db_adapter(app, db)
        app.logger.info("Database adapter initialized successfully")
    except ImportError as e:
        app.logger.warning(f"Could not initialize database adapter: {e}")
    except Exception as e:
        app.logger.error(f"Error initializing database adapter: {e}")
    
    # Configure CORS
    CORS(app, resources={r"/api/*": {"origins": app.config.get('CORS_ORIGINS')}})
    
    # Register blueprints
    from .api.auth import auth_bp
    from .api.parts import parts_bp
    from .api.journals import journals_bp
    from .api.relationships import relationships_bp
    from .api.systems import systems_bp
    from .api.conversations import conversations_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(parts_bp, url_prefix='/api')
    app.register_blueprint(journals_bp, url_prefix='/api')
    app.register_blueprint(relationships_bp, url_prefix='/api')
    app.register_blueprint(systems_bp, url_prefix='/api')
    app.register_blueprint(conversations_bp, url_prefix='/api')
    
    # Shell context for Flask CLI
    @app.shell_context_processor
    def ctx():
        return {'app': app, 'db': db}
    
    return app 