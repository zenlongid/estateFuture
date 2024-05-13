from flask import Blueprint, jsonify, render_template, request, redirect, url_for, session
from firebase_admin import credentials, auth, db
from flask_login import login_user, logout_user, login_required, logout_user, current_user
from .models import User

import hashlib

auth = Blueprint('auth', __name__)

@auth.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'GET':
        print("GET request received.")
        return render_template('login.html')

    else:
        print("POST request received.")
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:    
            return jsonify({'message': 'Missing email or password'}), 400
        
        email_key = email.replace('.', '').replace('@', '')  
        print(f"Attemtping to retrieve user with key:  {email_key}") 
        
        try:
            user_ref = db.reference(f'users/{email_key}')
            user_data = user_ref.get()
            
            #checking if user exists and password is correct

            if user_data and 'password' in user_data:
                stored_password = user_data['password']
                entered_password = password

                #Hashing the entered password
                md5 = hashlib.md5()
                md5.update(entered_password.encode('utf-8'))
                hashed_entered_password = md5.hexdigest()
                
                print("Stored password: ", stored_password)
                print("Entered password: ", entered_password)
                print("Hashed entered password: ", hashed_entered_password)
                
                #authenticating user
                if stored_password == hashed_entered_password:
                    print("before making class")
                    user = User(user_id=email_key, **user_data)
                    print("before")
                    print(user)
                    print("type of user: ", type(user))
                    login_user(user, remember=True)
                    print("after")
                    if user_data['profile'] == 'Admin':
                        return redirect(url_for('admin.adminDashboard'))
                    else:
                        return redirect(url_for('views.index'))
                else:
                    return jsonify({'message': 'Invalid email or password'}), 401
        
        except Exception as e:
    # Return a generic error message
            return jsonify({'message': 'User authentication failed. Please try again.'}), 400


@auth.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html', user = current_user)
    
    print("Received a POST request.")
    email = request.form.get('email')
    password = request.form.get('password')
    birthday = request.form.get('birthday')
    profile = "Customer"
    suspended = request.form.get('suspended', 'False')

    #hashing the password for security
    md5 = hashlib.md5()
    md5.update(password.encode('utf-8'))
    hashed_password = md5.hexdigest()
    
    #removing special characters from email
    email_key = email.replace('.', '').replace('@', '')

    try:
        ref_path = f'/users/{email_key}'
        print(ref_path)
        user_ref = db.reference(ref_path)
        user_ref.set({
            'email': email,
            'password': hashed_password,
            'profile': profile,
            'birthday': birthday,
            'suspended': suspended
        })

        return redirect(url_for('auth.login', user = current_user))
    
    except Exception as e:
        return jsonify({'message': 'User creation failed!'}), 400 

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))