import json
import pandas as pd
import numpy as np
from enums import EventType, Censor
from utils import deserializeToTimestamp, get_censor_date, get_patient_type, get_death_date, get_enrollment_date, get_emergency_department_uses, get_unplanned_inpatient_admissions
import warnings

'''
Example of patient_events:
    id  patient_type patient_type_description  event_type event_type_description  event_date
22   9             0                    USUAL          -1             ED_NOADMIT  2021-05-09
23   9             0                    USUAL          -1             ED_NOADMIT  2021-05-12
24   9             0                    USUAL           1               ED_ADMIT  2021-08-30
25   9             0                    USUAL           1               ED_ADMIT  2021-12-06
26   9             0                    USUAL           1               ED_ADMIT  2022-01-18
'''
def convert_patient_events_to_preschema(patient_events, start_dt, end_dt, group):
  event_dates = patient_events['event_date'].to_list()
  event_dts = [start_dt] + [deserializeToTimestamp(event_date) for event_date in event_dates] + [end_dt]
  days = [(event_dts[i+1]-event_dts[i]).days for i in range(len(event_dts)-1)]

  preschema = []
  time0 = 0
  for idx, d_time in enumerate(days):
    time = time0 + d_time
    preschema.append([i, group, time0, time, 0 if idx == len(days)-1 else 1])
    time0 = time

  return preschema

# output schema
# - id
# - group: 0 (usual) or 1 (sparkle)
# - time0
# - time
# - status: 0 (censored) or 1 (event occured)

with open('processed_data/patients.json', 'r') as f:
  patients = json.load(f)

events = pd.read_csv("processed_data/events.csv")

emergency_department_uses_preschema_of_all_patients = []
unplanned_inpatient_admissions_preschema_of_all_patients = []

for i in range(1,241):
  start_date = get_enrollment_date(events, i)
  start_dt = deserializeToTimestamp(start_date)

  death_date = get_death_date(events, i)
  death_dt = deserializeToTimestamp(death_date)
  censor_dt = get_censor_date()
  end_dt = censor_dt if (death_dt is None) or (death_dt > censor_dt) else death_dt

  group = get_patient_type(patients, i)

  if (start_dt is None) or (censor_dt < start_dt):
    raise ValueError('patient {0} has invalid or no start date'.format(i))

  emergency_department_uses = get_emergency_department_uses(events, i)
  emergency_department_uses_preschema_of_patient = convert_patient_events_to_preschema(emergency_department_uses, start_dt, end_dt, group)
  emergency_department_uses_preschema_of_all_patients += emergency_department_uses_preschema_of_patient

  unplanned_inpatient_admissions = get_unplanned_inpatient_admissions(events, i)
  unplanned_inpatient_admissions_preschema_of_patient = convert_patient_events_to_preschema(unplanned_inpatient_admissions, start_dt, end_dt, group)
  unplanned_inpatient_admissions_preschema_of_all_patients += unplanned_inpatient_admissions_preschema_of_patient

emergency_department_uses_schema = pd.DataFrame(
  np.array(emergency_department_uses_preschema_of_all_patients),
  columns=['id', 'group', 'time0', 'time', 'status']
)
print(emergency_department_uses_schema)

emergency_department_uses_schema.to_csv('processed_data/emergency_department_uses_analysis.csv', index=False)

unplanned_inpatient_admissions_schema = pd.DataFrame(
  np.array(unplanned_inpatient_admissions_preschema_of_all_patients),
  columns=['id', 'group', 'time0', 'time', 'status']
)
print(unplanned_inpatient_admissions_schema)

unplanned_inpatient_admissions_schema.to_csv('processed_data/unplanned_inpatient_admissions_analysis.csv', index=False)
