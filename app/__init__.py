from flask import Flask
from .db import init_db
from app.routes.usuarios import usuarios_bp
from app.routes.auth import auth_bp
from dotenv import load_dotenv
import os

def create_app():
    load_dotenv()

    app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates'))

    init_db()
    
    #app.secret_key = os.getenv('SECRET_KEY')
    app.secret_key = 'supersecretkey'

    app.register_blueprint(usuarios_bp)
    app.register_blueprint(auth_bp)

    return app
