from flask import Blueprint, render_template, request, jsonify
from firebase_admin import db
#from joblib import load
import pickle
from flask_login import login_required, current_user
import pandas as pd
import numpy as np
import requests
import json

predict = Blueprint('predict', __name__)

#loading trained model
#rf = load('C:\\Users\\Zen\\Documents\\GitHub\\Local\\TrainedModels\\rf.joblib')
#rf = load('C:\\Users\\admin\\Desktop\\Dataset\\randomForest.joblib')

@predict.route('/searchPage', methods=['GET', 'POST'])
@login_required
def searchPage():
    user = current_user
    return render_template('searchPage.html', user=user)
    
@predict.route('/searchByPostal', methods=['GET', 'POST'])
def searchByPostal():
    query = request.args.get('query').upper()
    print("Query: ", query)
    if not query:
        return jsonify([])

    ref = db.reference('/uniquePostal')

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

    
    #print("Results: ", results_list)
   # print("Results: ", jsonify(results_list))
    
    #response = jsonify(results_list)
    #json_data = response.get_data(as_text=True)
    #print(json_data)
    return jsonify(results_list)

@predict.route('/searchByStorey', methods=['GET', 'POST'])
def searchByStorey():
    postal_code = request.args.get('query')
    print("secondQuery: ", postal_code)

    storey_ranges = []
    if postal_code:
        ref = db.reference('/testfinal')
        storey_results = ref.order_by_child('postal_code').equal_to(postal_code).get()
        #print(storey_results)
        print("Storey Results: ", len(storey_results))   

        for key, value in storey_results.items():
            storey_ranges.append(value.get('storey_range'))
        
        unique_storey_ranges = list(set(storey_ranges))
    return jsonify(unique_storey_ranges)

@predict.route('/searchByType', methods=['GET', 'POST'])
def searchByType():
    postal_code = request.args.get('query')
    storey_range = request.args.get('storeyRange')
    print("Postal Code:", postal_code)
    print("Storey Range:", storey_range)    

    flat_types = []
    if postal_code and storey_range:
        ref = db.reference('/testfinal')
        data = ref.get()
        if data:
            for key, value in data.items():
                if 'postal_code' in value and 'storey_range' in value:
                    if value['postal_code'] == postal_code and value['storey_range'] == storey_range:
                        flat_type = value.get('flat_type')
                        if flat_type:
                            flat_types.append(flat_type)
    return jsonify(flat_types)

@predict.route('/searchResult', methods=['GET'])
def display_item():
    user = current_user 
    postal_code = request.args.get('postalCode')
    storey_range = request.args.get('storeyRange')
    flat_type = request.args.get('flatType')

    print("Postal Code:", postal_code)
    print("Storey Range:", storey_range)
    print("Flat Type:", flat_type)

    unit_duplicates_year = []
    if postal_code and storey_range and flat_type:

        #get from final database
        ref = db.reference('/testfinal')
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
   

    #unit_display_df = json.loads(unit_display)
    
    if isinstance(unit_display, dict):
        print("is an object")
    else:
        print("not an object")

    lambda_endpoint = 'https://aqiqs40n6a.execute-api.ap-southeast-2.amazonaws.com/deployment/predictDemo'

    unit_display = json.dumps(unit_display)
    
    response = requests.post(lambda_endpoint, json=unit_display)

    if response.status_code == 200:
        lambda_response = response.json()
        print("Lambda Response: ", lambda_response)
    else:
        return "Error in making prediction", 500
    #dropping unnecessary columns to pass into model
    #input_features = rf.feature_names_in_
    #columns_to_drop = [col for col in unit_display_df.columns if col not in input_features]
    #unit_display_df = unit_display_df.drop(columns=columns_to_drop)

    #unit_display_df = unit_display_df.reindex(columns=input_features, fill_value=0)

    #input feature to send to AWS
    #input_features = unit_display_df.to_json(orient='records')

    #make prediction            
    #prediction = make_prediction(rf, unit_display_df)
    #print("Prediction: ", prediction)

    #convert df to html
    #unit_display_html = unit_display_df.to_html()  
    #return render_template('predictResult.html', user=user, unit_display=unit_display, unit_display_html=unit_display_html, prediction=prediction[0])
    

    return render_template('index.html', user = current_user)