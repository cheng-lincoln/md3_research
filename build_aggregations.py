import pandas as pd
from utils import findITTGroup, findATGroup
from enums import *
from build_patients import PatientsData
from build_events import EventsData

def addEmptyRow(results_columns):
  """
  A convenience function to add an empty row to the results table

  Parameters:
    results_columns ({
      'characteristic': [],
      'itt (control)': [], # itt = 0
      'itt (intervention)': []
    }): a transposed object used to eventually create a DataFrame

  Returns:
    results_columns
  """
  results_columns['characteristic'].append('')
  results_columns['itt (control)'].append('')
  results_columns['itt (intervention)'].append('')

  return results_columns

def addBaselineCharacteristics(results_columns, characteristic_name, table, condition):
  """
  A convenience function that adds a row baseline characteristics

  Parameters:
    results_columns ({
      'characteristic': [],
      'itt (control)': [], # itt = 0
      'itt (intervention)': []
    }): a transposed object used to eventually create a DataFrame
    characteristic_name (string): name of the characteristic to aggregate
    table (DataFrame): the table to analyze
    condition (??): example => (patients['gender'] == Gender.FEMALE)

  Returns:
    results_columns
  """
  results_columns['characteristic'].append(characteristic_name)
  results_columns['itt (control)'].append(
    len(table[(table['itt'] == 0) & condition])
  )
  results_columns['itt (intervention)'].append(
    len(table[(table['itt'] == 1) & condition])
  )

  return results_columns

# ---

patientsData = PatientsData.load()

patients_columns = {
  'id': [],
  'patient_type': [],
  'compliance': [],

  'itt': [],
  'at': [],

  'gender': [],
  'race': [],
  'marital_status': [],
  'education_level': [],
  'employment_status': [],
  'performance': [],
  'cancer_type_layman': [],
  'has_treatment_surgery': [],
  'has_treatment_radiotherapy': [],
  'has_treatment_chemotherapy': [],
  'has_treatment_immunotherapy': [],
  'has_treatment_others': [],
}

for patient_id in [i for i in range(1,241) if i != 109]: # exclude patient 109
  patient = patientsData.getPatient(patient_id)
  patients_columns['id'].append(patient.id)
  patients_columns['patient_type'].append(patient.type)
  patients_columns['compliance'].append(patient.compliance)

  patients_columns['itt'].append(findITTGroup(patient.type, patient.compliance))
  patients_columns['at'].append(findATGroup(patient.type, patient.compliance))

  patients_columns['gender'].append(patient.demographics.gender)
  patients_columns['race'].append(patient.demographics.race)
  patients_columns['marital_status'].append(patient.demographics.marital_status)
  patients_columns['education_level'].append(patient.demographics.education_level)
  patients_columns['employment_status'].append(patient.demographics.employment_status)
  patients_columns['performance'].append(patient.demographics.performance)
  patients_columns['cancer_type_layman'].append(patient.demographics.cancer_type_layman)
  patients_columns['has_treatment_surgery'].append(True if TreatmentType.SURGERY in patient.demographics.treatment_types else False)
  patients_columns['has_treatment_radiotherapy'].append(True if TreatmentType.RADIOTHERAPY in patient.demographics.treatment_types else False)
  patients_columns['has_treatment_chemotherapy'].append(True if TreatmentType.CHEMOTHERAPY in patient.demographics.treatment_types else False)
  patients_columns['has_treatment_immunotherapy'].append(True if TreatmentType.IMMUNOTHERAPY in patient.demographics.treatment_types else False)
  patients_columns['has_treatment_others'].append(True if TreatmentType.OTHERS in patient.demographics.treatment_types else False)

patients = pd.DataFrame(data=patients_columns)

# ITT (control vs intervention)
results_columns = {
  'characteristic': [],
  'itt (control)': [], # itt = 0
  'itt (intervention)': [] # itt = 1
}

for gender in Gender:
  addBaselineCharacteristics(results_columns, Gender(gender).name.title(), patients, patients['gender'] == gender)
addEmptyRow(results_columns)

for race in Race:
  addBaselineCharacteristics(results_columns, Race(race).name.title(), patients, patients['race'] == race)
addEmptyRow(results_columns)

for marital_status in MaritalStatus:
  addBaselineCharacteristics(results_columns, MaritalStatus(marital_status).name.title(), patients, patients['marital_status'] == marital_status)
addEmptyRow(results_columns)

for education_level in EducationLevel:
  addBaselineCharacteristics(results_columns, EducationLevel(education_level).name.title(), patients, patients['education_level'] == education_level)
addEmptyRow(results_columns)

for employment_status in EmploymentStatus:
  addBaselineCharacteristics(results_columns, EmploymentStatus(employment_status).name.title(), patients, patients['employment_status'] == employment_status)
addEmptyRow(results_columns)

for performance in Performance:
  addBaselineCharacteristics(results_columns, Performance(performance).name.title(), patients, patients['performance'] == performance)
addEmptyRow(results_columns)

for cancer_type_layman in CancerTypeLayman:
  addBaselineCharacteristics(results_columns, CancerTypeLayman(cancer_type_layman).name.title(), patients, patients['cancer_type_layman'] == cancer_type_layman)
addEmptyRow(results_columns)

addBaselineCharacteristics(results_columns, TreatmentType.SURGERY.name.title(), patients, patients['has_treatment_surgery'] == True)
addBaselineCharacteristics(results_columns, TreatmentType.RADIOTHERAPY.name.title(), patients, patients['has_treatment_radiotherapy'] == True)
addBaselineCharacteristics(results_columns, TreatmentType.CHEMOTHERAPY.name.title(), patients, patients['has_treatment_chemotherapy'] == True)
addBaselineCharacteristics(results_columns, TreatmentType.IMMUNOTHERAPY.name.title(), patients, patients['has_treatment_immunotherapy'] == True)
addBaselineCharacteristics(results_columns, TreatmentType.OTHERS.name.title(), patients, patients['has_treatment_others'] == True)
addEmptyRow(results_columns)

eventsData = EventsData.load()
events = eventsData.events_df
events['itt'] = events.apply(lambda row: findITTGroup(row['patient_type'], row['patient_compliance']), axis=1)
events['at'] = events.apply(lambda row: findATGroup(row['patient_type'], row['patient_compliance']), axis=1)

addBaselineCharacteristics(
  results_columns,
  'Emergency Department Visits',
  events,
  ((events['event_type'] == EventType.ED_NOADMIT) | (events['event_type'] == EventType.ADMIT_ED))
)

addBaselineCharacteristics(
  results_columns,
  'Unplanned Inpatient Admissions',
  events,
  ((events['event_type'] == EventType.ADMIT_ED) | (events['event_type'] == EventType.ADMIT_CLINIC))
)

results = pd.DataFrame(data=results_columns)
results.set_index('characteristic')
print(results.to_markdown(index=False))
