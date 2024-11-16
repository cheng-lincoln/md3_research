from datetime import datetime
import json
import pandas as pd
from enums import EventType
from utils import serializeTimestamp, deserializeToTimestamp
from build_patients import PatientsData

class Event:
  """
  This class stores information of an event.

  Attributes:
    patient_id (int): ID of the patient involved
    type (EventType): What event occurred
    date (datetime): When the event occured
  """

  def __init__(self, patient_id, event_type, event_date):
    """
    Parameters:
      patient_id (int): ID of the patient involved
      event_type (EventType): What event occurred
      event_date (datetime): When the event occured
    """
    self.patient_id = patient_id
    self.type = event_type
    self.date = event_date

  def __repr__(self):
    return json.dumps(
      {
        'patient_id': self.patient_id,
        'event_type': self.type,
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
    return EventType(self.type).name

  def describeEventDate(self):
    """
    Returns:
      str: The event date in descriptive form.
    """
    return serializeTimestamp(self.date)

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

class EventsData:
  """
  This immutable object helps to write events data to and from storage.
  Omce initialized, events cannot be added or removed.

  Attributes:
    events_df (DataFrame): a pandas DataFrame of all the events
    patientsData (PatientsData): patient information
  """

  def __init__(self, events_df, patientsData):
    """
    Parameters:
      events_df (DataFrame): a pandas DataFrame of all events
      patientsData (PatientsData): patient information
    """
    self.events_df = events_df.sort_values(by=['id', 'event_date'])
    self.patientsData = patientsData

  def getPatientType(self, patient_id):
    return self.patientsData.getPatient(patient_id).type

  def findDeathDate(self, patient_id):
    """
    Retrieves the death date of a given patient, if any

    Parameters:
      patient_id (int): ID of the patient

    Returns:
      datetime: date of death
      None: if no death date found
    """
    event = self.events_df.loc[
      (self.events_df['id'] == patient_id) & (self.events_df['event_type'] == EventType.DEATH)
    ]

    if len(event) > 1:
      raise ValueError('there are >1 DEATH events for patient', patient_id)

    return deserializeToTimestamp(event['event_date'].values[0]) if not event.empty else None

  def findEnrollmentDate(self, patient_id):
    """
    Retrieves the enrollment date of a given patient

    Parameters:
      patient_id (int): ID of the patient

    Returns:
      datetime: date of enrollment
    """
    event = self.events_df.loc[(self.events_df['id'] == patient_id) & (self.events_df['event_type'] == EventType.ENROLLMENT)]

    if event.empty:
      raise ValueError('there are no ENROLLMENT events for patient', patient_id)

    if len(event) > 1:
      raise ValueError('there are >1 ENROLLMENT events for patient', patient_id)

    return deserializeToTimestamp(event['event_date'].values[0])

  def findPostEnrollmentEvents(self, patient_id):
    """
    Retrieves all events after enrollment

    Parameters:
      patient_id (int): ID of the patient

    Returns:
      DataFrame.loc: all post enrollment events of a patient
    """
    all_events = self.events_df.loc[self.events_df['id'] == patient_id].sort_values(by=['event_date'])

    all_postenrollment_events = all_events.loc[(all_events['event_type'] == EventType.ENROLLMENT).idxmax():]

    return all_postenrollment_events

  def findEmergencyDepartmentUses(self, patient_id):
    """
    Retrieves all emergency department uses AFTER enrollment

    Parameters:
      patient_id (int): ID of the patient

    Returns:
      DataFrame.loc: all emergency department uses AFTER enrollment
    """
    postEnrollmentEvents = self.findPostEnrollmentEvents(patient_id)

    return postEnrollmentEvents.loc[
      (postEnrollmentEvents['event_type'] == EventType.ED_ADMIT) |
      (postEnrollmentEvents['event_type'] == EventType.ED_NOADMIT)
    ]

  def findUnplannedInpatientAdmissions(self, patient_id):
    """
    Retrieves all unplanned inpatient admissions AFTER enrollment

    Parameters:
      patient_id (int): ID of the patient

    Returns:
      DataFrame.loc: all unplanned inpatient admissions AFTER enrollment
    """
    postEnrollmentEvents = self.findPostEnrollmentEvents(patient_id)

    return postEnrollmentEvents.loc[
      (postEnrollmentEvents['event_type'] == EventType.ED_ADMIT)
    ]

  def save(self, loc='processed_data/events.csv'):
    """
    Saves events data to disk.

    Parameters:
      loc (str): Location on disk to save to. Uses default location if none provided.
    """
    print(self.events_df)
    self.events_df.to_csv(loc, index=False)
    return

  @classmethod
  def load(cls, loc='processed_data/events.csv'):
    """
    Loads events data from disk.

    Parameters:
      loc (str): Location on disk to load from. Uses default location if none provided.

    Returns:
      EventsData: an EventsData object
    """
    events_df = pd.read_csv(loc)
    return EventsData(events_df, PatientsData.load())

  @classmethod
  def fromEvents(cls, events):
    """
    Creates EventsData from Event[]

    Parameters:
      events (Event[]): the list of events

    Returns:
      EventsData: an EventsData object
    """
    patientsData = PatientsData.load()

    events_transposed = {
    'id': [], # int[]
    'patient_type': [],
    'patient_type_description': [],

    'event_type': [],
    'event_type_description': [],

    'event_date': [] # str[]
    }

    for event in events:
      patient = patientsData.getPatient(event.patient_id)

      events_transposed['id'].append(patient.id)
      events_transposed['patient_type'].append(patient.type)
      events_transposed['patient_type_description'].append(patient.describePatientType())

      events_transposed['event_type'].append(event.type)
      events_transposed['event_type_description'].append(event.describeEventType())

      events_transposed['event_date'].append(serializeTimestamp(event.date))

    events_df = pd.DataFrame(data=events_transposed)

    return EventsData(events_df, patientsData)

# -------
events = [] # Events[]

enrollment_events = pd.read_excel('data/enrollment_events.xlsx')
for index, row in enrollment_events.iterrows():
  enrollment_event = extractEnrollmentEvent(row)
  events.append(enrollment_event)

# only add ED events with no admission
ed_events = pd.read_excel('data/emergency_department_events.xlsx')
for index, row in ed_events.iterrows():
  ed_event = extractEmergencyDepartmentEvent(row)
  if ed_event.type == EventType.ED_NOADMIT:
    events.append(ed_event)

death_events = pd.read_excel('data/death_events.xlsx')
for index, row in death_events.iterrows():
  death_event = checkForDeathEvent(row)
  if not death_event is None:
    events.append(death_event)

# Now we want to transform our Events[] into a transposed form so that pandas can create a DataFrame with it.
# We also want to add in patient_type information for each event

eventsData = EventsData.fromEvents(events)
eventsData.save()
