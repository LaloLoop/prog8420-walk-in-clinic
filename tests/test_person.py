import sqlite3

from src.repos.person import Person, PersonRepository


def test_create_table():
    db_dep = sqlite3.connect("file:mem1?mode=memory&cache=shared", uri=True)
    db_test = sqlite3.connect("file:mem1?mode=memory&cache=shared", uri=True)

    person_repository = PersonRepository(db_dep)
    person_repository.init_db()

    cur = db_test.cursor()
    cur.execute("SELECT sql FROM sqlite_schema WHERE name='Person'")
    r = cur.fetchone()

    assert r is not None


def test_create_person():
    db = sqlite3.connect("file:mem1?mode=memory&cache=shared", uri=True)
    db_create = sqlite3.connect("file:mem1?mode=memory&cache=shared", uri=True)
    db_test = sqlite3.connect("file:mem1?mode=memory&cache=shared", uri=True)

    first_name = "Marcos"
    last_name = "Doe"
    birthdate = "1970-12-03"
    street = "129 Louisa St"
    city = "Kitchener"
    province = "ON"
    postalcode = "N2H3E7"
    email = "marcos@conestogac.ca"
    phone_number = "5195926738"

    person = Person(
        1,
        first_name,
        last_name,
        birthdate,
        street,
        city,
        province,
        postalcode,
        email,
        phone_number
    )

    repo = PersonRepository(db)

    repo.init_db(db_create)
    created = repo.create(person)

    assert created == True

    cur = db_test.cursor()
    cur.execute("SELECT * FROM Person WHERE first_name=? AND last_name = ?", (first_name, last_name))
    r = cur.fetchone()

    assert r is not None
