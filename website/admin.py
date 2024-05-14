from flask import Blueprint, jsonify, render_template, request, redirect, url_for, session
from firebase_admin import credentials, auth, db
from flask_login import login_user, logout_user, login_required, logout_user, current_user
from .models import User

admin = Blueprint('admin', __name__)

@admin.route('/adminDashboard', methods=['GET', 'POST'])
def adminDashboard():
    return render_template('adminDashboard.html')

# FOR VIEWING ALL THE USERS
@admin.route('/adminViewUser', methods=['GET', 'POST'])    
def adminViewUsers():
    user_ref = db.reference('users')
    users = user_ref.get()

    if users:
        return render_template('adminViewUser.html', users=users)
    else:
        return "No users found!"
    
# FOR VIEWING A SPECIFIC USER
@admin.route('/userDetail/<user_id>', methods=['GET', 'POST'])
def view_user(user_id):
    user_ref = db.reference('users')
    user = user_ref.child(user_id).get()

    if user:
        print("Found user: ", user_id)
        return render_template('userDetail.html', user=user, user_id=user_id)
    else:
        return "User not found!"
    
@admin.route('/updateUserDetails/', methods=['POST'])
def updateUserDetails():
    user_id = request.form['user_id']
    new_profile = request.form['profile']
    print("User ID: ", user_id )
    print("New Profile: ", new_profile)

    user_ref = db.reference('users')
    user_ref.child(user_id).update({'profile': new_profile})

    return redirect(url_for('admin.adminViewUsers', user_id=user_id))