from os import pread
from re import I
from unicodedata import name
from click import password_option
from sqlalchemy.orm import Session
from sqlalchemy import select

import models, schemas

import constants as cs

def read_persons(db: Session):
    return db.execute(select(models.Person)).all()

def read_person(db: Session, person_id: int):
    return db.execute(select(models.Person).where(models.Person.id == person_id)).first()

def read_person_by_email(db: Session, email: str):
    return db.execute(select(models.Person).where(models.Person.email == email)).first()

def create_person(db: Session, person: schemas.PersonCreate):
    db_person = models.Person(**person.dict())
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    return db_person

def update_person(db: Session, person_id: int, person: schemas.PersonUpdate):
    db_person = read_person(db, person_id)
    if db_person:
        db_person.first_name = person.first_name
        db_person.last_name = person.last_name
        db_person.birthdate = person.birthdate
        db_person.street = person.street
        db_person.city = person.city
        db_person.province = person.province
        db_person.postalcode = person.postalcode
        db_person.email = person.email
        db_person.phone_number = person.phone_number
        db.commit()
        return db_person
    return None

def delete_person(db: Session, person_id: int):
    db_person = read_person(db, person_id)
    if db_person:
        db.delete(db_person)
        db.commit()
        return db_person
    return None

def read_jobs(db: Session):
    return db.execute(select(models.Job)).all()

def read_job(db: Session, job_id: int):
    return db.execute(select(models.Job).where(models.Job.id == job_id)).first()

def create_job(db: Session, job: schemas.JobCreate):
    db_job = models.Job(**job.dict())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

def update_job(db: Session, job_id: int, job: schemas.JobUpdate):
    db_job = read_job(db, job_id)
    if db_job:
        db_job.title = job.title
        db_job.speciality = job.speciality
        db.commit()
        return db_job
    return None

def delete_job(db: Session, job_id: int):
    db_job = read_job(db, job_id)
    if db_job:
        db.delete(db_job)
        db.commit()
        return db_job
    return None

def read_employees(db: Session):
    return db.execute(select(models.Employee)).all()

def read_employee(db: Session, employee_id: int):
    return db.execute(select(models.Employee).where(models.Employee.id == employee_id)).first()

def read_employee_by_person_id(db: Session, person_id: int):
    return db.execute(select(models.Employee).where(models.Employee.person_id == person_id)).first()

def read_employees_by_job_title(db: Session, job_title: str):
    return db.query(models.Employee).join(models.Job).filter(models.Job.title == job_title).all()

def read_employees_with_id_display_name(db: Session):
    query = db.execute(select(models.Employee.id,
                              models.Employee.person_id,
                              models.Person.email,
                              models.Job.id,
                              models.Job.title,
                              models.Employee.password
                              ).join(models.Person).join(models.Job)).all()
    result = []
    for row in query:
        result.append(schemas.EmployeeDisplay(id=row[0],
                                              person_id=row[1],
                                              person_display_name=row[2],
                                              job_id=row[3],
                                              job_display_name=row[4],
                                              password=row[5]))
    return result

def read_employee_with_id_display_name(db: Session, employee_id: int):
    query = db.execute(select(models.Employee.id,
                              models.Employee.person_id,
                              models.Person.email,
                              models.Job.id,
                              models.Job.title,
                              models.Employee.password
                              ).join(models.Person).join(models.Job
                              ).where(models.Employee.id == employee_id)).first()
    row = query
    result = schemas.EmployeeDisplay(id=row[0],
                                     person_id=row[1],
                                     person_display_name=row[2],
                                     job_id=row[3],
                                     job_display_name=row[4],
                                     password=row[5])
    return result

def create_employee(db: Session, employee: schemas.EmployeeCreate):
    db_employee = models.Employee(**employee.dict())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

def update_employee(db: Session, employee_id: int, employee: schemas.EmployeeUpdate):
    db_employee = read_employee(db, employee_id)
    if db_employee:
        db_employee.person_id = employee.person_id
        db_employee.job_id = employee.job_id
        db_employee.password = employee.password
        db.commit()
        return db_employee
    return None

def delete_employee(db: Session, employee_id: int):
    db_employee = read_employee(db, employee_id)
    if db_employee:
        db.delete(db_employee)
        db.commit()
        return db_employee
    return None

def read_patients(db: Session):
    return db.execute(select(models.Patient)).all()

def read_patient(db: Session, patient_id: int):
    return db.execute(select(models.Patient).where(models.Patient.id == patient_id)).first()

def read_patient_by_person_id(db: Session, person_id: int):
    return db.execute(select(models.Patient).where(models.Patient.person_id == person_id)).first()

def read_patients_with_id_display_name(db: Session):
    query = db.execute(select(models.Patient.id,
                              models.Patient.person_id,
                              models.Person.email,
                              models.Patient.ohip\
                              ).join(models.Person)).all()
    result = []
    for row in query:
        result.append(schemas.PatientDisplay(id=row[0],
                                             person_id=row[1],
                                             person_display_name=row[2],
                                             ohip=row[3]))
    return result
    
def read_patient_with_id_display_name(db: Session, patient_id: int):
    query = db.execute(select(models.Patient.id,
                              models.Patient.person_id,
                              models.Person.email,
                              models.Patient.ohip\
                              ).join(models.Person
                              ).where(models.Patient.id == patient_id)).first()
    row = query
    result = schemas.PatientDisplay(id=row[0],
                                    person_id=row[1],
                                    person_display_name=row[2],
                                    ohip=row[3])
    return result

def create_patient(db: Session, patient: schemas.PatientCreate):
    db_patient = models.Patient(**patient.dict())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

def update_patient(db: Session, patient_id: int, patient: schemas.PatientUpdate):
    db_patient = read_patient(db, patient_id)
    if db_patient:
        db_patient.person_id = patient.person_id
        db_patient.ohip = patient.ohip
        db.commit()
        return db_patient
    return None

def delete_patient(db: Session, patient_id: int):
    db_patient = read_patient(db, patient_id)
    if db_patient:
        db.delete(db_patient)
        db.commit()
        return db_patient
    return None

def read_units(db: Session):
    return db.execute(select(models.Unit)).all()

def read_unit(db: Session, unit_id: int):
    return db.execute(select(models.Unit).where(models.Unit.id == unit_id)).first()

def read_unit_by_name(db:Session, name: str):
    return db.execute(select(models.Unit).where(models.Unit.name == name)).first()

def create_unit(db: Session, unit: schemas.UnitCreate):
    db_unit = models.Unit(**unit.dict())
    db.add(db_unit)
    db.commit()
    db.refresh(db_unit)
    return db_unit

def create_unit_by_name(db:Session, unit_name: str):
    db_unit = models.Unit(name=unit_name)
    db.add(db_unit)
    db.commit()
    db.refresh(db_unit)

def update_unit(db: Session, unit_id: int, unit: schemas.UnitUpdate):
    db_unit = read_unit(db, unit_id)
    if db_unit:
        db_unit.name = unit.name
        db.commit()
        return db_unit
    return None

def delete_unit(db: Session, unit_id: int):
    db_unit = read_unit(db, unit_id)
    if db_unit:
        db.delete(db_unit)
        db.commit()
        return db_unit
    return None

def read_prescriptions(db: Session):
    return db.execute(select(models.Prescription).all())

def read_prescription(db: Session, prescription_id: int):
    return db.execute(select(models.Prescription).where(models.Prescription.id == prescription_id)).first()

def read_prescriptions_with_id_display_name(db: Session):
    query = db.execute(select(models.Prescription.id,
                              models.Prescription.unit_id,
                              models.Unit.name,
                              models.Prescription.medication,
                              models.Prescription.quantity,
                              ).join(models.Unit)).all()
    
    result = []
    for row in query:
        result.append(schemas.PrescriptionDisplay(id=row[0],
                                                  unit_id=row[1],
                                                  unit_display_name=row[2],
                                                  medication=row[3],
                                                  quantity=row[4]))
    return result
I
def read_prescription_with_id_display_name(db: Session, prescription_id: int):
    query = db.execute(select(models.Prescription.id,
                              models.Prescription.unit_id,
                              models.Unit.name,
                              models.Prescription.medication,
                              models.Prescription.quantity,
                              ).join(models.Unit
                              ).where(models.Prescription.id == prescription_id
                              )).first()
    
    row = query
    result = schemas.PrescriptionDisplay(id=row[0],
                                              unit_id=row[1],
                                              unit_display_name=row[2],
                                              medication=row[3],
                                              quantity=row[4])
    return result

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

def read_appointments(db: Session):
    return db.execute(select(models.Appointment)).scalars().all()

def read_appointments_by_patient_id(db: Session, patient_id: int):
    return db.execute(select(models.Appointment).where(models.Appointment.patient_id == patient_id)).all()

def read_appointment_by_staff_id(db: Session, staff_id: int):
    return db.execute(select(models.Appointment).where(models.Appointment.staff_id == staff_id)).all()

def read_appointments_by_doctor_id(db: Session, doctor_id: int):
    return db.execute(select(models.Appointment).where(models.Appointment.doctor_id == doctor_id)).all()

def read_appointments_by_prescription_id(db: Session, prescription_id: int):
    return db.execute(select(models.Appointment).where(models.Appointment.prescription_id == prescription_id)).all()

def read_appointment(db: Session, appointment_id: int):
    return db.execute(select(models.Appointment).where(models.Appointment.id == appointment_id)).first()

def read_appointment_by_patient_id(db: Session, patient_id: int):
    return db.execute(select(models.Appointment).where(models.Appointment.patient_id == patient_id)).first()

def read_appointments_with_id_display_name(db: Session):
    patients = select(models.Patient.id,
                      models.Person.email
                      ).join(models.Person).cte(name='patients')
    staffs =  select(models.Employee.id,
                     models.Person.email
                     ).join(models.Person).join(models.Job
                     ).where(models.Job.title == cs.STAFF_TITLE).cte(name='staffs')
    doctors = select(models.Employee.id,
                     models.Person.email
                     ).join(models.Person
                     ).join(models.Job
                     ).where(models.Job.title == cs.DOCTOR_TITLE).cte(name='doctors')
    prescriptions = select(models.Prescription.id,
                           models.Prescription.medication,
                           models.Prescription.quantity,
                           models.Unit.name,
                           ).join(models.Unit).cte(name='prescriptions')
    
    query = db.execute(select(models.Appointment.id,
                              models.Appointment.patient_id,
                              patients.c.email,
                              models.Appointment.staff_id,
                              staffs.c.email,
                              models.Appointment.doctor_id,
                              doctors.c.email,
                              models.Appointment.prescription_id,
                              prescriptions.c.medication,
                              prescriptions.c.quantity,
                              prescriptions.c.name, # unit name
                              models.Appointment.date_and_time,
                              models.Appointment.comments,
        ).join_from(models.Appointment, patients, models.Appointment.patient_id == patients.c.id
        ).join_from(models.Appointment, staffs, models.Appointment.staff_id == staffs.c.id
        ).join_from(models.Appointment, doctors, models.Appointment.doctor_id == doctors.c.id
        ).join_from(models.Appointment, prescriptions, models.Appointment.prescription_id == prescriptions.c.id
        )).all()

    result = []
    for row in query:
        result.append(schemas.AppointmentDisplay(id=row[0],
                                                 patient_id=row[1],
                                                 patient_display_name=row[2],
                                                 staff_id=row[3],
                                                 staff_display_name=row[4],
                                                 doctor_id=row[5],
                                                 doctor_display_name=row[6],
                                                 prescription_id=row[7],
                                                 prescription_display_name=
                                                 cs.get_prescription_display_name(row[8],
                                                                                  row[9],
                                                                                  row[10]),
                                                 date_and_time=row[11],
                                                 comments=row[12]))
    return result

def read_appointment_with_id_display_name(db: Session, appointment_id: int):
    patients = select(models.Patient.id,
                      models.Person.email
                      ).join(models.Person).cte(name='patients')
    staffs =  select(models.Employee.id,
                     models.Person.email
                     ).join(models.Person).join(models.Job
                     ).where(models.Job.title == cs.STAFF_TITLE).cte(name='staffs')
    doctors = select(models.Employee.id,
                     models.Person.email
                     ).join(models.Person
                     ).join(models.Job
                     ).where(models.Job.title == cs.DOCTOR_TITLE).cte(name='doctors')
    prescriptions = select(models.Prescription.id,
                           models.Prescription.medication,
                           models.Prescription.quantity,
                           models.Unit.name,
                           ).join(models.Unit).cte(name='prescriptions')
    
    query = db.execute(select(models.Appointment.id,
                              models.Appointment.patient_id,
                              patients.c.email,
                              models.Appointment.staff_id,
                              staffs.c.email,
                              models.Appointment.doctor_id,
                              doctors.c.email,
                              models.Appointment.prescription_id,
                              prescriptions.c.medication,
                              prescriptions.c.quantity,
                              prescriptions.c.name, # unit name
                              models.Appointment.date_and_time,
                              models.Appointment.comments,
        ).join_from(models.Appointment, patients, models.Appointment.patient_id == patients.c.id
        ).join_from(models.Appointment, staffs, models.Appointment.staff_id == staffs.c.id
        ).join_from(models.Appointment, doctors, models.Appointment.doctor_id == doctors.c.id
        ).join_from(models.Appointment, prescriptions, models.Appointment.prescription_id == prescriptions.c.id
        ).where(models.Appointment.id == appointment_id
        )).first()

    row = query
    result = schemas.AppointmentDisplay(id=row[0],
                                                 patient_id=row[1],
                                                 patient_display_name=row[2],
                                                 staff_id=row[3],
                                                 staff_display_name=row[4],
                                                 doctor_id=row[5],
                                                 doctor_display_name=row[6],
                                                 prescription_id=row[7],
                                                 prescription_display_name=
                                                 cs.get_prescription_display_name(row[8],
                                                                                  row[9],
                                                                                  row[10]),
                                                 date_and_time=row[11],
                                                 comments=row[12])
    return result

def read_appointments_by_patient_id_with_id_display_name(db: Session, patient_id: int):
    patients = select(models.Patient.id,
                      models.Person.email
                      ).join(models.Person).cte(name='patients')
    staffs =  select(models.Employee.id,
                     models.Person.email
                     ).join(models.Person).join(models.Job
                     ).where(models.Job.title == cs.STAFF_TITLE).cte(name='staffs')
    doctors = select(models.Employee.id,
                     models.Person.email
                     ).join(models.Person
                     ).join(models.Job
                     ).where(models.Job.title == cs.DOCTOR_TITLE).cte(name='doctors')
    prescriptions = select(models.Prescription.id,
                           models.Prescription.medication,
                           models.Prescription.quantity,
                           models.Unit.name,
                           ).join(models.Unit).cte(name='prescriptions')
    
    query = db.execute(select(models.Appointment.id,
                              models.Appointment.patient_id,
                              patients.c.email,
                              models.Appointment.staff_id,
                              staffs.c.email,
                              models.Appointment.doctor_id,
                              doctors.c.email,
                              models.Appointment.prescription_id,
                              prescriptions.c.medication,
                              prescriptions.c.quantity,
                              prescriptions.c.name, # unit name
                              models.Appointment.date_and_time,
                              models.Appointment.comments,
        ).join_from(models.Appointment, patients, models.Appointment.patient_id == patients.c.id
        ).join_from(models.Appointment, staffs, models.Appointment.staff_id == staffs.c.id
        ).join_from(models.Appointment, doctors, models.Appointment.doctor_id == doctors.c.id
        ).join_from(models.Appointment, prescriptions, models.Appointment.prescription_id == prescriptions.c.id
        ).where(models.Appointment.patient_id == patient_id
        )).all()

    result = []
    for row in query:
        result.append(schemas.AppointmentDisplay(id=row[0],
                                                 patient_id=row[1],
                                                 patient_display_name=row[2],
                                                 staff_id=row[3],
                                                 staff_display_name=row[4],
                                                 doctor_id=row[5],
                                                 doctor_display_name=row[6],
                                                 prescription_id=row[7],
                                                 prescription_display_name=
                                                 cs.get_prescription_display_name(row[8],
                                                                                  row[9],
                                                                                  row[10]),
                                                 date_and_time=row[11],
                                                 comments=row[12]))
    return result

def read_appointments_by_staff_id_with_id_display_name(db: Session, staff_id: int):
    patients = select(models.Patient.id,
                      models.Person.email
                      ).join(models.Person).cte(name='patients')
    staffs =  select(models.Employee.id,
                     models.Person.email
                     ).join(models.Person).join(models.Job
                     ).where(models.Job.title == cs.STAFF_TITLE).cte(name='staffs')
    doctors = select(models.Employee.id,
                     models.Person.email
                     ).join(models.Person
                     ).join(models.Job
                     ).where(models.Job.title == cs.DOCTOR_TITLE).cte(name='doctors')
    prescriptions = select(models.Prescription.id,
                           models.Prescription.medication,
                           models.Prescription.quantity,
                           models.Unit.name,
                           ).join(models.Unit).cte(name='prescriptions')
    
    query = db.execute(select(models.Appointment.id,
                              models.Appointment.patient_id,
                              patients.c.email,
                              models.Appointment.staff_id,
                              staffs.c.email,
                              models.Appointment.doctor_id,
                              doctors.c.email,
                              models.Appointment.prescription_id,
                              prescriptions.c.medication,
                              prescriptions.c.quantity,
                              prescriptions.c.name, # unit name
                              models.Appointment.date_and_time,
                              models.Appointment.comments,
        ).join_from(models.Appointment, patients, models.Appointment.patient_id == patients.c.id
        ).join_from(models.Appointment, staffs, models.Appointment.staff_id == staffs.c.id
        ).join_from(models.Appointment, doctors, models.Appointment.doctor_id == doctors.c.id
        ).join_from(models.Appointment, prescriptions, models.Appointment.prescription_id == prescriptions.c.id
        ).where(models.Appointment.staff_id == staff_id
        )).all()

    result = []
    for row in query:
        result.append(schemas.AppointmentDisplay(id=row[0],
                                                 patient_id=row[1],
                                                 patient_display_name=row[2],
                                                 staff_id=row[3],
                                                 staff_display_name=row[4],
                                                 doctor_id=row[5],
                                                 doctor_display_name=row[6],
                                                 prescription_id=row[7],
                                                 prescription_display_name=
                                                 cs.get_prescription_display_name(row[8],
                                                                                  row[9],
                                                                                  row[10]),
                                                 date_and_time=row[11],
                                                 comments=row[12]))
    return result

def read_appointments_by_doctor_id_with_id_display_name(db: Session, doctor_id: int):
    patients = select(models.Patient.id,
                      models.Person.email
                      ).join(models.Person).cte(name='patients')
    staffs =  select(models.Employee.id,
                     models.Person.email
                     ).join(models.Person).join(models.Job
                     ).where(models.Job.title == cs.STAFF_TITLE).cte(name='staffs')
    doctors = select(models.Employee.id,
                     models.Person.email
                     ).join(models.Person
                     ).join(models.Job
                     ).where(models.Job.title == cs.DOCTOR_TITLE).cte(name='doctors')
    prescriptions = select(models.Prescription.id,
                           models.Prescription.medication,
                           models.Prescription.quantity,
                           models.Unit.name,
                           ).join(models.Unit).cte(name='prescriptions')
    
    query = db.execute(select(models.Appointment.id,
                              models.Appointment.patient_id,
                              patients.c.email,
                              models.Appointment.staff_id,
                              staffs.c.email,
                              models.Appointment.doctor_id,
                              doctors.c.email,
                              models.Appointment.prescription_id,
                              prescriptions.c.medication,
                              prescriptions.c.quantity,
                              prescriptions.c.name, # unit name
                              models.Appointment.date_and_time,
                              models.Appointment.comments,
        ).join_from(models.Appointment, patients, models.Appointment.patient_id == patients.c.id
        ).join_from(models.Appointment, staffs, models.Appointment.staff_id == staffs.c.id
        ).join_from(models.Appointment, doctors, models.Appointment.doctor_id == doctors.c.id
        ).join_from(models.Appointment, prescriptions, models.Appointment.prescription_id == prescriptions.c.id
        ).where(models.Appointment.doctor_id == doctor_id
        )).all()

    result = []
    for row in query:
        result.append(schemas.AppointmentDisplay(id=row[0],
                                                 patient_id=row[1],
                                                 patient_display_name=row[2],
                                                 staff_id=row[3],
                                                 staff_display_name=row[4],
                                                 doctor_id=row[5],
                                                 doctor_display_name=row[6],
                                                 prescription_id=row[7],
                                                 prescription_display_name=
                                                 cs.get_prescription_display_name(row[8],
                                                                                  row[9],
                                                                                  row[10]),
                                                 date_and_time=row[11],
                                                 comments=row[12]))
    return result
    
def read_appointments_by_prescription_id_with_id_display_name(db: Session, prescription_id: int):
    patients = select(models.Patient.id,
                      models.Person.email
                      ).join(models.Person).cte(name='patients')
    staffs =  select(models.Employee.id,
                     models.Person.email
                     ).join(models.Person).join(models.Job
                     ).where(models.Job.title == cs.STAFF_TITLE).cte(name='staffs')
    doctors = select(models.Employee.id,
                     models.Person.email
                     ).join(models.Person
                     ).join(models.Job
                     ).where(models.Job.title == cs.DOCTOR_TITLE).cte(name='doctors')
    prescriptions = select(models.Prescription.id,
                           models.Prescription.medication,
                           models.Prescription.quantity,
                           models.Unit.name,
                           ).join(models.Unit).cte(name='prescriptions')
    
    query = db.execute(select(models.Appointment.id,
                              models.Appointment.patient_id,
                              patients.c.email,
                              models.Appointment.staff_id,
                              staffs.c.email,
                              models.Appointment.doctor_id,
                              doctors.c.email,
                              models.Appointment.prescription_id,
                              prescriptions.c.medication,
                              prescriptions.c.quantity,
                              prescriptions.c.name, # unit name
                              models.Appointment.date_and_time,
                              models.Appointment.comments,
        ).join_from(models.Appointment, patients, models.Appointment.patient_id == patients.c.id
        ).join_from(models.Appointment, staffs, models.Appointment.staff_id == staffs.c.id
        ).join_from(models.Appointment, doctors, models.Appointment.doctor_id == doctors.c.id
        ).join_from(models.Appointment, prescriptions, models.Appointment.prescription_id == prescriptions.c.id
        ).where(models.Appointment.prescription_id == prescription_id
        )).all()

    result = []
    for row in query:
        result.append(schemas.AppointmentDisplay(id=row[0],
                                                 patient_id=row[1],
                                                 patient_display_name=row[2],
                                                 staff_id=row[3],
                                                 staff_display_name=row[4],
                                                 doctor_id=row[5],
                                                 doctor_display_name=row[6],
                                                 prescription_id=row[7],
                                                 prescription_display_name=
                                                 cs.get_prescription_display_name(row[8],
                                                                                  row[9],
                                                                                  row[10]),
                                                 date_and_time=row[11],
                                                 comments=row[12]))
    return result
 
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