from sqlalchemy import create_engine
from sqlalchemy.engine.mock import MockConnection
from sqlalchemy.orm import sessionmaker, Session

from src.repos.entities import Base, Person, Employee, Job


class Controller:
    def __init__(self, engine: MockConnection):
        self.engine = engine
        self.session = sessionmaker(bind=engine)()

    def _init_admin(self):
        person = Person(first_name="John", last_name="Doe", email="admin@wic.com")
        job = Job(title="admin")
        admin = Employee(password="pr0g4dmin", person=person, job=job)

        self.session.add(admin)
        self.session.commit()

    def init_db(self):
        Base.metadata.create_all(self.engine)

        self._init_admin()

