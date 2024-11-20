from datetime import datetime
import numpy as np
from enums import PatientType, PatientCompliance
import math

DATE_FORMAT = '%Y-%m-%d'

LEFT_HALF_BAR = u'\u258c'
RIGHT_HALF_BAR = u'\u2590'
FULL_BAR = u'\u2588'

def serialize_timestamp(timestamp):
  """
  Converts a datetime to str in (e.g 2024-04-30) format

  Returns:
    str: the str equivalent
  """
  return timestamp.strftime(DATE_FORMAT)

def deserialize_to_timestamp(timestring):
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
  return np.datetime64(deserialize_to_timestamp('2024-04-30'))

def find_itt_group(patient_type, patient_compliance):
  """
  Finds out which Intention-To-Treat group a patient should be in

  Parameters:
    patient_type (PatientType)
    patient_compliance (PatientCompliance)

  Returns:
    (int): 0 = usual, 1 = sparkle
  """
  return 1 if patient_type == PatientType.SPARKLE else 0

def find_at_group(patient_type, patient_compliance):
  """
  Finds out which As-Treated group a patient should be in

  Parameters:
    patient_type (PatientType)
    patient_compliance (PatientCompliance)

  Returns:
    (int): 0 = usual or sparkle-noncompliant, 1 = sparkle-compliant
  """
  return 1 if (patient_type == PatientType.SPARKLE and patient_compliance == PatientCompliance.SPARKLE_COMPLIANT) else 0

def barify(numerator, denominator, resolution):
  """
  Creates an ascii bar to represent percentage

  Parameters:
    numerator (int):
    denominator (int):
    resolution (int): the number of fragments to represent 100%

  Returns:
    (str): an ascii bar
  """
  if type(numerator) is str:
    try:
      numerator = int(numerator)
    except ValueError:
      numerator = float(numerator)

  bar = ''
  n_fragments = math.floor(resolution * numerator / denominator)
  while n_fragments > 0:
    if n_fragments >= 2:
      bar += FULL_BAR
    elif n_fragments < 2:
      bar += LEFT_HALF_BAR
    n_fragments -= 2

  return bar
