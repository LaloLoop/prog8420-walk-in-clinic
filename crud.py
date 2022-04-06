from sqlalchemy.orm import Session

import models, schemas

def read_persons(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Person).offset(skip).limit(limit).all()

def read_person(db: Session, person_id: int):
    return db.query(models.Person).filter(models.Person.id == person_id).first()

def read_person_by_email(db: Session, email: str):
    return db.query(models.Person).filter(models.Person.email == email).first()

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

def read_employees(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Employee).offset(skip).limit(limit).all()

def read_employee(db: Session, employee_id: int):
    return db.query(models.Employee).filter(models.Employee.id == employee_id).first()

def read_employee_by_person_id(db: Session, person_id: int):
    return db.query(models.Employee).filter(models.Employee.person_id == person_id).first()

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

def read_jobs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Job).offset(skip).limit(limit).all()

def read_job(db: Session, job_id: int):
    return db.query(models.Job).filter(models.Job.id == job_id).first()

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

def read_patients(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Patient).offset(skip).limit(limit).all()

def read_patient(db: Session, patient_id: int):
    return db.query(models.Patient).filter(models.Patient.id == patient_id).first()

def read_patient_by_person_id(db: Session, person_id: int):
    return db.query(models.Patient).filter(models.Patient.person_id == person_id).first()

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

def read_units(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Unit).offset(skip).limit(limit).all()

def read_unit(db: Session, unit_id: int):
    return db.query(models.Unit).filter(models.Unit.id == unit_id).first()

def create_unit(db: Session, unit: schemas.UnitCreate):
    db_unit = models.Unit(**unit.dict())
    db.add(db_unit)
    db.commit()
    db.refresh(db_unit)
    return db_unit

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
