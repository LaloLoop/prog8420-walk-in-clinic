from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

from database import Base


class Person(Base):
    __tablename__ = 'Person'

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String)
    last_name = Column(String)
    birthdate = Column(String)
    street = Column(String)
    city = Column(String)
    province = Column(String)
    postalcode = Column(String)
    email = Column(String)
    phone_number = Column(String)

    employee = relationship("Employee", back_populates="person")

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), server_onupdate=func.now())


class Job(Base):
    __tablename__ = 'Job'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    speciality = Column(String)

    employees = relationship("Employee", back_populates="job")

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), server_onupdate=func.now())
    
    
class Employee(Base):
    __tablename__ = 'Employee'

    id = Column(Integer, primary_key=True, autoincrement=True)
    person_id = Column(Integer, ForeignKey('Person.id'))
    job_id = Column(Integer, ForeignKey('Job.id'))
    password = Column(String)
    #hashed_password = Column(String)

    person = relationship("Person")
    job = relationship("Job", back_populates="employees")

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), server_onupdate=func.now())


class Patient(Base):
    __tablename__ = 'Patient'

    id = Column(Integer, primary_key=True, autoincrement=True)
    person_id = Column(Integer, ForeignKey('Person.id'))
    ohip = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), server_onupdate=func.now())

    person = relationship("Person")

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), server_onupdate=func.now())


class Unit(Base):
    __tablename__ = 'Unit'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), server_onupdate=func.now())


class Prescription(Base):
    __tablename__ = 'Prescription'

    id = Column(Integer, primary_key=True, autoincrement=True)
    medication = Column(String)
    quantity = Column(Integer)
    unit_id = Column(Integer, ForeignKey('Unit.id'))

    unit = relationship("Unit")

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), server_onupdate=func.now())
    
    
class Appointment(Base):
    __tablename__ = 'Appointment'

    id = Column(Integer, primary_key=True, autoincrement=True)
    doctor_id = Column(Integer, ForeignKey('Employee.id'))
    patient_id = Column(Integer, ForeignKey('Patient.id'))
    staff_id = Column(Integer, ForeignKey('Employee.id'))
    prescription_id = Column(Integer, ForeignKey('Prescription.id'))
    date_and_time = Column(DateTime)
    comments = Column(String)

    staff = relationship("Employee", foreign_keys=[staff_id])
    doctor = relationship("Employee", foreign_keys=[doctor_id])
    patient = relationship("Patient")
    prescription = relationship("Prescription")

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), server_onupdate=func.now())