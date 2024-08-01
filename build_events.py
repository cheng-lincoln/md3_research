import json
import pandas as pd
from enums import EventType, PatientType, Gender
from utils import serializeTimestamp

def addToEvents(events, patient, event_type, event_date):
  # TODO: validate arguments

  patient_type = patient['patient_type']
  gender = patient['gender']

  events['id'].append(int(patient['id'])) #make id int for sortability
  events['patient_type'].append(patient_type)
  events['gender'].append(gender)
  events['event_type'].append(event_type)
  events['event_date'].append(event_date)

  events['patient_type_description'].append(PatientType(patient_type).name)
  events['gender_description'].append(Gender(gender).name)
  events['event_type_description'].append(EventType(event_type).name)

  return events

#==========================================================

with open('results/patients.json', 'r') as f:
  patients = json.load(f)

events = {
  'id': [],
  'patient_type': [],
  'gender': [],
  'event_type': [],
  'event_date': [],

  'patient_type_description': [],
  'gender_description': [],
  'event_type_description': []
}

ane = pd.read_excel('data/ANE.xlsx')
for index, row in ane.iterrows():
  id = str(row['record_id'])
  patient_with_id = patients[id]
  patient_with_id['id'] = id

  addToEvents(
    events,
    patient_with_id,
    EventType.ED_ADMIT if row['Discharge_Type_Description'] == 'I/P Admission' else EventType.ED_NOADMIT,
    serializeTimestamp(row['Admit_Visit_Date'])
  )

hdu = pd.read_excel('data/HD.xlsx')
# TODO: clean up "duplicate" HD events
for index, row in hdu.iterrows():
  id = str(row['record_id'])
  patient_with_id = patients[id]
  patient_with_id['id'] = id

  if row['Movement_Category_Description'] != 'Discharge':
    addToEvents(
      events,
      patient_with_id,
      EventType.HDU,
      serializeTimestamp(row['Admit_Date'])
    )

icu = pd.read_excel('data/ICU.xlsx')
for index, row in icu.iterrows():
  id = str(row['record_id'])
  patient_with_id = patients[id]
  patient_with_id['id'] = id

  if row['Movement_Category_Description'] != 'Discharge':
    addToEvents(
      events,
      patient_with_id,
      EventType.ICU,
      serializeTimestamp(row['Admit_Date'])
    )

inpatient = pd.read_excel('data/Inpatient.xlsx')
for index, row in inpatient.iterrows():
  id = str(row['record_id'])
  patient_with_id = patients[id]
  patient_with_id['id'] = id

  addToEvents(
    events,
    patient_with_id,
    EventType.INPATIENT,
    serializeTimestamp(row['Admit_Visit_Date'])
  )

death = pd.read_excel('data/Death_Details.xlsx')
for index, row in death.iterrows():
  id = str(row['record_id'])
  patient_with_id = patients[id]
  patient_with_id['id'] = id

  addToEvents(
    events,
    patient_with_id,
    EventType.ENROLLMENT,
    serializeTimestamp(row['Appt_Date'])
  )

  if not pd.isnull(row['Date_of_Death']):
    addToEvents(
      events,
      patient_with_id,
      EventType.DEATH,
      serializeTimestamp(row['Date_of_Death'])
    )

events_df = pd.DataFrame(data=events)
events_df = events_df.sort_values(by=['id', 'event_date'])
print(events_df)
events_df.to_csv('results/events.csv', index=False)
