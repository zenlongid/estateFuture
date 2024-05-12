from flask import Flask, redirect, url_for
import firebase_admin
from firebase_admin import credentials, initialize_app, db
from flask_login import LoginManager, current_user

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'beabeabea1'

    cred = credentials.Certificate('API KEY\csci321-fyp-firebase-adminsdk-1z8qo-568ba51373.json')
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://csci321-fyp-default-rtdb.asia-southeast1.firebasedatabase.app/'
    
    })
    
        
    
    from .views import views

    app.register_blueprint(views, url_prefix='/')
    
    return app
