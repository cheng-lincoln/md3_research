cls
clear all
import delimited processed_data/emergency_department_uses_table.csv
list, noobs
stset time, fail(status) exit(time .) id(id) enter(time0)
stcox itt at, efron vce(cluster id) nolog
translate @Results results/emergency_department_uses_analysis.txt, replace
