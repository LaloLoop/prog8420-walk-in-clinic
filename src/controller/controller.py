from sqlalchemy.engine.mock import MockConnection
from sqlalchemy.orm import sessionmaker

from src.repos.entities import Base, Person, Employee, Job
from src.repos.seed_db import seed_db 

class Controller:
    def __init__(self, engine: MockConnection):
        self.user_session = None
        self.engine = engine
        self.session = sessionmaker(bind=engine)()

    def _init_admin(self):
        role = self.session.query(Job).filter(Job.title == "admin").first()
        if role is None:
            person = Person(first_name="John", last_name="Doe", email="admin@wic.com")
            job = Job(title="admin")
            admin = Employee(password="pr0g4dmin", person=person, job=job)

            self.session.add(admin)
            self.session.commit()

    def init_db(self):
        
        Base.metadata.create_all(self.engine)

        seed_db(session=self.session)

        # self._init_admin()

    def login(self, login_data: dict):
        employee = self.session.query(Employee).join(Person).join(Job). \
            filter(Person.email == login_data['username']). \
            filter(Employee.password == login_data['password']).first()
        
        success = employee is not None
        if success:
            self.user_session = employee
        
        return success

    def logout(self):
        self.user_session = None