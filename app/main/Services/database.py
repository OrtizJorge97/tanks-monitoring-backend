# from backend.app.main import session
from .. import session
from ..models import *
from app.main import engine

from sqlalchemy.sql import text

class AsyncDataBaseManager:
    db_session = session

    def join_user_company_by_email(email):
        user_db = AsyncDataBaseManager.db_session.query(Users.name, Users.last_name, Users.password, Companies.company, Users.email, Users.role, Users.user_verified).select_from(Users)\
            .join(Companies, Companies.id == Users.company_id)\
            .filter(Users.email == email)\
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
        tank_db = AsyncDataBaseManager.db_session.query(Tanks).filter_by(
            tank_name=tankNewParameters["tankId"]).first()
        parameters_db = AsyncDataBaseManager.db_session.query(
            Measures_Categories).filter_by(tank_id=tank_db.id).all()
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
        # GET TANK OBJECT FILTERED
        tank_db = AsyncDataBaseManager.db_session.query(
            Tanks).filter_by(tank_name=tankId).first()

        # DELETE EVERYTHING IN MEASURE_CATEGORIES WHERE ID CORRESPONDS TO TANK_ID OBJECT
        AsyncDataBaseManager.db_session.query(
            Measures_Categories).filter_by(tank_id=tank_db.id).delete()

        # delete tank itself in tanks table.
        AsyncDataBaseManager.db_session.delete(tank_db)

        # COMMIT SESSION
        AsyncDataBaseManager.db_session.commit()

    def get_tank_company(tanksData):
        company = None
        tanks_name = tanksData.get('id')

        for tank_name in tanks_name:
            tank_exists, tank_name_db = (AsyncDataBaseManager.db_session.query(Tanks).filter_by(tank_name=tank_name).first(
            ) != None), AsyncDataBaseManager.db_session.query(Tanks).filter_by(tank_name=tank_name).first()
            print("-----DEBUGGING TANKS--------")
            print(
                f"tank name: {tank_name}, tank name from db: {tank_name_db}, tank exists?: {tank_exists}")

            if tank_exists:
                result_db = AsyncDataBaseManager.db_session.query(Tanks.tank_name, Companies.company)\
                    .select_from(Tanks)\
                    .join(Companies, Tanks.company_id == Companies.id)\
                    .filter(Tanks.tank_name == tank_name_db.tank_name)\
                    .first()
                company = result_db[1]

                break

        return company

    def get_company_tanks(company):
        company_tanks_db = AsyncDataBaseManager.db_session.query(Tanks.tank_name)\
            .select_from(Tanks)\
            .join(Companies, Tanks.company_id == Companies.id)\
            .filter(Companies.company == company)\
            .all()
        company_tanks = [tank_tuple[0] for tank_tuple in company_tanks_db]
        return company_tanks

    def get_tanks_parameters(company):
        tanks_parameters_db = AsyncDataBaseManager.db_session.query(Tanks.tank_name, Measures_Categories.measure_type, Measures_Categories.tank_min_value, Measures_Categories.tank_max_value)\
            .select_from(Tanks)\
            .join(Companies, Tanks.company_id == Companies.id)\
            .join(Measures_Categories, Measures_Categories.tank_id == Tanks.id)\
            .filter(Companies.company == company)\
            .all()
        return tanks_parameters_db

    def get_users(company):
        users_db = AsyncDataBaseManager.db_session.query(
            Users.name,
            Users.last_name,
            Users.email,
            Users.role
        ).select_from(Users).join(
            Companies, Companies.id == Users.company_id
        ).filter(
            Companies.company == company
        ).all()

        return [{
            'name': user_tuple[0],
            'lastName': user_tuple[1],
            'email': user_tuple[2],
            'role': user_tuple[3],
        } for user_tuple in users_db]

        print("------PRINTING USERS DB LIST--------")
        print(users_db_list)

    def get_user(email):
        user_db = AsyncDataBaseManager.db_session.query(
            Users).filter_by(email=email).first()
        return {
            "id": user_db.id,
            "name": user_db.name,
            "lastName": user_db.last_name,
            "email": user_db.email,
            "role": user_db.role
        }

    def update_user_by_id(new_user):
        # AsyncDataBaseManager.db_session.flush()
        print("-----new user---------")
        print(new_user)
        # CHECK THIShttps://www.kite.com/python/answers/how-to-update-existing-table-rows-in-sqlalchemy-in-python
        # TO UPDATE ROW DATA
        # user_db = AsyncDataBaseManager.db_session.query(Users)\
        #          .where(id=new_user["id"]).first()
        users_db = AsyncDataBaseManager.db_session.query(
            Users).filter_by(id=new_user["id"]).all()
        for user_db in users_db:
            print(user_db)
            print("-----PRINTING UPDATED USER---------")
            user_db.name = new_user['name']
            user_db.last_name = new_user['lastName']
            user_db.email = new_user['email']
            user_db.role = new_user['role']
            AsyncDataBaseManager.db_session.commit()

        updated_user_db = AsyncDataBaseManager.db_session.query(
            Users).filter_by(id=new_user["id"]).all()
        return {
            "id": updated_user_db[0].id,
            "name": updated_user_db[0].name,
            "lastName": updated_user_db[0].last_name,
            "email": updated_user_db[0].email,
            "role": updated_user_db[0].role
        }

    def delete_user(email):
        user_db = AsyncDataBaseManager.db_session.query(
            Users).filter_by(email=email).first()

        # delete tank itself in tanks table.
        AsyncDataBaseManager.db_session.delete(user_db)

        # COMMIT SESSION
        AsyncDataBaseManager.db_session.commit()

    def store_measurements(payload):
        # Get id of categories
        print("-------PRINTING TANKS ID---------")
        print(payload['id'])
        print(payload['WtrLvl'])
        print(payload['OxygenPercentage'])
        print(payload['Ph'])
        print(payload['timestamp'])

        tanks_id = payload['id']
        for tank_id_name in tanks_id:
            results = AsyncDataBaseManager.db_session.query(
                    Tanks.id, 
                    Measures_Categories.id,
                    Measures_Categories.measure_type
                )\
                .select_from(Tanks)\
                .join(Measures_Categories, Tanks.id == Measures_Categories.tank_id)\
                .filter(Tanks.tank_name == tank_id_name)\
                .all() #this returns [(1, 1, 'MT001', 'WtrLvl', 5.0, 200.0)]
            for tank_id, meas_cat_id, measure_type in results:
                measurement = Measurements(
                    value = float(payload[measure_type][payload['id'].index(tank_id_name)]),
                    timestamp = payload['timestamp'][payload['id'].index(tank_id_name)],
                    tank_id = tank_id,
                    measures_categories_id = meas_cat_id
                )

                AsyncDataBaseManager.db_session.add(measurement)
        try:
            print("COMMITED!")
            AsyncDataBaseManager.db_session.commit()
        except:
            print("ROLLBACK!")
            AsyncDataBaseManager.db_session.rollback()

    def get_historic(company):
        query = '''select t.tank_name, meas_cat.measure_type, meas_cat.tank_min_value, meas_cat.tank_max_value, meas.value, meas.timestamp from companies c 
        join tanks t on c.id = t.company_id
        join measurements meas on t.id = meas.tank_id
        join measures_categories meas_cat on meas_cat.id = meas.measures_categories_id
        where c.company = '{company}';'''.format(
            company = company
        )
        results_db = []
        with engine.connect() as con:
            results = con.execute(text(query))
            #print(con.columns)
            results_db = [dict(zip(row.keys(), row.values())) for row in results]
            print("---------------HISTORICAL DATA-----------------")
            print(results_db)
        
        tanks_name_list = list(set([row['tank_name'] for row in results_db]))
        print("--------PRINTING TANKS-------------")
        print(tanks_name_list)
        
        tanks_data_list = []
        for tank_name in tanks_name_list:
            tank_data = {
                'tank_name': tank_name,
                'WtrLvlValues': [],
                'OxygenPercentageValues': [],
                'PhValues': [],
                'ph_timestamp': [],
                'oxygen_timestamp': [],
                'timestamp': []
            }
            for row in results_db:
                if row['tank_name'] == tank_name:
                    if row['measure_type'] == 'WtrLvl':
                        tank_data['WtrLvlValues'].append(row['value'])
                        tank_data['timestamp'].append(row['timestamp'])
                    elif row['measure_type'] == 'OxygenPercentage':
                        tank_data['OxygenPercentageValues'].append(row['value'])
                        tank_data['oxygen_timestamp'].append(row['timestamp'])
                    elif row['measure_type'] == 'OxygenPercentage':
                        tank_data['OxygenPercentageValues'].append(row['value'])
                        tank_data['oxygen_timestamp'].append(row['timestamp'])
                    elif row['measure_type'] == 'Ph':
                        tank_data['PhValues'].append(row['value'])
                        tank_data['ph_timestamp'].append(row['timestamp'])
                    
            tanks_data_list.append(tank_data)
        
        print("--------------PRINTING LIST TANK DATA---------------")
        print(tanks_data_list)

        return tanks_data_list

    def get_company_staff(company):
        query = '''select email 
                    from users u
                    join companies c on c.id = u.company_id
                    where c.company='{company}' and role in ('Supervisor', 'Administrator');'''.format(
                        company=company
                    )
        email_results = None
        with engine.connect() as con:
            results = con.execute(text(query))
            #print(con.columns)
            email_results = [dict(zip(row.keys(), row.values())) for row in results]
            print("---------------SUPERVISOR AND ADMINISTRATOR EMAILS-----------------")
            print(email_results)

        return email_results

    def get_tanks_parameters_query(company):
        query = '''
        select t.tank_name, meas_cat.measure_type, meas_cat.tank_min_value, meas_cat.tank_max_value
        from tanks t
        join measures_categories meas_cat on t.id = meas_cat.tank_id
        join companies c on t.company_id = c.id
        where c.company = '{company}';'''.format(
            company=company
        )
        tanks_parameters_results = None
        with engine.connect() as con:
            results = con.execute(text(query))
            #print(con.columns)
            tanks_parameters_results = [dict(zip(row.keys(), row.values())) for row in results]
            print("---------------SUPERVISOR AND ADMINISTRATOR EMAILS-----------------")
            print(tanks_parameters_results)
        
        return tanks_parameters_results


"""
class Measurements(Base):
    __tablename__ = "measurements"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
    value = Column(Float, nullable=False)
    timestamp = Column(Integer, nullable=False)
    tank_id = Column(Integer, ForeignKey('tanks.id'))
    measures_categories_id = Column(Integer, ForeignKey('measures_categories.id'))

select t.id as tanks_id, mc.id as meas_cat_id, t.tank_name, mc.measure_type, mc.tank_min_value, mc.tank_min_value 
from tanks t 
join measures_categories mc on t.id = mc.tank_id
where tank_name = 'MT001';
"""


"""
id = Column(Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
    name = Column(String(20))
    last_name = Column(String(50))
    email = Column(String(40), unique=True, nullable=False)
    password = Column(Text)
    user_verified = Column(Boolean())
    role = Column(String(10))


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
