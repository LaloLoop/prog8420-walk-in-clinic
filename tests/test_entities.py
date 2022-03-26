from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from src.repos.entities import Person, Base, Employee

person_data = {
    "first_name": "Marcos",
    "last_name": "Doe",
    "birthdate": "1970-12-03",
    "street": "129 Louisa St",
    "city": "Kitchener",
    "province": "ON",
    "postalcode": "N2H3E7",
    "email": "marcos@conestogac.ca",
    "phone_number": "5195926738"
}


def _create_test_person(engine, session):
    person = Person(**person_data)

    session.add(person)
    session.commit()

    return person


def test_create_person():
    engine = create_engine('sqlite:///:memory:', echo=True)
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    person = _create_test_person(engine, session)

    # Check the person was inserted
    result = session.query(Person).first()

    assert result.id == 1
    for k, v in person_data.items():
        assert result.__dict__.get(k) == v


def test_create_employee():
    engine = create_engine('sqlite:///:memory:', echo=True)
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    person = _create_test_person(engine, session)
    employee = Employee(password="super-secret")

    employee.person = person

    Session = sessionmaker(bind=engine)
    session = Session()

    session.add(employee)
    session.commit()

    # Check the person was inserted
    result = session.query(Employee).first()

    assert result.id == 1
    assert result.person_id == 1
    assert result.password == "super-secret"

def test_create_job():
    pass