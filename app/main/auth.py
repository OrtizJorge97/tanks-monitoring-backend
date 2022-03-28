from flask import Flask, json, request, jsonify, make_response, url_for, render_template
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt
from flask_jwt_extended import create_refresh_token
import bcrypt
import concurrent.futures

import time
from datetime import timedelta

from .. import ts, email_salt, host_url, front_url
from . import auth_blueprint, session
from .models import *
from .utilities.constants import *
from .Services.database import AsyncDataBaseManager
from .Services.notifications import send_email

# Create a route to authenticate your users and return JWTs. The
# create_access_token() function is used to actually generate the JWT.
@auth_blueprint.route("/add-user", methods=["POST"])
def add_user():
    try:
        user = request.get_json()
        name = user["name"]
        last_name = user["lastName"]
        email = user["email"]
        password = user["password"]
        company = user["company"]
        role = roles["Supervisor"]

        #If company does not exist, then add it
        company_db = session.query(Companies).filter_by(company=company).first()
        if not company_db:
            print("company added")
            session.add(Companies(company=company,
                                address=""))
            session.commit()
        
        #add the user getting the id of company for relationships
        company_db = session.query(Companies).filter_by(company=company).first()
        user_db = session.query(Users).filter_by(email=email).first()
        print("PRINTING USER DB")
        print(user_db)
        if user_db:
            print(f"returned user_db {user_db.email}")
            return make_response(jsonify({"msg": "User already registered"}), 200)

        user_db_supervisor = session.query(Users).select_from(Users)\
                                    .join(Companies, Companies.id == Users.company_id)\
                                    .filter(Companies.company==company, Users.role==roles["Supervisor"])\
                                    .first()

        if user_db_supervisor:
            role = roles["Operator"]
       
        session.add(Users(name= name,
                          last_name = last_name,
                          email = email,
                          password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=8)),
                          user_verified = False,
                          role = role,
                          company_id = company_db.id))
        session.commit()
        token = ts.dumps(email, salt=email_salt)
        print("----------PRINTING URL FOR CONFIRMATION ACCOUNT------------")
        print(url_for('auth.confirm_account', token=token))
        activation_url = host_url + url_for('auth.confirm_account', token=token)
        executor = concurrent.futures.ThreadPoolExecutor()
        future = executor.submit(send_email, email, "Tanks Platform confirm email", f"Please click in this link {activation_url} to activate your account")
        future.result()
        return make_response(jsonify({"msg": "Succesfully added user"}), 200)

    except Exception as e:
        print(str(e))
        return make_response(jsonify({"msg": str(e)}), 500)


@auth_blueprint.route("/resend-confirmation-email", methods=['POST'])
def resend_confirmation_email():
    try:
        bodyJson = request.get_json()
        email = bodyJson['email']

        print(email)
        token = ts.dumps(email, salt=email_salt)
        print("----------PRINTING URL FOR CONFIRMATION ACCOUNT------------")
        print(url_for('auth.confirm_account', token=token))
        activation_url = host_url + url_for('auth.confirm_account', token=token)
        executor = concurrent.futures.ThreadPoolExecutor()
        future = executor.submit(send_email, email, "Tanks Platform confirm email", f"Please click in this link {activation_url} to activate your account")
        future.result()
        return make_response(jsonify({"msg": "Confirmation email successfully resent"}), 200)
    except Exception as e:
        print(str(e))
        return make_response(jsonify({"msg": str(e)}), 500)


@auth_blueprint.route("/confirm-account/<token>")
def confirm_account(token):

    status_message = 'Success Activating account :)'
    try:
        email = ts.loads(token, salt=email_salt, max_age=86400)
        print(email)
    except:
        status_message = 'Invalid token!'
        return render_template('activation_status.html', account_status_message = status_message, front_url = front_url + '/log-in')
    
    try:
        user_db = session.query(Users).filter_by(email=email).first()
        if not user_db.user_verified:
            user_db.user_verified = True
            AsyncDataBaseManager.db_session.add(user_db)
            AsyncDataBaseManager.db_session.commit()
            return render_template('activation_status.html', account_status_message = status_message, front_url = front_url + '/log-in')
        status_message = "Account already activated :)"
        return render_template('activation_status.html', account_status_message = status_message, front_url = front_url + '/log-in')
    except Exception as e:
        print(str(e))
        return make_response(jsonify({"msg": str(e)}), 500)

# Create a route to authenticate your users and return JWTs. The
# create_access_token() function is used to actually generate the JWT.
@auth_blueprint.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)

    executor = concurrent.futures.ThreadPoolExecutor()
    future = executor.submit(AsyncDataBaseManager.join_user_company_by_email, email)
    user_db = future.result()

    print("user db weee")
    print(user_db)
    #mail not found, meaning user does not exist
    if not user_db:
        return make_response(jsonify({"msg": "User not found"}), 404)

    if not user_db[6]:
        return make_response(jsonify({"msg": "Account has not been activated, please check your email for confirming your account."}), 404)

    #password incorrect, notify user.
    if not bcrypt.checkpw(password.encode("utf-8"), user_db[2].encode("utf-8")):
        return make_response(jsonify({"msg": "Password incorrect"}), 200)

    user_claims = {
        "name": user_db[0], 
        "last_name": user_db[1], 
        "company": user_db[3],
        "email": user_db[4],
        "role": user_db[5]
    }
    access_token = create_access_token(identity=email, additional_claims=user_claims)
    refresh_token = create_refresh_token(identity=email, additional_claims=user_claims)
    return make_response(jsonify(msg="Succesfully authenticated",
                                 access_token=access_token, 
                                 refresh_token=refresh_token,
                                 user=user_claims), 200)


@auth_blueprint.route("/get-user", methods=["GET"])
@jwt_required()
def get_user():
    claims = get_jwt()
    print(claims["email"])
    return make_response(jsonify(msg="Succesfully authenticated",
                                 name=claims["name"],
                                 last_name=claims["last_name"],
                                 company=claims["company"],
                                 email=claims["email"],
                                 role=claims["role"]), 200)

# In a protected view, get the claims you added to the jwt with the
# get_jwt() method
@auth_blueprint.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    claims = get_jwt()
    return jsonify(user=claims["user"])

# We are using the `refresh=True` options in jwt_required to only allow
# refresh tokens to access this route.
@auth_blueprint.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    user = get_jwt_identity()
    print(user)
    user_claims = {"user": user}
    access_token = create_access_token(identity=user, additional_claims=user_claims)
    return jsonify(access_token=access_token)