from dataclasses import dataclass

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

Base = declarative_base()


class Person(Base):
    __tablename__ = 'Person'

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String)
    last_name = Column(String)
    birthdate = Column(String)
    street = Column(String)
    city = Column(String)
    province = Column(String)
    postalcode = Column(String)
    email = Column(String)
    phone_number = Column(String)

    employee = relationship("Employee", back_populates="person")


class Employee(Base):
    __tablename__ = 'Employee'

    id = Column(Integer, primary_key=True, autoincrement=True)
    person_id = Column(Integer, ForeignKey('Person.id'))
    password = Column(String)

    person = relationship("Person")

