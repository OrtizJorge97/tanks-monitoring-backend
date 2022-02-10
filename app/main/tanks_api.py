from flask import Flask, request, Blueprint, jsonify, make_response
import concurrent.futures
from flask_socketio import emit

from . import tank_api_blueprint, session
from .models import *
from .. import socketio
from .Services.database import AsyncDataBaseManager

# DATA TO RECEIVE FROM TANKS AND TO SAVE IT INTO HISTORIC DATA


@tank_api_blueprint.route("/post-data", methods=["POST"])
def post_data():
    try:
        payload = request.get_json()
        print("-----IN TANKS POST DATA-------")
        print(payload)

        executor = concurrent.futures.ThreadPoolExecutor()
        future = executor.submit(AsyncDataBaseManager.get_tank_company, payload)
        company = future.result()

        #future = executor.submit(AsyncDataBaseManager.store_measurements, payload)
        #result = future.result()

        print(company)

        #emit('tanks_data', payload, namespace='/private', to=company)
        socketio.emit('tanks_data', payload, namespace='/private', to=company)
        socketio.emit('get_tank_data', payload, namespace='/private', to=company)
        socketio.emit('get_historic_data', payload, namespace='/private', to=company)
        return make_response(jsonify(msg="Success"), 200)
    except Exception as e:
        print(str(e))
        return make_response(jsonify(msg=str(e)), 500)

# DATA TO RECEIVE FROM TANKS AND TO SAVE IT INTO HISTORIC DATA


@tank_api_blueprint.route("/fetch-tanks", methods=["GET"])
def fetch_tanks():
    print("sdsddddddd")
    try:
        company = request.args.get('company')

        executor = concurrent.futures.ThreadPoolExecutor()
        future = executor.submit(
            AsyncDataBaseManager.get_company_tanks, company)
        tanks_company = future.result()

        executor = concurrent.futures.ThreadPoolExecutor()
        future = executor.submit(
            AsyncDataBaseManager.get_tanks_parameters, company)
        tanks_parameters = future.result()

        tanks_parameters_list = []
        for tank_id in tanks_company:
            tank_parameters_dict = {
                'id': tank_id
            }
            for tank_parameter_tuple in tanks_parameters:
                if tank_parameter_tuple[0] == tank_id:
                    tank_parameters_dict[f"{tank_parameter_tuple[1]}Min"] = tank_parameter_tuple[2]
                    tank_parameters_dict[f"{tank_parameter_tuple[1]}Max"] = tank_parameter_tuple[3]
                    """
                    if tank_parameter_tuple[1] == 'WtrLvl':
                        tank_parameters_dict['WtrLvlMin'] = tank_parameter_tuple[2]
                        tank_parameters_dict['WtrLvlMax'] = tank_parameter_tuple[3]
                    elif tank_parameter_tuple[1] == 'OxygenPercentage':
                        tank_parameters_dict['OxygenPercentageMin'] = tank_parameter_tuple[2]
                        tank_parameters_dict['OxygenPercentageMax'] = tank_parameter_tuple[3]
                    elif tank_parameter_tuple[1] == 'Ph':
                        tank_parameters_dict['PhMin'] = tank_parameter_tuple[2]
                        tank_parameters_dict['PhMax'] = tank_parameter_tuple[3]
                    """
            tanks_parameters_list.append(tank_parameters_dict)
        print(tanks_parameters_list)

        return make_response(jsonify(msg="Success fetching", tanks=tanks_parameters_list), 200)
    except Exception as e:
        return make_response(jsonify(msg=str(e)), 500)
