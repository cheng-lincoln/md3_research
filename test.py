#from enums import PatientType

# a = ['a','b','c']
# for i, x in enumerate(a):
#   if i == len(a) - 1:
#     print('last')
#   else:
#     print(x)

# print([1,2] + [3,4] + [5,6])

# print(PatientType(1).name)

# x = []
# x.append([1,2,3])
# x.append([4,5,6])
# print(x)

# x = []
# a = [[1,2,3], [4,5,6]]
# b = [[7,8,9], [10,11,12]]

# x += a
# x += b
# print(x)

for patient_id in [i for i in range(1,241) if i != 109]:
  print(patient_id)
