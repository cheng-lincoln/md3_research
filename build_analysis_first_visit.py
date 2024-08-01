import pandas as pd
import numpy as np
from datetime import datetime
import json
from enums import EventType, Censor
from utils import deserializeToTimestamp, get_healthcare_utilization_censor_datetime, get_patient_type, get_death_date, get_enrollment_date, get_inpatient_admissions_after_enrollment
import warnings

def get_first_inpatient_date(events, patient_id):
  inpatient_admissions_after_enrollment = get_inpatient_admissions_after_enrollment(events, patient_id)
  return inpatient_admissions_after_enrollment.iloc[0]['event_date'] if not inpatient_admissions_after_enrollment.empty else None

# output schema
# - id
# - time
# - cens: 0 (censored) or 1 (event occured)
# - treat: 0 (usual) or 1 (sparkle)

# scenarios
# 1) patient with at least 1 inpatient visit (e.g patient 2)
# 2) patient never had an inpatient visit until healthcare utilization censor date (e.g patient 4)
# 3) patient never had an inpatient visit until death (e.g patient 3)
# 4) patient never had an inpatinet visit until death, but death date is after healthcare utilization date

with open('results/patients.json', 'r') as f:
  patients = json.load(f)

events = pd.read_csv("results/events.csv")

data = []

for i in range(1,241):
  start_date = get_enrollment_date(events, i)
  start_dt = deserializeToTimestamp(start_date)

  hu_censor_dt = get_healthcare_utilization_censor_datetime()

  death_date = get_death_date(events, i)
  death_dt = deserializeToTimestamp(death_date)

  if start_dt and (hu_censor_dt > start_dt): # patients must have an valid enrollment date
    treat = get_patient_type(patients, i)

    first_inpatient_date = get_first_inpatient_date(events, i)
    first_inpatient_dt = deserializeToTimestamp(first_inpatient_date)

    if first_inpatient_dt: # scenario 1
      time = (first_inpatient_dt - start_dt).days

      row = [i, time, Censor.EVENT_OCCURRED, treat]
      data.append(row)

    elif death_dt: # scenario 3 & 4
      time = (death_dt - start_dt).days if (death_dt < hu_censor_dt) else (hu_censor_dt - start_dt).days

      row = [i, time, Censor.CENSORED, treat]
      data.append(row)

    else: # scenario 2
      time = (hu_censor_dt - start_dt).days

      row = [i, time, Censor.CENSORED, treat]
      data.append(row)
  else:
    warnings.warn('patient {0} has invalid/no start date'.format(i))

analysis = pd.DataFrame(
  np.array(data),
  columns=['id', 'time', 'cens', 'treat']
)
print(analysis)

analysis.to_csv('results/analysis_first_visit.csv', index=False)
