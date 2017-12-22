from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import msgprint
from frappe.utils import flt, cint
from frappe.utils.data import get_first_day, get_last_day, add_years

def check_hire_end():
	all_doc = frappe.db.sql("select a.equipment, (select b.branch from `tabEquipment` b where b.name = a.equipment) as branch, a.equipment_number, c.customer, a.to_date from `tabHiring Approval Details` a, `tabEquipment Hiring Form` c where c.docstatus = 1 and c.name = a.parent and a.to_date = DATE_ADD(CURDATE(), INTERVAL 5 DAY)", as_dict=True)	
	all_data = {}
	for a in all_doc:
		if all_data.has_key(a.branch):
			row = {"eq": a.equipment, "en": a.equipment_number, "date": a.to_date, "cus": a.customer}
			row = str(a.equipment) + " " + str(a.equipment_number) + " " + str(a.to_date) + " " + str(a.customer) + "\n"  
			all_data[a.branch] += str(row)
		else:
			row = {"eq": a.equipment, "en": a.equipment_number, "date": a.to_date, "cus": a.customer}
			row = str(a.equipment) + " " + str(a.equipment_number) + " " + str(a.to_date) + " " + str(a.customer) + "\n"  
			all_data[a.branch] = str(row);

	for d in all_data:
		print(str(d) + " ==> " + str(all_data[d]))

