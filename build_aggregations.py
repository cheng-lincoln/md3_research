import pandas as pd
from utils import find_itt_group, find_at_group, barify, numberify
from enums import *
from build_patients import PatientsData
from build_events import EventsData

class Characteristic:
  """
  A helper class that collates data and generate visualizations for a characteristic.

  Attributes:
    data ({ str: [] }): a dictionary where the keys are column names, and values are lists of row values for that column
    is_visualization_generated (bool):
  """
  INDEX_COLUMN_NAME = 'characteristic'
  CONTROL_COLUMN_NAME = 'control'
  INTERVENTION_COLUMN_NAME = 'intervention'
  CONTROL_VISUALIZATION_COLUMN_NAME = ' '
  INTERVENTION_VISUALIZATION_COLUMN_NAME = '  '

  def __init__(self):
    self.data = Characteristic.init_data()
    self.is_visualization_generated = False

  def add_row(self, index_value, control_value, intervention_value):
    """
    Adds a row to the characteristic.

    Parameters:
      index_value (str):
      control_value (int or float):
      intervention_value (int or float):

    Returns:
      [index_value, control_value, intervention_value]:
    """
    self.data[Characteristic.INDEX_COLUMN_NAME].append(index_value)
    self.data[Characteristic.CONTROL_COLUMN_NAME].append(control_value)
    self.data[Characteristic.INTERVENTION_COLUMN_NAME].append(intervention_value)

    return [index_value, control_value, intervention_value]

  def add_aggregation(self, index_value, table, condition, intervention_only=False):
    """
    Adds a row to the characteristic, counting how many items in a given table
    matches the condition as described by that row

    Parameters:
      index_value (str):
      table (DataFrame): A pandas dataframe where the condition will be applied to
      condition (??): a pandas dataframe Select-like condition
      intervention_only (bool): only aggregate across the intervention group

    Returns:
      [(int or float), (int or float), (int or float),]: values of the row added
    """
    return self.add_row(
      index_value,
      control_value = len(table[(table['itt'] == 0) & condition]) if not intervention_only else '',
      intervention_value = len(table[(table['itt'] == 1) & condition]),
    )

  def generate_visualizations(self, resolution = 20):
    """
    Generates the visualization columns for the characteristic. Only run this after you finish populating the characteristic.

    Parameters:
      resolution (int): how many fragments a full bar should have

    Returns:
      (None)
    """
    control_values = [numberify(value) for value in self.data[Characteristic.CONTROL_COLUMN_NAME]]
    self.data[Characteristic.CONTROL_VISUALIZATION_COLUMN_NAME] = [
      barify(value, sum(control_values), resolution) if None not in control_values else ''
      for value
      in control_values
    ]

    intervention_values = [numberify(value) for value in self.data[Characteristic.INTERVENTION_COLUMN_NAME]]
    self.data[Characteristic.INTERVENTION_VISUALIZATION_COLUMN_NAME] = [
      barify(value, sum(intervention_values), resolution) if None not in intervention_values else ''
      for value
      in intervention_values
    ]

    self.is_visualization_generated = True

  @classmethod
  def init_data(cls):
    """
    Initializes an empty data object used by Characteristic.
    """
    data = dict(zip(
      (
        Characteristic.INDEX_COLUMN_NAME,
        Characteristic.CONTROL_COLUMN_NAME,
        Characteristic.CONTROL_VISUALIZATION_COLUMN_NAME,
        Characteristic.INTERVENTION_COLUMN_NAME,
        Characteristic.INTERVENTION_VISUALIZATION_COLUMN_NAME
      ),
      ([], [], [], [], [])
    ))

    return data

  @classmethod
  def join(cls, characteristics, separator=None):
    """
    Joins the data of multiple characteristics, with an option to add separator rows between each characteristic.

    Parameters:
      characteristics (Characteristic[]):
      separator (string or None): if None, no separator rows are added

    Returns:
      ({ str: [] }): an object with each key being a column name, and values the list of row values for that column.
    """
    result = Characteristic.init_data()

    for characteristic in characteristics:
      result[Characteristic.INDEX_COLUMN_NAME].extend(characteristic.data[Characteristic.INDEX_COLUMN_NAME])
      result[Characteristic.CONTROL_COLUMN_NAME].extend(characteristic.data[Characteristic.CONTROL_COLUMN_NAME])
      result[Characteristic.INTERVENTION_COLUMN_NAME].extend(characteristic.data[Characteristic.INTERVENTION_COLUMN_NAME])

      result[Characteristic.CONTROL_VISUALIZATION_COLUMN_NAME].extend(
        characteristic.data[Characteristic.CONTROL_VISUALIZATION_COLUMN_NAME]
        if characteristic.is_visualization_generated
        else ['' for _ in characteristic.data[Characteristic.CONTROL_COLUMN_NAME]]
      )
      result[Characteristic.INTERVENTION_VISUALIZATION_COLUMN_NAME].extend(
        characteristic.data[Characteristic.INTERVENTION_VISUALIZATION_COLUMN_NAME]
        if characteristic.is_visualization_generated
        else ['' for _ in characteristic.data[Characteristic.INTERVENTION_COLUMN_NAME]]
      )

      # Append breaks between characteristics
      if separator is not None:
        result[Characteristic.INDEX_COLUMN_NAME].append(separator)
        result[Characteristic.CONTROL_COLUMN_NAME].append(separator)
        result[Characteristic.INTERVENTION_COLUMN_NAME].append(separator)
        result[Characteristic.CONTROL_VISUALIZATION_COLUMN_NAME].append(separator)
        result[Characteristic.INTERVENTION_VISUALIZATION_COLUMN_NAME].append(separator)

    return result

# ---
patients_data = PatientsData.load()

patients_columns = {
  'id': [],
  'patient_type': [],
  'compliance': [],

  'itt': [],
  'at': [],

  'gender': [],
  'age': [],
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
  patient = patients_data.get_patient(patient_id)
  patients_columns['id'].append(patient.id)
  patients_columns['patient_type'].append(patient.type)
  patients_columns['compliance'].append(patient.compliance)

  patients_columns['itt'].append(find_itt_group(patient.type, patient.compliance))
  patients_columns['at'].append(find_at_group(patient.type, patient.compliance))

  patients_columns['gender'].append(patient.demographics.gender)
  patients_columns['age'].append(patient.demographics.age)
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

gender_characteristic = Characteristic()
for gender in Gender:
  gender_characteristic.add_aggregation(
    Gender(gender).name.title(),
    patients,
    patients['gender'] == gender
  )

age_characteristic = Characteristic()
age0 = 0
for age in [18, 35, 50, 65]:
  age_characteristic.add_aggregation(
    '{0} - {1} years old'.format(age0, age),
    patients,
    ((patients['age'] >= age0) & (patients['age'] < age))
  )
  age0 = age
age_characteristic.add_aggregation(
  '>{0} years old'.format(age0),
  patients,
  (patients['age'] >= age0)
)

race_characteristic = Characteristic()
for race in Race:
  race_characteristic.add_aggregation(
    Race(race).name.title(),
    patients,
    patients['race'] == race
  )

marital_status_characteristic = Characteristic()
for marital_status in MaritalStatus:
  marital_status_characteristic.add_aggregation(
    MaritalStatus(marital_status).name.title(),
    patients,
    patients['marital_status'] == marital_status
  )

education_level_characteristic = Characteristic()
for education_level in EducationLevel:
  education_level_characteristic.add_aggregation(
    EducationLevel(education_level).name.title(),
    patients,
    patients['education_level'] == education_level
  )

employment_status_characteristic = Characteristic()
for employment_status in EmploymentStatus:
  employment_status_characteristic.add_aggregation(
    EmploymentStatus(employment_status).name.title(),
    patients,
    patients['employment_status'] == employment_status
  )

performance_characteristic = Characteristic()
for performance in Performance:
  performance_characteristic.add_aggregation(
    Performance(performance).name.title(),
    patients,
    patients['performance'] == performance
  )

cancer_type_layman_characteristic = Characteristic()
for cancer_type_layman in [
  CancerTypeLayman.LUNG,
  CancerTypeLayman.HEAD_NECK,
  CancerTypeLayman.RENAL,
  CancerTypeLayman.PROSTATE,
  CancerTypeLayman.GI
]:
  cancer_type_layman_characteristic.add_aggregation(
    CancerTypeLayman(cancer_type_layman).name.title(),
    patients,
    patients['cancer_type_layman'] == cancer_type_layman
  )
cancer_type_layman_characteristic.add_aggregation(
  'Others',
  patients,
  patients['cancer_type_layman'] > CancerTypeLayman.GI
)


treatment_type_characteristic = Characteristic()
treatment_type_characteristic.add_aggregation(
  TreatmentType.SURGERY.name.title(),
  patients,
  patients['has_treatment_surgery'] == True
)
treatment_type_characteristic.add_aggregation(
  TreatmentType.RADIOTHERAPY.name.title(),
  patients,
  patients['has_treatment_radiotherapy'] == True
)
treatment_type_characteristic.add_aggregation(
  TreatmentType.CHEMOTHERAPY.name.title(),
  patients,
  patients['has_treatment_chemotherapy'] == True
)
treatment_type_characteristic.add_aggregation(
  TreatmentType.IMMUNOTHERAPY.name.title(),
  patients,
  patients['has_treatment_immunotherapy'] == True
)
treatment_type_characteristic.add_aggregation(
  TreatmentType.OTHERS.name.title(),
  patients,
  patients['has_treatment_others'] == True
)

events_data = EventsData.load()
events = events_data.events_df
events['itt'] = events.apply(lambda row: find_itt_group(row['patient_type'], row['patient_compliance']), axis=1)
events['at'] = events.apply(lambda row: find_at_group(row['patient_type'], row['patient_compliance']), axis=1)

events_characteristic = Characteristic()
_, control_edvisits, intervention_edvisits = events_characteristic.add_aggregation(
  'Emergency Department Visits',
  events,
  ((events['event_type'] == EventType.ED_NOADMIT) | (events['event_type'] == EventType.ADMIT_ED))
)

_, control_admissions, intervention_admissions = events_characteristic.add_aggregation(
  'Unplanned Inpatient Admissions',
  events,
  ((events['event_type'] == EventType.ADMIT_ED) | (events['event_type'] == EventType.ADMIT_CLINIC))
)

control_followup_days = 0
intervention_followup_days = 0
for patient_id in [i for i in range(1,241) if i != 109]:
  start_date, end_date = events_data.find_effective_start_end_dates(patient_id)
  followup_days = (pd.Timestamp(end_date) - pd.Timestamp(start_date)).days
  if (patients[(patients['id'] == patient_id)]['itt'].values[0] == 0):
    control_followup_days += followup_days
  else:
    intervention_followup_days += followup_days

events_characteristic.add_row(
  'Follow-Up [person-yrs]',
  '{:.2f}'.format(control_followup_days / 365),
  '{:.2f}'.format(intervention_followup_days / 365)
)
events_characteristic.add_row(
  'Incidence (ED Visits) [visits/person/yr]',
  '{:.2f}'.format(control_edvisits/(control_followup_days / 365)),
  '{:.2f}'.format(intervention_edvisits/(intervention_followup_days / 365))
)
events_characteristic.add_row(
  'Incidence (Admissions) [visits/person/yr]',
  '{:.2f}'.format(control_admissions/(control_followup_days / 365)),
  '{:.2f}'.format(intervention_admissions/(intervention_followup_days / 365))
)

intervention_characteristic = Characteristic()
for compliance in [PatientCompliance.SPARKLE_COMPLIANT, PatientCompliance.SPARKLE_NONCOMPLIANT]:
  intervention_characteristic.add_aggregation(
    PatientCompliance(compliance).name.title(),
    patients,
    patients['compliance'] == compliance,
    intervention_only = True
  )

gender_characteristic.generate_visualizations()
age_characteristic.generate_visualizations()
race_characteristic.generate_visualizations()
marital_status_characteristic.generate_visualizations()
education_level_characteristic.generate_visualizations()
employment_status_characteristic.generate_visualizations()
performance_characteristic.generate_visualizations()
cancer_type_layman_characteristic.generate_visualizations()
treatment_type_characteristic.generate_visualizations()
intervention_characteristic.generate_visualizations()

characteristics = Characteristic.join([
    gender_characteristic,
    age_characteristic,
    race_characteristic,
    marital_status_characteristic,
    education_level_characteristic,
    employment_status_characteristic,
    performance_characteristic,
    cancer_type_layman_characteristic,
    treatment_type_characteristic,
    events_characteristic,
    intervention_characteristic
  ],
  separator='---'
)

results = pd.DataFrame(data=characteristics)
results.set_index(Characteristic.INDEX_COLUMN_NAME)

with open('results/aggregations.md', 'w') as f:
  print(results.to_markdown(index=False), file=f)
