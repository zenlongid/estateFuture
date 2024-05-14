from flask import Flask, redirect, url_for
import firebase_admin
from firebase_admin import credentials, initialize_app, db
from flask_login import LoginManager, current_user
import os

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'beabeabea1'

    cred_path =os.path.join('website','API','csci321-fyp-firebase-adminsdk-1z8qo-568ba51373.json')
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://csci321-fyp-default-rtdb.asia-southeast1.firebasedatabase.app/'
    
    })

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        print("Loading user: ", user_id)
        user_ref = db.reference(f'users/{user_id}')
        user_snapshot = user_ref.get()
        
        if user_snapshot:
            email = user_snapshot.get('email')
            password = user_snapshot.get('password')
            profile = user_snapshot.get('profile')
            birthday = user_snapshot.get('birthday')
            suspended = user_snapshot.get('suspended')
            bookmarks = user_snapshot.get('bookmarks')  
            name = user_snapshot.get('name')
            
            user = User(user_id, email, password, profile, birthday, suspended, name, bookmarks)
            return user
        else:
            return None
        
    
    from .views import views
    from .predict import predict
    from .auth import auth
    from .admin import admin
    from .customer import customer
    
    from .models import User


    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(predict, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(admin, url_prefix='/')  
    app.register_blueprint(customer, url_prefix='/')
    
    return app
