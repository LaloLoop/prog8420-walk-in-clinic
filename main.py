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

@app.get("/employees_with_id_display_name/", response_model=List[schemas.EmployeeDisplay], tags=["employee"])
async def read_employees_joined(crud_helper: crud.EmployeeCRUD = Depends(crud.employee_crud)):
    db_employees = await crud_helper.read_employees_with_id_display_name()
    if db_employees is None:
        raise HTTPException(status_code=404, detail="Employees not found")

    return db_employees

@app.get("/employees/", response_model=List[schemas.Employee], tags=["employee"])
async def read_employees(skip: int = 0, limit: int = 100, crud_helper: crud.EmployeeCRUD = Depends(crud.employee_crud)):
    db_employees = await crud_helper.read_employees(skip=skip, limit=limit)
    return db_employees

@app.get("/employee/{employee_id}", response_model=schemas.Employee, tags=["employee"])
async def read_employee(employee_id: UUID4, crud_helper: crud.EmployeeCRUD = Depends(crud.employee_crud)):
    db_employee = await crud_helper.read_employee(employee_id=employee_id)
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_employee

@app.get("/employee_with_id_display_name/{employee_id}", response_model=schemas.EmployeeDisplay, tags=["employee"])
async def read_employee_joined(employee_id: UUID4, crud_helper: crud.EmployeeCRUD = Depends(crud.employee_crud)):
    db_employee = await crud_helper.read_employee_with_id_display_name(employee_id=employee_id)
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_employee

@app.get("/patients_with_id_display_name/", response_model=List[schemas.PatientDisplay], tags=["patient"])
async def read_patients_joined(crud_helper: crud.PatientCRUD = Depends(crud.patient_crud)):
    return await crud_helper.read_patients_with_id_display_name()

@app.get("/patients/", response_model=List[schemas.Patient], tags=["patient"])
async def read_patients(skip: int = 0, limit: int = 100, crud_helper: crud.PatientCRUD = Depends(crud.patient_crud)):
    db_patients = await crud_helper.read_patients(skip=skip, limit=limit)
    if db_patients is None:
        raise HTTPException(status_code=404, detail="Patients not found")
    return db_patients

@app.get("/patient/{patient_id}", response_model=schemas.Patient, tags=["patient"])
async def read_patient(patient_id: int, crud_helper: crud.PatientCRUD = Depends(crud.patient_crud)):
    db_patient = await crud_helper.read_patient(patient_id=patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return db_patient


@app.get("/patient_with_id_display_name/{patient_id}", response_model=schemas.PatientDisplay, tags=["patient"])
async def read_patient_joined(patient_id: int, crud_helper: crud.PatientCRUD = Depends(crud.patient_crud)):
    db_patient = await crud_helper.read_patient_with_id_display_name(patient_id=patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return db_patient


@app.post("/patient/", response_model=schemas.Patient, status_code=status.HTTP_201_CREATED, tags=["patient"])
async def create_patient(patient: schemas.PatientCreate, crud_helper: crud.PatientCRUD = Depends(crud.patient_crud)):
    db_patient = await crud_helper.read_patient_by_person_id(patient.person_id)
    if db_patient:
        raise HTTPException(status_code=400, detail="Patient with this person_id already exists")
    return await crud_helper.create_patient(patient=patient)

@app.put("/patient/{patient_id}", response_model=schemas.Patient, tags=["patient"])
async def update_patient(patient_id: int, patient: schemas.PatientUpdate, crud_helper: crud.PatientCRUD = Depends(crud.patient_crud)):
    db_patient = await crud_helper.read_patient(patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return await crud_helper.update_patient(patient_id=patient_id, patient=patient)


@app.delete("/patient/{patient_id}", response_model=schemas.Patient, tags=["patient"])
async def delete_patient(patient_id: int, crud_helper: crud.PatientCRUD = Depends(crud.patient_crud)):
    db_patient = await crud_helper.read_patient(patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    await crud_helper.delete_patient(patient_id=patient_id)
    return db_patient

  
@app.get("/units/", response_model=List[schemas.Unit], tags=["units"])
async def read_units(skip: int = 0, limit: int = 100, crud_helper: crud.UnitCRUD = Depends(crud.unit_crud)):
    db_units = await crud_helper.read_units(skip=skip, limit=limit)
    if db_units is None:
        raise HTTPException(status_code=404, detail="Units not found")
    return db_units

@app.get("/unit/{unit_id}", response_model=schemas.Unit, tags=["units"])
async def read_unit(unit_id: int, crud_helper: crud.UnitCRUD = Depends(crud.unit_crud)):
    db_unit = await crud_helper.read_unit(unit_id=unit_id)
    if db_unit is None:
        raise HTTPException(status_code=404, detail="Unit not found")
    return db_unit

@app.post("/unit/", response_model=schemas.Unit, status_code=status.HTTP_201_CREATED, tags=["unints"])
async def create_unit(unit: schemas.UnitCreate, crud_helper: crud.UnitCRUD = Depends(crud.unit_crud)):
    db_unit = await crud_helper.read_unit_by_name(unit.name)
    if db_unit:
        raise HTTPException(status_code=400, detail="Unit with this name already exists")
    return await crud_helper.create_unit(unit=unit)

@app.put("/unit/{unit_id}", response_model=schemas.Unit, tags=["units"])
async def update_unit(unit_id: int, unit: schemas.UnitUpdate, crud_helper: crud.UnitCRUD = Depends(crud.unit_crud)):
    db_unit = await crud_helper.read_unit(unit_id)
    if db_unit is None:
        raise HTTPException(status_code=404, detail="Unit not found")
    return await crud_helper.update_unit(unit_id=unit_id, unit=unit)

@app.delete("/unit/{unit_id}", response_model=schemas.Unit, tags=["units"])
async def delete_unit(unit_id: int, crud_helper: crud.UnitCRUD = Depends(crud.unit_crud)):
    db_unit = await crud_helper.read_unit(unit_id)
    if db_unit is None:
        raise HTTPException(status_code=404, detail="Person not found")
    await crud_helper.delete_unit(unit_id=unit_id)
    return db_unit


@app.get("/prescriptions_with_id_display_name/", response_model=List[schemas.PrescriptionDisplay], tags=["prescriptions"])
async def read_prescriptions_joined(crud_helper: crud.PrescriptionCRUD = Depends(crud.prescription_crud)):
    db_prescriptions = await crud_helper.read_prescriptions_with_id_display_name()
    return db_prescriptions

@app.get("/prescriptions/", response_model=List[schemas.Prescription], tags=["prescriptions"])
async def read_prescriptions(skip: int = 0, limit: int = 100, crud_helper: crud.PrescriptionCRUD = Depends(crud.prescription_crud)):
    db_prescriptions = await crud_helper.read_prescriptions(skip=skip, limit=limit)
    if db_prescriptions is None:
        raise HTTPException(status_code=404, detail="Prescriptions not found")
    return db_prescriptions

@app.get("/prescription/{prescription_id}", response_model=schemas.Prescription, tags=["prescriptions"])
async def read_prescription(prescription_id: int, crud_helper: crud.PrescriptionCRUD = Depends(crud.prescription_crud)):
    db_prescription = await crud_helper.read_prescription(prescription_id=prescription_id)
    if db_prescription is None:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return db_prescription


@app.get("/prescription_with_id_display_name/{prescription_id}", response_model=schemas.PrescriptionDisplay, tags=["prescriptions"])
async def read_prescription_joined(prescription_id: int, crud_helper: crud.PrescriptionCRUD = Depends(crud.prescription_crud)):
    db_prescription = await crud_helper.read_prescription_with_id_display_name(prescription_id=prescription_id)
    if db_prescription is None:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return db_prescription


@app.post("/prescription/", response_model=schemas.Prescription, status_code=status.HTTP_201_CREATED, tags=["prescriptions"])
async def create_prescription(prescription: schemas.PrescriptionCreate, crud_helper: crud.PrescriptionCRUD = Depends(crud.prescription_crud)):
    db_prescription = await crud_helper.read_prescription_by_name(prescription.medication)
    if db_prescription:
        raise HTTPException(status_code=400, detail="Prescription with this name already exists")
    return await crud_helper.create_prescription(prescription=prescription)

@app.put("/prescription/{prescription_id}", response_model=schemas.Prescription, tags=["prescriptions"])
async def update_prescription(prescription_id: int, prescription: schemas.PrescriptionUpdate, crud_helper: crud.PrescriptionCRUD = Depends(crud.prescription_crud)):
    db_prescription = await crud_helper.read_prescription(prescription_id)
    if db_prescription is None:
        raise HTTPException(status_code=404, detail="Unit not found")
    return await crud_helper.update_prescription(prescription_id=prescription_id, prescription=prescription)

@app.delete("/prescription/{prescription_id}", response_model=schemas.Prescription, tags=["prescriptions"])
async def delete_prescription(prescription_id: int, crud_helper: crud.PrescriptionCRUD = Depends(crud.prescription_crud)):
    db_prescription = await crud_helper.read_prescription(prescription_id)
    if db_prescription is None:
        raise HTTPException(status_code=404, detail="Person not found")
    await crud_helper.delete_prescription(prescription_id=prescription_id)
    return db_prescription


@app.get("/appointments_with_id_display_name/", response_model=List[schemas.AppointmentDisplay], tags=["appointments"])
async def read_appointments_joined(crud_helper: crud.AppointmentCRUD = Depends(crud.appointment_crud)):
    db_appointments = await crud_helper.read_appointments_with_id_display_name()
    return db_appointments

@app.get("/appointments/", response_model=List[schemas.Appointment], tags=["appointments"])
async def read_appointments(skip: int = 0, limit: int = 100, crud_helper: crud.AppointmentCRUD = Depends(crud.appointment_crud)):
    db_appointments = await crud_helper.read_appointments(skip=skip, limit=limit)
    if db_appointments is None:
        raise HTTPException(status_code=404, detail="Appointments not found")
    return db_appointments

@app.get("/appointment/{appointment_id}", response_model=schemas.Appointment, tags=["appointments"])
async def read_appointment(appointment_id: int, crud_helper: crud.AppointmentCRUD = Depends(crud.appointment_crud)):
    db_appointment = await crud_helper.read_appointment(appointment_id)
    if db_appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return db_appointment

@app.get("/appointment_with_id_display_name/{appointment_id}", response_model=schemas.AppointmentDisplay, tags=["appointments"])
async def read_appointment_joined(appointment_id: int, crud_helper: crud.AppointmentCRUD = Depends(crud.appointment_crud)):
    db_appointment = await crud_helper.read_appointment_with_id_display_name(appointment_id)
    if db_appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return db_appointment

@app.get("/appointments_by_doctor_id_with_id_display_name/{doctor_id}", response_model=List[schemas.AppointmentDisplay], tags=["appointments"])
async def read_appointment_by_doctor_id_with_id_display_name(doctor_id: UUID4, crud_helper: crud.AppointmentCRUD = Depends(crud.appointment_crud)):
    db_appointments = await crud_helper.read_appointments_by_doctor_id_with_id_display_name(doctor_id=doctor_id)
    if db_appointments is None:
        raise HTTPException(status_code=404, detail="Appointments not found")
    return db_appointments

@app.get("/appointments_by_patient_id_with_id_display_name/{patient_id}", response_model=List[schemas.AppointmentDisplay])
def read_appointment_by_patient_id_with_id_display_name(patient_id: int, crud_helper: crud.AppointmentCRUD = Depends(crud.appointment_crud)):
    db_appointments = crud_helper.read_appointments_by_patient_id_with_id_display_name(patient_id=patient_id)
    if db_appointments is None:
        raise HTTPException(status_code=404, detail="Appointments not found")
    return db_appointments

@app.get("/appointments_by_staff_id_with_id_display_name/{staff_id}", response_model=List[schemas.AppointmentDisplay])
def read_appointment_by_staff_id_with_id_display_name(staff_id: int, crud_helper: crud.AppointmentCRUD = Depends(crud.appointment_crud)):
    db_appointments = crud_helper.read_appointments_by_staff_id_with_id_display_name(staff_id=staff_id)
    if db_appointments is None:
        raise HTTPException(status_code=404, detail="Appointments not found")
    return db_appointments

@app.get("/appointments_by_prescription_id_with_id_display_name/{prescription_id}", response_model=List[schemas.AppointmentDisplay])
def read_appointment_by_prescription_id_with_id_display_name(prescription_id: int, crud_helper: crud.AppointmentCRUD = Depends(crud.appointment_crud)):
    db_appointments = crud_helper.read_appointments_by_prescription_id_with_id_display_name(db, prescription_id=prescription_id)
    if db_appointments is None:
        raise HTTPException(status_code=404, detail="Appointments not found")
    return db_appointments

@app.post("/appointment/", response_model=schemas.Appointment, status_code=status.HTTP_201_CREATED, tags=["appointments"])
async def create_appointment(appointment: schemas.AppointmentCreate, crud_helper: crud.AppointmentCRUD = Depends(crud.appointment_crud)):
    db_appointment = await crud_helper.read_appointment_by_patient_id(appointment.patient_id)
    if db_appointment:
        raise HTTPException(status_code=400, detail="Appointment with this patient already exists")
    return await crud_helper.create_appointment(appointment=appointment)

@app.put("/appointment/{appointment_id}", response_model=schemas.Appointment, tags=["appointments"])
async def update_appointment(appointment_id: int, appointment: schemas.AppointmentUpdate, crud_helper: crud.AppointmentCRUD = Depends(crud.appointment_crud)):
    db_appointment = await crud_helper.read_appointment(appointment_id)
    if db_appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return await crud_helper.update_appointment(appointment_id=appointment_id, appointment=appointment)

@app.delete("/appointment/{appointment_id}", response_model=schemas.Appointment, tags=["appointments"])
async def delete_appointment(appointment_id: int, crud_helper: crud.AppointmentCRUD = Depends(crud.appointment_crud)):
    db_appointment = await crud_helper.read_appointment(appointment_id)
    if db_appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    await crud_helper.delete_appointment(appointment_id=appointment_id)
    return db_appointment