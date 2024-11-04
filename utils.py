from datetime import datetime

def serializeTimestamp(timeStamp):
  """
  Converts a datetime to str in (e.g 2024-04-30) format

  Returns:
    str: the str equivalent
  """
  return timeStamp.strftime('%Y-%m-%d')

def deserializeToTimestamp(timeString):
  """
  Converts a str to datetime in (e.g 2024-04-30) format

  Returns:
    datetime: the datetime equivalent
  """
  return datetime.strptime(timeString, '%Y-%m-%d') if timeString is not None else None

def get_censor_date():
  """
  Returns:
    datetime: The censor date used
  """
  return deserializeToTimestamp('2024-04-30')

