from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from src.repos.entities import Person, Base, Employee, Job, Patient, Appointment, Unit, Prescription

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

staff_data = {
    "first_name": "Sarah",
    "last_name": "Williams",
    "birthdate": "1983-10-01",
    "street": "101 Charles St",
    "city": "Kitchener",
    "province": "ON",
    "postalcode": "N2HN2P",
    "email": "sarah@conestogac.ca",
    "phone_number": "5198920923"
}

patient_data = {
    "first_name": "Elon",
    "last_name": "Musk",
    "birthdate": "1979-09-10",
    "street": "12 El Paso",
    "city": "Waterloo",
    "province": "ON",
    "postalcode": "N2HNT7",
    "email": "elon@conestogac.ca",
    "phone_number": "5196738983"
}

appointment_data = {
    'date': datetime.fromisoformat('2022-04-22 10:10:10'),
    'comments': 'Patient is healthy!'
}

job_dr_data = {
    'title': 'Doctor',
    'speciality': 'Neurologist'
}

job_staff_data = {
    'title': 'Secretary',
    'speciality': ''
}

advil_data = {
    'medication': 'Advil',
    'quantity': 12
}


def _create_test_person(session, data=None):
    if data is None:
        data = person_data

    person = Person(**data)

    session.add(person)
    session.commit()

    return person


def _create_test_employee(session, person, job):
    employee = Employee(password="super-secret")
    employee.person = person
    employee.job = job

    session.add(employee)
    session.commit()

    return employee


def _create_test_patient(session, person):
    patient = Patient(ohip="3873933093")
    patient.person = person

    session.add(patient)
    session.commit()

    return patient


def _create_test_job(session, job_data=None):
    if job_data is None:
        job_data = job_dr_data

    job = Job(**job_data)

    session.add(job)
    session.commit()

    return job


def _create_test_unit(session, name):
    unit = Unit(name=name)

    session.add(unit)
    session.commit()

    return unit


def _create_test_prescription(session, unit, prescription_data):
    prescription = Prescription(**prescription_data)

    prescription.unit = unit

    session.add(prescription)
    session.commit()

    return prescription


def _create_test_appointment(session, staff: Employee, patient: Patient, employee: Employee, prescription: Prescription,
                             appointment_data: dict) -> Appointment:
    appointment = Appointment(**appointment_data)
    appointment.staff = staff
    appointment.patient = patient
    appointment.doctor = employee
    appointment.prescription = prescription

    session.add(appointment)
    session.commit()

    return appointment


def test_create_person(session):

    _create_test_person(session)

    # Check the person was inserted
    result = session.query(Person).first()

    assert result.id == 1
    for k, v in person_data.items():
        assert result.__dict__.get(k) == v


def test_create_job(session):

    _create_test_job(session)

    result = session.query(Job).first()

    assert result.id == 1
    assert result.title == "Doctor"
    assert result.speciality == "Neurologist"


def test_create_employee(session):

    person = _create_test_person(session)
    job = _create_test_job(session)
    _create_test_employee(session, person, job)

    # Check the person was inserted
    result = session.query(Employee).first()

    assert result.id == 1
    assert result.person_id == 1
    assert result.password == "super-secret"
    assert result.job.id == job.id
    assert result.job.title == job.title
    assert result.job.speciality == job.speciality


def test_create_patient(session):

    person = _create_test_person(session)
    _create_test_patient(session, person)

    result = session.query(Patient).first()

    assert person.id == 1
    assert result.ohip == "3873933093"
    assert result.person.id == person.id
    assert result.person.first_name == person.first_name


def test_create_prescription(session):

    unit = _create_test_unit(session, "mg")

    _create_test_prescription(session, unit, advil_data)

    result = session.query(Prescription).first()

    assert result.id == 1
    assert result.medication == "Advil"
    assert result.quantity == 12
    assert result.unit.id == unit.id


def test_create_appointment(session):

    person = _create_test_person(session)
    job = _create_test_job(session)
    doctor = _create_test_employee(session, person, job)

    unit = _create_test_unit(session, "mg")
    prescription = _create_test_prescription(session, unit, advil_data)

    staff = _create_test_employee(
        session,
        _create_test_person(session, staff_data),
        _create_test_job(session, job_staff_data)
    )

    patient = _create_test_patient(
        session,
        _create_test_person(session, patient_data)
    )

    _create_test_appointment(session, staff, patient, doctor, prescription, appointment_data)

    result = session.query(Appointment).first()

    assert result.id == 1
    assert result.patient.id == patient.id
    assert result.doctor.id == doctor.id
    assert result.staff.id == staff.id
    assert result.date == appointment_data['date']
    assert result.prescription.id == prescription.id


def test_create_unit(session):

    _create_test_unit(session, "mg")

    result = session.query(Unit).first()

    assert result.id == 1
    assert result.name == "mg"
