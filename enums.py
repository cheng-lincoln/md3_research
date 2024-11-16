from enum import IntEnum

class EventType(IntEnum):
  # Values should be sortable: if 2 events occur on the same day, which should come first?
  ENROLLMENT = 0
  ED_NOADMIT = 1

  ADMIT_ED = 21
  ADMIT_CLINIC = 22
  ADMIT_ELECTIVE = 23

  ADMIT_ED_ENDS = 31
  ADMIT_CLINIC_ENDS = 32
  ADMIT_ELECTIVE_ENDS = 33

  DEATH = 999

class PatientType(IntEnum):
  USUAL = 0
  SPARKLE = 1

class Censor(IntEnum):
  CENSORED = 0
  EVENT_OCCURRED = 1
