from enum import IntEnum

class EventType(IntEnum):
  OUTPATIENT = -2
  ED_NOADMIT = -1
  ENROLLMENT = 0
  ED_ADMIT = 1
  INPATIENT = 2
  HDU = 3
  ICU = 4
  DEATH = 5

class PatientType(IntEnum):
  USUAL = 0
  SPARKLE = 1

class Gender(IntEnum):
  FEMALE = 0
  MALE = 1

class Censor(IntEnum):
  CENSORED = 0
  EVENT_OCCURRED = 1
