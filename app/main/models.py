from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()

class Users(Base): #child table of companies
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
    name = Column(String(20))
    last_name = Column(String(50))
    email = Column(String(40), unique=True, nullable=False)
    password = Column(Text)
    user_verified = Column(Boolean())
    role = Column(String(10))
    company_id = Column(Integer, ForeignKey('companies.id'))
    sessions = relationship('Sessions')

class Sessions(Base): #child table of users
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
    session_identifier = Column(Text)
    user_id = Column(Integer, ForeignKey('users.id'))

class Companies(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
    company = Column(String(30), nullable=False)
    address = Column(Text)
    users = relationship('Users')