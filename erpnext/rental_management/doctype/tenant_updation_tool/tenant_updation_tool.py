# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt, getdate, cint, today, add_years, date_diff, nowdate

class TenantUpdationTool(Document):
	def validate(self):
		pass

	def on_submit(self):
		self.update_history()
		frappe.db.sql ("update `tabTenant Information` set ministry_agency = \'"+ str(self.new_ministry_agency) +"\', department = \'"+ str(self.new_department) +"\', floor_area = '{0}' where name= '{1}' ".format(self.new_floor_area, self.tenant))
	
		#self.update_history()		

	def update_history(self):
		ti = frappe.get_doc("Tenant Information", self.tenant)
		if not ti.tenant_history:
			ti.append("tenant_history",{
					"department": ti.department,
					"ministry_agency": ti.ministry_agency,
					"floor_area": ti.floor_area,
					"from_date": ti.allocated_date,
					"to_date" : nowdate(),
					"creation": nowdate(),
					"modified_by": frappe.session.user,
					"modified": nowdate(),
					})
			ti.append("tenant_history",{
                                        "department": self.new_department,
                                        "ministry_agency": self.new_ministry_agency,
                                        "floor_area": self.new_floor_area,
                                        "from_date": nowdate(),
                                        "creation": nowdate(),
                                        "modified_by": frappe.session.user,
                                        "modified": nowdate()
          			      })

		else:
			ti.append("tenant_history",{
					"department": self.new_department,
					"ministry_agency": self.new_ministry_agency,
					"floor_area": self.new_floor_area,
					"from_date": nowdate(),
					"creation": nowdate(),
					"modified_by": frappe.session.user,
					"modified": nowdate()
		})
		#ti.save()
	
		#doc = frappe.get_doc("Tenant Information", self.tenant)
		#ti.department = self.new_department
		#ti.ministry_agency = self.new_ministry_agency
		#ti.floor_area = self.new_floor_area
		#doc.from_date = today()
		#doc.to_date = ""
		ti.save()

		
