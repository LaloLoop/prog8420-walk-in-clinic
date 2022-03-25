from dataclasses import dataclass


@dataclass
class Person:
    id: int
    first_name: str
    last_name: str
    birthdate: str
    street: str
    city: str
    province: str
    postalcode: str
    email: str
    phone_number: str


class PersonRepository:

    def __init__(self, db):
        self.db = db

    def init_db(self, db=None):
        if db is None:
            db=self.db

        cur = db.cursor()

        cur.execute('''CREATE TABLE IF NOT EXISTS Person (
                                   ID INTEGER PRIMARY KEY,
                                   first_name TEXT,
                                   last_name TEXT,
                                   birthdate TEXT,
                                   street TEXT,
                                   city TEXT,
                                   province TEXT,
                                   postalcode TEXT,
                                   email TEXT,
                                   phone_number TEXT
                                   )''')

        db.commit()

        db.close()

    def create(self, person):
        cur = self.db.cursor()

        cur.execute(
            '''INSERT INTO Person("first_name", 
            "last_name",
            "birthdate",
            "street",
            "city",
            "province",
            "postalcode",
            "email",
            "phone_number"
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                person.first_name,
                person.last_name,
                person.birthdate,
                person.street,
                person.city,
                person.province,
                person.postalcode,
                person.email,
                person.phone_number
            )
        )

        inserted = cur.rowcount > 0

        self.db.commit()
        self.db.close()

        return inserted
