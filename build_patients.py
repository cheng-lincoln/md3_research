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

class PatientsData:
  """
  This object helps to write and retrieve patient information to and from storage.

  Attributes:
    patients ({<patient_id>: Patient}): A dictionary of Patient objects
  """

  def __init__(self):
    """
    Initializes an empty PatientsData object
    """
    self.patients = {} # {<patient_id>: Patient}

  def addPatient(self, patient):
    """
    Adds a patient

    Parameters:
      patient (Patient): The patient to be added
    """
    if patient.id in self.patients:
      raise ValueError('Cannot add patient to PatientsData object because patient already exists')

    self.patients[patient.id] = patient

  def getPatient(self, patient_id):
    """
    Retrieves a patient given the patient's ID

    Parameters:
      patient_id (int): ID of the patient to retrieve

    Returns:
      Patient: the respective Patient
    """
    if not patient_id in self.patients:
      raise ValueError('Patient {0} does not exist in PatientsData object'.format(patient_id))

    return self.patients[patient_id]

  def save(self, loc='processed_data/patients.json'):
    """
    Saves patients data to disk.

    Parameters:
      loc (str): Location on disk to save to. Uses default location if none provided.
    """
    storage_obj = {}

    for patient_id, patient in self.patients.items():
      storage_obj[patient_id] = {
        'patient_type': patient.type
      }

    with open(loc, 'w') as f:
      json.dump(storage_obj, f, sort_keys=True, indent=2)

  @classmethod
  def load(cls, loc='processed_data/patients.json'):
    """
    Loads patients data from disk.

    Parameters:
      loc (str): Location on disk to load from. Uses default location if none provided.

    Returns:
      PatientsData: a PatientsData object
    """
    with open(loc, 'r') as f:
      storage_obj = json.load(f)

    patientsData = PatientsData()

    for patient_id, patient_info in storage_obj.items():
      patientsData.addPatient(
        Patient(
          int(patient_id),
          patient_info['patient_type']
        )
      )

    return patientsData

# -------
patientsData = PatientsData()

patients_info = pd.read_excel('data/patient_information.xlsx')
for index, row in patients_info.iterrows():
  patient = extractPatient(row)
  patientsData.addPatient(patient)

patientsData.save()
