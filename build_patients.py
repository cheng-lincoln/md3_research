import pandas as pd
import json
from datetime import datetime
from enums import *

class Patient:
  """
  This class stores information of a patient.

  Attributes:
    id (int): The ID of the patient
    type (PatientType): Whether the patient is randomized to SPARKLE or Usual intervention
    compliance (PatientCompliance): Whether the patient is compliant to SPARKLE intervention (if SPARKLE)
    demographics (Demographics): Demographics of the patient
  """

  def __init__(self, id, patient_type, compliance=None, demographics=None):
    """
    Parameters:
      id (int): The ID of the patient
      patient_type (PatientType): Whether the patient is randomized to SPARKLE or Usual intervention
      compliance (PatientCompliance): Whether the patient is compliant to SPARKLE intervention (if SPARKLE)
    """
    self.id = id
    self.type = patient_type

    # optional
    self.compliance = compliance
    self.demographics = demographics

  def toJSON(self):
    return {
      'id': self.id,
      'patient_type': self.type,
      'compliance': self.compliance,
      'demographics': self.demographics.toJSON(),
      '_description': {
        'patient_type': self.describe_patient_type(),
        'compliance': self.describe_patient_compliance(),
      }
    }

  def __repr__(self):
    return json.dumps(
      self.toJSON(),
      indent=2
    )

  def describe_patient_type(self):
    """
    Returns:
      str: The patient type (i.e SPARKLE or Usual) in descriptive form.
    """
    return PatientType(self.type).name

  def describe_patient_compliance(self):
    """
    Returns:
      str: The patient compliance in descriptive form.
    """
    return PatientCompliance(self.compliance).name

  def set_compliance(self, compliance):
    """
    Parameters:
      compliance (PatientCompliance): Whether the patient is compliant to SPARKLE intervention (if SPARKLE)
    """
    self.compliance = compliance

  def set_demographics(self, demographics):
    """
    Parameters:
      demographics (Demographics): Demographics of the patient
    """
    self.demographics = demographics

class Demographics:
  """
  This class stores demographics (of a patient).

  Attributes:
    gender (Gender):
    race (Race):
    age (int):
    marital_status (MaritalStatus):
    education_level (EducationLevel):
    employment_status (EmploymentStatus):
    performance (Performance):
    cancer_type_layman (CancerTypeLayman):
    treatment_types (TreatmentType[]):
  """
  def __init__(
      self,
      gender,
      age,
      race,
      marital_status,
      education_level,
      employment_status,
      performance,
      cancer_type_layman,
      treatment_types
    ):
    self.gender = gender
    self.age = age
    self.race = race
    self.marital_status = marital_status
    self.education_level = education_level
    self.employment_status = employment_status
    self.performance = performance
    self.cancer_type_layman = cancer_type_layman
    self.treatment_types = treatment_types

  def toJSON(self):
    return {
      'gender': self.gender,
      'race': self.race,
      'age': self.age,
      'marital_status': self.marital_status,
      'education_level': self.education_level,
      'employment_status': self.employment_status,
      'performance': self.performance,
      'cancer_type_layman': self.cancer_type_layman,
      'treatment_types': self.treatment_types,
      '_description': {
        'gender': self.describe_gender(),
        'race': self.describe_race(),
        'marital_status': self.describe_marital_status(),
        'education_level': self.describe_education_level(),
        'employment_status': self.describe_employment_status(),
        'performance': self.describe_performance(),
        'cancer_type_layman': self.describe_cancer_type_layman(),
        'treatment_types': self.describe_treatment_types()
      }
    }

  def __repr__(self):
    return json.dumps(
      self.toJSON(),
      indent=2
    )

  def describe_gender(self):
    return Gender(self.gender).name

  def describe_race(self):
    return Race(self.race).name

  def describe_marital_status(self):
    return MaritalStatus(self.marital_status).name

  def describe_education_level(self):
    return EducationLevel(self.education_level).name

  def describe_employment_status(self):
    return EmploymentStatus(self.employment_status).name

  def describe_performance(self):
    return Performance(self.performance).name

  def describe_cancer_type_layman(self):
    return CancerTypeLayman(self.cancer_type_layman).name

  def describe_treatment_types(self):
    return [
      TreatmentType(treatment_type).name
      for treatment_type
      in self.treatment_types
    ]

def extract_patient(row):
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

def extract_compliance(ipos, patient_id):
  """
  Extracts compliance information of a patient from ipos.xlsx

  Args:
    ipos (DataFrame): the dataframe of the ipos.xlsx file
    patient_id (int): The Patient ID

  Returns:
    int: number of weeks of IPOS questionnaire completed by the patient
  """
  ipos_completed_dates = ipos.loc[
    (ipos['record_id'] == patient_id) &
    ipos['event_name'].str.contains('^ipos_week_(?:1[0-6]{1}|0[1-9]{1})$', regex=True)
  ]['ipos_completed_date'].to_list()

  return sum(1 for ipos_completed_date in ipos_completed_dates if isinstance(ipos_completed_date, datetime))

def extract_demographics(ipos, patient_id):
  """
  Extracts demographics information of a patient from ipos.xlsx

  Args:
    ipos (DataFrame): the dataframe of the ipos.xlsx file
    patient_id (int): The Patient ID

  Returns:
    (Demographics): a demographic object
  """
  patient_demographics = ipos.loc[
    (ipos['record_id'] == patient_id) &
    (ipos['event_name'] == 'demographics')
  ]

  gender = patient_demographics['Male_gender'].values[0]
  age = patient_demographics['pt_age'].values[0]
  race = patient_demographics['pt_race'].values[0]
  marital_status = patient_demographics['pt_marital_status'].values[0]
  education_level = patient_demographics['pt_education_level'].values[0]
  employment_status = patient_demographics['pt_employment'].values[0]
  performance = patient_demographics['pt_performance_status'].values[0]
  cancer_type_layman = patient_demographics['pt_primary_cancer'].values[0]
  TREATMENT_TYPES = [
    TreatmentType.SURGERY,
    TreatmentType.RADIOTHERAPY,
    TreatmentType.CHEMOTHERAPY,
    TreatmentType.IMMUNOTHERAPY,
    TreatmentType.OTHERS
  ]
  treatment_type_flags = [
    patient_demographics['pt_cancer_treatment_type___1'].values[0],
    patient_demographics['pt_cancer_treatment_type___2'].values[0],
    patient_demographics['pt_cancer_treatment_type___3'].values[0],
    patient_demographics['pt_cancer_treatment_type___4'].values[0],
    patient_demographics['pt_cancer_treatment_type___5'].values[0]
  ]
  treatment_types = [row for row, keep in zip(TREATMENT_TYPES, treatment_type_flags) if keep]

  return Demographics(
    gender,
    age,
    race,
    marital_status,
    education_level,
    employment_status,
    performance,
    cancer_type_layman,
    treatment_types
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

  def add_patient(self, patient):
    """
    Adds a patient

    Parameters:
      patient (Patient): The patient to be added
    """
    if patient.id in self.patients:
      raise ValueError('Cannot add patient to PatientsData object because patient already exists')

    self.patients[patient.id] = patient

  def get_patient(self, patient_id):
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
      storage_obj[patient_id] = patient.toJSON()

    with open(loc, 'w') as f:
      json.dump(storage_obj, f, indent=2)

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

    patients_data = PatientsData()

    for patient_id, patient_info in storage_obj.items():
      patients_data.add_patient(
        Patient(
          int(patient_id),
          patient_info['patient_type'],
          patient_info['compliance'],
          Demographics(
            patient_info['demographics']['gender'],
            patient_info['demographics']['age'],
            patient_info['demographics']['race'],
            patient_info['demographics']['marital_status'],
            patient_info['demographics']['education_level'],
            patient_info['demographics']['employment_status'],
            patient_info['demographics']['performance'],
            patient_info['demographics']['cancer_type_layman'],
            patient_info['demographics']['treatment_types']
          )
        )
      )

    return patients_data

# -------
patients_data = PatientsData()

ipos = pd.read_excel('data/ipos.xlsx')

patients_info = pd.read_excel('data/patient_information.xlsx')
for index, row in patients_info.iterrows():
  patient = extract_patient(row)

  ipos_weeks_completed = extract_compliance(ipos, patient.id)
  if (patient.type == PatientType.SPARKLE):
    # see Enums.py for definition of compliance
    patient.set_compliance(
      PatientCompliance.SPARKLE_COMPLIANT if ipos_weeks_completed >= 12
      else PatientCompliance.SPARKLE_NONCOMPLIANT
    )
  else:
    if (ipos_weeks_completed > 0):
      raise ValueError('Patient {0} is usual intervention but has >0 IPOS questionnaires completed'.format(patient.id))

    patient.set_compliance(PatientCompliance.NOT_APPLICABLE)

  demographics = extract_demographics(ipos, patient.id)
  patient.set_demographics(demographics)

  patients_data.add_patient(patient)

patients_data.save()
