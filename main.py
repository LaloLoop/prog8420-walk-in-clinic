from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, status

from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session

import crud, models, schemas

from database import SessionLocal, engine
from seed_db import seed_database
import constants as cs

models.Base.metadata.create_all(bind=engine)

seed_database()

app = FastAPI()

origins = [
    "http://localhost:3030", # allow ANVIL client to access the API
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


#print(crud.read_employees_joined(SessionLocal()))
    
#import sys
#sys.exit(0)


@app.get("/")
async def root():
    return {"message": "Go to <base_url>/docs to see the Swagger Page"}

@app.get("/persons/", response_model=List[schemas.Person])
def read_persons(db: Session = Depends(get_db)):
    db_persons = crud.read_persons(db)
    if db_persons is None:
        raise HTTPException(status_code=404, detail="Persons not found")
    return db_persons

@app.get("/person/{person_id}", response_model=schemas.Person)
def read_person(person_id: int, db: Session = Depends(get_db)):
    db_person = crud.read_person(db, person_id=person_id)
    if db_person is None:
        raise HTTPException(status_code=404, detail="Person not found")
    return db_person

@app.post("/person/", response_model=schemas.Person, status_code=status.HTTP_201_CREATED)
def create_person(person: schemas.PersonCreate, db: Session = Depends(get_db)):
    db_person = crud.read_person_by_email(db, person.email)
    if db_person is not None:
        raise HTTPException(status_code=400, detail="Person with this email already exists")
    return crud.create_person(db=db, person=person)

@app.put("/person/{person_id}", response_model=schemas.Person)
def update_person(person_id: int, person: schemas.PersonUpdate, db: Session = Depends(get_db)):
    return crud.update_person(db=db, person_id=person_id, person=person)

@app.delete("/person/{person_id}", response_model=schemas.Person)
def delete_person(person_id: int, db: Session = Depends(get_db)):
    return crud.delete_person(db=db, person_id=person_id)

@app.get("/jobs/", response_model=List[schemas.Job])
def read_jobs(db: Session = Depends(get_db)):
    db_jobs = crud.read_jobs(db)
    if db_jobs is None:
        raise HTTPException(status_code=404, detail="Jobs not found")
    return db_jobs

@app.get("/job/{job_id}", response_model=schemas.Job)
def read_job(job_id: int, db: Session = Depends(get_db)):
    db_job = crud.read_job(db, job_id=job_id)
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return db_job

@app.post("/job/", response_model=schemas.Job, status_code=status.HTTP_201_CREATED)
def create_job(job: schemas.JobCreate, db: Session = Depends(get_db)):
    return crud.create_job(db=db, job=job)

@app.put("/job/{job_id}", response_model=schemas.Job)
def update_job(job_id: int, job: schemas.JobUpdate, db: Session = Depends(get_db)):
    return crud.update_job(db=db, job_id=job_id, job=job)

@app.delete("/job/{job_id}", response_model=schemas.Job)
def delete_job(job_id: int, db: Session = Depends(get_db)):
    return crud.delete_job(db=db, job_id=job_id)

@app.get("/employees/", response_model=List[schemas.Employee])
def read_employees(db: Session = Depends(get_db)):
    db_employees = crud.read_employees(db)
    return db_employees

@app.get("/employees_with_id_display_name/", response_model=List[schemas.EmployeeDisplay])
def read_employees_joined(db: Session = Depends(get_db)):
    db_employees = crud.read_employees_with_id_display_name(db)
    if db_employees is None:
        raise HTTPException(status_code=404, detail="Employees not found")
    return db_employees

@app.get("/employee/{employee_id}", response_model=schemas.Employee)
def read_employee(employee_id: int, db: Session = Depends(get_db)):
    db_employee = crud.read_employee(db, employee_id=employee_id)
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_employee

@app.get("/employee_with_id_display_name/{employee_id}", response_model=schemas.EmployeeDisplay)
def read_employee_joined(employee_id: int, db: Session = Depends(get_db)):
    db_employee = crud.read_employee_with_id_display_name(db, employee_id=employee_id)
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_employee

@app.post("/employee/", response_model=schemas.Employee, status_code=status.HTTP_201_CREATED)
def create_employee(employee: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    db_employee = crud.read_employee_by_person_id(db, employee.person_id)
    if db_employee:
        raise HTTPException(status_code=400, detail="Employee with this person_id already exists")
    return crud.create_employee(db=db, employee=employee)

@app.put("/employee/{employee_id}", response_model=schemas.Employee)
def update_employee(employee_id: int, employee: schemas.EmployeeUpdate, db: Session = Depends(get_db)):
    return crud.update_employee(db=db, employee_id=employee_id, employee=employee)

@app.delete("/employee/{employee_id}", response_model=schemas.Employee)
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    return crud.delete_employee(db=db, employee_id=employee_id)

@app.get("/patients/", response_model=List[schemas.Patient])
def read_patients(db: Session = Depends(get_db)):
    db_patients = crud.read_patients(db)
    if db_patients is None:
        raise HTTPException(status_code=404, detail="Patients not found")
    return db_patients

@app.get("/patients_with_id_display_name/", response_model=List[schemas.PatientDisplay])
def read_patients_joined(db: Session = Depends(get_db)):
    db_patients = crud.read_patients_with_id_display_name(db)
    if db_patients is None:
        raise HTTPException(status_code=404, detail="Patients not found")
    return db_patients

@app.get("/patient/{patient_id}", response_model=schemas.Patient)
def read_patient(patient_id: int, db: Session = Depends(get_db)):
    db_patient = crud.read_patient(db, patient_id=patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return db_patient

@app.get("/patient_with_id_display_name/{patient_id}", response_model=schemas.PatientDisplay)
def read_patient_joined(patient_id: int, db: Session = Depends(get_db)):
    db_patient = crud.read_patient_with_id_display_name(db, patient_id=patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return db_patient

@app.post("/patient/", response_model=schemas.Patient, status_code=status.HTTP_201_CREATED)
def create_patient(patient: schemas.PatientCreate, db: Session = Depends(get_db)):
    db_patient = crud.read_patient_by_person_id(db, patient.person_id)
    if db_patient:
        raise HTTPException(status_code=400, detail="Patient with this person_id already exists")
    return crud.create_patient(db=db, patient=patient)

@app.put("/patient/{patient_id}", response_model=schemas.Patient)
def update_patient(patient_id: int, patient: schemas.PatientUpdate, db: Session = Depends(get_db)):
    return crud.update_patient(db=db, patient_id=patient_id, patient=patient)

@app.delete("/patient/{patient_id}", response_model=schemas.Patient)
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    return crud.delete_patient(db=db, patient_id=patient_id)

@app.get("/units/", response_model=List[schemas.Unit])
def read_units(db: Session = Depends(get_db)):
    db_units = crud.read_units(db)
    if db_units is None:
        raise HTTPException(status_code=404, detail="Units not found")
    return db_units

@app.get("/unit/{unit_id}", response_model=schemas.Unit)
def read_unit(unit_id: int, db: Session = Depends(get_db)):
    db_unit = crud.read_unit(db, unit_id=unit_id)
    if db_unit is None:
        raise HTTPException(status_code=404, detail="Unit not found")
    return db_unit

@app.post("/unit/", response_model=schemas.Unit, status_code=status.HTTP_201_CREATED)
def create_unit(unit: schemas.UnitCreate, db: Session = Depends(get_db)):
    db_unit = crud.read_unit_by_name(db, unit.name)
    if db_unit:
        raise HTTPException(status_code=400, detail="Unit with this name already exists")
    return crud.create_unit(db=db, unit=unit)

@app.put("/unit/{unit_id}", response_model=schemas.Unit)
def update_unit(unit_id: int, unit: schemas.UnitUpdate, db: Session = Depends(get_db)):
    return crud.update_unit(db=db, unit_id=unit_id, unit=unit)

@app.delete("/unit/{unit_id}", response_model=schemas.Unit)
def delete_unit(unit_id: int, db: Session = Depends(get_db)):
    return crud.delete_unit(db=db, unit_id=unit_id)

@app.get("/prescriptions/", response_model=List[schemas.Prescription])
def read_prescriptions(db: Session = Depends(get_db)):
    db_prescriptions = crud.read_prescriptions(db)
    if db_prescriptions is None:
        raise HTTPException(status_code=404, detail="Prescriptions not found")
    return db_prescriptions

@app.get("/prescriptions_with_id_display_name/", response_model=List[schemas.PrescriptionDisplay])
def read_prescriptions_joined(db: Session = Depends(get_db)):
    db_prescriptions = crud.read_prescriptions_with_id_display_name(db)
    if db_prescriptions is None:
        raise HTTPException(status_code=404, detail="Prescriptions not found")
    return db_prescriptions

@app.get("/prescription/{prescription_id}", response_model=schemas.Prescription)
def read_prescription(prescription_id: int, db: Session = Depends(get_db)):
    db_prescription = crud.read_prescription(db, prescription_id=prescription_id)
    if db_prescription is None:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return db_prescription

@app.get("/prescription_with_id_display_name/{prescription_id}", response_model=schemas.PrescriptionDisplay)
def read_prescription_joined(prescription_id: int, db: Session = Depends(get_db)):
    db_prescription = crud.read_prescription_with_id_display_name(db, prescription_id=prescription_id)
    if db_prescription is None:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return db_prescription

@app.post("/prescription/", response_model=schemas.Prescription, status_code=status.HTTP_201_CREATED)
def create_prescription(prescription: schemas.PrescriptionCreate, db: Session = Depends(get_db)):
    return crud.create_prescription(db=db, prescription=prescription)

@app.put("/prescription/{prescription_id}", response_model=schemas.Prescription)
def update_prescription(prescription_id: int, prescription: schemas.PrescriptionUpdate, db: Session = Depends(get_db)):
    return crud.update_prescription(db=db, prescription_id=prescription_id, prescription=prescription)

@app.delete("/prescription/{prescription_id}", response_model=schemas.Prescription)
def delete_prescription(prescription_id: int, db: Session = Depends(get_db)):
    return crud.delete_prescription(db=db, prescription_id=prescription_id)

@app.get("/appointments/", response_model=List[schemas.Appointment])
def read_appointments(db: Session = Depends(get_db)):
    db_appointments = crud.read_appointments(db)
    if db_appointments is None:
        raise HTTPException(status_code=404, detail="Appointments not found")
    return db_appointments

@app.get("/appointments_with_id_display_name/", response_model=List[schemas.AppointmentDisplay])
def read_appointments_joined(db: Session = Depends(get_db)):
    db_appointments = crud.read_appointments_with_id_display_name(db)
    if db_appointments is None:
        raise HTTPException(status_code=404, detail="Appointments not found")
    return db_appointments

@app.get("/appointment/{appointment_id}", response_model=schemas.Appointment)
def read_appointment(appointment_id: int, db: Session = Depends(get_db)):
    db_appointment = crud.read_appointment(db, appointment_id)
    if db_appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return db_appointment

@app.get("/appointment_with_id_display_name/{appointment_id}", response_model=schemas.AppointmentDisplay)
def read_appointment_joined(appointment_id: int, db: Session = Depends(get_db)):
    db_appointment = crud.read_appointment_with_id_display_name(db, appointment_id)
    if db_appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return db_appointment

@app.get("/appointments_by_doctor_id_with_id_display_name/{doctor_id}", response_model=List[schemas.AppointmentDisplay])
def read_appointment_by_doctor_id_with_id_display_name(doctor_id: int, db: Session = Depends(get_db)):
    db_appointments = crud.read_appointments_by_doctor_id_with_id_display_name(db, doctor_id=doctor_id)
    if db_appointments is None:
        raise HTTPException(status_code=404, detail="Appointments not found")
    return db_appointments

@app.get("/appointments_by_patient_id_with_id_display_name/{patient_id}", response_model=List[schemas.AppointmentDisplay])
def read_appointment_by_patient_id_with_id_display_name(patient_id: int, db: Session = Depends(get_db)):
    db_appointments = crud.read_appointments_by_patient_id_with_id_display_name(db, patient_id=patient_id)
    if db_appointments is None:
        raise HTTPException(status_code=404, detail="Appointments not found")
    return db_appointments

@app.get("/appointments_by_staff_id_with_id_display_name/{staff_id}", response_model=List[schemas.AppointmentDisplay])
def read_appointment_by_staff_id_with_id_display_name(staff_id: int, db: Session = Depends(get_db)):
    db_appointments = crud.read_appointments_by_staff_id_with_id_display_name(db, staff_id=staff_id)
    if db_appointments is None:
        raise HTTPException(status_code=404, detail="Appointments not found")
    return db_appointments

@app.get("/appointments_by_prescription_id_with_id_display_name/{prescription_id}", response_model=List[schemas.AppointmentDisplay])
def read_appointment_by_prescription_id_with_id_display_name(prescription_id: int, db: Session = Depends(get_db)):
    db_appointments = crud.read_appointments_by_prescription_id_with_id_display_name(db, prescription_id=prescription_id)
    if db_appointments is None:
        raise HTTPException(status_code=404, detail="Appointments not found")
    return db_appointments

@app.post("/appointment/", response_model=schemas.Appointment, status_code=status.HTTP_201_CREATED)
def create_appointment(appointment: schemas.AppointmentCreate, db: Session = Depends(get_db)):
    db_appointment = crud.read_appointment_by_patient_id(db, appointment.person_id)
    if db_appointment:
        raise HTTPException(status_code=400, detail="Appointment with this person_id already exists")
    return crud.create_appointment(db=db, appointment=appointment)

@app.put("/appointment/{appointment_id}", response_model=schemas.Appointment)
def update_appointment(appointment_id: int, appointment: schemas.AppointmentUpdate, db: Session = Depends(get_db)):
    return crud.update_appointment(db=db, appointment_id=appointment_id, appointment=appointment)

@app.delete("/appointment/{appointment_id}", response_model=schemas.Appointment)
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    return crud.delete_appointment(db=db, appointment_id=appointment_id)