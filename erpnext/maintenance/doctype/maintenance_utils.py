from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import msgprint
from frappe.utils import flt, cint
from frappe.utils.data import get_first_day, get_last_day, add_years

def check_hire_end():
	all_doc = frappe.db.sql("select a.equipment, (select b.branch from `tabEquipment` b where b.name = a.equipment) as branch, a.equipment_number, c.customer from `tabHiring Approval Details` a, `tabEquipment Hiring Form` c where c.docstatus = 1 and c.name = a.parent and a.to_date = DATE_ADD(NOW(), INTERVAL 5 DAY)")	
	print(str(all_doc))


