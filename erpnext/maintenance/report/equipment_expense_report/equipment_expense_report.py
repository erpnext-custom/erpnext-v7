# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	#columns, data = [], []
	columns = get_columns(filters)
	data = get_data(filters)
	return data, columns
def get_data(filters):
	if filters.branch:
		branch =  str(filters.from_date)
	else:
		branch = "e.branch"

	#equipment_number = frappe.db.sql("select e.equipment_number from `tabEquipment` e where e.branch = %s", %branch)
	'''current_operator = frappe.db.sql("select z.operator from `tabEquipment Operator` z where \
	z.start_date between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\' \
	or z.end_date between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\'")'''

	for i in frappe.db.sql("select e.equipment_number from `tabEquipment` e where e.branch = %s" %branch):
		frappe.msgprint(i[0])
		query = "select jc.goods_amount, jc.services_amount from  `tabJob Card` jc where  jc.posting_date between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\' and jc.equipment_number = %s " %i
		return frappe.db.sql(query)
	#frappe.db.sql(query)
		#frappe.msgprint(equ)0
	#return frappe.db.sql(query)""
	#result = frappe.db.sql(query, {"from_date":filters.from_date, "to_date": filters.to_date})


def get_columns(filters):
	cols = [
		("Registration No") + ":Currency:120",
		("Equipment Type.") + ":Currency:120",

	]
	return cols
