from datetime import datetime
import numpy as np
from enums import PatientType, PatientCompliance

DATE_FORMAT = '%Y-%m-%d'

def serializeTimestamp(timestamp):
  """
  Converts a datetime to str in (e.g 2024-04-30) format

  Returns:
    str: the str equivalent
  """
  return timestamp.strftime(DATE_FORMAT)

def deserializeToTimestamp(timestring):
  """
  Converts a str to datetime in (e.g 2024-04-30) format

  Returns:
    datetime: the datetime equivalent
  """
  return datetime.strptime(timestring, DATE_FORMAT) if timestring is not None else None

def get_censor_date():
  """
  Returns:
    numpy.datetime64: The censor date used
  """
  return np.datetime64(deserializeToTimestamp('2024-04-30'))

def findITTGroup(patient_type, patient_compliance):
  """
  Finds out which Intention-To-Treat group a patient should be in

  Parameters:
    patient_type (PatientType)
    patient_compliance (PatientCompliance)

  Returns:
    (int): 0 = usual, 1 = sparkle
  """
  return 1 if patient_type == PatientType.SPARKLE else 0

def findATGroup(patient_type, patient_compliance):
  """
  Finds out which As-Treated group a patient should be in

  Parameters:
    patient_type (PatientType)
    patient_compliance (PatientCompliance)

  Returns:
    (int): 0 = usual or sparkle-noncompliant, 1 = sparkle-compliant
  """
  return 1 if (patient_type == PatientType.SPARKLE and patient_compliance == PatientCompliance.SPARKLE_COMPLIANT) else 0
