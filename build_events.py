import json
import pandas as pd
from enums import EventType, PatientType
from utils import serializeTimestamp

def addToEvents(events, patient_id, patient_type, event_type, event_date):
  events['id'].append(int(patient_id)) # make id int for sortability

  events['patient_type'].append(patient_type)
  events['patient_type_description'].append(PatientType(patient_type).name)

  events['event_type'].append(event_type)
  events['event_type_description'].append(EventType(event_type).name)

  events['event_date'].append(event_date)

  return events

#==========================================================

with open('processed_data/patients.json', 'r') as f:
  patients = json.load(f)

events = {
  'id': [],
  'patient_type': [],
  'patient_type_description': [],

  'event_type': [],
  'event_type_description': [],

  'event_date': []
}

ane = pd.read_excel('data/A&E.xlsx')
for index, row in ane.iterrows():
  patient_id = str(row['record_id'])
  patient_info = patients[patient_id]

  addToEvents(
    events,
    patient_id,
    patient_info['patient_type'],
    EventType.ED_ADMIT if row['Discharge Type Description'] == 'I/P Admission' else EventType.ED_NOADMIT,
    serializeTimestamp(row['Admit/Visit Date'])
  )

enrollment = pd.read_excel('data/SPARKLE_enrollment.xlsx')
for index, row in enrollment.iterrows():
  patient_id = str(row['record_id'])
  patient_info = patients[patient_id]

  addToEvents(
    events,
    patient_id,
    patient_info['patient_type'],
    EventType.ENROLLMENT,
    serializeTimestamp(row['Appt_Date'])
  )

death = pd.read_excel('data/Death Data.xlsx')
for index, row in death.iterrows():
  patient_id = str(row['Record_id'])
  patient_info = patients[patient_id]

  if not pd.isnull(row['Deathdate']):
    addToEvents(
      events,
      patient_id,
      patient_info['patient_type'],
      EventType.DEATH,
      serializeTimestamp(row['Deathdate'])
    )

events_df = pd.DataFrame(data=events)
events_df = events_df.sort_values(by=['id', 'event_date'])
print(events_df)
events_df.to_csv('processed_data/events.csv', index=False)
