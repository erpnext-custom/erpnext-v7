# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns =  get_column(filters)
 	data = get_data(filters)
	return columns, data

def get_data(filters):
    query = """
		select 
      		fiscal_year,
			title,
			employee,
			department,
   			department_head_name,
			evaluation_start_date,
			evaluation_end_date,
			date,
   			final_score,
			approver_name
		from `tabPMS Evaluation` 
		where docstatus = 1
     	"""
    data = frappe.db.sql(query)
    return data


def get_column(filters):
    columns = [
		_("Fiscal Year") + ":Link/Fiscal Year:130",
		_("Title") + ":Data:130",
		_("Department Head") + ":Link/Employee:130",
		_("Department") + ":Link/Department:130",
		_("Department Head Name") + ":Data:130",
		_("Evaluation Start Date") + ":Date:130",
		_("Evaluation End Date") + ":Date:130",
		_("Posting Date") + ":Date:130",
		_("Final Score") + ":Data:130",
		_("Approver Name") + ":Data:130"
	]
    return columns
