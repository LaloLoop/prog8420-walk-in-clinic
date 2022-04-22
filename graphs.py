from io import BytesIO
from fastapi import Depends
from crud import AppointmentCRUD, EmployeeCRUD, JobCRUD, PatientCRUD, PersonCRUD, PrescriptionCRUD, UnitCRUD, appointment_crud, employee_crud, job_crud, patient_crud, person_crud, prescription_crud, unit_crud
from schemas import AppointmentDisplay, EmployeeDisplay
import pandas as pd
import matplotlib.pyplot as plt

import constants as cs

class AppointmentGraphs:
    def __init__(self, crud: AppointmentCRUD):
        self.crud = crud

    async def availability(self):
        appointments_db = await self.crud.read_appointments_with_id_display_name()

        appointments = [AppointmentDisplay.from_orm(appt).dict() for appt in appointments_db]

        appointments_df = pd.DataFrame.from_dict(appointments)

        appointments_by_doctor = appointments_df.groupby("doctor_display_name").agg({'patient_id': "count"})

        appt_by_doctor = appointments_by_doctor.reset_index()
        doctors = appt_by_doctor['doctor_display_name']
        counts = appt_by_doctor['patient_id']

        # Figure Size
        fig, ax = plt.subplots(figsize =(16, 9))

        # Horizontal Bar Plot
        ax.barh(doctors, counts)
        ax.vlines(x=16, ymin=-1, ymax=len(doctors), colors='r', linestyle='--', label="Max. appointments per day")

        # Remove axes splines
        for s in ['top', 'bottom', 'left', 'right']:
            ax.spines[s].set_visible(False)
        
        # Remove x, y Ticks
        ax.xaxis.set_ticks_position('none')
        ax.yaxis.set_ticks_position('none')
        
        # Add padding between axes and labels
        ax.xaxis.set_tick_params(pad = 5)
        ax.yaxis.set_tick_params(pad = 10)
        
        # Add x, y gridlines
        ax.grid(b = True, color ='grey',
                linestyle ='-.', linewidth = 0.5,
                alpha = 0.2)
        
        # Show top values
        ax.invert_yaxis()
        
        # Add annotation to bars
        for i in ax.patches:
            plt.text(i.get_width()+0.2, i.get_y()+0.5,
                    str(round((i.get_width()), 2)),
                    fontsize = 10, fontweight ='bold',
                    color ='grey')
        
        # Add Plot Title
        ax.set_title('Appointments by doctor',
                    loc ='left', )
        
        plt.legend(loc='upper left')
        
        buf = BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)

        return buf

async def appointment_graphs(appt_crud: AppointmentCRUD = Depends(appointment_crud)):
    yield AppointmentGraphs(appt_crud)
   
  
class EntityCountGraphs:
    
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
 
    async def entity_count(self):
        
        persons = await self.person_crud.read_persons()

        jobs = await self.job_crud.read_jobs()

        employees = await self.emp_crud.read_employees()

        patients = await self.patient_crud.read_patients()

        units = await self.unit_crud.read_units()

        prescriptions = await self.prescription_crud.read_prescriptions()

        appointments = await self.appointment_crud.read_appointments()

        data = {'Person': len(persons),
                'Job': len(jobs),
                'Employee': len(employees),
                'Patient': len(patients),
                'Unit': len(units),
                'Prescription': len(prescriptions),
                'Appointment': len(appointments)}

        columns = ['# Entity Type In Database']
        
        df = pd.DataFrame.from_dict(data, orient='index', columns=columns)
        
        fig, ax = plt.subplots(figsize=(16, 9))
        
        ax.bar(x=list(df.index),
                     height=list(df[columns[0]]),
                     color=('green','yellow','red','blue','pink','purple','orange'),
                )

        ax.set_xlabel('Entity Type')
        ax.set_ylabel('# Of Entities in Database')
        ax.set_title(f'Count of Entity Types in Database')
        ax.legend()

        # Add x, y gridlines
        ax.grid(b = True, color ='grey',
                linestyle ='-.', linewidth = 0.5,
                alpha = 0.2)

        # Add annotation to bars
        for i, p in enumerate(ax.patches):
            plt.text(i - p.get_width()/10, p.get_height()+0.5, str(p.get_height()),
                    fontsize = 10, fontweight ='bold', color ='grey')

        buf = BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        
        return buf

async def entity_count_graphs(person_crud: PersonCRUD = Depends(person_crud),
                              job_crud: JobCRUD = Depends(job_crud),
                              emp_crud: EmployeeCRUD = Depends(employee_crud),
                              patient_crud: PatientCRUD = Depends(patient_crud),
                              unit_crud: UnitCRUD = Depends(unit_crud),
                              prescription_crud: PrescriptionCRUD = Depends(prescription_crud),
                              appointment_crud: AppointmentCRUD = Depends(appointment_crud)):
    yield EntityCountGraphs(person_crud, job_crud, emp_crud, patient_crud, unit_crud, prescription_crud, appointment_crud)
    
  
   
class PersonBreakdownGraphs:

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
         
        data = {'Patients': len(patient_ids), 'Admins': len(employee_ids) - len(staff_ids) - len(doctor_ids), 
                'Staffs': len(staff_ids), 'Doctors': len(doctor_ids), 'Un-Assigned': len(person_unassigned_ids)}

        columns = [f'Number of Person Type (of {len(person_ids)} People)']
       
        df = pd.DataFrame.from_dict(data, orient='index', columns=columns)

        df.index.name = 'Person Type'

        import matplotlib.pyplot as plt

        # Figure Size
        fig, ax = plt.subplots(figsize=(16, 9))

        ax = df.plot.pie(ax=ax, y=columns[0],
                         title="Person Breakdown",
                         legend=True,
                         autopct='%1.1f%%',
                         shadow=True,
                         startangle=0)
        
        buf = BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        
        return buf
    
        
async def person_breakdown_graphs(person_crud: PersonCRUD = Depends(person_crud), patient_crud: PatientCRUD = Depends(patient_crud), emp_crud: EmployeeCRUD = Depends(employee_crud)):
    yield PersonBreakdownGraphs(person_crud, patient_crud, emp_crud)
    
class TimeslotUsageGraphs:
    
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
                    
        data = {ts[ts.index('T')+1:]: (len(timeslot_to_doctor_ids[ts]) * 1.0) / len(doctor_ids) * 100 for ts in timeslot_to_doctor_ids}
        columns = [f'% Timeslot Filled ({len(doctor_ids)} Doctors)'] 
        df = pd.DataFrame.from_dict(data, orient='index', columns=columns)
        
        df.index.name = 'Appointment Timeslot'

        # Figure Size
        fig, ax = plt.subplots(figsize=(16, 9))

        ax = df.plot(ax=ax,
                     kind='bar',
                     color='red',
                     xlabel='Appointment Timeslot',
                     ylabel='% Timeslot Filled',
                     ylim=(0,100),
                     legend=True)
       
        # Remove axes splines
        for s in ['top', 'bottom', 'left', 'right']:
            ax.spines[s].set_visible(False)
        
        # Remove x, y Ticks
        ax.xaxis.set_ticks_position('none')
        ax.yaxis.set_ticks_position('none')
        
        # Add padding between axes and labels
        ax.xaxis.set_tick_params(pad = 5)
        ax.yaxis.set_tick_params(pad = 10)
        
        # Add x, y gridlines
        ax.grid(b = True, color ='grey',
                linestyle ='-.', linewidth = 0.5,
                alpha = 0.2)
        
        # Add Plot Title
        ax.set_title(f'Timeslot Usage (for {len(doctor_ids)} Doctors)',
                    loc ='left')
       
        ax.legend(loc='upper left')
        
        buf = BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        
        return buf
         

async def timeslot_usage_graphs(emp_crud: EmployeeCRUD = Depends(employee_crud), appt_crud: AppointmentCRUD = Depends(appointment_crud)):
    yield TimeslotUsageGraphs(emp_crud, appt_crud)