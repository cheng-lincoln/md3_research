
import os

tick = u'\u2705'
boo = u'\u274c'

if os.path.exists("data"):
  print('data/ directory exists. {0}'.format(tick))
else:
  print('data/ directory does not exist... ')
  try:
    os.makedirs("data")
    print('created data/ directory. {0}'.format(tick))
  except OSError as error:
    print('failed to create data/ directory. {1}'.format(boo))

print('data/')
required_files = [
  'data/patient_information.xlsx',
  'data/enrollment_events.xlsx',
  'data/emergency_department_events.xlsx',
  'data/death_events.xlsx'
]
for required_file in required_files:
  if os.path.isfile(required_file):
    print('  {0} exists. {1}'.format(required_file, tick))
  else:
    print('  {0} is missing. Please add it to the data/ folder. {1}'.format(required_file, boo))

print('')

if os.path.exists("processed_data"):
  print('processed_data/ directory exists. {0}'.format(tick))
else:
  print('processed_data/ directory does not exist... ')
  try:
    os.makedirs("processed_data")
    print('created processed_data/ directory. {0}'.format(tick))
  except OSError as error:
    print('failed to create processed_data/ directory. {1}'.format(boo))

print('')

if os.path.exists("results"):
  print('results/ directory exists. {0}'.format(tick))
else:
  print('results/ directory does not exist... ')
  try:
    os.makedirs("results")
    print('created results/ directory. {0}'.format(tick))
  except OSError as error:
    print('failed to create results/ directory. {1}'.format(boo))
