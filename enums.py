from enum import IntEnum

class EventType(IntEnum):
  ENROLLMENT = 0
  DEATH = 1
  ED_NOADMIT = 2

  ADMIT_ED = 31
  ADMIT_CLINIC = 32
  ADMIT_ELECTIVE = 33

  ADMIT_ED_ENDS = 41
  ADMIT_CLINIC_ENDS = 42
  ADMIT_ELECTIVE_ENDS = 43


class PatientType(IntEnum):
  USUAL = 0
  SPARKLE = 1

class Censor(IntEnum):
  CENSORED = 0
  EVENT_OCCURRED = 1
