from datetime import datetime
import numpy as np

DATE_FORMAT = '%Y-%m-%d'

def serializeTimestamp(timeStamp):
  """
  Converts a datetime to str in (e.g 2024-04-30) format

  Returns:
    str: the str equivalent
  """
  return timeStamp.strftime(DATE_FORMAT)

def deserializeToTimestamp(timeString):
  """
  Converts a str to datetime in (e.g 2024-04-30) format

  Returns:
    datetime: the datetime equivalent
  """
  return datetime.strptime(timeString, DATE_FORMAT) if timeString is not None else None

def get_censor_date():
  """
  Returns:
    numpy.datetime64: The censor date used
  """
  return np.datetime64(deserializeToTimestamp('2024-04-30'))

