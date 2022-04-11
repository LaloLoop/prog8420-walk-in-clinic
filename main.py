from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, status

from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session

from pydantic import UUID4

import crud, schemas

from seed_db import spawn_db_seed
from users import auth_backend, create_db_and_tables, get_async_session, current_active_user, fastapi_users

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

## AUTH ##

app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(fastapi_users.get_register_router(), prefix="/auth", tags=["auth"])
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(fastapi_users.get_users_router(), prefix="/users", tags=["users"])


@app.get("/authenticated-route")
async def authenticated_route(user: schemas.EmployeeDB = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}


### SETUP ###

@app.on_event("startup")
async def on_startup():
    # Not needed if you setup a migration system like Alembic
    await create_db_and_tables()
    await spawn_db_seed()

###### >>>>> COMMON APP Routes <<<<<< ####
@app.get("/")
async def root():
    return {"message": "Go to <base_url>/docs to see the Swagger Page"}

@app.get("/persons/", response_model=List[schemas.Person], tags=["person"])
async def read_persons(skip: int = 0, limit: int = 100, crud_helper: crud.PersonCRUD = Depends(crud.person_crud)):
    db_persons = await crud_helper.read_persons(skip=skip, limit=limit)
    if db_persons is None:
        raise HTTPException(status_code=404, detail="Persons not found")
    return db_persons

@app.get("/person/{person_id}", response_model=schemas.Person, tags=["person"])
async def read_person(person_id: int, crud_helper: crud.PersonCRUD = Depends(crud.person_crud)):
    db_person = await crud_helper.read_person(person_id=person_id)
    if db_person is None:
        raise HTTPException(status_code=404, detail="Person not found")
    return db_person

@app.post("/person/", response_model=schemas.Person, status_code=status.HTTP_201_CREATED, tags=["person"])
async def create_person(person: schemas.PersonCreate, crud_helper: crud.PersonCRUD = Depends(crud.person_crud)):
    db_person = await crud_helper.read_person_by_email(person.email)
    if db_person is not None:
        raise HTTPException(status_code=400, detail="Person with this email already exists")
    return await crud_helper.create_person(person=person)

@app.put("/person/{person_id}", response_model=schemas.Person, tags=["person"])
async def update_person(person_id: int, person: schemas.PersonUpdate, crud_helper: crud.PersonCRUD = Depends(crud.person_crud)):
    db_person = await crud_helper.read_person(person_id)
    if db_person is None:
        raise HTTPException(status_code=404, detail="Person not found")
    return await crud_helper.update_person(person_id=person_id, person=person)

@app.delete("/person/{person_id}", response_model=schemas.Person, tags=["person"])
async def delete_person(person_id: int, crud_helper: crud.PersonCRUD = Depends(crud.person_crud)):
    db_person = await crud_helper.read_person(person_id)
    if db_person is None:
        raise HTTPException(status_code=404, detail="Person not found")
    await crud_helper.delete_person(person_id=person_id)
    return db_person

@app.get("/jobs/", response_model=List[schemas.Job], tags=["job"])
async def read_jobs(skip: int = 0, limit: int = 100, crud_helper: crud.JobCRUD = Depends(crud.job_crud)):
    db_jobs = await crud_helper.read_jobs(skip=skip, limit=limit)
    if db_jobs is None:
        raise HTTPException(status_code=404, detail="Jobs not found")
    return db_jobs

@app.get("/job/{job_id}", response_model=schemas.Job, tags=["job"])
async def read_job(job_id: int, crud_helper: crud.JobCRUD = Depends(crud.job_crud)):
    db_job = await crud_helper.read_job(job_id=job_id)
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return db_job

@app.post("/job/", response_model=schemas.Job, status_code=status.HTTP_201_CREATED, tags=["job"])
async def create_job(job: schemas.JobCreate, crud_helper: crud.JobCRUD = Depends(crud.job_crud)):
    return await crud_helper.create_job(job=job)

@app.put("/job/{job_id}", response_model=schemas.Job, tags=["job"])
async def update_job(job_id: int, job: schemas.JobUpdate, crud_helper: crud.JobCRUD = Depends(crud.job_crud)):
    return await crud_helper.update_job(job_id=job_id, job=job)

@app.delete("/job/{job_id}", response_model=schemas.Job, tags=["job"])
async def delete_job(job_id: int, crud_helper: crud.JobCRUD = Depends(crud.job_crud)):
    db_person = await crud_helper.read_job(job_id)
    if db_person is None:
        raise HTTPException(status_code=404, detail="Person not found")
    await crud_helper.delete_job(job_id=job_id)
    return db_person

@app.get("/employees/", response_model=List[schemas.Employee], tags=["employee"])
async def create_employee(skip: int = 0, limit: int = 100, crud_helper: crud.EmployeeCRUD = Depends(crud.employee_crud)):
    db_employees = await crud_helper.read_employees(skip=skip, limit=limit)
    return db_employees

@app.get("/employee/{employee_id}", response_model=schemas.Employee, tags=["employee"])
async def read_employee(employee_id: UUID4, crud_helper: crud.EmployeeCRUD = Depends(crud.employee_crud)):
    db_employee = await crud_helper.read_employee(employee_id=employee_id)
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_employee

@app.get("/patients/", response_model=List[schemas.Patient], tags=["patient"])
def read_patients(skip: int = 0, limit: int = 100, db: Session = Depends(get_async_session)):
    db_patients = crud.read_patients(db, skip=skip, limit=limit)
    if db_patients is None:
        raise HTTPException(status_code=404, detail="Patients not found")
    return db_patients

@app.get("/patient/{patient_id}", response_model=schemas.Patient, tags=["patient"])
def read_patient(patient_id: int, db: Session = Depends(get_async_session)):
    db_patient = crud.read_patient(db, patient_id=patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return db_patient

@app.post("/patient/", response_model=schemas.Patient, status_code=status.HTTP_201_CREATED, tags=["patient"])
def create_patient(patient: schemas.PatientCreate, db: Session = Depends(get_async_session)):
    db_patient = crud.read_patient_by_person_id(db, patient.person_id)
    if db_patient:
        raise HTTPException(status_code=400, detail="Patient with this person_id already exists")
    return crud.create_patient(db=db, patient=patient)

@app.put("/patient/{patient_id}", response_model=schemas.Patient, tags=["patient"])
def update_patient(patient_id: int, patient: schemas.PatientUpdate, db: Session = Depends(get_async_session)):
    return crud.update_patient(db=db, patient_id=patient_id, patient=patient)

@app.delete("/patient/{patient_id}", response_model=schemas.Patient, tags=["patient"])
def delete_patient(patient_id: int, db: Session = Depends(get_async_session)):
    return crud.delete_patient(db=db, patient_id=patient_id)

@app.get("/units/", response_model=List[schemas.Unit], tags=["unints"])
def read_units(skip: int = 0, limit: int = 100, db: Session = Depends(get_async_session)):
    db_units = crud.read_units(db, skip=skip, limit=limit)
    if db_units is None:
        raise HTTPException(status_code=404, detail="Units not found")
    return db_units

@app.get("/unit/{unit_id}", response_model=schemas.Unit, tags=["unints"])
def read_unit(unit_id: int, db: Session = Depends(get_async_session)):
    db_unit = crud.read_unit(db, unit_id=unit_id)
    if db_unit is None:
        raise HTTPException(status_code=404, detail="Unit not found")
    return db_unit

@app.post("/unit/", response_model=schemas.Unit, status_code=status.HTTP_201_CREATED, tags=["unints"])
def create_unit(unit: schemas.UnitCreate, db: Session = Depends(get_async_session)):
    db_unit = crud.read_unit_by_name(db, unit.name)
    if db_unit:
        raise HTTPException(status_code=400, detail="Unit with this name already exists")
    return crud.create_unit(db=db, unit=unit)

@app.put("/unit/{unit_id}", response_model=schemas.Unit, tags=["unints"])
def update_unit(unit_id: int, unit: schemas.UnitUpdate, db: Session = Depends(get_async_session)):
    return crud.update_unit(db=db, unit_id=unit_id, unit=unit)

@app.delete("/unit/{unit_id}", response_model=schemas.Unit, tags=["unints"])
def delete_unit(unit_id: int, db: Session = Depends(get_async_session)):
    return crud.delete_unit(db=db, unit_id=unit_id)

@app.get("/prescriptions/", response_model=List[schemas.Prescription], tags=["prescriptions"])
def read_prescriptions(skip: int = 0, limit: int = 100, db: Session = Depends(get_async_session)):
    db_prescriptions = crud.read_prescriptions(db, skip=skip, limit=limit)
    if db_prescriptions is None:
        raise HTTPException(status_code=404, detail="Prescriptions not found")
    return db_prescriptions

@app.get("/prescription/{prescription_id}", response_model=schemas.Prescription, tags=["prescriptions"])
def read_prescription(prescription_id: int, db: Session = Depends(get_async_session)):
    db_prescription = crud.read_prescription(db, prescription_id=prescription_id)
    if db_prescription is None:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return db_prescription

@app.post("/prescription/", response_model=schemas.Prescription, status_code=status.HTTP_201_CREATED, tags=["prescriptions"])
def create_prescription(prescription: schemas.PrescriptionCreate, db: Session = Depends(get_async_session)):
    db_prescription = crud.read_prescription_by_name(db, prescription.name)
    if db_prescription:
        raise HTTPException(status_code=400, detail="Prescription with this name already exists")
    return crud.create_prescription(db=db, prescription=prescription)

@app.put("/prescription/{prescription_id}", response_model=schemas.Prescription, tags=["prescriptions"])
def update_prescription(prescription_id: int, prescription: schemas.PrescriptionUpdate, db: Session = Depends(get_async_session)):
    return crud.update_prescription(db=db, prescription_id=prescription_id, prescription=prescription)

@app.delete("/prescription/{prescription_id}", response_model=schemas.Prescription, tags=["prescriptions"])
def delete_prescription(prescription_id: int, db: Session = Depends(get_async_session)):
    return crud.delete_prescription(db=db, prescription_id=prescription_id)

@app.get("/appointments/", response_model=List[schemas.Appointment], tags=["appointments"])
def read_appointments(skip: int = 0, limit: int = 100, db: Session = Depends(get_async_session)):
    db_appointments = crud.read_appointments(db, skip=skip, limit=limit)
    if db_appointments is None:
        raise HTTPException(status_code=404, detail="Appointments not found")
    return db_appointments

@app.get("/appointment/{appointment_id}", response_model=schemas.Appointment, tags=["appointments"])
def read_appointment(appointment_id: int, db: Session = Depends(get_async_session)):
    db_appointment = crud.read_appointment(db, appointment_id)
    if db_appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return db_appointment

@app.post("/appointment/", response_model=schemas.Appointment, status_code=status.HTTP_201_CREATED, tags=["appointments"])
def create_appointment(appointment: schemas.AppointmentCreate, db: Session = Depends(get_async_session)):
    db_appointment = crud.read_appointment_by_person_id(db, appointment.person_id)
    if db_appointment:
        raise HTTPException(status_code=400, detail="Appointment with this person_id already exists")
    return crud.create_appointment(db=db, appointment=appointment)

@app.put("/appointment/{appointment_id}", response_model=schemas.Appointment, tags=["appointments"])
def update_appointment(appointment_id: int, appointment: schemas.AppointmentUpdate, db: Session = Depends(get_async_session)):
    return crud.update_appointment(db=db, appointment_id=appointment_id, appointment=appointment)

@app.delete("/appointment/{appointment_id}", response_model=schemas.Appointment, tags=["appointments"])
def delete_appointment(appointment_id: int, db: Session = Depends(get_async_session)):
    return crud.delete_appointment(db=db, appointment_id=appointment_id)