import datetime
from datetime import timedelta
import math
from pathlib import Path
from openpyxl import load_workbook
from src.repos.models import Appointment,Employee, Job

OPENING_HOUR_TIME_DELTA = timedelta(hours=8)

START_LUNCH_TIME_DELTA = timedelta(hours=12)
END_LUNCH_TIME_DELTA = timedelta(hours=13)

CLOSING_HOUR_TIME_DELTA = timedelta(hours=17)

APPOINTMENT_LENGTH_TIME_DELTA = timedelta(minutes=30)

FAKER_LOCALE = 'en_CA'

NUM_ADMIN = 1 # less than 5
NUM_STAFF = 3 # less than 5
NUM_DOCTORS = 5 # less than 5

ADMIN_TITLE = 'admin'
STAFF_TITLE = 'staff'
DOCTOR_TITLE = 'doctor'
JOB_TITLES = [ADMIN_TITLE] * NUM_ADMIN + [STAFF_TITLE] * NUM_STAFF + [DOCTOR_TITLE] * NUM_DOCTORS

ADMIN_SPECIALTIES = ['geek', 'database admin', 'system admin', 'network admin', 'security admin']
STAFF_SPECIALTIES = ['receptionist', 'nurse', 'health worker', 'pharmacist', 'therapist', 'social worker']
DOCTOR_SPECIALTIES = ['general', 'pediatrics', 'cardiology', 'dermatology', 'neurology', 'obstetrics']
JOB_SPECIALTIES =   ADMIN_SPECIALTIES[0:NUM_ADMIN] + \
                    STAFF_SPECIALTIES[0:NUM_STAFF] + \
                    DOCTOR_SPECIALTIES[0:NUM_DOCTORS]
                    
INIT_NUM_PATIENTS = 81

UNIT_NAMES = ['mg','mL','g','oz']

PRESCRIPTION_QUANTITIES = [1, 2, 3, 4, 5, 10, 20, 30, 40, 50, 100, 200, 300, 400, 500, 1000]

PROVINCES = ['AB','BC','MB','NB','NL','NS','NT','NU','ON','PE','QC','SK','YT']

NUM_PRESCRIPTIONS = INIT_NUM_PATIENTS

PROVINCES = ['ON']

MEDICATION_XLSX_FILENAME = 'Clin_Calc_dot_com_the_top_200_drugs_of_2019.xlsx'

# THIS assumes that constants.py and MEDICATION_XLSX_FILENAME are in the same directory
# AND main.py is in the same directory as the parent directory of constants.py
MEDICATION_XLSX_FILEPATH = Path.cwd() / 'src' / MEDICATION_XLSX_FILENAME

def generate_10_digit_with_2_letter_version_code_OHIP_number(faker):
    return str(faker.random_number(digits=10)) + faker.random_letter().upper() + faker.random_letter().upper()

def get_medication_names_from_xlsx_file():
    wb = load_workbook(filename = MEDICATION_XLSX_FILEPATH)
    sheet = wb.active
    
    medication_names = []
    
    for row in sheet.iter_rows(min_row=2, max_row=sheet.max_row, min_col=2, max_col=2):
        medication_names.append(row[0].value.split('; ')[0])
        
    return medication_names

def get_todays_opening_datetime():
    return datetime.datetime.combine(datetime.date.today(), datetime.time(0)) + OPENING_HOUR_TIME_DELTA


def get_todays_closing_datetime():
    return datetime.datetime.combine(datetime.date.today(), datetime.time(0)) + CLOSING_HOUR_TIME_DELTA


def get_number_of_appointments_available_today(session):
    time_available_in_day_time_delta = CLOSING_HOUR_TIME_DELTA - OPENING_HOUR_TIME_DELTA - \
                                       (END_LUNCH_TIME_DELTA - START_LUNCH_TIME_DELTA)
   
    doctors = session.query(Employee).join(Job).filter(Job.title == DOCTOR_TITLE).all()
    return math.floor(time_available_in_day_time_delta.seconds * len(doctors) / APPOINTMENT_LENGTH_TIME_DELTA.seconds)


#### VVVV BELOW IS UNIMPLEMENTED/BRAINSTORMING ONLY VVVV ####

def get_number_of_appointments_available_today_per_doctor(session, employee_id):
    pass
    
    time_available_in_day_time_delta = CLOSING_HOUR_TIME_DELTA - OPENING_HOUR_TIME_DELTA - \
                                       (END_LUNCH_TIME_DELTA - START_LUNCH_TIME_DELTA)
    
    doctor = session.query(Employee).filter(Employee.id == employee_id).first()
    
    
    return math.floor(time_available_in_day_time_delta.seconds * len(doctor) / APPOINTMENT_LENGTH_TIME_DELTA.seconds)

def check_if_speciality_doctor_is_available(session, appointment_datetime):
    pass
    
    if appointment_datetime <= get_todays_opening_datetime() or appointment_datetime >= get_todays_closing_datetime():
        return False
    if appointment_datetime >= START_LUNCH_TIME_DELTA and appointment_datetime < END_LUNCH_TIME_DELTA:
        return False
    
    todays_appointments = session.query(Appointment).filter(Appointment.date.between(get_todays_opening_datetime(), get_todays_closing_datetime()))
    
    if todays_appointments is None:
        return True
    
    doctors_with_appointments_today_dict = {}
    
    for appointment in todays_appointments:
        if appointment.doctor_id not in doctors_with_appointments_today_dict:
            doctors_with_appointments_today_dict[appointment.doctor_id] = []
        doctors_with_appointments_today_dict[appointment.doctor_id].append(appointment.datetime)
        
    # count up number of available appointments for each doctor
    # check if appointment_datetime is in the list of appointments for that doctor
    # if it is, then the doctor is not available
    # if it is not, then the doctor is available
        
    return True