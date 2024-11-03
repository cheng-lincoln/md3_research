import pandas as pd
import json
from enums import PatientType

class Patient:
  """
  This class stores information of a patient.

  Attributes:
    id (int): The ID of the patient
    type (PatientType): Whether the patient is randomized to SPARKLE or Usual intervention
  """

  def __init__(self, id, patient_type):
    """
    Parameters:
      id (int): The ID of the patient
      ptype (PatientType): Whether the patient is randomized to SPARKLE or Usual intervention
    """
    self.id = id
    self.type = patient_type

  def __repr__(self):
    return json.dumps(
      {
        'id': self.id,
        'patient_type': self.type,
        'patient_type_description': self.describePatientType()
      },
      indent=2
    )

  def describePatientType(self):
    """
    Returns:
      str: The patient type (i.e SPARKLE or Usual) in descriptive form.
    """
    return PatientType(self.type).name

def extractPatient(row):
  """
  Extracts patient information from a row in patient_information excel sheet

  Args:
    row (Series): a row from the excel sheet, represented as a Pandas DataFrame's Series

  Returns:
    Patient: A Patient object
  """
  id = row['REDCap_No']
  if not type(id) is int:
    raise ValueError('The id of a patient extracted from the patient_information excel sheet is not an integer type')

  patient_type = row['Combined_data_allocation']
  if (not patient_type == 'SPARKLE') and (not patient_type == 'Usual'):
    raise ValueError('The patient type of a patient extracted from the patient_information excel sheet is neither SPARKLE or Usual')

  return Patient(
    id,
    PatientType.SPARKLE if row['Combined_data_allocation'] == 'SPARKLE' else PatientType.USUAL
  )

# -------
patients = {}

patients_info = pd.read_excel('data/patient_information.xlsx')
for index, row in patients_info.iterrows():
  patient = extractPatient(row)

  patients[str(patient.id)] = {
    'patient_type': patient.type
  }

with open('processed_data/patients.json', 'w') as f:
    json.dump(patients, f, sort_keys=True, indent=2)
