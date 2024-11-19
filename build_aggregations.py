import pandas as pd
from utils import findITTGroup, findATGroup
from enums import *
from build_patients import PatientsData
from build_events import EventsData

def addRow(results_columns, characteristic_column_value, control_column_value, intervention_column_value):
  """
  Adds a row to the results table

  Parameters:
    results_columns ({
      'characteristic': [],
      'itt (control)': [], # itt = 0
      'itt (intervention)': []
    }): a transposed object used to eventually create a DataFrame

  Returns:
    [control_column_value, intervention_column_value]: the values in the control and intervention column
  """
  results_columns['characteristic'].append(characteristic_column_value)
  results_columns['itt (control)'].append(control_column_value)
  results_columns['itt (intervention)'].append(intervention_column_value)

  return [control_column_value, intervention_column_value]

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
    ['', '']: the values in the control and intervention column
  """
  return addRow(results_columns, '---', '---', '---')

def addBaselineCharacteristics(results_columns, characteristic_name, table, condition):
  """
  A convenience function that adds a row baseline characteristics

  Parameters:
    results_columns ({
      'characteristic': [],
      'itt (control)': [], # itt = 0
      'itt (intervention)': [] # itt = 1
    }): a transposed object used to eventually create a DataFrame
    characteristic_name (string): name of the characteristic to aggregate
    table (DataFrame): the table to analyze
    condition (??): example => (table['gender'] == Gender.FEMALE)

  Returns:
    [, ]: the values in the control and intervention column
  """
  return addRow(
    results_columns,
    characteristic_name,
    len(table[(table['itt'] == 0) & condition]),
    len(table[(table['itt'] == 1) & condition])
  )
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

itt_control_emergency_visits, itt_intervention_emergency_visits = addBaselineCharacteristics(
  results_columns,
  'Emergency Department Visits',
  events,
  ((events['event_type'] == EventType.ED_NOADMIT) | (events['event_type'] == EventType.ADMIT_ED))
)

itt_control_unplanned_inpatient_admissions, itt_intervention_unplanned_inpatient_admissions = addBaselineCharacteristics(
  results_columns,
  'Unplanned Inpatient Admissions',
  events,
  ((events['event_type'] == EventType.ADMIT_ED) | (events['event_type'] == EventType.ADMIT_CLINIC))
)

itt_control_followup_days = 0
itt_intervention_followup_days = 0
for patient_id in [i for i in range(1,241) if i != 109]:
  start_date, end_date = eventsData.findEffectiveStartEndDates(patient_id)
  followup_days = (pd.Timestamp(end_date) - pd.Timestamp(start_date)).days
  if (patients[(patients['id'] == patient_id)]['itt'].values[0] == 0):
    itt_control_followup_days += followup_days
  else:
    itt_intervention_followup_days += followup_days

# addRow(results_columns, 'Follow-Up [person-days]', itt_control_followup_days, itt_intervention_followup_days)
addRow(
  results_columns,
  'Follow-Up [person-years]',
  '{:.2f}'.format(itt_control_followup_days / 365),
  '{:.2f}'.format(itt_intervention_followup_days / 365)
)
addRow(
  results_columns,
  'Incidence (Emergency Department Visits)\n[visits/person/year]',
  '{:.2f}'.format(itt_control_emergency_visits/(itt_control_followup_days / 365)),
  '{:.2f}'.format(itt_intervention_emergency_visits/(itt_intervention_followup_days / 365)),
)
addRow(
  results_columns,
  'Incidence (Unplanned Inpatient Admissions)\n[visits/person/year]',
  '{:.2f}'.format(itt_control_unplanned_inpatient_admissions/(itt_control_followup_days / 365)),
  '{:.2f}'.format(itt_intervention_unplanned_inpatient_admissions/(itt_intervention_followup_days / 365)),
)

results = pd.DataFrame(data=results_columns)
results.set_index('characteristic')

with open('results/aggregations.md', 'w') as f:
  print(results.to_markdown(index=False), file=f)
