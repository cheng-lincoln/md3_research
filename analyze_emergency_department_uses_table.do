cls
clear all
import delimited processed_data/emergency_department_uses_table.csv
list, noobs
stset time, fail(status) exit(time .) id(id) enter(time0)
stcox group, nohr efron vce(robust) nolog
translate @Results results/emergency_department_uses_analysis.txt, replace
