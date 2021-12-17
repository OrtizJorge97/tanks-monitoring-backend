from flask import Blueprint
from flask_cors import CORS
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base

main = Blueprint('main', __name__)
CORS(main, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

#ADD HERE DIFFERENTS BLUEPRINTS SO WE CAN MAKE THIS MODULAR - NOT TESTED YET
api_blueprint = Blueprint('api', __name__, url_prefix="/api")
CORS(api_blueprint, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

auth_blueprint = Blueprint('auth', __name__, url_prefix="/auth")
CORS(auth_blueprint, resources={r"/auth/*": {"origins": "*"}}, supports_credentials=True)

print("1")
engine = create_engine('mysql://flask:flask_password@localhost/tanks_db', echo=True)
Session = sessionmaker(engine)
session = Session()
print("2")
Base.metadata.create_all(engine)
print("tables created!")

from . import api, socket, auth