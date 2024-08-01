import json
import pandas as pd
import numpy as np
from enums import EventType, Censor
from utils import deserializeToTimestamp, get_healthcare_utilization_censor_datetime, get_patient_type, get_death_date, get_enrollment_date, get_inpatient_admissions_after_enrollment
import warnings

# output schema
# - id
# - group: 0 (usual) or 1 (sparkle)
# - time0
# - time
# - status: 0 (censored) or 1 (event occured)

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

  group = get_patient_type(patients, i)

  if start_dt and (hu_censor_dt > start_dt):
    inpatient_admissions_after_enrollment = get_inpatient_admissions_after_enrollment(events, i)

    # A patient admitted to ED, and then ICU on same day will have 2 inpatient records of the same day
    inpatient_admissions_after_enrollment = inpatient_admissions_after_enrollment.drop_duplicates(subset=['event_date'], keep='first')

    event_dates = inpatient_admissions_after_enrollment['event_date'].to_list()
    end_dt = hu_censor_dt if (death_dt is None) or (death_dt > hu_censor_dt) else death_dt
    event_dts = [start_dt] + [deserializeToTimestamp(event_date) for event_date in event_dates] + [end_dt]
    days = [(event_dts[i+1]-event_dts[i]).days for i in range(len(event_dts)-1)]

    time0 = 0
    for idx, d_time in enumerate(days):
      time = time0 + d_time
      data.append([i, group, time0, time, 0 if idx == len(days)-1 else 1])
      time0 = time
  else:
    warnings.warn('patient {0} has invalid/no start date'.format(i))

analysis = pd.DataFrame(
  np.array(data),
  columns=['id', 'group', 'time0', 'time', 'status']
)
print(analysis)

analysis.to_csv('results/analysis_recurrent_visits.csv', index=False)
