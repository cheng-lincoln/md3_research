import pandas as pd
import numpy as np
from utils import findATGroup, findITTGroup
from enums import Censor, EventType
from build_events import EventsData

class AndersenGillFormatter:
  """
  Creates an object that helps format events of a patient into Andersen-Gill Table format.

  Attributes:
    patient_id (int): ID of the patient
    start_date (numpy.datetime64): start date used in the analysis (enrollment date)
    end_date (numpy.datetime64): end date used in the analysis (derived death date, if any, and censor date)
    itt (int): 0 = usual, 1 = sparkle
    at (int): 0 = usual or sparkle-noncompliant, 1 = sparkle-compliant
    TODO pp (int): 0 = usual, 1 = sparkle-compliant
    emergency_department_uses (DataFrame.loc): all post-enrollment emergency department events of the patient
    unplanned_inpatient_admissions (DataFrame.loc): all post-enrollment unplanned inpatient admission events of the patient
  """

  def __init__(self, patient_id, eventsData):
    """
    Parameters:
      patient_id (int): ID of the patient
      eventsData (EventsDAta): an EventsData object
    """
    start_date, end_date = eventsData.findEffectiveStartEndDates(patient_id)
    self.start_date = start_date
    self.end_date = end_date

    patient_type = eventsData.getPatientType(patient_id)
    patient_compliance = eventsData.getPatientCompliance(patient_id)
    self.itt = findITTGroup(patient_type, patient_compliance)
    self.at = findATGroup(patient_type, patient_compliance)

    self.emergency_department_uses = eventsData.findEmergencyDepartmentUsesBetween(
      patient_id,
      self.start_date,
      self.end_date
    )

    self.unplanned_inpatient_admissions = eventsData.findUnplannedInpatientAdmissionsBetween(
      patient_id,
      self.start_date,
      self.end_date
    )

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
      id (int), itt (int), time0 (int), time (int), status (int)
      [
        [ , , , , ],
        [ , , , , ],
        ...
      ]
    """
    # Somehow when we convert to_list, pandas converts all numpy.datetime64 to pd.Timestamp -.-
    event_dates = events['event_date'].to_list()
    event_timestamps = [pd.Timestamp(self.start_date)] + [event_date for event_date in event_dates] + [pd.Timestamp(self.end_date)]
    days = [(event_timestamps[i+1]-event_timestamps[i]).days for i in range(len(event_timestamps)-1)]

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
      table.append([self.patient_id, self.itt, self.at, time0, time, Censor.CENSORED if idx == len(days)-1 else Censor.EVENT_OCCURRED])
      time0 = time

    masked_table = [row for row, keep in zip(table, to_keep) if keep]

    return masked_table

# -------
'''
We want to build the Andersen-Gill Table from all the

Andersen-Gill Table has these columns:
- id
- itt: 0 (usual) or 1 (sparkle)
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
  columns=['id', 'itt', 'at', 'time0', 'time', 'status']
)
print(emergency_department_uses_table_df)
emergency_department_uses_table_df.to_csv('processed_data/emergency_department_uses_table.csv', index=False)

unplanned_inpatient_admissions_table_df = pd.DataFrame(
  np.array(unplanned_inpatient_admissions_table),
  columns=['id', 'itt', 'at', 'time0', 'time', 'status']
)
print(unplanned_inpatient_admissions_table_df)
unplanned_inpatient_admissions_table_df.to_csv('processed_data/unplanned_inpatient_admissions_table.csv', index=False)
