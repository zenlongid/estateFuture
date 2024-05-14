from flask import Blueprint, jsonify, render_template, request, redirect, url_for, session
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

@customer.route('FAQ')
def FAQ():
    return render_template('FAQ.html')

@login_required
@customer.route('/subscriptionPlans')
def paymentPlans():
    return render_template('subscriptionPlans.html', user=current_user)

@customer.route('/processPayment', methods=['POST'])
def processPayment():
    user_id = current_user.get_id()
    requested_plan = request.json['subscriptionPlan']
    amount = calculateAmount(requested_plan)

    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": 
        {
            "payment_method": "paypal"
        },
        "transactions": [
            {
            "amount": {
                "total": amount,
                "currency": "SGD"
            }
        }],
        "redirect_urls":
        {
            "return_url": url_for('views.index', _external=True),
            "cancel_url": url_for('customer.payment_cancel', _external=True)
        }
    })

    if payment.create():
        current_user.profile = 'Paying Customer'
        users_ref = db.reference('users')
        users_ref.child(current_user.get_id()).update({'profile': 'Paying Customer'})
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

@customer.route('/bookmarksPage')
def bookmarksPage():
    if current_user.is_authenticated:
        user_id = current_user.id
        ref = db.reference(f'/users/{user_id}/bookmarks')
        bookmarks_snapshot = ref.get()
        print("Bookmarks Snapshot: ", bookmarks_snapshot)
        bookmarks_details = []

        if bookmarks_snapshot:
            for bookmark_key in bookmarks_snapshot.values():
                # Assuming 'addresses' is the reference to the addresses in your database
                print("Bookmark Key: ", bookmark_key)
                address_ref = db.reference(f'/testfinal/{bookmark_key}')
                address_details = address_ref.get()
                if address_details:
                    bookmarks_details.append(address_details)

            # Redirect to bookmarks page with the bookmarks details as URL parameters
            return render_template('bookmarksPage.html', bookmarks=bookmarks_details)
        else:
            return jsonify({'message': 'No bookmarks found'}), 404
    else:
        return jsonify({'message': 'User not authenticated'}), 401

