CREATE TABLE Person (
    -- Personal info
    ID INTEGER NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    -- Dates can be stored TEXT
    -- https://stackoverflow.com/a/13712078/3211335
    birthdate INTEGER NOT NULL,
    -- Address
    street TEXT NOT NULL,
    city TEXT NOT NULL,
    province TEXT NOT NULL,
    postalcode TEXT NOT NULL,
    -- Contact information
    email TEXT NOT NULL,
    phone_number TEXT,

    CONSTRAINT PK_Person PRIMARY KEY(ID)
);

CREATE TABLE User (
    ID INTEGER PRIMARY KEY,
    person_id INTEGER NOT NULL,
    password TEXT,

    CONSTRAINT PK_Users PRIMARY KEY (ID)
);

CREATE TABLE Patients (
    ID INTEGER PRIMARY KEY,
    username TEXT
)