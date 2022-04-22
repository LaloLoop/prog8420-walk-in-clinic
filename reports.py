from cgitb import reset
from fastapi import Depends
from crud import AppointmentCRUD, EmployeeCRUD, JobCRUD, PatientCRUD, PersonCRUD, PrescriptionCRUD, UnitCRUD, appointment_crud, employee_crud, job_crud, patient_crud, person_crud, prescription_crud, unit_crud
import pandas as pd
import numpy as np
from schemas import AppointmentDisplay, EmployeeDisplay

import constants as cs

class AvailabilityReport:

    def __init__(self, appt_crud: AppointmentCRUD):
        self.appt_crud = appt_crud

    async def by_doctor(self):
        appointments_db = await self.appt_crud.read_appointments_with_id_display_name()
        appointments = [AppointmentDisplay.from_orm(appt).dict() for appt in appointments_db]

        appointments_df = pd.DataFrame.from_dict(appointments)
  
        appt_by_doctor_by_time = appointments_df.groupby(["doctor_display_name", "date_and_time"]).agg({'patient_id': "count"}).reset_index()
        availability_pivot = appt_by_doctor_by_time.pivot_table('patient_id', ['doctor_display_name'], 'date_and_time')
        
        available_schedules = availability_pivot.reset_index()
        schedules = available_schedules.replace(np.nan, 'Available')
        schedules = schedules.replace(1.0, 'Busy')
        
        response = {
            'columns': schedules.columns.to_list()
            ,'data': list(schedules.transpose().to_dict().values())
        }

        return response


async def availability_report(appt_crud: AppointmentCRUD = Depends(appointment_crud)):
    yield AvailabilityReport(appt_crud)
  

class EntityCountReport:
    
    def __init__(self,
                 person_crud: PersonCRUD, 
                 job_crud: JobCRUD,
                 emp_crud: EmployeeCRUD,
                 patient_crud: PatientCRUD,
                 unit_crud: UnitCRUD,
                 prescription_crud: PrescriptionCRUD,
                 appointment_crud: AppointmentCRUD):
        self.person_crud = person_crud
        self.job_crud = job_crud
        self.emp_crud = emp_crud
        self.patient_crud = patient_crud
        self.unit_crud = unit_crud
        self.prescription_crud = prescription_crud
        self.appointment_crud = appointment_crud
 
    async def entity_counts(self):
        
        persons = await self.person_crud.read_persons()

        jobs = await self.job_crud.read_jobs()

        employees = await self.emp_crud.read_employees()

        patients = await self.patient_crud.read_patients()

        units = await self.unit_crud.read_units()

        prescriptions = await self.prescription_crud.read_prescriptions()

        appointments = await self.appointment_crud.read_appointments()

        data = [{'Entity Type':'Number of Entity Type',
                'Person': len(persons),
                'Job': len(jobs),
                'Employee': len(employees),
                'Patient': len(patients),
                'Unit': len(units),
                'Prescription': len(prescriptions),
                'Appointment': len(appointments)
                }]

        columns = ['Entity Type', 'Person', 'Job', 'Employee', 'Patient', 'Unit', 'Prescription', 'Appointment']

        response = {
            'columns': columns,
            'data': data
        }
        
        return response

async def entity_count_report(person_crud: PersonCRUD = Depends(person_crud),
                              job_crud: JobCRUD = Depends(job_crud),
                              emp_crud: EmployeeCRUD = Depends(employee_crud),
                              patient_crud: PatientCRUD = Depends(patient_crud),
                              unit_crud: UnitCRUD = Depends(unit_crud),
                              prescription_crud: PrescriptionCRUD = Depends(prescription_crud),
                              appointment_crud: AppointmentCRUD = Depends(appointment_crud)):
    yield EntityCountReport(person_crud, job_crud, emp_crud, patient_crud, unit_crud, prescription_crud, appointment_crud)
  
   
class PersonBreakdownReport:
    
    def __init__(self, person_crud: PersonCRUD, patient_crud: PatientCRUD, emp_crud: EmployeeCRUD):
        self.person_crud = person_crud
        self.patient_crud = patient_crud
        self.emp_crud = emp_crud
        
    async def person_breakdown(self):
        
        person_ids = await self.person_crud.read_persons()

        person_unassigned_ids = await self.person_crud.read_persons_unassigned() 

        patient_ids = await self.patient_crud.read_patients() 

        employee_ids = await self.emp_crud.read_employees()
         
        staff_ids = await self.emp_crud.read_employees_staff_with_id_display_name() 
         
        doctor_ids = await self.emp_crud.read_employees_doctor_with_id_display_name()
        
        columns = ['Person Type', 'Patients', 'Admins','Staffs', 'Doctors', 'Un-Assigned']         
        data = [{'Person Type':f'# People (out of {len(person_ids)})',
                'Patients': len(patient_ids),
                'Admins': len(employee_ids) - len(staff_ids) - len(doctor_ids),
                'Staffs': len(staff_ids),
                'Doctors': len(doctor_ids),
                'Un-Assigned': len(person_unassigned_ids)
                }]
       
        response = {
            'columns': columns,
            'data': data   
        }
        
        return response
        
        
async def person_breakdown_report(person_crud: PersonCRUD = Depends(person_crud),
                                  patient_crud: PatientCRUD = Depends(patient_crud),
                                  emp_crud: EmployeeCRUD = Depends(employee_crud)):
    yield PersonBreakdownReport(person_crud, patient_crud, emp_crud)
 
class TimeslotUsageReport:
    
    def __init__(self, emp_crud: EmployeeCRUD, appt_crud: AppointmentCRUD):
        self.emp_crud = emp_crud
        self.appt_crud = appt_crud
        
    async def timeslot_percent_usage(self):
        
        doctor_ids = [d.id for d in await self.emp_crud.read_employees_doctor_with_id_display_name()]

        timeslots = [str(ts).replace(' ','T') for ts in cs.get_list_of_possible_available_appointment_datetimes_available_per_one_doctor_per_day()]

        doctor_id_to_timeslots = {}

        for doctor_id in doctor_ids:
            doctor_id_to_timeslots[doctor_id] = [str(a.date_and_time).replace(' ','T') for a in await self.appt_crud.read_appointments_by_doctor_id_with_id_display_name(doctor_id)]
           
        timeslot_to_doctor_ids = {}

        for timeslot in timeslots:
            timeslot_to_doctor_ids[timeslot] = []
            for doctor_id in doctor_ids:
                if timeslot in doctor_id_to_timeslots[doctor_id]:
                    timeslot_to_doctor_ids[timeslot].append(doctor_id)
                   
        # transpose rows and columns so data grid isn't so vertical
        formatted_timeslots =  [ts[ts.index('T')+1:] for ts in timeslot_to_doctor_ids] 
        columns = ['Timeslot'] + formatted_timeslots
       
        helper_dict = {}
        helper_dict['Timeslot'] = f'% Timeslot Filled ({len(doctor_ids)} Doctors)'
        for fts, ts in zip(formatted_timeslots, timeslot_to_doctor_ids):
            helper_dict[fts] = len(timeslot_to_doctor_ids[ts]) * 1.0 / len(doctor_ids) * 100
        data = [helper_dict] # rows needs to be in a list 
        
        response = {
            'columns': columns
            ,'data': data
        }
        
        return response

async def timeslot_usage_report(emp_crud: EmployeeCRUD = Depends(employee_crud), 
                                appt_crud: AppointmentCRUD = Depends(appointment_crud)):
    yield TimeslotUsageReport(emp_crud, appt_crud)