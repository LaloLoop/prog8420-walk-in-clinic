from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

import crud, models, schemas, seed_db
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

seed_db(session= Depends(get_db))

@app.get("/persons/", response_model=List[schemas.Person])
def read_persons(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    persons = crud.get_persons(db, skip=skip, limit=limit)
    if persons is None:
        raise HTTPException(status_code=404, detail="Persons not found")
    return persons

@app.get("/person/{person_id}", response_model=schemas.Person)
def get_person(person_id: int, db: Session = Depends(get_db)):
    db_person = crud.get_person(db, person_id=person_id)
    if db_person is None:
        raise HTTPException(status_code=404, detail="Person not found")
    return db_person

@app.post("/person/", response_model=schemas.Person)
def create_person(person: schemas.PersonCreate, db: Session = Depends(get_db)):
    person = crud.get_person_by_email(db, person.email)
    if person:
        raise HTTPException(status_code=400, detail="Person with this email already exists")
    return crud.create_person(db=db, person=person)

@app.put("/person/{person_id}", response_model=schemas.Person)
def update_person(person_id: int, person: schemas.PersonUpdate, db: Session = Depends(get_db)):
    return crud.update_person(db=db, person_id=person_id, person=person)

@app.delete("/person/{person_id}", response_model=schemas.Person)
def delete_person(person_id: int, db: Session = Depends(get_db)):
    return crud.delete_person(db=db, person_id=person_id)

@app.get("/jobs/", response_model=List[schemas.Job])
def get_jobs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    jobs = crud.get_jobs(db, skip=skip, limit=limit)
    if jobs is None:
        raise HTTPException(status_code=404, detail="Jobs not found")
    return jobs

@app.get("/job/{job_id}", response_model=schemas.Job)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = crud.get_job(db, job_id=job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.post("/job/", response_model=schemas.Job)
def create_job(job: schemas.JobCreate, db: Session = Depends(get_db)):
    return crud.create_job(db=db, job=job)

@app.put("/job/{job_id}", response_model=schemas.Job)
def update_job(job_id: int, job: schemas.JobUpdate, db: Session = Depends(get_db)):
    return crud.update_job(db=db, job_id=job_id, job=job)

@app.delete("/job/{job_id}", response_model=schemas.Job)
def delete_job(job_id: int, db: Session = Depends(get_db)):
    return crud.delete_job(db=db, job_id=job_id)

@app.get("/employees/", response_model=List[schemas.Employee])
def create_employee(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    employees = crud.get_employees(db, skip=skip, limit=limit)
    return employees

@app.get("/employee/{employee_id}", response_model=schemas.Employee)
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    db_employee = crud.get_employee(db, employee_id=employee_id)
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_employee

@app.post("/employee/", response_model=schemas.Employee)
def create_employee(employee: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    employee = crud.get_employee_by_person_id(db, employee.person_id)
    if employee:
        raise HTTPException(status_code=400, detail="Employee with this person_id already exists")
    return crud.create_employee(db=db, employee=employee)

@app.put("/employee/{employee_id}", response_model=schemas.Employee)
def update_employee(employee_id: int, employee: schemas.EmployeeUpdate, db: Session = Depends(get_db)):
    return crud.update_employee(db=db, employee_id=employee_id, employee=employee)

@app.delete("/employee/{employee_id}", response_model=schemas.Employee)
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    return crud.delete_employee(db=db, employee_id=employee_id)

@app.get("/patients/", response_model=List[schemas.Patient])
def get_patients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    patients = crud.get_patients(db, skip=skip, limit=limit)
    if patients is None:
        raise HTTPException(status_code=404, detail="Patients not found")
    return patients

@app.get("/patient/{patient_id}", response_model=schemas.Patient)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    db_patient = crud.get_patient(db, patient_id=patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return db_patient

@app.post("/patient/", response_model=schemas.Patient)
def create_patient(patient: schemas.PatientCreate, db: Session = Depends(get_db)):
    patient = crud.get_patient_by_person_id(db, patient.person_id)
    if patient:
        raise HTTPException(status_code=400, detail="Patient with this person_id already exists")
    return crud.create_patient(db=db, patient=patient)

@app.put("/patient/{patient_id}", response_model=schemas.Patient)
def update_patient(patient_id: int, patient: schemas.PatientUpdate, db: Session = Depends(get_db)):
    return crud.update_patient(db=db, patient_id=patient_id, patient=patient)

@app.delete("/patient/{patient_id}", response_model=schemas.Patient)
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    return crud.delete_patient(db=db, patient_id=patient_id)

@app.get("/units/", response_model=List[schemas.Unit])
def get_units(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    units = crud.get_units(db, skip=skip, limit=limit)
    if units is None:
        raise HTTPException(status_code=404, detail="Units not found")
    return units

@app.get("/unit/{unit_id}", response_model=schemas.Unit)
def get_unit(unit_id: int, db: Session = Depends(get_db)):
    db_unit = crud.get_unit(db, unit_id=unit_id)
    if db_unit is None:
        raise HTTPException(status_code=404, detail="Unit not found")
    return db_unit

@app.post("/unit/", response_model=schemas.Unit)
def create_unit(unit: schemas.UnitCreate, db: Session = Depends(get_db)):
    unit = crud.get_unit_by_name(db, unit.name)
    if unit:
        raise HTTPException(status_code=400, detail="Unit with this name already exists")
    return crud.create_unit(db=db, unit=unit)

@app.put("/unit/{unit_id}", response_model=schemas.Unit)
def update_unit(unit_id: int, unit: schemas.UnitUpdate, db: Session = Depends(get_db)):
    return crud.update_unit(db=db, unit_id=unit_id, unit=unit)

@app.delete("/unit/{unit_id}", response_model=schemas.Unit)
def delete_unit(unit_id: int, db: Session = Depends(get_db)):
    return crud.delete_unit(db=db, unit_id=unit_id)

@app.get("/prescriptions/", response_model=List[schemas.Prescription])
def get_prescriptions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    prescriptions = crud.get_prescriptions(db, skip=skip, limit=limit)
    if prescriptions is None:
        raise HTTPException(status_code=404, detail="Prescriptions not found")
    return prescriptions

@app.get("/prescription/{prescription_id}", response_model=schemas.Prescription)
def get_prescription(prescription_id: int, db: Session = Depends(get_db)):
    db_prescription = crud.get_prescription(db, prescription_id=prescription_id)
    if db_prescription is None:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return db_prescription

@app.post("/prescription/", response_model=schemas.Prescription)
def create_prescription(prescription: schemas.PrescriptionCreate, db: Session = Depends(get_db)):
    prescription = crud.get_prescription_by_name(db, prescription.name)
    if prescription:
        raise HTTPException(status_code=400, detail="Prescription with this name already exists")
    return crud.create_prescription(db=db, prescription=prescription)

@app.put("/prescription/{prescription_id}", response_model=schemas.Prescription)
def update_prescription(prescription_id: int, prescription: schemas.PrescriptionUpdate, db: Session = Depends(get_db)):
    return crud.update_prescription(db=db, prescription_id=prescription_id, prescription=prescription)

@app.delete("/prescription/{prescription_id}", response_model=schemas.Prescription)
def delete_prescription(prescription_id: int, db: Session = Depends(get_db)):
    return crud.delete_prescription(db=db, prescription_id=prescription_id)

@app.get("/appointments/", response_model=List[schemas.Appointment])
def get_appointments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    appointments = crud.get_appointments(db, skip=skip, limit=limit)
    if appointments is None:
        raise HTTPException(status_code=404, detail="Appointments not found")
    return appointments

@app.get("/appointment/{appointment_id}", response_model=schemas.Appointment)
def get_appointment(appointment_id: int, db: Session = Depends(get_db)):
    db_appointment = crud.get_appointment(db, appointment_id)
    if db_appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return db_appointment

@app.post("/appointment/", response_model=schemas.Appointment)
def create_appointment(appointment: schemas.AppointmentCreate, db: Session = Depends(get_db)):
    appointment = crud.get_appointment_by_person_id(db, appointment.person_id)
    if appointment:
        raise HTTPException(status_code=400, detail="Appointment with this person_id already exists")
    return crud.create_appointment(db=db, appointment=appointment)

@app.put("/appointment/{appointment_id}", response_model=schemas.Appointment)
def update_appointment(appointment_id: int, appointment: schemas.AppointmentUpdate, db: Session = Depends(get_db)):
    return crud.update_appointment(db=db, appointment_id=appointment_id, appointment=appointment)

@app.delete("/appointment/{appointment_id}", response_model=schemas.Appointment)
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    return crud.delete_appointment(db=db, appointment_id=appointment_id)

