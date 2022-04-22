import asyncio
import contextlib
from random import choice, random

from fastapi_users_db_sqlalchemy import AsyncSession
from database import SessionLocal
from models import Appointment, Employee, Job, Patient, Person, Prescription, Unit
from time import time
import constants as cs
from crud import AppointmentCRUD
from faker import Faker
from schemas import EmployeeCreate
from fastapi_users.manager import UserAlreadyExists
from sqlalchemy.future import select

from users import UserManager, get_async_session, get_user_db, get_user_manager

get_async_session_context = contextlib.asynccontextmanager(get_async_session)
get_user_db_context = contextlib.asynccontextmanager(get_user_db)
get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)

def seed_jobs(faker):
    def seeder(session):
        if session.query(Job).first() is None:
            for title,speciality in zip(cs.JOB_TITLES, cs.JOB_SPECIALTIES):
                session.add(Job(title=title,
                                speciality=speciality,
                                )
                            )
            session.commit()
    
    return seeder

def seed_person(faker):
    def seeder(session):
        if session.query(Person).first() is None:
            for i in range(0, len(cs.JOB_TITLES) + cs.INIT_NUM_PATIENTS):
                
                postcode = faker.postcode()
                if len(postcode) == 6:
                    postcode = postcode[:3] + ' ' + postcode[3:]
                    
                firstname = faker.first_name()
                lastname = faker.last_name()
                
                email = firstname[0:1].lower() + lastname.lower() + '@' + 'gmail.com'
                    
                session.add(Person(first_name=firstname,
                                last_name=lastname,
                                birthdate=faker.date_of_birth(),
                                street=faker.street_address(),
                                city=faker.city(),
                                province=cs.PROVINCES[faker.random_int(min=0, max=len(cs.PROVINCES) - 1)],
                                postalcode=postcode,
                                email=email,
                                phone_number=faker.phone_number(),
                                )
                            )  
            session.commit()
    
    return seeder

def seed_units(faker):
    def seeder(session):
        if session.query(Unit).first() is None:
            for unit_name in cs.UNIT_NAMES:
                session.add(Unit(name=unit_name))

            session.commit()
    return seeder

def seed_prescription(faker):
    def seeder(session):
        if session.query(Prescription).first() is None:
            units = session.query(Unit).all()
            
            medications = cs.get_medication_names_from_xlsx_file()
            medications = [medications[i % len(medications)] for i in range(0, cs.NUM_PRESCRIPTIONS)]
            
            for i in range(0, cs.NUM_PRESCRIPTIONS):
                session.add(Prescription(medication=medications[i],
                                        quantity=cs.PRESCRIPTION_QUANTITIES[
                                            faker.random_int(min=0, max=len(cs.PRESCRIPTION_QUANTITIES) - 1)],
                                        unit_id=units[i % len(units)].id,
                                        )
                            )
            session.commit()

    return seeder

def seed_patient(faker):
    def seeder(session):
        if session.query(Patient).first() is None:
            people = session.query(Person).filter(Person.id > len(cs.JOB_TITLES)).all()
            for person in people:
                session.add(Patient(person_id = person.id,
                                    ohip = cs.generate_10_digit_with_2_letter_version_code_OHIP_number(faker),
                                    )
                            )
            session.commit()

    return seeder

async def seed_appointments(faker, session: AsyncSession):
    appointmentCrud = AppointmentCRUD(session)

    appointment = (await session.execute(select(Appointment))).first()

    if appointment is None:
        patients = (await session.execute(select(Patient))).scalars().all()
        
        doctors = (await session.execute(select(Employee).where(Employee.job.has(title=cs.DOCTOR_TITLE)))).scalars().all()
        doctors = [doctors[i % len(doctors)] for i in range(0, len(patients))]
        
        staffs = (await session.execute(select(Employee).where(Employee.job.has(title=cs.STAFF_TITLE)))).scalars().all()
        staffs = [staffs[i % len(staffs)] for i in range(0, len(patients))]
        
        prescriptions = (await session.execute(select(Prescription))).scalars().all()
        prescriptions = [prescriptions[i % len(prescriptions)] for i in range(0, len(patients))]
        
        for doctor, staff, patient, prescription in zip(doctors, staffs, patients, prescriptions):
        
            if random() > 0.75:
                continue

            # find a open date for the given doctor,
            available_appointments = await appointmentCrud.read_available_appointment_datetimes_by_doctor_id(doctor.id)
            
            session.add(Appointment(doctor_id=doctor.id,
                                    patient_id=patient.id,
                                    staff_id=staff.id,
                                    prescription_id=prescription.id,
                                    date_and_time=choice(available_appointments),
                                    comments=faker.sentence(),
                                    )
                        )
            
        await session.commit()

async def spawn_db_seed():
    async with get_async_session_context() as session:
        async with get_user_db_context(session) as user_db:
            async with get_user_manager_context(user_db) as user_manager:
                await seed_database(session, user_manager)

async def seed_database(session: AsyncSession, user_manager: UserManager):

    Faker.seed(cs.FAKER_SEED)
    faker = Faker(cs.FAKER_LOCALE)
    
    await session.run_sync(seed_jobs(faker))
    await session.run_sync(seed_person(faker))
    await session.run_sync(seed_units(faker))
    await session.run_sync(seed_prescription(faker))
    await session.run_sync(seed_patient(faker))
    await session.commit()
    
    result = await session.execute(select(Employee))

    found = result.scalars().first()

    if found is None:
        result = await session.execute(select(Person).limit(len(cs.JOB_TITLES)))
        people = result.scalars().all()

        result = await session.execute(select(Job))
        jobs = result.scalars().all()

        for person, job in zip(people, jobs):
            is_admin = job.title == "admin"
            password = "admin" if is_admin else faker.password()
            try:
                user = await user_manager.create(
                    EmployeeCreate(
                        email=person.email,
                        password=password,
                        job_id=job.id,
                        person_id=person.id,
                        is_superuser=is_admin
                    )
                )
                print(f"User created username {user.email} with pass. {password}")
            except UserAlreadyExists:
                print(f"User {person.email} already exists")


    result = await session.execute(select(Employee).join(Job).where(Job.title == cs.DOCTOR_TITLE))
    num_doctors = len(result.all())

    num_appointments_available_today = cs.get_number_of_appointments_available_today(num_doctors)
    if cs.INIT_NUM_PATIENTS > num_appointments_available_today:
       raise Exception(f'Not enough appointments ({num_appointments_available_today}) '
                       f'available for the number of patients ({cs.INIT_NUM_PATIENTS}) today')

    
    await seed_appointments(faker, session)