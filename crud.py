from fastapi import Depends
from fastapi_users_db_sqlalchemy import AsyncSession
from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

import models, schemas
from users import get_async_session

class PersonCRUD:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def read_person_by_email(self, email: str, session: AsyncSession = Depends(get_async_session)):
        result = await self.session.execute(select(models.Person).where(models.Person.email == email))
        return result.scalars().first()

    async def read_persons(self, skip: int = 0, limit: int = 100):
        result = await self.session.execute(select(models.Person).offset(skip).limit(limit))
        
        persons = result.scalars().all()

        return persons

    async def read_person(self, person_id: int):
        result = await self.session.execute(select(models.Person).where(models.Person.id == person_id))

        return result.scalars().first()


    async def create_person(self, person: schemas.PersonCreate):
        db_person = models.Person(**person.dict())

        self.session.add(db_person)
        await self.session.commit()

        return db_person

    async def update_person(self, person_id: int, person: schemas.PersonUpdate):
        p_values = person.dict()
        for k,v in {**p_values}.items():
            if v is None:
                del p_values[k]
        await self.session.execute(update(models.Person).where(models.Person.id == person_id).values(**p_values))
        await self.session.commit()

        return await self.read_person(person_id)

    async def delete_person(self, person_id: int):
        await self.session.execute(delete(models.Person).where(models.Person.id == person_id))
        await self.session.commit()

class EmployeeCRUD:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def read_employees(self, skip: int = 0, limit: int = 100):
        result = await self.session.execute(select(models.Employee).offset(skip).limit(limit))

        return result.scalars().all()

    async def read_employee(self, employee_id: int):
        result = await self.session.execute(select(models.Employee).where(models.Employee.id == employee_id))
        return result.scalars().first()

    async def read_employee_by_person_id(self, person_id: int):
        result = await self.session.execute(select(models.Employee).where(models.Employee.person_id == person_id))
        return result.scalars().first()

    def delete_employee(db: Session, employee_id: int):
        db_employee = read_employee(db, employee_id)
        if db_employee:
            db.delete(db_employee)
            db.commit()
            return db_employee
        return None

class JobCRUD:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def read_jobs(self, skip: int = 0, limit: int = 100):
        result = await self.session.execute(select(models.Job).offset(skip).limit(limit))
        
        return result.scalars().all()

    async def read_job(self, job_id: int):
        result = await self.session.execute(select(models.Job).where(models.Job.id == job_id))

        return result.scalars().first()

    async def create_job(self, job: schemas.JobCreate):
        db_job = models.Job(**job.dict())
        self.session.add(db_job)
        await self.session.commit()

        return db_job

    async def update_job(self, job_id: int, job: schemas.JobUpdate):
        p_values = job.dict()
        for k,v in {**p_values}.items():
            if v is None:
                del p_values[k]
        
        await self.session.execute(update(models.Job).where(models.Job.id == job_id).values(**p_values))
        await self.session.commit()

        return await self.read_job(job_id)

    async def delete_job(self, job_id: int):
        await self.session.execute(delete(models.Job).where(models.Job.id == job_id))
        await self.session.commit()

class PatientCRUD:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def read_patients(self, skip: int = 0, limit: int = 100):
        result = await self.session.execute(select(models.Patient).offset(skip).limit(limit))
        
        return result.scalars().all()

    async def read_patient(self, patient_id: int):
        result = await self.session.execute(select(models.Patient).where(models.Patient.id == patient_id))

        return result.scalars().first()

    async def read_patient_by_person_id(self, person_id: int):
        result = await self.session.execute(select(models.Patient).where(models.Patient.person_id == person_id))

        return result.scalars().first()

    async def create_patient(self, patient: schemas.PatientCreate):
        db_patient = models.Patient(**patient.dict())

        self.session.add(db_patient)
        await self.session.commit()

        return db_patient


    async def update_patient(self, patient_id: int, patient: schemas.PatientUpdate):
        p_values = patient.dict()
        for k,v in {**p_values}.items():
            if v is None:
                del p_values[k]
        await self.session.execute(update(models.Patient).where(models.Patient.id == patient_id).values(**p_values))
        await self.session.commit()

        return await self.read_patient(patient_id)

    async def delete_patient(self, patient_id: int):
        await self.session.execute(delete(models.Patient).where(models.Patient.id == patient_id))
        await self.session.commit()

class UnitCRUD:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def read_units(self, skip: int = 0, limit: int = 100):
        result = await self.session.execute(select(models.Unit).offset(skip).limit(limit))
        
        return result.scalars().all()

    async def read_unit(self, unit_id: int):
        result = await self.session.execute(select(models.Unit).where(models.Unit.id == unit_id))

        return result.scalars().first()

    async def read_unit_by_name(self, name: str):
        result = await self.session.execute(select(models.Unit).where(models.Unit.name == name))

        return result.scalars().first()

    async def create_unit(self, unit: schemas.UnitCreate):
        db_unit = models.Unit(**unit.dict())

        self.session.add(db_unit)
        await self.session.commit()

        return db_unit

    async def update_unit(self, unit_id: int, unit: schemas.UnitUpdate):
        p_values = unit.dict()
        for k,v in {**p_values}.items():
            if v is None:
                del p_values[k]
        await self.session.execute(update(models.Unit).where(models.Unit.id == unit_id).values(**p_values))
        await self.session.commit()

        return await self.read_unit(unit_id)

    async def delete_unit(self, unit_id: int):
        await self.session.execute(delete(models.Unit).where(models.Unit.id == unit_id))
        await self.session.commit()


async def person_crud(session=Depends(get_async_session)):
    yield PersonCRUD(session)

async def employee_crud(session=Depends(get_async_session)):
    yield EmployeeCRUD(session)

async def job_crud(session=Depends(get_async_session)):
    yield JobCRUD(session)

async def patient_crud(session=Depends(get_async_session)):
    yield PatientCRUD(session)

async def unit_crud(session=Depends(get_async_session)):
    yield UnitCRUD(session)

def read_prescriptions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Prescription).offset(skip).limit(limit).all()

def read_prescription(db: Session, prescription_id: int):
    return db.query(models.Prescription).filter(models.Prescription.id == prescription_id).first()

def create_prescription(db: Session, prescription: schemas.PrescriptionCreate):
    db_prescription = models.Prescription(**prescription.dict())
    db.add(db_prescription)
    db.commit()
    db.refresh(db_prescription)
    return db_prescription

def update_prescription(db: Session, prescription_id: int, prescription: schemas.PrescriptionUpdate):
    db_prescription = read_prescription(db, prescription_id)
    if db_prescription:
        db_prescription.medication = prescription.medication
        db_prescription.quantity = prescription.quantity
        db_prescription.unit_id = prescription.unit_id
        db.commit()
        return db_prescription
    return None

def delete_prescription(db: Session, prescription_id: int):
    db_prescription = read_prescription(db, prescription_id)
    if db_prescription:
        db.delete(db_prescription)
        db.commit()
        return db_prescription
    return None

def read_appointments(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Appointment).offset(skip).limit(limit).all()

def read_appointment(db: Session, appointment_id: int):
    return db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()

def create_appointment(db: Session, appointment: schemas.AppointmentCreate):
    db_appointment = models.Appointment(**appointment.dict())
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

def update_appointment(db: Session, appointment_id: int, appointment: schemas.AppointmentUpdate):
    db_appointment = read_appointment(db, appointment_id)
    if db_appointment:
        db_appointment.doctor_id = appointment.doctor_id
        db_appointment.patient_id = appointment.patient_id
        db_appointment.staff_id = appointment.staff_id
        db_appointment.prescription_id = appointment.prescription_id
        db_appointment.date_and_time = appointment.date_and_time
        db_appointment.comments = appointment.comments
        db.commit()
        return db_appointment
    return None

def delete_appointment(db: Session, appointment_id: int):
    db_appointment = read_appointment(db, appointment_id)
    if db_appointment:
        db.delete(db_appointment)
        db.commit()
        return db_appointment
    return None
