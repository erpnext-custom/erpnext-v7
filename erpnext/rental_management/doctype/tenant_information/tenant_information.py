# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils.data import get_first_day, get_last_day, add_days, add_years
from frappe.utils import cint, flt, nowdate, money_in_words

class TenantInformation(Document):
	def validate(self):
		if self.building_category != "Pilot Housing":
			self.rent_amount = flt(self.floor_area) * flt(self.rate_per_sq_ft)

		self.validate_allocation()
		#if not self.rental_charges:
		#	self.calculate_rent_charges()
		if frappe.db.exists("Customer", self.customer_code) and self.docstatus==1:
			self.update_customer()
		else:
			frappe.db.set(self, 'customer_code', '')

		if self.building_category == "Pilot Housing":
			self.cal_monthly_installment_for_pilot_housing()

		if not self.rental_charges and self.building_category == "Pilot Housing":
			self.update_rental_charges()

		if not self.structure_no:
			if self.location_id and self.block_no:
				self.structure_no = self.location_id + "/" + self.block_no
			else:
				frappe.msgprint("Structure No. not able to assign as Locaton Id and Block No are missing")

	
	def cal_monthly_installment_for_pilot_housing(self):
		if self.pilot_account_details:
			monthly_installment_amount = 0.0
			for a in self.pilot_account_details:
				monthly_installment_amount += flt(a.amount)

			self.original_monthly_instalment = monthly_installment_amount
	
	def validate_allocation(self):
		cid = frappe.db.get_value("Tenant Information", {"location":self.location, "building_category":self.building_category, "block_no":self.block_no, "flat_no":self.flat_no, "docstatus":1}, "cid")
		if cid:
			frappe.throw("The Flat is already rented to a Tenant with CID No: {0}".format(cid))		
	
	def on_submit(self):
		#Validate Creation of Duplicate Customer in Customer Master
		customer_code = frappe.db.sql("select customer_code from `tabCustomer` where customer_id = %s and customer_group ='Rental'",str(self.cid))
		if not customer_code:
			self.create_customer()
		#else:
		#	frappe.throw("Rental Customer of same CID is already registered with customer code <b>{0}</b>".format(customer_code[0][0]))
		if not self.rental_charges:
			
			if self.building_category != "Pilot Housing":
				self.calculate_rent_charges()
			#else:
			#	self.update_rental_charges()

	
	def update_rental_charges(self):
		rent_obj = self.append("rental_charges", {
					"from_date": self.from_date,
					"to_date": self.to_date,
					"increment": 0.0,
					"rental_amount": self.original_monthly_instalment
				})
		#frappe.msgprint("Before save")
		#rent_obj.save()
		#frappe.msgprint("Afer Save")
	
	def calculate_rent_charges(self):
		percentage = 0.1
                increment = 0
                actual_rent = 0

		start_date = get_first_day(self.allocated_date)
		end_date   = add_years(get_last_day(add_days(start_date, -10)), 2)
		for i in range(0, 10, 2):
			if i > 1:
				start_date = add_years(start_date, 2)
				end_date = add_years(end_date, 2)
				increment = actual_rent * percentage if actual_rent > 0 else self.rent_amount * percentage
				actual_rent = actual_rent + increment if actual_rent > 0 else self.rent_amount + increment
			actual_rent = actual_rent if actual_rent > 0 else self.rent_amount		
			#frappe.msgprint("{0} start: {1} and  end_date: {2} increment {3} and rent {4}".format(i, start_date, end_date, increment, actual_rent))
			rent_obj = self.append("rental_charges", {
						"from_date": start_date,
						"to_date": end_date,
						"increment": increment,
						"rental_amount": actual_rent
					})

			rent_obj.save()
		
	def update_customer(self):
		cus = frappe.get_doc("Customer", self.customer_code)
		cus.customer_name = self.tenant_name
		cus.customer_id = self.cid
		cus.mobile_no = self.mobile_no
		cus.location = self.location
		cus.dzongkhag = self.dzongkhag
		cus.save()

	def create_customer(self):
		last_customer_code = frappe.db.sql("select customer_code from tabCustomer where customer_group='Rental' order by customer_code desc limit 1;");
		if last_customer_code:
			customer_code = str(int(last_customer_code[0][0]) + 1)
		else:
			customer_code = frappe.db.get_value("Customer Group", "Rental", "customer_code_base")
			if not customer_code:
				frappe.throw("Setup Customer Code Base in Rental Customer Group")
		self.db_set("customer_code", customer_code)	
		cus_name = self.tenant_name + "-" + customer_code
			
		cus = frappe.new_doc("Customer")
		cus.customer_code = customer_code
		cus.name = customer_code
		cus.customer_name = cus_name
		cus.customer_group = "Rental"
		cus.customer_id = self.cid
		cus.territory = "Bhutan"
		cus.mobile_no = self.mobile_no
		cus.location = self.location
		cus.dzongkhag = self.dzongkhag
		cus.cost_center = "Real Estate Management - NHDCL"
		cus.branch = self.branch
		cus.insert()

@frappe.whitelist()
def get_distinct_structure_no():
	data = []
	for a in frappe.db.sql("select distinct(t.structure_no) as structure_no from `tabTenant Information` t where t.structure_no is not NULL and docstatus =1 and not exists (select 1 from `tabAsset` a where a.structure_no= t.structure_no and docstatus = 1)", as_dict=1):
		data.append(a.structure_no)

	return data
