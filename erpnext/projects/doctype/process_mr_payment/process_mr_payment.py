# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class ProcessMRPayment(Document):
	pass

@frappe.whitelist()
def get_records(from_date, to_date, project):
	return frappe.db.sql("select a.name, a.person_name, a.id_card, a.rate_per_day, a.rate_per_hour, (select sum(1) from `tabMR Attendance` b where b.muster_roll_employee = a.name and b.date between %s and %s and b.project = %s and b.status = 'Present' and b.docstatus = 1) as number_of_days, (select sum(c.number_of_hours) from `tabOvertime Entry` c where c.number = a.name and c.date between %s and %s and c.project = %s and c.docstatus = 1) as number_of_hours from `tabMuster Roll Employee` a where a.project = %s order by a.person_name", (str(from_date), str(to_date), str(project), str(from_date), str(to_date), str(project), str(project)), as_dict=True)
