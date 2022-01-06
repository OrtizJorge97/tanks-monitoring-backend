#from backend.app.main import session
from .. import session
from ..models import *

class AsyncDataBaseManager:
    db_session = session

    def join_user_company_by_email(email):
        user_db = AsyncDataBaseManager.db_session.query(Users.name, Users.last_name, Users.password, Companies.company, Users.email, Users.role).select_from(Users)\
                                            .join(Companies, Companies.id == Users.company_id)\
                                            .filter(Users.email==email)\
                                            .first()
        return user_db

    def get_tank_parameters(tankId):
        tank_parameter_db = AsyncDataBaseManager.db_session.query(Tanks.tank_name, Measures_Categories.measure_type, Measures_Categories.tank_min_value, Measures_Categories.tank_max_value)\
                                            .select_from(Tanks)\
                                            .join(Measures_Categories, Tanks.id == Measures_Categories.tank_id, isouter=True)\
                                            .filter(Tanks.tank_name == tankId)\
                                            .all()
        print("-------------TANK PARAMETERS------------------")
        print(tank_parameter_db)
        return tank_parameter_db

    def update_tank_parameters(tankNewParameters):
        tank_db = AsyncDataBaseManager.db_session.query(Tanks).filter_by(tank_name=tankNewParameters["tankId"]).first()
        parameters_db = AsyncDataBaseManager.db_session.query(Measures_Categories).filter_by(tank_id=tank_db.id).all()
        for parameter in parameters_db:
            if parameter.measure_type == 'WtrLvl':
                parameter.tank_min_value = tankNewParameters["WtrLvlMin"]
                parameter.tank_max_value = tankNewParameters["WtrLvlMax"]
            if parameter.measure_type == 'OxygenPercentage':
                parameter.tank_min_value = tankNewParameters["OxygenPercentageMin"]
                parameter.tank_max_value = tankNewParameters["OxygenPercentageMax"]
            if parameter.measure_type == 'Ph':
                parameter.tank_min_value = tankNewParameters["PhMin"]
                parameter.tank_max_value = tankNewParameters["PhMax"]
            
            AsyncDataBaseManager.db_session.commit()
        
        print("------------SUCCESS UPDATING!-----------")

    def delete_tank(tankId):
        #GET TANK OBJECT FILTERED
        tank_db = AsyncDataBaseManager.db_session.query(Tanks).filter_by(tank_name=tankId).first()

        #DELETE EVERYTHING IN MEASURE_CATEGORIES WHERE ID CORRESPONDS TO TANK_ID OBJECT
        AsyncDataBaseManager.db_session.query(Measures_Categories).filter_by(tank_id=tank_db.id).delete()

        #delete tank itself in tanks table.
        AsyncDataBaseManager.db_session.delete(tank_db)

        #COMMIT SESSION
        AsyncDataBaseManager.db_session.commit()

        



"""
class Tanks(Base): #child from companies
    __tablename__ = "tanks"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
    tank_name = Column(String(30), nullable=False)
    company_id = Column(Integer, ForeignKey('companies.id'))
    tanks = relationship('Measures_Categories')

class Measures_Categories(Base): #child from tanks
    __tablename__ = "measures_categories"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
    measure_type = Column(String(30), nullable=False)
    tank_min_value = Column(Float, nullable=False)
    tank_max_value = Column(Float, nullable=False)
    tank_id = Column(Integer, ForeignKey('tanks.id'))
"""