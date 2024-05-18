from flask import Blueprint, jsonify, render_template, request, redirect, url_for, session, flash
from firebase_admin import credentials, auth, db
from flask_login import login_user, logout_user, login_required, logout_user, current_user
from .models import User

import paypalrestsdk
from paypalrestsdk import Payment
 
paypalrestsdk.configure({
    'mode': 'sandbox',  # Set 'sandbox' for testing or 'live' for production
    'client_id': 'ARi_Q0e9up4QuPVcjiExXFxRufyeIQCoG2Gqr1WkDtJ6-kYhvNomUVojzaCQzvQ6JVqO8Bh9Me-JWId8',
    'client_secret': 'EKhGj4lICgToiRDHwnvNojscN3466_9glUpXYJCq98fH4apUa547isq1WhaRkXvVAaw07wnHSFb9DuG0'
})
customer = Blueprint('customer', __name__)

@customer.route('/customerFAQ')
def customerFAQ():
    return render_template('customerFAQ.html')

@login_required
@customer.route('/subscriptionPlans')
def subscriptionPlans():
    return render_template('subscriptionPlans.html', user=current_user)

@customer.route('/processPayment', methods=['POST'])
def processPayment():
    user_id = current_user.get_id()
    requested_plan = request.json['subscriptionPlan']
    amount = calculateAmount(requested_plan)

    # Map subscription plans to profile names
    plan_to_profile = {
        'monthly': 'Monthly',
        'quarterly': 'Quarterly',
        'annual': 'Annual'
    }

    # Get the corresponding profile name for the selected plan
    new_profile = plan_to_profile.get(requested_plan, 'Paying Customer')

    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "transactions": [{
            "amount": {
                "total": amount,
                "currency": "SGD"
            }
        }],
        "redirect_urls": {
            "return_url": url_for('views.index', _external=True, user=current_user),
            "cancel_url": url_for('customer.payment_cancel', _external=True)
        }
    })

    if payment.create():
        # Update the user's profile
        current_user.profile = new_profile
        users_ref = db.reference('users')
        users_ref.child(user_id).update({'profile': new_profile})
        return jsonify({'success': True, 'approvalUrl': payment.links[1].href})
    else:
        return jsonify({'success': False, 'error': payment.error['message']}), 500

@customer.route('/paymentSuccess')
def payment_success():
    return render_template('paymentSuccess.html')

@customer.route('/paymentCancel')
def payment_cancel():
    # Handle payment cancelation
    return render_template('paymentCancel.html')

def calculateAmount(subscriptionPlan):
    base_prices ={
        'monthly': '39.95',
        'quarterly': '59.85',
        'annual': '119.40'
    }
    return base_prices.get(subscriptionPlan, '0.0')


@customer.route('/addBookmark/<unit_key>', methods=['POST'])
def AddBookmark(unit_key):
    if current_user.is_authenticated:
        user_id = current_user.id
        print("User ID: ", user_id)
        print("Unit Key: ", unit_key)

        ref = db.reference(f'/users/{user_id}/bookmarks')

        # Check if 'test' key exists in bookmarks
        bookmarks_snapshot = ref.get()
        if isinstance(bookmarks_snapshot, list):
            if unit_key in bookmarks_snapshot:
                return jsonify({'message': 'Bookmark already exists'}), 409  # Return 409 Conflict status code
            
        elif isinstance(bookmarks_snapshot, dict):
            if unit_key in bookmarks_snapshot.values():
                return jsonify({'message': 'Bookmark already exists'}), 409 
            # Check if 'test' is in the list
            if "test" in bookmarks_snapshot:
                # Remove 'test' from the list
                bookmarks_snapshot.remove("test")
                print("Deleted 'test' bookmark")
                ref.set(bookmarks_snapshot)  # Update the bookmarks list in the database

        # Push the current unit key
        ref.push().set(unit_key)  # Add unit_key to the list of bookmarks
        return jsonify({'message': 'Bookmark added successfully'})
    else:
        return jsonify({'message': 'User not authenticated'}), 401  # Return 401 Unauthorized status code
    
@customer.route('/bookmarksPage' , methods=['GET', 'POST'])
def bookmarksPage():
    if current_user.is_authenticated:
        user_id = current_user.id
        ref = db.reference(f'/users/{user_id}/bookmarks')
        bookmarks_snapshot = ref.get()
        print("Bookmarks Snapshot: ", bookmarks_snapshot)
        bookmarks_details = []

        if bookmarks_snapshot:
            if isinstance(bookmarks_snapshot, list):
                flash('Add bookmarks first!', category='eror')
                return redirect(url_for('predict.searchPage'))  # Redi
            
            elif isinstance(bookmarks_snapshot, dict):
                for bookmark_key in bookmarks_snapshot.values():
                    print("Bookmark Key: ", bookmark_key)

                    address_ref = db.reference(f'/testfinal/{bookmark_key}')
                    address_details = address_ref.get()

                    if address_details:
                        bookmarks_details.append((bookmark_key, address_details))
        return render_template('bookmarksPage.html', bookmarks=bookmarks_details, user=current_user)           
    else:
        return jsonify({'message': 'User not authenticated'}), 401

@customer.route('/compareBookmarks', methods=['GET', 'POST'])
def compareBookmarks():
    if not request.is_json:
        print("Invalid Content-Type, must be application/json")
        return jsonify({"error": "Invalid Content-Type, must be application/json"}), 400

    try:
        selected_address_query = request.get_json()
        print("Received JSON data:", selected_address_query)  # Step 1: Check the received JSON data

        if not isinstance(selected_address_query, list):
            print("Invalid JSON structure: expected a list")
            return jsonify({"error": "Invalid JSON structure: expected a list"}), 400

        selected_addresses_details = []

        for address_id in selected_address_query:
            address_ref = db.reference(f'/testfinal/{address_id}')
            #print("Address reference for ID", address_id, ":", address_ref)  
            address_details = address_ref.get()
            #print("Address details for ID", address_id, ":", address_details)  
            if address_details:
                selected_addresses_details.append((address_id, address_details))
            print("Address ID", address_id)

        session['selected_addresses'] = selected_addresses_details
        return jsonify({"redirect_url": url_for('customer.showCompareBookmarks')})
        #print("Selected addresses details:", selected_addresses_details) 
    
    except Exception as e:
        print("Exception occurred:", e)
        return jsonify({"error": "An error occurred processing the request"}), 500
    
@customer.route('/showCompareBookmarks', methods=['GET'])
def showCompareBookmarks():
    selected_addresses = session.get('selected_addresses', [])
    return render_template('compareBookmarks.html', addresses=selected_addresses, user=current_user)

@login_required
@customer.route('/userDetail/', methods=['GET', 'POST'])
def view_user():

    user_id = current_user.get_id()
    user_ref = db.reference(f'/users/{user_id}')
    user = user_ref.get()
    print(user)

    if user:
        print("Found user: ", user_id)
        return render_template('userAccount.html', user = current_user, userDetails=user, user_id=user_id)
    else:
        return "User not found!"
    
@customer.route('/UserUpdateUserDetails/', methods=['POST'])
def UserUpdateUserDetails():
    user_id = current_user.get_id()
    user_ref = db.reference(f'users/{user_id}')
    
    # Get the form data and prepare the update data
    update_data = {}
    for key, value in request.form.items():
        if key == 'confirm-password':
            continue  # Skip the confirm-password field
        update_data[key] = value
        print(f"Updating {key} to {value}")

    # Update the user data in Firebase
    user_ref.update(update_data)
    flash('User details updated successfully!', category='success')
    return redirect(url_for('views.index', user_id=user_id))

@customer.route('/guestFAQ')
def guestFAQ():
    return render_template('guestFAQ.html')