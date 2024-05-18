from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from firebase_admin import db
from flask_login import login_required, current_user
import pandas as pd
import numpy as np
import requests
import json
import os

guest = Blueprint('guest', __name__)


@guest.route('/guestSearchPage')
def guestSearchPage():
    if not current_user.is_authenticated:
        flash('Trial Valutaion! To access full features, please subscribe to one of our plans.', 'success')
        return render_template('guestSearchPage.html', user=current_user)

    
@guest.route('/guestSearchByPostal', methods=['GET', 'POST'])
def guestSearchByPostal():
    query = request.args.get('query').upper()
    print("Query: ", query)
    if not query:
        return jsonify([])

    ref = db.reference('/userTrial')

    results1 = ref.order_by_child('town').start_at(query).end_at(query + '\uf8ff').get()
    results2 = ref.order_by_child('address').start_at(query).end_at(query + '\uf8ff').get()
    results3 = ref.order_by_child('postal_code').start_at(query).end_at(query + '\uf8ff').get()

    results_list = []
    if results1:
        for key, value in results1.items():
            value['key'] = key  # Add primary key to each result
            results_list.append(value)
    if results2:
        for key, value in results2.items():
            value['key'] = key
            results_list.append(value)
    if results3:
        for key, value in results3.items():
            value['key'] = key
            results_list.append(value)

    return jsonify(results_list)

@guest.route('/guestSearchByStorey', methods=['GET', 'POST'])
def guestSearchByStorey():
    postal_code = request.args.get('query')
    print("secondQuery: ", postal_code)

    storey_ranges = []
    if postal_code:
        ref = db.reference('/userTrial')
        storey_results = ref.order_by_child('postal_code').equal_to(postal_code).get()
        print("Storey Results: ", len(storey_results))   

        for key, value in storey_results.items():
            storey_ranges.append(value.get('storey_range'))
        
        unique_storey_ranges = list(set(storey_ranges))
    return jsonify(unique_storey_ranges)

@guest.route('/guestSearchByType', methods=['GET', 'POST'])
def guestSearchByType():
    postal_code = request.args.get('query')
    storey_range = request.args.get('storeyRange')
    print("Postal Code:", postal_code)
    print("Storey Range:", storey_range)    

    flat_types = []
    if postal_code and storey_range:
        ref = db.reference('/userTrial')
        data = ref.get()
        if data:
            for key, value in data.items():
                if 'postal_code' in value and 'storey_range' in value:
                    if value['postal_code'] == postal_code and value['storey_range'] == storey_range:
                        flat_type = value.get('flat_type')
                        if flat_type:
                            flat_types.append(flat_type)
    return jsonify(flat_types)

@guest.route('/guestSearchResult', methods=['GET'])
def display_item():
    postal_code = request.args.get('postalCode')
    storey_range = request.args.get('storeyRange')
    flat_type = request.args.get('flatType')

    print("Postal Code:", postal_code)
    print("Storey Range:", storey_range)
    print("Flat Type:", flat_type)

    unit_duplicates_year = []
    if postal_code and storey_range and flat_type:

        #get from final database
        ref = db.reference('/userTrial')
        data = ref.get()
        if data:
            for key, value in data.items():
                if 'postal_code' in value and 'storey_range' in value and 'flat_type' in value:
                    if value['postal_code'] == postal_code and value['storey_range'] == storey_range and value['flat_type'] == flat_type:
                        value['key'] = key
                        unit_duplicates_year.append(value)

    print("Length: ", len(unit_duplicates_year))
    unit_display = unit_duplicates_year[-1]
    print("Unit Display: ", unit_display)
    
    if unit_duplicates_year:  # Check if the list is not empty
        unit_display = unit_duplicates_year[-1]
        if 'key' in unit_display:  # Check if the key 'key' is present in the dictionary
            print("Unit Display Key:", unit_display['key'])
        else:
            print("Key 'key' not found in unit_display dict")

    key = unit_display['key']

    #convert df to html
    #unit_display_html = unit_display_df.to_html()  
    return render_template('guestSearchResult.html', user=current_user, unit_display=unit_display, key=key)
