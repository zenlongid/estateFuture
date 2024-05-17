from flask import Blueprint, jsonify, render_template, request, redirect, url_for, session, flash
from firebase_admin import credentials, auth, db
from flask_login import login_user, logout_user, login_required, logout_user, current_user
from .models import User
import hashlib

admin = Blueprint('admin', __name__)

@login_required
@admin.route('/adminDashboard', methods=['GET', 'POST'])
def adminDashboard():
    return render_template('adminDashboard.html', user = current_user)

@login_required
@admin.route('/adminViewUser', methods=['GET', 'POST'])    
def adminViewUsers():
    user_ref = db.reference('users')
    users = user_ref.get()

    if users:
        return render_template('adminViewUser.html', users=users, user = current_user)
    else:
        return "No users found!"

@login_required
@admin.route('/userDetail/<user_id>', methods=['GET', 'POST'])
def view_user(user_id):
    user_ref = db.reference('users')
    found_user = user_ref.child(user_id).get()

    if found_user:
        print("Found user: ", user_id)
        return render_template('userDetail.html', user=current_user, user_id=user_id, found_user=found_user)
    else:
        return "User not found!"

@login_required    
@admin.route('/updateUserDetails/', methods=['POST'])
def updateUserDetails():
    user_id = request.form['user_id']
    user_ref = db.reference('users').child(user_id)
    
    # Get the existing user data
    user_data = user_ref.get()
    
    # Collect fields to update
    updates = {}
    if 'name' in request.form and request.form['name'] != user_data.get('name'):
        updates['name'] = request.form['name']
    if 'birthday' in request.form and request.form['birthday'] != user_data.get('birthday'):
        updates['birthday'] = request.form['birthday']
    if 'profile' in request.form and request.form['profile'] != user_data.get('profile'):
        updates['profile'] = request.form['profile']

    # Update only the fields that have changed
    if updates:
        user_ref.update(updates)
        flash('User details updated successfully!', category='success')
    else:
        flash('No changes detected.', category='info')
    
    return redirect(url_for('admin.adminViewUsers', user_id=user_id))

@admin.route('/adminCreateProfile', methods=['GET', 'POST'])
def adminCreateProfile():
    
    if request.method == 'GET':
        return render_template('adminCreateProfile.html', user = current_user)

    print("POST request received.")
    email = request.form.get('email')
    password = request.form.get('password')
    name = request.form.get('name')
    birthday = request.form.get('birthday')
    profile = request.form.get('profile')
    suspended = request.form.get('suspended', 'False')
    bookmarks = ['test']

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
            'name': name,
            'password': hashed_password,
            'profile': profile,
            'birthday': birthday,
            'bookmarks': bookmarks,
            'suspended': suspended
        })
        flash(f'Successfully created Account!', category='success')
        return redirect(url_for('admin.adminCreateProfile', user = current_user))
    except Exception as e:
        return jsonify({'message': 'User creation failed!'}), 400 

@admin.route('/adminViewProfiles', methods=['GET', 'POST'])
def adminViewProfiles():
    user = current_user
    profile_ref = db.reference('profile-data')
    profiles = profile_ref.get()

    if profiles:
        profiles_list = [{'profile_name': key, **value} for key, value in profiles.items()]
        print("Current User's Name", user.name)
        return render_template('adminViewProfiles.html', profiles=profiles_list, user=user)
    else:
        return "No Profiles found!"
