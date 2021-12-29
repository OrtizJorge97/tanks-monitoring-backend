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
from .utilities import constants

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

#DATA TO RECEIVE FROM TANKS AND TO SAVE IT INTO HISTORIC DATA
@api_blueprint.route("/post-data", methods=["POST"])
def post_data():
    payload = request.get_json()
    print(payload)
    socketio.emit('tanks_data', payload, namespace='/private', to=payload["company"])
    return make_response(jsonify(msg="Success"), 200)

@api_blueprint.route("/fetch-tanks", methods=["GET"])
@jwt_required()
def fetch_tanks():
    claims = get_jwt()
    company = session.query(Companies).filter_by(company=claims["company"]).first()
    print("ID OF COMPANY: " + str(company.id))
    tanks_company_db = session.query(Tanks.tank_name, Companies.company).select_from(Tanks)\
                                .join(Companies, Tanks.company_id == Companies.id)\
                                .filter(Companies.id==company.id).all()

    constants.tanks_company["tanks"] = []
    print("------------------------RESULTS OF JOIN QUERY---------------------------")
    for tank_company in tanks_company_db:
        constants.tanks_company["tanks"].append(tank_company[0])

    print(constants.tanks_company["tanks"])
    return make_response(jsonify(msg="Success fetching", tanks=constants.tanks_company["tanks"]), 200)

"""
user_db_supervisor = session.query(Users).select_from(Users)\
                                    .join(Companies, Companies.id == Users.company_id)\
                                    .filter(Companies.company==company, Users.role==roles["Supervisor"])\
                                    .first()"""
@api_blueprint.route("/add-tank", methods=["POST"])
@jwt_required()
def add_tank():
    try:
        tank = request.get_json()
        print(tank)
        company = session.query(Companies).filter_by(company=tank['company']).first()
        tank_db = session.query(Tanks).filter_by(tank_name=tank['tankId']).first()
        
        if tank_db:
            return make_response(jsonify(msg="Tank already added, please modify or delete."), 200)

        session.add(Tanks(tank_name=tank['tankId'],
                        company_id=company.id))
        session.commit()

        tank_db = session.query(Tanks).filter_by(tank_name=tank['tankId']).first()
        session.add(Measures_Categories(measure_type="WtrLvl",
                                        tank_min_value=tank['WtrLvlMin'],
                                        tank_max_value=tank['WtrLvlMax'], 
                                        tank_id = tank_db.id))
        session.add(Measures_Categories(measure_type="OxygenPercentage",
                                        tank_min_value=tank['OxygenPercentageMin'],
                                        tank_max_value=tank['OxygenPercentageMax'], 
                                        tank_id = tank_db.id))
        session.add(Measures_Categories(measure_type="Ph",
                                        tank_min_value=tank['PhMin'],
                                        tank_max_value=tank['PhMax'], 
                                        tank_id = tank_db.id))
        session.commit()

        return make_response(jsonify(msg="Success adding"), 200)

    except Exception as e:
        return make_response(jsonify(msg=str(e)), 500)


"""
class Measures_Categories(Base): #child from tanks
    __tablename__ = "measures_categories"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
    measure_type = Column(String(30), nullable=False)
    tank_min_value = Column(Float, nullable=False)
    tank_max_value = Column(Float, nullable=False)
    tank_id = Column(Integer, ForeignKey('tanks.id'))
"""

"""
tank_name = Column(String(30), nullable=False)
    company_id = Column(Integer, ForeignKey('companies.id'))"""

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