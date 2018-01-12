# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.desk.reportview import get_match_cond

class IssuePOL(Document):
	def validate(self):
		if not self.items:
			frappe.throw("Should have a POL Issue Details to Submit")

	def on_submit(self):
		self.consume_pol()

	def on_cancel(self):
		self.cancel_consumed_pol()

	def consume_pol(self):
		for a in self.items:
			con = frappe.new_doc("Consumed POL")	
			con.equipment = a.equipment
			con.branch = self.branch
			con.pol_type = self.pol_type
			con.date = self.date
			con.qty = a.qty
			con.reference_type = "Issue POL"
			con.reference_name = self.name
			con.submit()
	
	def cancel_consumed_pol(self):
		frappe.db.sql("update `tabConsumed POL` set docstatus = 2 where reference_type = 'Issue POL' and reference_name = %s", (self.name))

def equipment_query(doctype, txt, searchfield, start, page_len, filters):
        return frappe.db.sql("""
                        select
                                e.name,
                                e.equipment_type,
                                e.equipment_number
                        from `tabEquipment` e
                        where e.branch = %(branch)s
                        and e.is_disabled != 1
                        and e.not_cdcl = 0
                        and exists(select 1
                                     from `tabEquipment Type` t
                                    where t.name = e.equipment_type
                                      and t.is_container = 1)
                        and (
                                {key} like %(txt)s
                                or
                                e.equipment_type like %(txt)s
                                or
                                e.equipment_number like %(txt)s
                        )
                        {mcond}
                        order by
                                if(locate(%(_txt)s, e.name), locate(%(_txt)s, e.name), 99999),
                                if(locate(%(_txt)s, e.equipment_type), locate(%(_txt)s, e.equipment_type), 99999),
                                if(locate(%(_txt)s, e.equipment_number), locate(%(_txt)s, e.equipment_number), 99999),
                                idx desc,
                                e.name, e.equipment_type, e.equipment_number
                        limit %(start)s, %(page_len)s
                        """.format(**{
                                'key': searchfield,
                                'mcond': get_match_cond(doctype)
                        }),
                        {
				"txt": "%%%s%%" % txt,
				"_txt": txt.replace("%", ""),
				"start": start,
				"page_len": page_len,
                                "branch": filters['branch']
			})
