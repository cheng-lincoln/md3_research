import delimited processed_data/emergency_department_uses_andersengill_table.csv
list, noobs
stset time, fail(status) exit(time .) id(id) enter(time0)
stcox group, nohr efron vce(robust) nolog
