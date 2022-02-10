from pickletools import read_uint1
from flask import Flask, request, Blueprint, jsonify, make_response
from flask_cors import CORS
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt
from flask_socketio import emit

import concurrent.futures

#from . import main
from . import api_blueprint, session
from .models import *
from .. import socketio
from .utilities import constants
from .Services.database import AsyncDataBaseManager
from .utilities.convertions import *


@api_blueprint.route("/", methods=["GET"])
def index():
    # print(request.sid)
    return "loooo"


@api_blueprint.route("/add-company", methods=["POST"])
def add_company():
    # print(request.sid)
    try:
        company = request.get_json()

        company_db = Companies(name=company["company_name"],
                               address=company["address"])

        session.add(company_db)
        session.commit()
        return make_response(jsonify({"message": "Successfully added"}), 200)
    except Exception as e:
        return make_response(jsonify({"message": str(e)}), 500)


@api_blueprint.route("/add-user", methods=["POST"])
def add_user():
    # print(request.sid)
    try:
        user = request.get_json()
        query = session.query(Companies).filter_by(company=user["company"])
        company = query.first()
        print("puto: " + company.company)
        """
        user_db = Users(name=user["name"],
                        last_name=user["address"],
                        email=user["email"],
                        password=user["password"],
                        user_verified=user["user_verified"],
                        role=user["role"],
                        company_id=user["company_id"])
        """

        return make_response(jsonify({"message": "Successfully added"}), 200)
    except Exception as e:
        return make_response(jsonify({"message": str(e)}), 500)


@api_blueprint.route("/fetch-tanks", methods=["GET"])
@jwt_required()
def fetch_tanks():
    claims = get_jwt()
    company = session.query(Companies).filter_by(
        company=claims["company"]).first()
    print("ID OF COMPANY: " + str(company.id))
    tanks_company_db = session.query(Tanks.tank_name, Companies.company).select_from(Tanks)\
        .join(Companies, Tanks.company_id == Companies.id)\
        .filter(Companies.id == company.id).all()

    constants.tanks_company["tanks"] = []
    print("------------------------RESULTS OF JOIN QUERY---------------------------")
    for tank_company in tanks_company_db:
        constants.tanks_company["tanks"].append(tank_company[0])

    print(constants.tanks_company["tanks"])
    return make_response(jsonify(
        msg="Success fetching",
        tanks=constants.tanks_company["tanks"],
        email=claims['email'],
        company=claims['company']), 200)


@api_blueprint.route("/add-tank", methods=["POST"])
@jwt_required()
def add_tank():
    try:
        tank = request.get_json()
        print(tank)
        company = session.query(Companies).filter_by(
            company=tank['company']).first()
        tank_db = session.query(Tanks).filter_by(
            tank_name=tank['tankId']).first()

        if tank_db:
            return make_response(jsonify(msg="Tank already added, please modify or delete."), 200)

        session.add(Tanks(tank_name=tank['tankId'],
                          company_id=company.id))
        session.commit()

        tank_db = session.query(Tanks).filter_by(
            tank_name=tank['tankId']).first()
        session.add(Measures_Categories(measure_type="WtrLvl",
                                        tank_min_value=tank['WtrLvlMin'],
                                        tank_max_value=tank['WtrLvlMax'],
                                        tank_id=tank_db.id))
        session.add(Measures_Categories(measure_type="OxygenPercentage",
                                        tank_min_value=tank['OxygenPercentageMin'],
                                        tank_max_value=tank['OxygenPercentageMax'],
                                        tank_id=tank_db.id))
        session.add(Measures_Categories(measure_type="Ph",
                                        tank_min_value=tank['PhMin'],
                                        tank_max_value=tank['PhMax'],
                                        tank_id=tank_db.id))
        session.commit()

        return make_response(jsonify(msg="Success adding"), 200)

    except Exception as e:
        return make_response(jsonify(msg=str(e)), 500)


@api_blueprint.route("/fetch-tank", methods=["GET"])
@jwt_required()
def fetch_tank():
    try:
        tankId = request.args.get("tankId")

        executor = concurrent.futures.ThreadPoolExecutor()
        future = executor.submit(
            AsyncDataBaseManager.get_tank_parameters, tankId)
        future_result = future.result()

        tank_parameters = convert_tank_parameters(future_result)

        return make_response(jsonify(msg="Successfully fetched",
                                     parameters=tank_parameters,
                                     tankId=tankId), 200)
    except Exception as e:
        return make_response(jsonify(msg=str(e)), 500)


@api_blueprint.route("/update-tank", methods=["POST"])
@jwt_required()
def update_tank():
    try:
        tank_new_values = request.get_json()
        print("-------TANK ID NEW VALUES----------")
        print(tank_new_values)
        executor = concurrent.futures.ThreadPoolExecutor()
        future = executor.submit(
            AsyncDataBaseManager.update_tank_parameters, tank_new_values)
        future.result()

        return make_response(jsonify(msg="Succesfully updated"), 200)
    except Exception as e:
        return make_response(jsonify(msg=str(e)), 500)


@api_blueprint.route("/delete-tank", methods=["DELETE"])
@jwt_required()
def delete_tank():
    try:
        tank = request.get_json()
        print("------------TANK NAME TO DELETE-----------")
        print(tank)

        executor = concurrent.futures.ThreadPoolExecutor()
        future = executor.submit(
            AsyncDataBaseManager.delete_tank, tank['tankId'])
        future.result()

        return make_response(jsonify(msg="Operation Succeded"), 200)
    except Exception as e:
        return make_response(jsonify(msg=str(e)), 500)


@api_blueprint.route("/fetch-historic", methods=["GET"])
@jwt_required()
def fetch_historic():
    company = request.args.get("company")
    print("---------PRINTING COMPANY----------")
    print(company)
    executor = concurrent.futures.ThreadPoolExecutor()
    future = executor.submit(AsyncDataBaseManager.get_historic, company)
    result = future.result()

    return make_response(jsonify(msg="Successfully fetched", data=result), 200)


@api_blueprint.route("/fetch-users", methods=["GET"])
@jwt_required()
def fetch_users():
    try:
        company = request.args.get("company")
        executor = concurrent.futures.ThreadPoolExecutor()
        future = executor.submit(AsyncDataBaseManager.get_users, company)
        users = future.result()
        print(users)

        return make_response(jsonify(msg="Success Fetching", users=users), 200)
    except Exception as e:
        return make_response(jsonify(msg=str(e)), 200)


@api_blueprint.route("/fetch-user", methods=["GET"])
@jwt_required()
def fetch_user():
    try:
        email = request.args.get("email")
        executor = concurrent.futures.ThreadPoolExecutor()
        future = executor.submit(AsyncDataBaseManager.get_user, email)
        return make_response(jsonify(msg="Succesfully fetched", user=future.result()), 200)
    except Exception as e:
        return make_response(jsonify(msg=str(e)), 200)


@api_blueprint.route("/update-user", methods=["PUT"])
@jwt_required()
def update_user():
    try:
        new_user = request.get_json()
        print(new_user)
        executor = concurrent.futures.ThreadPoolExecutor()
        future = executor.submit(
            AsyncDataBaseManager.update_user_by_id, new_user['user'])
        updated_user = future.result()
        return make_response(jsonify(msg="Succesfully updated", user=updated_user), 200)
    except Exception as e:
        print(e)
        return make_response(jsonify(msg=str(e)), 500)


@api_blueprint.route("/delete-user", methods=["DELETE"])
@jwt_required()
def delete_user():
    try:
        print(request.get_json())
        email = request.get_json().get("email", None)
        executor = concurrent.futures.ThreadPoolExecutor()
        future = executor.submit(
            AsyncDataBaseManager.delete_user,
            email
        )
        result = future.result()

        return make_response(jsonify(msg="Operation Succeded"), 200)
    except Exception as e:
        return make_response(jsonify(msg=str(e)), 500)
