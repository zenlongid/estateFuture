from flask import Blueprint, render_template
from flask_login import current_user

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template('index.html', user = current_user)

@views.route('/index')
def index():
    return render_template('index.html', user = current_user)
