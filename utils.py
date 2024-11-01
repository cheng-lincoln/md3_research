from datetime import datetime
from enums import EventType

def serializeTimestamp(timeStamp):
  return timeStamp.strftime('%Y-%m-%d')

def deserializeToTimestamp(timeString):
  return datetime.strptime(timeString, '%Y-%m-%d') if timeString is not None else None

def get_censor_date():
  return deserializeToTimestamp('2024-04-30')

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

def get_emergency_department_uses(events, patient_id):
  events_after_enrollment = get_events_after_enrollment(events, patient_id)

  return events_after_enrollment.loc[
    (events_after_enrollment['event_type'] == EventType.ED_ADMIT) |
    (events_after_enrollment['event_type'] == EventType.ED_NOADMIT)
  ]

def get_unplanned_inpatient_admissions(events, patient_id):
  events_after_enrollment = get_events_after_enrollment(events, patient_id)

  return events_after_enrollment.loc[
    (events_after_enrollment['event_type'] == EventType.ED_ADMIT)
  ]

def get_events_after_enrollment(events, patient_id):
  all_patient_events = events.loc[events['id'] == patient_id].sort_values(by=['event_date'])

  all_patient_events_after_enrollment = all_patient_events.loc[(all_patient_events['event_type'] == EventType.ENROLLMENT).idxmax():]

  return all_patient_events_after_enrollment
