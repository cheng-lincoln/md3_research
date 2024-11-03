import pandas as pd
import json
from enums import PatientType

def upsertPatient(patients, id, patient_type):
  #TODO: validate arguments

  #Create Patient if patient does not exist
  if not id in patients:
    patients[id] = {
      'patient_type': None
    }

  if patient_type is not None:
    patients[id]['patient_type'] = patient_type

  return

patients = {}

# Is a patient SPARKLE or normal?
patient_info = pd.read_excel('data/Allocated groups of patients.xlsx')
for index, row in patient_info.iterrows():
  upsertPatient(
    patients,
    id=row['REDCap_No'],
    patient_type=PatientType.SPARKLE if row['Combined_data_allocation'] == 'SPARKLE' else PatientType.USUAL
  )

with open('processed_data/patients.json', 'w') as f:
    json.dump(patients, f, sort_keys=True, indent=2)
