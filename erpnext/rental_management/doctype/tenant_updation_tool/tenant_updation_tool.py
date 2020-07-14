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
		doc = frappe.get_doc("Tenant Information", self.tenant)
		ministry_agency = self.new_ministry_agency if self.new_ministry_agency else doc.ministry_agency
		department = self.new_department if self.new_department else doc.department
		floor_area = self.new_floor_area if self.new_floor_area else doc.floor_area
		tenant_section = self.new_tenant_section if self.new_tenant_section else doc.tenant

		frappe.db.sql("update `tabTenant Information` set ministry_agency = \'"+ str(ministry_agency) +"\', department = \'"+ str(department) +"\', floor_area = \'" + str(floor_area) + "\', tenant_section = \'" + str(tenant_section) + "\' where name= \'" + str(self.tenant) + "\'")


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

		
