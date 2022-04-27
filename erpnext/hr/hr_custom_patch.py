# Copyright (c) 2016, Druk Holding & Investments Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt, cint
from frappe.utils.data import get_first_day, get_last_day, add_days
from erpnext.custom_utils import get_year_start_date, get_year_end_date

# following method created by SHIV on 2022/04/27
def mpi_2021():
	li = frappe.db.sql("""
			SELECT m.employee, ss.name salary_structure, m.amount
			FROM mpi_2021 m, `tabEmployee` e, `tabSalary Structure` ss
			WHERE e.name = m.employee
			AND ss.employee = e.name
			AND ss.is_active = 'Yes'
			AND NOT EXISTS(SELECT 1
					FROM `tabSalary Detail` sd
					WHERE sd.parent = ss.name
					AND sd.salary_component = 'Salary Arrears'
					AND sd.reference_number != 'MPIFOR2021'
					)
			""", as_dict=True)
	counter = 0
	for i in li:
		counter += 1
		print(counter,i.employee, i.salary_structure, i.amount)
		if flt(i.amount) <= 0:
			frappe.throw(_("ERROR: Invalid Amount"))

		# continue
		sst = frappe.get_doc("Salary Structure", i.salary_structure)
		row = sst.append("earnings", {})
		row.salary_component 	= "Salary Arrears"
		row.salary_component_type = "Earning"
		row.amount 				= flt(i.amount)
		row.from_date 			= "2022-04-01"
		row.to_date 			= "2022-04-30"
		row.reference_number 	= "MPIFOR2021"
		row.save(ignore_permissions=True)
		sst.save(ignore_permissions=True)
	frappe.db.commit()

# following method created by SHIV on 2021/05/27
def refresh_salary_structures():
	counter = 0
	for i in frappe.db.get_all("Salary Structure", {"is_active": "Yes"}):
		counter += 1
		print counter, i
		sst = frappe.get_doc("Salary Structure", i.name)
		sst.save()

# following method created by SHIV on 2021/04/23
def mpi_2020():
	li = frappe.db.sql("""
			SELECT m.employee, ss.name salary_structure, m.amount
			FROM mpi_2020 m, `tabEmployee` e, `tabSalary Structure` ss
			WHERE e.name = m.employee
			AND ss.employee = e.name
			AND (ss.is_active = 'Yes' OR (ss.from_date <= '2020-04-30' AND IFNULL(ss.to_date,NOW()) >= '2020-04-01'))
			AND NOT EXISTS(SELECT 1
					FROM `tabSalary Detail` sd
					WHERE sd.parent = ss.name
					AND sd.salary_component = 'Salary Arrears'
					AND sd.reference_number != 'MPIFOR2020'
					)
			""", as_dict=True)
	counter = 0
	for i in li:
		counter += 1
		print(counter,i.employee, i.salary_structure, i.amount)
		if flt(i.amount) <= 0:
			frappe.throw(_("ERROR: Invalid Amount"))

		# continue
		sst = frappe.get_doc("Salary Structure", i.salary_structure)
		row = sst.append("earnings", {})
		row.salary_component 	= "Salary Arrears"
		row.salary_component_type = "Earning"
		row.amount 				= flt(i.amount)
		row.from_date 			= "2021-04-01"
		row.to_date 			= "2021-04-30"
		row.reference_number 	= "MPIFOR2020"
		row.save(ignore_permissions=True)
		sst.save(ignore_permissions=True)
	frappe.db.commit()
