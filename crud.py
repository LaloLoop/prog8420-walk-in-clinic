from os import pread
from re import I
from unicodedata import name

from fastapi import Depends
from fastapi_users_db_sqlalchemy import UUID4, AsyncSession
from sqlalchemy import delete, select, update

from sqlalchemy.orm import Session

import models
import schemas
from users import get_async_session
import constants as cs


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
        for k, v in {**p_values}.items():
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

    async def read_employees_by_job_title(self, job_title: str):
        result = await self.session.execute(select(models.Employee).join(models.Job).where(models.Job.title == job_title))
        return result.scalars().all()

    async def read_employees_with_id_display_name(self):
        query = await self.session.execute(select(models.Employee.id,
                                                  models.Employee.person_id,
                                                  models.Person.email,
                                                  models.Job.id,
                                                  models.Job.title
                                                  ).join(models.Person).join(models.Job))
        result = []

        for row in query:
            result.append(schemas.EmployeeDisplay(id=row[0],
                                                  person_id=row[1],
                                                  person_display_name=row[2],
                                                  email=row[2],
                                                  job_id=row[3],
                                                  job_display_name=row[4],))
        return result

    async def read_employee_with_id_display_name(self, employee_id: int):
        query = await self.session.execute(select(models.Employee.id,
                                                  models.Employee.person_id,
                                                  models.Person.email,
                                                  models.Job.id,
                                                  models.Job.title
                                                  ).join(models.Person).join(models.Job
                                                                             ).where(models.Employee.id == employee_id))
        row = next(query)

        if row is not None:
            return schemas.EmployeeDisplay(id=row[0],
                                           person_id=row[1],
                                           person_display_name=row[2],
                                           email=row[2],
                                           job_id=row[3],
                                           job_display_name=row[4])
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
        for k, v in {**p_values}.items():
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

    async def read_patients_with_id_display_name(self):
        query = await self.session.execute(select(models.Patient.id,
                                                  models.Patient.person_id,
                                                  models.Person.email,
                                                  models.Patient.ohip
                                                  ).join(models.Person))
        result = []
        for row in query:
            result.append(schemas.PatientDisplay(id=row[0],
                                                 person_id=row[1],
                                                 person_display_name=row[2],
                                                 ohip=row[3]))
        return result

    async def read_patient_with_id_display_name(self, patient_id: int):
        query = await self.session.execute(select(models.Patient.id,
                                                  models.Patient.person_id,
                                                  models.Person.email,
                                                  models.Patient.ohip
                                                  ).join(models.Person
                                                         ).where(models.Patient.id == patient_id))
        row = query.first()
        result = schemas.PatientDisplay(id=row[0],
                                        person_id=row[1],
                                        person_display_name=row[2],
                                        ohip=row[3])
        return result

    async def update_patient(self, patient_id: int, patient: schemas.PatientUpdate):
        p_values = patient.dict()
        for k, v in {**p_values}.items():
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

    def create_unit_by_name(db: Session, unit_name: str):
        db_unit = models.Unit(name=unit_name)
        db.add(db_unit)
        db.commit()
        db.refresh(db_unit)

    async def update_unit(self, unit_id: int, unit: schemas.UnitUpdate):
        p_values = unit.dict()
        for k, v in {**p_values}.items():
            if v is None:
                del p_values[k]
        await self.session.execute(update(models.Unit).where(models.Unit.id == unit_id).values(**p_values))
        await self.session.commit()

        return await self.read_unit(unit_id)

    async def delete_unit(self, unit_id: int):
        await self.session.execute(delete(models.Unit).where(models.Unit.id == unit_id))
        await self.session.commit()


class PrescriptionCRUD:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def read_prescriptions(self, skip: int = 0, limit: int = 100):
        result = await self.session.execute(select(models.Prescription).offset(skip).limit(limit))

        return result.scalars().all()

    async def read_prescription(self, prescription_id: int):
        result = await self.session.execute(select(models.Prescription).where(models.Prescription.id == prescription_id))

        return result.scalars().first()

    async def read_prescription_by_name(self, name: int):
        result = await self.session.execute(select(models.Prescription).where(models.Prescription.medication == name))

        return result.scalars().first()

    async def create_prescription(self, prescription: schemas.PrescriptionCreate):
        db_prescription = models.Prescription(**prescription.dict())

        self.session.add(db_prescription)
        await self.session.commit()

        return db_prescription

    async def read_prescriptions_with_id_display_name(self):
        query = await self.session.execute(select(models.Prescription.id,
                                                  models.Prescription.unit_id,
                                                  models.Unit.name,
                                                  models.Prescription.medication,
                                                  models.Prescription.quantity,
                                                  ).join(models.Unit))

        result = []
        for row in query:
            result.append(schemas.PrescriptionDisplay(id=row[0],
                                                      unit_id=row[1],
                                                      unit_display_name=row[2],
                                                      medication=row[3],
                                                      quantity=row[4]))
        return result

    async def read_prescription_with_id_display_name(self, prescription_id: int):
        query = await self.session.execute(select(models.Prescription.id,
                                                  models.Prescription.unit_id,
                                                  models.Unit.name,
                                                  models.Prescription.medication,
                                                  models.Prescription.quantity,
                                                  ).join(models.Unit
                                                         ).where(models.Prescription.id == prescription_id
                                                                 ))

        row = query.first()
        result = schemas.PrescriptionDisplay(id=row[0],
                                             unit_id=row[1],
                                             unit_display_name=row[2],
                                             medication=row[3],
                                             quantity=row[4])
        return result

    async def update_prescription(self, prescription_id: int, prescription: schemas.PrescriptionUpdate):
        p_values = prescription.dict()
        for k, v in {**p_values}.items():
            if v is None:
                del p_values[k]
        await self.session.execute(update(models.Prescription).where(models.Prescription.id == prescription_id).values(**p_values))
        await self.session.commit()

        return await self.read_prescription(prescription_id)

    async def delete_prescription(self, prescription_id: int):
        await self.session.execute(delete(models.Prescription).where(models.Prescription.id == prescription_id))
        await self.session.commit()


class AppointmentCRUD:
    def __init__(self, session):
        self.session = session

    async def read_appointments(self, skip: int = 0, limit: int = 100):
        result = await self.session.execute(select(models.Appointment).offset(skip).limit(limit))

        return result.scalars().all()

    async def read_appointment(self, appointment_id: int):
        result = await self.session.execute(select(models.Appointment).where(models.Appointment.id == appointment_id))

        return result.scalars().first()

    async def read_appointment_by_patient_id(self, person_id: int):
        result = await self.session.execute(select(models.Appointment).where(models.Appointment.prescription_id == person_id))

        return result.scalars().first()

    async def create_appointment(self, appointment: schemas.AppointmentCreate):
        db_appointment = models.Appointment(**appointment.dict())

        self.session.add(db_appointment)
        await self.session.commit()

        return db_appointment

    def read_appointment_by_staff_id(db: Session, staff_id: int):
        return db.execute(select(models.Appointment).where(models.Appointment.staff_id == staff_id)).all()

    def read_appointments_by_doctor_id(db: Session, doctor_id: int):
        return db.execute(select(models.Appointment).where(models.Appointment.doctor_id == doctor_id)).all()

    def read_appointments_by_prescription_id(db: Session, prescription_id: int):
        return db.execute(select(models.Appointment).where(models.Appointment.prescription_id == prescription_id)).all()

    async def read_appointments_with_id_display_name(self):
        patients = select(models.Patient.id,
                          models.Person.email
                          ).join(models.Person).cte(name='patients')
        staffs = select(models.Employee.id,
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

        query = await self.session.execute(select(
            models.Appointment.id,
            models.Appointment.patient_id,
            patients.c.email,
            models.Appointment.staff_id,
            staffs.c.email,
            models.Appointment.doctor_id,
            doctors.c.email,
            models.Appointment.prescription_id,
            prescriptions.c.medication,
            prescriptions.c.quantity,
            prescriptions.c.name,  # unit name
            models.Appointment.date_and_time,
            models.Appointment.comments,
        ).join_from(models.Appointment, patients, models.Appointment.patient_id == patients.c.id
                    ).join_from(models.Appointment, staffs, models.Appointment.staff_id == staffs.c.id
                                ).join_from(models.Appointment, doctors, models.Appointment.doctor_id == doctors.c.id
                                            ).join_from(models.Appointment, prescriptions, models.Appointment.prescription_id == prescriptions.c.id
                                                        ))

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
                                                     prescription_display_name=cs.get_prescription_display_name(row[8],
                                                                                                                row[9],
                                                                                                                row[10]),
                                                     date_and_time=row[11],
                                                     comments=row[12]))
        return result

    async def read_appointment_with_id_display_name(self, appointment_id: int):
        patients = select(models.Patient.id,
                          models.Person.email
                          ).join(models.Person).cte(name='patients')
        staffs = select(models.Employee.id,
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

        query = await self.session.execute(select(models.Appointment.id,
                                                  models.Appointment.patient_id,
                                                  patients.c.email,
                                                  models.Appointment.staff_id,
                                                  staffs.c.email,
                                                  models.Appointment.doctor_id,
                                                  doctors.c.email,
                                                  models.Appointment.prescription_id,
                                                  prescriptions.c.medication,
                                                  prescriptions.c.quantity,
                                                  prescriptions.c.name,  # unit name
                                                  models.Appointment.date_and_time,
                                                  models.Appointment.comments,
                                                  ).join_from(models.Appointment, patients, models.Appointment.patient_id == patients.c.id
                                                              ).join_from(models.Appointment, staffs, models.Appointment.staff_id == staffs.c.id
                                                                          ).join_from(models.Appointment, doctors, models.Appointment.doctor_id == doctors.c.id
                                                                                      ).join_from(models.Appointment, prescriptions, models.Appointment.prescription_id == prescriptions.c.id
                                                                                                  ).where(models.Appointment.id == appointment_id
                                                                                                          ))

        row = query.first()
        result = schemas.AppointmentDisplay(id=row[0],
                                            patient_id=row[1],
                                            patient_display_name=row[2],
                                            staff_id=row[3],
                                            staff_display_name=row[4],
                                            doctor_id=row[5],
                                            doctor_display_name=row[6],
                                            prescription_id=row[7],
                                            prescription_display_name=cs.get_prescription_display_name(row[8],
                                                                                                       row[9],
                                                                                                       row[10]),
                                            date_and_time=row[11],
                                            comments=row[12])
        return result

    async def read_appointments_by_patient_id_with_id_display_name(self, patient_id: int):
        patients = select(models.Patient.id,
                          models.Person.email
                          ).join(models.Person).cte(name='patients')
        staffs = select(models.Employee.id,
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

        query = await self.session.execute(select(models.Appointment.id,
                                  models.Appointment.patient_id,
                                  patients.c.email,
                                  models.Appointment.staff_id,
                                  staffs.c.email,
                                  models.Appointment.doctor_id,
                                  doctors.c.email,
                                  models.Appointment.prescription_id,
                                  prescriptions.c.medication,
                                  prescriptions.c.quantity,
                                  prescriptions.c.name,  # unit name
                                  models.Appointment.date_and_time,
                                  models.Appointment.comments,
                                  ).join_from(models.Appointment, patients, models.Appointment.patient_id == patients.c.id
                                              ).join_from(models.Appointment, staffs, models.Appointment.staff_id == staffs.c.id
                                                          ).join_from(models.Appointment, doctors, models.Appointment.doctor_id == doctors.c.id
                                                                      ).join_from(models.Appointment, prescriptions, models.Appointment.prescription_id == prescriptions.c.id
                                                                                  ).where(models.Appointment.patient_id == patient_id
                                                                                          ))

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
                                                     prescription_display_name=cs.get_prescription_display_name(row[8],
                                                                                                                row[9],
                                                                                                                row[10]),
                                                     date_and_time=row[11],
                                                     comments=row[12]))
        return result

    async def read_appointments_by_staff_id_with_id_display_name(self, staff_id: int):
        patients = select(models.Patient.id,
                          models.Person.email
                          ).join(models.Person).cte(name='patients')
        staffs = select(models.Employee.id,
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

        query = await self.session.execute(select(models.Appointment.id,
                                  models.Appointment.patient_id,
                                  patients.c.email,
                                  models.Appointment.staff_id,
                                  staffs.c.email,
                                  models.Appointment.doctor_id,
                                  doctors.c.email,
                                  models.Appointment.prescription_id,
                                  prescriptions.c.medication,
                                  prescriptions.c.quantity,
                                  prescriptions.c.name,  # unit name
                                  models.Appointment.date_and_time,
                                  models.Appointment.comments,
                                  ).join_from(models.Appointment, patients, models.Appointment.patient_id == patients.c.id
                                              ).join_from(models.Appointment, staffs, models.Appointment.staff_id == staffs.c.id
                                                          ).join_from(models.Appointment, doctors, models.Appointment.doctor_id == doctors.c.id
                                                                      ).join_from(models.Appointment, prescriptions, models.Appointment.prescription_id == prescriptions.c.id
                                                                                  ).where(models.Appointment.staff_id == staff_id
                                                                                          ))

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
                                                     prescription_display_name=cs.get_prescription_display_name(row[8],
                                                                                                                row[9],
                                                                                                                row[10]),
                                                     date_and_time=row[11],
                                                     comments=row[12]))
        return result

    async def read_appointments_by_doctor_id_with_id_display_name(self, doctor_id: UUID4):
        patients = select(models.Patient.id,
                          models.Person.email
                          ).join(models.Person).cte(name='patients')
        staffs = select(models.Employee.id,
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

        query = await self.session.execute(select(models.Appointment.id,
                                  models.Appointment.patient_id,
                                  patients.c.email,
                                  models.Appointment.staff_id,
                                  staffs.c.email,
                                  models.Appointment.doctor_id,
                                  doctors.c.email,
                                  models.Appointment.prescription_id,
                                  prescriptions.c.medication,
                                  prescriptions.c.quantity,
                                  prescriptions.c.name,  # unit name
                                  models.Appointment.date_and_time,
                                  models.Appointment.comments,
                                  ).join_from(models.Appointment, patients, models.Appointment.patient_id == patients.c.id
                                              ).join_from(models.Appointment, staffs, models.Appointment.staff_id == staffs.c.id
                                                          ).join_from(models.Appointment, doctors, models.Appointment.doctor_id == doctors.c.id
                                                                      ).join_from(models.Appointment, prescriptions, models.Appointment.prescription_id == prescriptions.c.id
                                                                                  ).where(models.Appointment.doctor_id == doctor_id
                                                                                          ))

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
                                                     prescription_display_name=cs.get_prescription_display_name(row[8],
                                                                                                                row[9],
                                                                                                                row[10]),
                                                     date_and_time=row[11],
                                                     comments=row[12]))
        return result

    def read_appointments_by_prescription_id_with_id_display_name(db: Session, prescription_id: int):
        patients = select(models.Patient.id,
                          models.Person.email
                          ).join(models.Person).cte(name='patients')
        staffs = select(models.Employee.id,
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
                                  prescriptions.c.name,  # unit name
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
                                                     prescription_display_name=cs.get_prescription_display_name(row[8],
                                                                                                                row[9],
                                                                                                                row[10]),
                                                     date_and_time=row[11],
                                                     comments=row[12]))
        return result


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


async def prescription_crud(session=Depends(get_async_session)):
    yield PrescriptionCRUD(session)


async def appointment_crud(session=Depends(get_async_session)):
    yield AppointmentCRUD(session)
