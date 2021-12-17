from flask import Flask, json, request, jsonify, make_response
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt
from flask_jwt_extended import create_refresh_token
import bcrypt

import time
from datetime import timedelta

from . import auth_blueprint, session
from .models import *
from .utilities.constants import *

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
        if user_db:
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
        return make_response(jsonify({"msg": "Succesfully added user"}), 200)

    except Exception as e:
        return make_response(jsonify({"msg": str(e)}), 500)


"""
id = Column(Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
    name = Column(String(20))
    last_name = Column(String(50))
    email = Column(String(40), unique=True, nullable=False)
    password = Column(Text)
    user_verified = Column(Boolean())
    role = Column(String(10))
    company_id = Column(Integer, ForeignKey('companies.id'))
    sessions = relationship('Sessions')

class Companies(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
    company = Column(String(30), nullable=False)
    address = Column(Text)
    users = relationship('Users')
    """


# Create a route to authenticate your users and return JWTs. The
# create_access_token() function is used to actually generate the JWT.
@auth_blueprint.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    print(request.get_json())
    user_db = session.query(Users.name, Users.last_name, Users.password, Companies.company, Users.email, Users.role).select_from(Users)\
                                  .join(Companies, Companies.id == Users.company_id)\
                                  .filter(Users.email==email)\
                                  .first()
    print("user db weee")
    print(user_db)
    #mail not found, meaning user does not exist
    if not user_db:
        return make_response(jsonify({"message": "User not found"}), 404)

    #password incorrect, notify user.
    if not bcrypt.checkpw(password.encode("utf-8"), user_db[2].encode("utf-8")):
        return make_response(jsonify({"message": "Password incorect"}), 200)

    user_claims = {
        "name": user_db[0], 
        "last_name": user_db[1], 
        "company": user_db[3],
        "email": user_db[4],
        "role": user_db[5]
    }
    access_token = create_access_token(identity=email, additional_claims=user_claims)
    refresh_token = create_refresh_token(identity=email, additional_claims=user_claims)
    return make_response(jsonify(message="Succesfully authenticated",
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