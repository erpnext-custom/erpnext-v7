# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class ProcessGEPPayment(Document):
	pass

@frappe.whitelist()
def get_records(from_date, to_date, branch, project=None):
	if not project:
		condition = " a.branch = " + str(branch) + " and a.project = \'\' "
	else:
		condition = " a.project = " + str(project) + " " 

	ans = frappe.db.sql("select a.name, a.person_name, a.id_card, a.salary, a.ot_amount, (select sum(c.number_of_hours) from `tabOvertime Entry` c where c.number = a.name and c.date between %s and %s and c.docstatus = 1) as number_of_hours from `tabGEP Employee` a where %s order by a.person_name", (str(from_date), str(to_date), condition), as_dict=True)
	frappe.throw(str(ans))
