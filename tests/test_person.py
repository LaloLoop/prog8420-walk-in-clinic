from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.repos.person import Person, PersonRepository


def test_create_table():
    engine = create_engine('sqlite:///:memory:', echo=True)

    person_repository = PersonRepository(engine)
    person_repository.init_db()


def test_create_person():
    engine = create_engine('sqlite:///:memory:', echo=True)

    data = {
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

    person = Person(**data)

    repo = PersonRepository(engine)

    repo.init_db()
    created = repo.create(person)

    assert created == True

    Session = sessionmaker(bind=engine)
    session = Session()
    result = session.query(Person).first()

    assert result.id == 1
    for k, v in data.items():
        assert result.__dict__.get(k) == v
