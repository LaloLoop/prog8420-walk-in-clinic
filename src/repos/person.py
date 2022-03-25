from dataclasses import dataclass

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

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


class PersonRepository:

    def __init__(self, engine):
        self.engine = engine

    def init_db(self):
        Base.metadata.create_all(self.engine)

    def create(self, person):
        Session = sessionmaker(bind=self.engine)
        session = Session()

        session.add(person)
        session.commit()

        return True
