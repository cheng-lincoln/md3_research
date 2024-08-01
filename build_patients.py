import pandas as pd
import json
from enums import PatientType, Gender
from utils import serializeTimestamp

def createOrUpdatePatient(patients, id, patient_type, gender):
  #TODO: validate arguments

  #Create Patient if patient does not exist
  if not id in patients:
    patients[id] = {
      'patient_type': None,
      'gender': None
    }

  if patient_type is not None:
    patients[id]['patient_type'] = patient_type

  if gender is not None:
    patients[id]['gender'] = gender

  return

#========================================================
patients = {}

demographics = pd.read_excel('data/Allocated groups of patients.xlsx')
for index, row in demographics.iterrows():
  createOrUpdatePatient(
    patients,
    id=row['REDCap_No'],
    patient_type=PatientType.SPARKLE if row['Combined_data_allocation'] == 'SPARKLE' else PatientType.USUAL,
    gender=None
  )

death_details = pd.read_excel('data/Death_Details.xlsx')
for index, row in death_details.iterrows():
  createOrUpdatePatient(
    patients,
    id=row['record_id'],
    patient_type=None,
    gender=Gender.MALE if row['PT_GEN'] == 'M' else Gender.FEMALE
  )

with open('results/patients.json', 'w') as f:
    json.dump(patients, f, sort_keys=True, indent=2)
