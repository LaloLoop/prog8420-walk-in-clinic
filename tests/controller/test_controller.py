import unittest.mock

from sqlalchemy.engine.mock import MockConnection
from sqlalchemy.orm import Session, sessionmaker

from src.controller.controller import Controller
from src.repos.entities import Employee, Person, Job


def test_init_db(engine: MockConnection):
    controller = Controller(engine)
    session = sessionmaker(bind=engine)()

    controller.init_db()

    default_username = "admin@wic.com"
    default_job_title = "admin"
    default_password = "pr0g4dmin"

    admin = session.query(Employee).join(Person).join(Job).\
        filter(Person.email == default_username).\
        filter(Employee.password == default_password).\
        filter(Job.title == default_job_title).first()

    assert admin.person.email == default_username
    assert admin.job.title == default_job_title
    assert admin.password == default_password
