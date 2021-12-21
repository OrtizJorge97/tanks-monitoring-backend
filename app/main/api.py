from flask import Flask, request, Blueprint, jsonify, make_response
from flask_cors import CORS
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt
from flask_socketio import emit

#from . import main
from . import api_blueprint, session
from .models import *
from .. import socketio

@api_blueprint.route("/", methods=["GET"])
def index():
    #print(request.sid)
    return "loooo"

@api_blueprint.route("/add-company", methods=["POST"])
def add_company():
    #print(request.sid)
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
    #print(request.sid)
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

@api_blueprint.route("/post-data", methods=["POST"])
def post_data():
    payload = request.get_json()
    print(payload)
    socketio.emit('tanks_data', payload, namespace='/private', to=payload["company"])
    return make_response(jsonify(msg="Success"), 200)
"""
@main.route("/", methods=["GET"])
def index():
    #print(request.sid)
    return "loooo"

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
    company = Column(Integer, nullable=False)
    address = Column(Text)
    users = relationship('Users')
"""