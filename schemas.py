import re
import datetime
from datetime import date, timezone
from typing import List, Optional
from unicodedata import name
from fastapi_users_db_sqlalchemy import BaseUserDatabase
from pydantic import BaseModel, validator, UUID4

from fastapi_users import models

import constants as cs

# taken from https://stackoverflow.com/a/47802790
def check_canadian_postalcode(p, strictCapitalization=False, fixSpace=True):
    '''returns a Tuple of (boolean, string):
    - (True, postalCode) or 
    - (False, error message) 
    By default lower and upper case characters are allowed,  
    a missing middle space will be substituted.'''

    pc = p.strip()                   # copy p, strip whitespaces front/end
    if fixSpace and len(pc) == 6:
        pc = pc[0:3] + " " + pc[3:]    # if allowed / needed insert missing space

    nums = "0123456789"              # allowed numbers
    alph = "ABCEGHJKLMNPRSTVWXYZ"    # allowed characters (WZ handled below)
    mustBeNums = [1,4,6]             # index of number
    mustBeAlph = [0,2,5]             # index of character (WZ handled below)

    illegalCharacters = [x for x in pc 
                         if x not in (nums + alph.lower() + alph + " ")]

    if strictCapitalization:
        illegalCharacters = [x for x in pc
                             if x not in (alph + nums + " ")]

    if illegalCharacters:
        return(False, "Illegal characters detected: " + str(illegalCharacters))

    postalCode = [x.upper() for x in pc]          # copy to uppercase list

    if len(postalCode) != 7:                      # length-validation
        return (False, "Length not 7")

    for idx in range(0,len(postalCode)):          # loop over all indexes
        ch = postalCode[idx]
        if ch in nums and idx not in mustBeNums:  # is is number, check index
            return (False, "Format not 'ADA DAD'")     
        elif ch in alph and idx not in mustBeAlph: # id is character, check index
            return (False, "Format not 'ADA DAD'") # alpha / digit
        elif ch == " " and idx != 3:               # is space in between
            return (False, "Format not 'ADA DAD'")

    if postalCode[0] in "WZ":                      # no W or Z first char
        return (False, "Cant start with W or Z")

    return (True,"".join(postalCode))    # yep - all good

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
    
    @validator('first_name', 'last_name', 'street', 'city')
    def string_must_be_between_2_and_100_characters(cls, v):
        if len(v) < 2 or len(v) > 100:
            raise ValueError(f'{v} must be between 2 and 100 characters')
        return v
    
    @validator('first_name', 'last_name')
    def string_must_be_alphabetic(cls, v):
        if not re.match(r"^[A-Za-z ]*$", v):
            raise ValueError(f'{v} must have alphabetic (space allowed) characters')
        return v
    
    @validator('birthdate')
    def birthdate_must_be_a_date_type(cls, v):
        if not isinstance(v, date):
            raise ValueError(f'{v} must be a date type')
        return v
    
    @validator('birthdate')
    def birthdate_must_be_in_the_past(cls, v):
        if v > date.today():
            raise ValueError(f'{v} must be in the past')
        return v
    
    @validator('birthdate')
    def birthdate_must_not_be_older_than_150_years(cls, v):
        if v < date.today() - datetime.timedelta(days=120*365):
            raise ValueError(f'{v} must not be older than 150 years')
        return v
    
    @validator('city', 'street')
    def must_be_alphanumeric(cls, v):
        if not re.match(r"^[A-Za-z0-9. ]*$", v):
            raise ValueError(f'{v} must be alphanumeric (period and space allowed)')
        return v
    
    @validator('province')
    def province_must_be_in_list_of_provinces(cls, v):
        if v not in cs.PROVINCES:
            raise ValueError(f'{v} must be in list of provinces')
        return v
   
    @validator('postalcode')
    def postal_code_must_be_valid_canadian_postal_code(cls, v):
        valid, v_or_msg = check_canadian_postalcode(v,
                                                   strictCapitalization=cs.STRICT_POSTAL_CODE_CAPITALIZATION,
                                                   fixSpace=cs.FIX_SPACE_IN_POSTAL_CODE)
        if not valid:
            raise ValueError(f'Bad postalcode: {v_or_msg}')
        return v_or_msg
   
    @validator('email')
    def email_must_be_valid(cls, v):
        regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'  
        valid = re.search(regex, v)
        if not valid:
            raise ValueError('Email must be valid, i.e. aa@b.cc')
        return valid.group(0)
    
    # https://www.tripadvisor.ca/Travel-g153339-s605/Canada:Telephones.html
    @validator('phone_number')
    def phone_number_must_contain_at_least_7_digits_within_string(cls, v):
        num_digits_found = 0
        
        for char in v:
            if char.isdigit():
                num_digits_found += 1
                if num_digits_found == 7:
                    return v
            
        if num_digits_found < 7:
            raise ValueError(f'{v} must contain at least 7 digits')
        return v
    
class PersonCreate(PersonBase):
    pass

class PersonUpdate(PersonBase):
    pass

class Person(PersonBase):
    id: int
    
    class Config:
        orm_mode = True

class JobBase(BaseModel):
    title: str
    speciality: Optional[str] = None
    
    @validator('title')
    def title_must_be_one_of_possible_job_titles(cls, v):
        possible_job_titles = list(set(cs.JOB_TITLES))
        if v not in possible_job_titles:
            raise ValueError(f'{v} must be one of the possible job titles, ie: {", ".join(possible_job_titles)}')
        return v
   
    # TODO: allow adding new/different specialties 
    @validator('speciality')
    def speciality_must_be_between_1_and_50_characters(cls, v):
        if not( 1 <= len(v) <= 50 ):
            raise ValueError(f'{v} must be between 1 and 50 characters')
        return v
    
class JobCreate(JobBase):
    pass

class JobUpdate(JobBase):
    pass

class Job(JobBase):
    id: int
    
    class Config:
        orm_mode = True
        
class EmployeeCreate(models.BaseUserCreate):
    person_id: int
    job_id: int

class EmployeeUpdate(models.BaseUserUpdate):
    job_id: int

class Employee(models.BaseUser):
    person_id: int
    job_id: int
    
    class Config:
        orm_mode = True
        
class EmployeeDisplay(models.BaseUser):
    person_id: int
    person_display_name: str
    job_id: int
    job_display_name: str
    
    class Config:
        orm_mode = True

class EmployeeDB(Employee, models.BaseUserDB):
    pass

class PatientBase(BaseModel):
    ohip: str
    person_id: int
    
    @validator('ohip')
    def check_ohip_is_10_digits_followed_by_2_uppercase_letters(cls, v):
        err_msg = f'{v} must be 10 digits followed by 2 uppercase letters'
        if len(v) != 12:
            raise ValueError(err_msg)
        elif not v[0:9].isdigit() or not v[-2:].isalpha():
            raise ValueError(err_msg)
        return v 
    
class PatientCreate(PatientBase):
    pass

class PatientUpdate(PatientBase):
    pass

class Patient(PatientBase):
    id: int
    person_id: int
    
    class Config:
        orm_mode = True
        
class PatientDisplay(PatientBase):
    id: int
    person_id: int
    person_display_name: str
    
    class Config:
        orm_mode = True
        
class AppointmentBase(BaseModel):
    date_and_time: datetime.datetime
    comments: Optional[str] = ""
    
    @validator('date_and_time')
    def date_and_time_must_not_be_during_lunch_hour(cls, v: datetime.datetime):

        if cs.BYPASS_DATE_AND_TIME_VALIDATION:
            return v
        else:
            starting_lunch_datetime = cs.get_todays_starting_lunch_time_datetime().replace(tzinfo=v.tzinfo)
            ending_lunch_datetime = cs.get_todays_ending_lunch_time_datetime().replace(tzinfo=v.tzinfo)

            if v >= starting_lunch_datetime and v < ending_lunch_datetime:
                raise ValueError(f'{v} must not be during lunch hour, between {starting_lunch_datetime.hour} and {ending_lunch_datetime.hour} today')
            return v
   
    @validator('date_and_time')
    def date_and_time_must_not_be_outside_of_regular_hours(cls, v: datetime.datetime):
        if cs.BYPASS_DATE_AND_TIME_VALIDATION:
            return v
        else:
            opening_time_datetime = cs.get_todays_opening_time_datetime().replace(tzinfo=v.tzinfo)
            closing_time_datetime = cs.get_todays_closing_datetime().replace(tzinfo=v.tzinfo)
            if v < opening_time_datetime or v > closing_time_datetime:
                raise ValueError(f'{v} must be during regular hours, between {opening_time_datetime} and {closing_time_datetime} today')
            return v
    
    @validator('comments')
    def comments_must_be_less_than_500_characters(cls, v):
        if len(v) > 500:
            raise ValueError(f'{v} must be less than 500 characters')
        return v
      
class AppointmentCreate(AppointmentBase):
    doctor_id: UUID4
    patient_id: int
    staff_id: UUID4
    prescription_id: Optional[int] = None
      
    # TODO: this may conflict with seeding the database 
    @validator('date_and_time')
    def date_and_time_must_be_in_the_future_or_less_than_1_appointment_length_in_the_past(cls, v):
        if cs.BYPASS_DATE_AND_TIME_VALIDATION:
            return v
        else:
          if v < datetime.datetime.now().replace(tzinfo=timezone.utc):
              raise ValueError(f'{v} must be in the future')
          return v

    @validator('date_and_time')
    def date_and_time_must_not_be_before_or_after_opening_and_closing_hours_respectively(cls, v):
        if cs.BYPASS_DATE_AND_TIME_VALIDATION:
            return v
        else:
          opening_datetime = cs.get_todays_opening_datetime().replace(tzinfo=v.tzinfo)
          closing_datetime = cs.get_todays_closing_datetime().replace(tzinfo=v.tzinfo)

          if v < opening_datetime or v >= closing_datetime:
              raise ValueError(f'{v} must be between {opening_datetime.hour} and {closing_datetime.hour} today')
          return

class AppointmentUpdate(AppointmentBase):
    date_and_time: datetime.datetime = None
    prescription_id: Optional[int] = None

    # TODO: this may conflict with seeding the database 
    @validator('date_and_time')
    def date_and_time_must_be_in_the_future_or_less_than_1_appointment_length_in_the_past(cls, v):
        if cs.BYPASS_DATE_AND_TIME_VALIDATION:
            return v
        else:
          if v < datetime.datetime.now().replace(tzinfo=timezone.utc):
              raise ValueError(f'{v} must be in the future')
          return v

    @validator('date_and_time')
    def date_and_time_must_not_be_before_or_after_opening_and_closing_hours_respectively(cls, v):
        if cs.BYPASS_DATE_AND_TIME_VALIDATION:
            return v
        else:
          opening_datetime = cs.get_todays_opening_datetime().replace(tzinfo=v.tzinfo)
          closing_datetime = cs.get_todays_closing_datetime().replace(tzinfo=v.tzinfo)

          if v < opening_datetime or v >= closing_datetime:
              raise ValueError(f'{v} must be between {opening_datetime.hour} and {closing_datetime.hour} today')
          return

class Appointment(AppointmentBase):
    id: int
    doctor_id: UUID4
    patient_id: int
    staff_id: UUID4
    prescription_id: Optional[int] = None
    
    class Config:
        orm_mode = True

class AppointmentDisplay(AppointmentBase):
    id: int
    appointment_display_name: str 
    patient_id: int
    patient_display_name: str
    staff_id: UUID4
    staff_display_name: str
    doctor_id: UUID4
    doctor_display_name: str
    prescription_id: Optional[int] = None
    prescription_display_name: Optional[str] = None
    
    class Config:
        orm_mode = True
        
class UnitBase(BaseModel):
    name: str
    
    @validator('name')
    def name_must_be_betwwen_1_and_10_characters_long(cls, v):
        if not (1 <= len(v) <= 10):
            raise ValueError(f'{v} must be between 1 and 10 characters long')
        return v
    
class UnitCreate(UnitBase):
    pass

class UnitUpdate(UnitBase):
    pass

class Unit(UnitBase):
    id: int
    
    class Config:
        orm_mode = True

class PrescriptionBase(BaseModel):
    medication: str
    quantity: int
    unit_id: int
    
    @validator('medication')
    def medication_must_be_less_than_100_characters(cls, v):
        if len(v) > 100:
            raise ValueError(f'{v} must be less than 100 characters')
        return v
    
    @validator('quantity')
    def quantity_must_be_greater_than_0(cls, v):
        if v <= 0:
            raise ValueError(f'{v} must be greater than 0')
        return v
    
class PrescriptionCreate(PrescriptionBase):
    pass

class PrescriptionUpdate(PrescriptionBase):
    pass

class Prescription(PrescriptionBase):
    id: int
    
    class Config:
        orm_mode = True
        
class PrescriptionDisplay(PrescriptionBase):
    id: int
    prescription_display_name: str
    unit_id: int
    unit_display_name: str
    
    class Config:
        orm_mode = True
        