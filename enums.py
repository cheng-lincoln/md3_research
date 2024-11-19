from enum import IntEnum

class EventType(IntEnum):
  # Values should be sortable: if 2 events occur on the same day, which should come first (smaller number should occur first)?
  ENROLLMENT = 0
  ED_NOADMIT = 1

  ADMIT_ED = 21
  ADMIT_CLINIC = 22
  ADMIT_ELECTIVE = 23

  ADMIT_ED_ENDS = 31
  ADMIT_CLINIC_ENDS = 32
  ADMIT_ELECTIVE_ENDS = 33

  DEATH = 999

class Censor(IntEnum):
  CENSORED = 0
  EVENT_OCCURRED = 1

class PatientType(IntEnum):
  USUAL = 0
  SPARKLE = 1

class PatientCompliance(IntEnum):
  # Compliance = completed >= 12 of the IPOS questionnairs (total 16)
  NOT_APPLICABLE = 0
  SPARKLE_COMPLIANT = 10
  SPARKLE_NONCOMPLIANT = 11

class Gender(IntEnum):
  FEMALE = 0
  MALE = 1

class Race(IntEnum):
  CHINESE = 1
  MALAY = 2
  INDIAN = 3
  OTHERS = 4

class MaritalStatus(IntEnum):
  MARRIED = 1
  SINGLE = 2
  DIVORCED_SEPARATED = 3
  WIDOWED = 4

class EducationLevel(IntEnum):
  NO_FORMAL_EDUCATION = 1
  PRIMARY_SCHOOL = 2
  SECONDARY_SCHOOL_OR_ITE = 3
  POST_SECONDARY = 4

class EmploymentStatus(IntEnum):
  FULL_TIME = 1
  PART_TIME = 2
  RETIREE = 3
  HOUSEWIFE = 4
  STUDENT = 5
  UNEMPLOYED = 6
  STOPPED_WORKING_FOR_CAREGIVING = 7
  OTHERS = 8

class Performance(IntEnum):
  UNKNOWN = 0
  FULLY_AMBULATORY = 1
  MOSTLY_AMBULATORY = 2 # < 50% in bed
  MOSTLY_IN_BED = 3 # >= 50% in bed

class CancerTypeLayman(IntEnum):
  LUNG = 1
  HEAD_NECK = 2
  RENAL = 3
  PROSTATE = 4
  GI = 5
  ADRENAL = 6
  APPENDIX = 7
  BLADDER = 8
  BREAST = 9
  GALLBLADDER = 10
  GI_SARCOMA = 11
  LYMPHOMA = 12
  MELANOMA = 13
  TESTIS = 14
  THYMUS = 15
  THYROID = 16
  URETER = 17
  OVARY = 18

class TreatmentType(IntEnum):
  SURGERY = 1
  RADIOTHERAPY = 2
  CHEMOTHERAPY = 3
  IMMUNOTHERAPY = 4
  OTHERS = 5
