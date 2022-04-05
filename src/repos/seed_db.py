
from re import S
from time import time
from sqlalchemy.orm import sessionmaker
from src import constants as cs
from src.repos.entities import Appointment, Employee, Job, Patient, Person, Prescription, Unit

from faker import Faker

def seed_db(session):
    
    faker = Faker(cs.FAKER_LOCALE)
    
    if session.query(Job).first() is None:
        for title,speciality in zip(cs.JOB_TITLES, cs.JOB_SPECIALTIES):
            session.add(Job(title=title,
                            speciality=speciality,
                            )
                        )
        session.commit()
    if session.query(Person).first() is None:
        for i in range(0, len(cs.JOB_TITLES) + cs.INIT_NUM_PATIENTS):
            session.add(Person(first_name=faker.first_name(),
                            last_name=faker.last_name(),
                            birthdate=faker.date_of_birth(),
                            street=faker.street_address(),
                            city=faker.city(),
                            province=cs.PROVINCES[faker.random_int(min=0, max=len(cs.PROVINCES) - 1)],
                            postalcode=faker.postcode(),
                            email=faker.email(),
                            phone_number=faker.phone_number(),
                            )
                        )  
        session.commit()
    if session.query(Employee).first() is None:
        people = session.query(Person).limit(len(cs.JOB_TITLES)).all()
        for person, job in zip(people, session.query(Job).all()):
            session.add(Employee(person_id = person.id,
                                 job_id = job.id,
                                 password = faker.password(),
                                 )
                        )
        session.commit()

    num_appointments_available_today = cs.get_number_of_appointments_available_today(session)
    if cs.INIT_NUM_PATIENTS > num_appointments_available_today:
       raise Exception(f'Not enough appointments ({num_appointments_available_today}) '
                       f'available for the number of patients ({cs.INIT_NUM_PATIENTS}) today')

    if session.query(Patient).first() is None:
        people = session.query(Person).filter(Person.id > len(cs.JOB_TITLES)).all()
        for person in people:
            session.add(Patient(person_id = person.id,
                                ohip = cs.generate_10_digit_with_2_letter_version_code_OHIP_number(faker),
                                )
                        )
        session.commit()
    if session.query(Unit).first() is None:
        for unit_name in cs.UNIT_NAMES:
            session.add(Unit(name=unit_name))
        session.commit()
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
    if session.query(Appointment).first() is None:
        patients = session.query(Patient).all()
        doctors = session.query(Employee).filter(Employee.job.has(title=cs.DOCTOR_TITLE)).all()
        doctors = [doctors[i % len(doctors)] for i in range(0, len(patients))]
        staffs = session.query(Employee).filter(Employee.job.has(title=cs.STAFF_TITLE)).all()
        staffs = [staffs[i % len(staffs)] for i in range(0, len(patients))]
        prescriptions = session.query(Prescription).all()
        prescriptions = [prescriptions[i % len(prescriptions)] for i in range(0, len(patients))]
        for doctor, staff, patient, prescription in zip(doctors, staffs, patients, prescriptions):
           
            # find a open date for the given doctor,
            # SHOULD depend on the time of day currently (can't schedule appointments for the past)) 
            dummy_date = cs.get_todays_opening_datetime()
            
            #TODO: find a way to make sure the appointment is not in the past, or already booked
            
        
            session.add(Appointment(doctor_id=doctor.id,
                                    patient_id=patient.id,
                                    staff_id=staff.id,
                                    prescription_id = prescription.id,
                                    date=dummy_date,
                                    comments = faker.sentence(),
                                    )
                        )
            
            # should commit one by one to ensure that the appointments aren't repeated
            session.commit()

    

