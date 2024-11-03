from enum import IntEnum

class EventType(IntEnum):
  ENROLLMENT = 0
  ED_ADMIT = 1
  ED_NOADMIT = 2
  DEATH = 3

class PatientType(IntEnum):
  USUAL = 0
  SPARKLE = 1

class Censor(IntEnum):
  CENSORED = 0
  EVENT_OCCURRED = 1
