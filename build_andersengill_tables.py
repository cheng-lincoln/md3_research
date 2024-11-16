import pandas as pd
import numpy as np
from utils import deserializeToTimestamp, get_censor_date
from enums import Censor, EventType
from build_events import EventsData

class AndersenGillFormatter:
  """
  Creates an object that helps format events of a patient into Andersen-Gill Table format.

  Attributes:
    patient_id (int): ID of the patient
    start_date (datetime): start date used in the analysis (enrollment date)
    end_date (datetime): end date used in the analysis (derived death date, if any, and censor date)
    group (PatientType): 0 = usual, 1 = sparkle
    emergency_department_uses (DataFrame.loc): all post-enrollment emergency department events of the patient
    unplanned_inpatient_admissions (DataFrame.loc): all post-enrollment unplanned inpatient admission events of the patient
  """

  def __init__(self, patient_id, eventsData):
    """
    Parameters:
      patient_id (int): ID of the patient
      eventsData (EventsDAta): an EventsData object
    """
    enrollment_date = eventsData.findEnrollmentDate(patient_id)
    self.start_date = enrollment_date

    censor_date = get_censor_date()
    if (censor_date < enrollment_date):
      raise ValueError('patient {0} is enrolled after the censor date'.format(patient_id))

    death_date = eventsData.findDeathDate(patient_id)
    self.end_date = censor_date if (death_date is None) or (death_date > censor_date) else death_date

    self.group = eventsData.getPatientType(patient_id)

    self.emergency_department_uses = eventsData.findEmergencyDepartmentUses(patient_id)

    self.unplanned_inpatient_admissions = eventsData.findUnplannedInpatientAdmissions(patient_id)

    self.patient_id = patient_id

  def formatEmergencyDepartmentUses(self):
    return self._convertEvents(self.emergency_department_uses)

  def formatUnplannedInpatientAdmissions(self):
    return self._convertEvents(self.unplanned_inpatient_admissions)

  def _convertEvents(self, events):
    """
    Converts a set of events to Andersen-Gill Table format.

    Parameters:
      events (DataFrame.loc): events of concern (should either be self.emergency_department_uses or self.unplanned_inpatient_admissions)

      Example of self.unplanned_inpatient_admissions:
          id  patient_type patient_type_description  event_type event_type_description  event_date
          157 1            SPARKLE                   0          ENROLLMENT              2022-03-10
          157 1            SPARKLE                   31         ADMIT_ED                2023-07-05
          157 1            SPARKLE                   41         ADMIT_ED_ENDS           2023-07-07
          157 1            SPARKLE                   32         ADMIT_CLINIC            2023-07-26
          157 1            SPARKLE                   42         ADMIT_CLINIC_ENDS       2023-08-01
          157 1            SPARKLE                   2          ED_NOADMIT              2023-10-30
          157 1            SPARKLE                   1          DEATH                   2024-01-10

    Returns:
      id (int), group (int), time0 (int), time (int), status (int)
      [
        [ , , , , ],
        [ , , , , ],
        ...
      ]
    """

    event_dates = events['event_date'].to_list()
    event_dts = [self.start_date] + [deserializeToTimestamp(event_date) for event_date in event_dates] + [self.end_date]
    days = [(event_dts[i+1]-event_dts[i]).days for i in range(len(event_dts)-1)]

    # Create a mask to remove timeframe where patient is hospitalized,
    # since during this period the patient is not at risk of an acute event
    to_keep = [
      False if event_type in [EventType.ADMIT_ED_ENDS, EventType.ADMIT_CLINIC_ENDS] else True
      for event_type
      in events['event_type'].to_list()
    ]
    to_keep.append(True)

    table = []
    time0 = 0
    for idx, d_time in enumerate(days):
      time = time0 + d_time
      table.append([self.patient_id, self.group, time0, time, Censor.CENSORED if idx == len(days)-1 else Censor.EVENT_OCCURRED])
      time0 = time

    masked_table = [row for row, keep in zip(table, to_keep) if keep]

    return masked_table

# -------
'''
We want to build the Andersen-Gill Table from all the

Andersen-Gill Table has these columns:
- id
- group: 0 (usual) or 1 (sparkle)
- time0
- time
- status: 0 (censored) or 1 (event occured)
'''

eventsData = EventsData.load()

emergency_department_uses_table = []
unplanned_inpatient_admissions_table = []

for patient_id in [i for i in range(1,241) if i != 109]: # exclude patient 109
  andersenGillFormatter = AndersenGillFormatter(patient_id, eventsData)

  emergency_department_uses_table += andersenGillFormatter.formatEmergencyDepartmentUses()

  unplanned_inpatient_admissions_table += andersenGillFormatter.formatUnplannedInpatientAdmissions()

emergency_department_uses_table_df = pd.DataFrame(
  np.array(emergency_department_uses_table),
  columns=['id', 'group', 'time0', 'time', 'status']
)
print(emergency_department_uses_table_df)
emergency_department_uses_table_df.to_csv('processed_data/emergency_department_uses_table.csv', index=False)

unplanned_inpatient_admissions_table_df = pd.DataFrame(
  np.array(unplanned_inpatient_admissions_table),
  columns=['id', 'group', 'time0', 'time', 'status']
)
print(unplanned_inpatient_admissions_table_df)
unplanned_inpatient_admissions_table_df.to_csv('processed_data/unplanned_inpatient_admissions_table.csv', index=False)
