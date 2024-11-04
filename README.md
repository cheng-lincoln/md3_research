## Background

TBD

#### Others

The censor date used is <u>30 Apr 2024</u>.

Patient <u>109</u> is excluded from the analysis.



## Pre-requisites

#### Software Requirements

1) Python (most recent python installations should be compatible)
   - It is recommended to use a virtual environment to prevent library incompatibilities with your native python installation (see <a name="how_to_run">How to Run</a> section below)
2) STATA (any edition should be compatible)

#### Data Requirements

1. Data files need to be obtained with permission for use.



## Architecture

#### Overview

![image](https://github.com/user-attachments/assets/4d8eda9e-4589-414f-a07f-0f6f411c7a51)

#### Repository Structure

The important files and folders are explained:

```yaml
/
- data/
  # not included in code repository
  -- patient_information.xlsx
  -- enrollment_events.xlsx
  -- emergency_department_events.xlsx
  -- death_events.xlsx
- processed_data/
  # files here are generated by .py scripts
  -- patients.json
  -- events.csv
  -- emergency_department_uses_table.csv
  -- unplanned_inpatient_admissions_table.csv
- results/
  # files here are generated by STATA .do files
  -- emergency_department_uses_analysis.txt
  -- unplanned_inpatient_admissions_analysis.txt

- init.py # creates required directories and checks for required data files
- build_patients.py # extracts patient information from raw data
- build_events.py # extract relevant events from raw data
- build_andersengill_tables.py # formats events into target tables
- utils.py # utility functions

# analyzes tables using andersen-gill model in STATA
- analyze_emergency_department_uses_table.do 
- analyze_unplanned_inpatient_admissions_table.do

```



#### [How to run](#how_to_run)
