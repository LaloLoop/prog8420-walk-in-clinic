from datetime import datetime
from datetime import date
from typing import List, Optional
from unicodedata import name

from pydantic import BaseModel
from src.repos.models import Prescription

class PersonBase(BaseModel):
    first_name: str
    last_name: str
    birthdate: date
    street: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postalcode: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None

class PersonCreate(PersonBase):
    pass

class PersonUpdate(PersonBase):
    pass

class Person(PersonBase):
    id: int
    
    class Config:
        orm_mode = True
        
class EmployeeBase(BaseModel):
    password: str
    
class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(EmployeeBase):
    pass

class Employee(EmployeeBase):
    id: int
    person_id: int
    job_id: int
    
    class Config:
        orm_mode = True
        
class JobBase(BaseModel):
    title: str
    speciality: Optional[str] = None
    
class JobCreate(JobBase):
    pass

class JobUpdate(JobBase):
    pass

class Job(JobBase):
    id: int
    
    class Config:
        orm_mode = True
        
class PatientBase(BaseModel):
    ohip: str
    
class PatientCreate(PatientBase):
    pass

class PatientUpdate(PatientBase):
    pass

class Patient(PatientBase):
    id: int
    person_id: int
    
    class Config:
        orm_mode = True
        
class AppointmentBase(BaseModel):
    date_and_time: datetime.datetime
    comments: Optional[str] = None

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(AppointmentBase):
    pass

class Appointment(AppointmentBase):
    id: int
    doctor_id: int
    patient_id: int
    staff_id: int
    prescription_id: Optional[int] = None
    
    class Config:
        orm_mode = True

class UnitBase(BaseModel):
    name: str
    
class UnitCreate(UnitBase):
    pass

class UnitUpdate(UnitBase):
    pass

class Unit(UnitBase):
    id: int
    
    class Config:
        orm_mode = True
        
class PrescriptionBase(BaseModel):
    name: str
    medication: str
    quantity: int
    
class PrescriptionCreate(PrescriptionBase):
    pass

class PrescriptionUpdate(PrescriptionBase):
    pass

class Prescription(PrescriptionBase):
    id: int
    unit_id: int
    
    class Config:
        orm_mode = True