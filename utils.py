from datetime import datetime
from enums import EventType

def serializeTimestamp(timeStamp):
  return timeStamp.strftime('%Y-%m-%d')

def deserializeToTimestamp(timeString):
  return datetime.strptime(timeString, '%Y-%m-%d') if timeString is not None else None

def get_healthcare_utilization_censor_datetime():
  return deserializeToTimestamp('2024-01-31')

def get_patient_type(patients, patient_id):
  return patients[str(patient_id)]['patient_type']

def get_death_date(events, patient_id):
  event = events.loc[(events['id'] == patient_id) & (events['event_type'] == EventType.DEATH)]

  if len(event) > 1:
    raise ValueError('there are >1 DEATH events for patient', patient_id)

  return event['event_date'].values[0] if not event.empty else None

def get_enrollment_date(events, patient_id):
  event = events.loc[(events['id'] == patient_id) & (events['event_type'] == EventType.ENROLLMENT)]

  if len(event) > 1:
    raise ValueError('there are >1 ENROLLMENT events for patient', patient_id)

  return event['event_date'].values[0] if not event.empty else None

def get_inpatient_admissions_after_enrollment(events, patient_id):
  all_patient_events = events.loc[events['id'] == patient_id]
  all_patient_events = all_patient_events.sort_values(by=['event_date'])

  all_patient_events_after_enrollment = all_patient_events.loc[(all_patient_events['event_type'] == EventType.ENROLLMENT).idxmax():]

  all_inpatient_admissions_after_enrollment = all_patient_events_after_enrollment.loc[
    (all_patient_events_after_enrollment['event_type'] == EventType.INPATIENT) |
    (all_patient_events_after_enrollment['event_type'] == EventType.ED_ADMIT) |
    (all_patient_events_after_enrollment['event_type'] == EventType.HDU) |
    (all_patient_events_after_enrollment['event_type'] == EventType.ICU)
  ]

  return all_inpatient_admissions_after_enrollment
