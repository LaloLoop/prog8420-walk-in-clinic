from cgitb import reset
from fastapi import Depends
from crud import AppointmentCRUD, appointment_crud
import pandas as pd
import numpy as np
from schemas import AppointmentDisplay

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