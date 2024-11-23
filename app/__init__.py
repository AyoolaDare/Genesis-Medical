from flask import Flask, redirect, url_for
from flask_bcrypt import Bcrypt
from config import Config
import boto3

bcrypt = Bcrypt()
dynamodb = boto3.resource('dynamodb')

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    bcrypt.init_app(app)
    
    from app.auth import bp as auth_bp
    from app.admin import bp as admin_bp
    from app.patient import bp as patient_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(patient_bp)

    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    return app