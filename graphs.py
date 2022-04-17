from io import BytesIO
from fastapi import Depends
from crud import AppointmentCRUD, appointment_crud
from schemas import AppointmentDisplay
import pandas as pd
import matplotlib.pyplot as plt


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
        plt.savefig(buf, format="png")
        buf.seek(0)

        return buf

async def appointment_graphs(appt_crud: AppointmentCRUD = Depends(appointment_crud)):
    yield AppointmentGraphs(appt_crud)