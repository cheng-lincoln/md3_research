cls
clear all
import delimited processed_data/unplanned_inpatient_admissions_table.csv
list, noobs
stset time, fail(status) exit(time .) id(id) enter(time0)
stcox group, efron vce(cluster id) nolog
translate @Results results/unplanned_inpatient_admissions_analysis.txt, replace
