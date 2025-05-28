from flask import Flask
from .config import Config
from .models import db
from .routes import bp

def create_app():
    app = Flask(__name__,  template_folder='../templates')
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(bp)
    
    return app