from flask import Flask
from .db import init_db
from app.routes.usuarios import usuarios_bp
from dotenv import load_dotenv
import os

def create_app():
    load_dotenv()

    app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates'))

    init_db()

    app.register_blueprint(usuarios_bp)

    return app
