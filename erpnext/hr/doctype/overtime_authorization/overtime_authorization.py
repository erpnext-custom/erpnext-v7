# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from erpnext.custom_workflow import validate_workflow_states
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt

class OvertimeAuthorization(Document):
	def validate(self):
		validate_workflow_states(self)
		self.validate_duplicate_date()	

	def validate_duplicate_date(self):
		ot_authorization = frappe.db.sql("""
                                        select name from `tabOvertime Authorization` 
                                        where to_date between '{0}' and '{1}'
                                        and employee = '{2}'
					and docstatus = 1 
                """.format(self.from_date, self.to_date, self.employee), as_dict=True)
		if ot_authorization:
			for a in ot_authorization:
				frappe.throw("Overtime Authorization approval already exist {0}".format(a.name))




@frappe.whitelist()
def make_overtime_claim(source_name, target_doc=None):
	def update_so(source, target):
		basic = frappe.db.sql("select a.amount as basic_pay from `tabSalary Detail` a, `tabSalary Structure` b where a.parent = b.name and a.salary_component = 'Basic Pay' and b.is_active = 'Yes' and b.employee = '{0}'".format(source.employee), as_dict=True)
		if basic:
			ot_rate = flt(((basic[0].basic_pay) * 1.5) / (30 * 8))
		else:
			frappe.throw("No Salary Structure foudn for the employee")
		target.rate = ot_rate
		
        doclist = get_mapped_doc("Overtime Authorization", source_name, {
                "Overtime Authorization": {
                        "doctype": "Overtime Claim",
                        "field_map": {
                                "parent": "name",
                        },
                        "validation": {
                                "docstatus": ["=", 1]
                        }
                },
        }, target_doc, update_so)

        return doclist
