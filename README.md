## Background

This code repository is created for the investigation of ...

#### Others

The censor date used is **30 Apr 2024**.

Patient **109** is excluded from the analysis.



## <a name="prereq">Pre-requisites</a>

#### Software Requirements

1. **Python 3** (most recent python installations should be compatible)
   To check that python is successfully installed, type the following in your shell (on Macbook open **terminal**, on Windows open **Powershell**):

   ```bash
   python3 --version
   
   # The version number should appear (the first number should be 3):
   Python 3.12.4
   ```

2. **STATA** (any edition should be compatible)



#### Data Requirements

1. Data files need to be obtained with permission for use.



## Architecture

#### Overview

![image](https://github.com/user-attachments/assets/4d8eda9e-4589-414f-a07f-0f6f411c7a51)



> [!NOTE]
>
> For the purpose of reproducibility:
>
>  - STATA code is stored as `.do` files
>
>  - Python code is broken up into 3 main modules:
>
>    - `build_patients.py`
>    - `build_events.py`
>    - `build_andersengill_tables.py`
>
>    Each of this modules outputs a file that can be checked for correctness.



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



#### How to run

> [!IMPORTANT]
>
> This section assumes that you have already fulfilled all the [pre-requisities](#prereq) above.

###### Setup

1) Download the folder from GitHub.

   There are 2 ways to do this:

   - if you are `git` savvy, you can clone the repository
   - if you are not familiar with `git`:
     1. click **Code > Download ZIP**
     2. unzip the `.zip` file to your desired location (e.g on your desktop)

   For the purposes of this example, I will assume the code folder is stored on a Mac desktop, which has the location `~/Desktop/md3_research-main`

2) Open the shell.
   On Macbook: open **terminal**

   On Windows: open **Powershell**

3) Change the working directory in the shell to the code folder:
   ```bash
   cd ~/Desktop/md3_research-main
   ```

4) You could run the code folder directly with your computer's native python, but we will use a virtual environment instead. This will prevent any incompatible dependencies with you computer's native python. To do this:

   1) We first create a folder called `.venv` in code folder to store the virtual environment:
      ```bash
      mkdir .venv
      ```

   2) Then we create a virtual environment in the `.venv` folder:
      ```bash
      python3 -m venv .venv
      ```

   3) Then we activate the virtual environment:
      ```bash
      # If using terminal on Mac:
      source .venv/bin/activate
      
      # If using Powershell on Windows:
      .venv\Scripts\Activate.ps1
      ```

   4) You should see `(.venv)` appear before whatever you type from now on:
      ```bash
      # Example in terminal on Mac:
      (.venv) Lincolns-Mackbook-Pro:md3_research-main lincoln$ ...
      ```

5) Now that we have activated the virtual environment, we can safely work within this environment. We will proceed to install the dependencies for this code repository:
   ```bash
   pip3 install -r requirements.txt
   ```

   With the dependencies installed, we are now ready to start!



###### Data Processing in Python

1) First we want to initialize the required folders and check if we have the correct raw data files. To do this, run:
   ```bash
   python3 -m init
   
   # You should see only green ticks.
   
   # If you see red ticks:
   # -> If it mentions data files missing, add them to the corresponding folders
   # -> If it mentions being not able to create directories (i.e folders), you can manually create them
   # AFTER DOING THAT, run the above command again to ensure that only green ticks appear
   ```

2) Next, we run the code to extract patient information:
   ```bash
   python3 -m build_patients # this might take a few seconds
   ```

   This creates a `patients.json` file in the `processed_data` folder. We should be able to see it with this command:

   ```bash
   ls processed_data/
   
   # We should see the following line:
   patients.json
   ```

3) Next, we run the code to extract events:
   ```bash
   python3 -m build_events
   
   # We should see a snippet of the events table printed
   # ...
   ```

   This creates an `events.csv` file in the `processed_data` folder. We should be able to see it with this command:

   ```bash
   ls processed_data/
   
   # We should see the following line:
   events.csv		patients.json
   ```

4) Next we want to build the tables for Andersen-Gill model from the events. We do this by:
   ```bash
   python3 -m build_andersengill_tables
   
   # We will see a snippet of each of the 2 tables printed
   # (ignore the reprint of the events table)
   ```

   This creates 2 files in the `processed_data` folder. Again, we can see them with:

   ```bash
   ls processed_data/
   
   # We should see the following lines:
   emergency_department_uses_table.csv		patients.json		events.csv		unplanned_inpatient_admissions_table.csv
   ```

   Now that we have the tables ready for analysis, lets switch to STATA!



###### Data Analysis in STATA

> [!IMPORTANT]
>
> Before doing anything in STATA, **change the working directory** in STATA to the code folder's location. Using the example above:
>
> 1) File > Change Working Directory...
> 2) Choose the code folder (i.e at `~/Desktop/md3_research-main`)

1. Run both `.do` files:

   - `analyze_emergency_department_uses_table.do`
   - `analyze_unplanned_inpatient_admissions_table`

   Do this in STATA with: 

   	1. File > Do...
   	1. Choose the respective `.do` file


   Analysis results are stored in `results/` folder, we can see this with this command (works whether in the shell or in STATA's command panel):

   ```bash
   ls results/
   
   # We should see the following files
   emergency_department_uses_analysis.txt		unplanned_inpatient_admissions_analysis.txt
   ```

   
