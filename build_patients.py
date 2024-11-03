import pandas as pd
import json
from enums import PatientType

class PatientInfo:
  """
  This class patient information.

  Attributes:
    id (int): The ID of the patient
    patient_type (PatientType): Whether the patient is randomized to SPARKLE or Usual intervention
  """

  def __init__(self, id, patient_type):
    """
    Parameters:
      id (int): The ID of the patient
      patient_type (PatientType): Whether the patient is randomized to SPARKLE or Usual intervention
    """
    self.id = id
    self.patient_type = patient_type

def extractPatientInfo(row):
  """
  Extracts patient information from a row in patient_information excel sheet

  Args:
    row (Series): a row from the excel sheet, represented as a Pandas DataFrame's Series

  Returns:
    PatientInfo: A PatientInfo object
  """
  id = row['REDCap_No']
  if not type(id) is int:
    raise ValueError('The id of a patient extracted from the patient_information excel sheet is not an integer type')

  patient_type = row['Combined_data_allocation']
  if (not patient_type == 'SPARKLE') and (not patient_type == 'Usual'):
    raise ValueError('The patient type of a patient extracted from the patient_information excel sheet is neither SPARKLE or Usual')

  return PatientInfo(
    id,
    PatientType.SPARKLE if row['Combined_data_allocation'] == 'SPARKLE' else PatientType.USUAL
  )

# -------
patients = {}

patients_info = pd.read_excel('data/patient_information.xlsx')
for index, row in patients_info.iterrows():
  patient_info = extractPatientInfo(row)

  patients[str(patient_info.id)] = {
    'patient_type': patient_info.patient_type
  }

with open('processed_data/patients.json', 'w') as f:
    json.dump(patients, f, sort_keys=True, indent=2)
