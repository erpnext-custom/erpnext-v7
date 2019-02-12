# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.desk.reportview import get_match_cond

class SalaryRemittanceTemplate(Document):
	pass

'''def get_salary_component(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql("""
		select name
		from(
		select name
		from `tabSalary Component`
		where is_remittable = 1
		union all
		select 'Salary Remittance' as name
		) as x
		order by name
		"""
	)


	return frappe.db.sql("""
		select `name`
		from(
		select `name`
		from `tabSalary Component`
		where is_remittable = 1
		union all
		select 'Salary Remittance' as `name`
		) as x
		where {key} like %(txt)s
		{mcond}
		order by if(locate(%(_txt)s, name), locate(%(_txt)s, name), 99999),	name
	""".format(**{
		'key': searchfield,
		'mcond': ''
	}),
	{
		"txt": "%%%s%%" % txt,
		"_txt": txt.replace("%", ""),
		"start": start,
		"page_len": page_len
	}
	)
	'''
