from flask import Flask
from app.routes import main
import os

def create_app():
    app = Flask(__name__)
    app.secret_key = os.urandom(24) 
    
    app.config['UPLOAD_FOLDER'] = os.path.join('app', 'static', 'images')
    app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png', 'gif'}

    
    
    from.routes import main
    app.register_blueprint(main)

    return app





   

   
