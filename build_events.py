from datetime import datetime
import json
import pandas as pd
from enums import EventType, PatientType
from utils import serializeTimestamp
from build_patients import Patient

class Event:
  """
  This class stores information of an event.

  Attributes:
    patient_id (int): ID of the patient involved
    event_type (EventType): What event occurred
    event_date (datetime): When the event occured
  """

  def __init__(self, patient_id, event_type, event_date):
    """
    Parameters:
      patient_id (int): ID of the patient involved
      event_type (EventType): What event occurred
      event_date (datetime): When the event occured
    """
    self.patient_id = patient_id
    self.event_type = event_type
    self.event_date = event_date

  def __repr__(self):
    return json.dumps(
      {
        'patient_id': self.patient_id,
        'event_type': self.event_type,
        'event_type_description': self.describeEventType(),
        'event_date_description': self.describeEventDate()
      },
      indent=2
    )

  def describeEventType(self):
    """
    Returns:
      str: The event type (e.g ENROLLMENT, ED_ADMIT, ED_NOADMIT, DEATH) in descriptive form.
    """
    return EventType(self.event_type).name

  def describeEventDate(self):
    """
    Returns:
      str: The event date in descriptive form.
    """
    return serializeTimestamp(self.event_date)

def extractEnrollmentEvent(row):
  """
  Extracts enrollement event information from a row in enrollment_events excel sheet

  Args:
    row (Series): a row from the excel sheet, represented as a Pandas DataFrame's Series

  Returns:
    Event: An Event object
  """
  patient_id = row['record_id']
  if not type(patient_id) is int:
    raise ValueError('The patient id extracted from the enrollment_events excel sheet is not an integer type')

  event_date = row['Appt_Date']
  if not isinstance(event_date, datetime):
    raise ValueError('The event date extracted from enrollment events excel_sheet is not a datetime object')

  return Event(
    patient_id,
    EventType.ENROLLMENT,
    event_date
  )

def extractEmergencyDepartmentEvent(row):
  """
  Extracts emergency department event information from a row in emergency_department_events excel sheet

  Args:
    row (Series): a row from the excel sheet, represented as a Pandas DataFrame's Series

  Returns:
    Event: An Event object
  """
  patient_id = row['record_id']
  if not type(patient_id) is int:
    raise ValueError('The patient id extracted from the emergency_department_events excel sheet is not an integer type')

  event_date = row['Admit/Visit Date']
  if not isinstance(event_date, datetime):
    raise ValueError('The event date extracted from emergency_department_events excel_sheet is not a datetime object')

  event_type = EventType.ED_ADMIT if row['Discharge Type Description'] == 'I/P Admission' else EventType.ED_NOADMIT

  return Event(patient_id, event_type, event_date)

def checkForDeathEvent(row):
  """
  Extracts death event information (if any) from a row in death_events excel sheet

  Args:
    row (Series): a row from the excel sheet, represented as a Pandas DataFrame's Series

  Returns:
    Event: An Event object if a death event occured
    OR
    None: None if no death event occured
  """
  event_date = row['Deathdate']
  if pd.isnull(event_date):
    return None

  if not isinstance(event_date, datetime):
    raise ValueError('The death date extracted from death_events excel_sheet is not a datetime object')

  patient_id = row['Record_id']
  if not type(patient_id) is int:
    raise ValueError('The patient id extracted from the death_events excel sheet is not an integer type')

  return Event(patient_id, EventType.DEATH, event_date)

#==========================================================
events = [] # Event[]

enrollment_events = pd.read_excel('data/enrollment_events.xlsx')
for index, row in enrollment_events.iterrows():
  enrollment_event = extractEnrollmentEvent(row)
  events.append(enrollment_event)

ed_events = pd.read_excel('data/emergency_department_events.xlsx')
for index, row in ed_events.iterrows():
  ed_event = extractEmergencyDepartmentEvent(row)
  events.append(ed_event)

death_events = pd.read_excel('data/death_events.xlsx')
for index, row in death_events.iterrows():
  death_event = checkForDeathEvent(row)
  if not death_event is None:
    events.append(death_event)

# Now we want to transform our Events[] into a transposed form so that pandas can create a DataFrame with it.
# We also want to add in patient_type information for each event

with open('processed_data/patients.json', 'r') as f:
  patients = json.load(f)

events_transposed = {
  'id': [], # int[]
  'patient_type': [],
  'patient_type_description': [],

  'event_type': [],
  'event_type_description': [],

  'event_date': [] # str[]
}

for event in events:
  patient = Patient(
   event.patient_id,
   patients[str(event.patient_id)]['patient_type']
  )

  events_transposed['id'].append(patient.id)
  events_transposed['patient_type'].append(patient.patient_type)
  events_transposed['patient_type_description'].append(patient.describePatientType())

  events_transposed['event_type'].append(event.event_type)
  events_transposed['event_type_description'].append(event.describeEventType())

  events_transposed['event_date'].append(serializeTimestamp(event.event_date))

events_df = pd.DataFrame(data=events_transposed)
events_df = events_df.sort_values(by=['id', 'event_date'])
print(events_df)
events_df.to_csv('processed_data/events.csv', index=False)
