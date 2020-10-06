# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import msgprint, _
import json

class TenantFlatTransferTool(Document):
    def validate(self):
        self.validate_tenant_info()

    def validate_tenant_info (self):        
        old_tenant_info = frappe.get_doc("Tenant Information", self.cid)
        if old_tenant_info.status == "Surrendered" : 
            frappe.throw("Tenant {} has surrendered his/her flat".format(old_tenant_info.tenant_name))

        # The order is how it appears in the tenant information doctype
        # self.new_customer_code = old_tenant_info.customer_code
        self.location = old_tenant_info.location
        self.location_id = old_tenant_info.location_id
        self.dzongkhag = old_tenant_info.dzongkhag
        self.town_category = old_tenant_info.town_category
        self.building_classification = old_tenant_info.building_classification
        self.building_category = old_tenant_info.building_category
        self.structure_no = old_tenant_info.structure_no
        self.block_no = old_tenant_info.block_no
        self.flat_no = old_tenant_info.flat_no
        self.percent_of_increment = old_tenant_info.percent_of_increment
        self.no_of_year_for_increment = old_tenant_info.no_of_year_for_increment
        self.tenant_name = old_tenant_info.tenant_name # old tenant name
        # self.tenant_name =  old_tenant_info.tenant_name
        # self.designation = old_tenant_info.designation
        # self.employee_id =old_tenant_info.employee_id
        # self.grade = old_tenant_info.grade
        # self.ministry_agency= old_tenant_info.ministry_agency
        # self.department = old_tenant_info.department
        self.tenant_section = old_tenant_info.tenant_section
        # self.mobile_no = old_tenant_info.mobile_no
        self.floor_area = old_tenant_info.floor_area
        self.rate_per_sq_ft = old_tenant_info.rate_per_sq_ft
        self.rent_amount= old_tenant_info.rent_amount
        self.security_deposit = old_tenant_info.security_deposit
        self.receipt_no = old_tenant_info.receipt_no
        self.receipt_date = old_tenant_info.receipt_date
        self.initial_allotment_date = old_tenant_info.initial_allotment_date
        self.allocated_date = old_tenant_info.allocated_date
        # self.status = old_tenant_info.status #Dont think you need this in the new doc.
        self.m_start_date = old_tenant_info.m_start_date
        self.m_end_date = old_tenant_info.m_end_date
        self.house_no = old_tenant_info.house_no
        self.sale_price = old_tenant_info.sale_price
        self.from_date = old_tenant_info.from_date
        self.area = old_tenant_info.area
        self.security_deposit_pilot = old_tenant_info.security_deposit_pilot
        self.to_date = old_tenant_info.to_date
        self.repayment_period = old_tenant_info.repayment_period
        self.original_monthly_instalment = old_tenant_info.original_monthly_instalment

        # Update the Child Table of Rental Charges
        for data in old_tenant_info.rental_charges: 
            self.append("rental_charges", {
                    "from_date": data.from_date,
                    "to_date": data.to_date,
                    "increment": data.increment,
                    "rental_amount": data.rental_amount
                })
        # Update the Child Table of Family Details
        for data in old_tenant_info.family_details: 
            self.append("family_details", {
                    "full_name": data.full_name,
                    "cid": data.cid,
                    "relationship": data.relationship,
                    "dob": data.dob 
                })

        # Update the Child Table of Tenant History
        for data in old_tenant_info.tenant_history: 
            self.append("tenant_history", {
                    "department": data.department,
                    "ministry_agency": data.ministry_agency,
                    "floor_area": data.floor_area,
                    "from_date": data.from_date , 
                    "to_date" : data.to_date
                })
        
        # Update the Child Table of Pilot Account Details
        for data in old_tenant_info.pilot_account_details: 
            self.append("pilot_account_details", {
                    "party_type": data.party_type,
                    "account": data.account,
                    "amount": data.amount,
                })


    def on_submit(self):
		if self.owner_ship_transfer == 1:
			# self.create_customer_code()
			self.create_tenant_info()
		if self.floor_area_change ==  1:
			self.update_floor_area()


    def update_floor_area(self): 
        # NEED TO WORK ON MAKING THE SUBMITTED COPY A DRAFT AND THEN SUBMITTING THIS AGAIN. 
        doc = frappe.get_doc("Tenant Information", self.cid)
        doc.amend()
        doc.floor_area = self.new_floor_area
        doc.save()

    def create_customer(self):
		#Validate Creation of Duplicate Customer in Customer Master
		if frappe.db.exists("Customer", {"customer_id":self.cid, "customer_group": "Rental"}):
			cus = frappe.get_doc("Customer", {"customer_id":self.cid, "customer_group": "Rental"})
			existing_customer_code = frappe.db.get_value("Customer", {"customer_id":self.cid, "customer_group": "Rental"}, "customer_code")
			if existing_customer_code:
				self.customer_code = existing_customer_code
			else:
				last_customer_code = frappe.db.sql("select customer_code from tabCustomer where customer_group='Rental' order by customer_code desc limit 1;");
				if last_customer_code:
					customer_code = str(int(last_customer_code[0][0]) + 1)
				else:
					customer_code = frappe.db.get_value("Customer Group", "Rental", "customer_code_base")
					if not customer_code:
						frappe.throw("Setup Customer Code Base in Rental Customer Group")
				self.db_set("customer_code", customer_code)
				cus.customer_code = customer_code

			cus.mobile_no = self.new_mobile_no
			cus.location = self.location
			cus.dzongkhag = self.dzongkhag
			cus.save()
				
		else:
			last_customer_code = frappe.db.sql("select customer_code from tabCustomer where customer_group='Rental' order by customer_code desc limit 1;");
			if last_customer_code:
				customer_code = str(int(last_customer_code[0][0]) + 1)
			else:
				customer_code = frappe.db.get_value("Customer Group", "Rental", "customer_code_base")
				if not customer_code:
					frappe.throw("Setup Customer Code Base in Rental Customer Group")
			self.db_set("customer_code", customer_code)
				
			cus_name = self.new_tenant_name + "-" + customer_code
				
			cus = frappe.new_doc("Customer")
			cus.customer_code = customer_code
			cus.name = customer_code
			cus.customer_name = cus_name
			cus.customer_group = "Rental"
			cus.customer_id = self.new_citizen_id
			cus.territory = "Bhutan"
			cus.mobile_no = self.new_mobile_no
			cus.location = self.location
			cus.dzongkhag = self.dzongkhag
			cus.cost_center = "Real Estate Management - NHDCL"
			cus.branch = self.branch
			cus.insert()
            
    def create_tenant_info(self):
        old_doc = frappe.get_doc("Tenant Information", self.cid)
        old_doc.status = "Surrendered"
        old_doc.save()
        
        doc = frappe.new_doc('Tenant Information')
        doc.doctype = "Tenant Information"
        doc.title = self.new_citizen_id
        doc.cid = self.new_citizen_id
        doc.status = "Allocated"
        doc.tenant_name = self.new_tenant_name
        doc.new_customer_code = self.customer_code
        doc.location = self.location
        doc.location_id = self.location_id
        doc.dzongkhag = self.dzongkhag
        doc.town_category = self.town_category
        doc.building_classification = self.building_classification
        doc.building_category = self.building_category
        doc.structure_no = self.structure_no
        doc.block_no = self.block_no
        doc.flat_no = self.flat_no
        doc.percent_of_increment = self.percent_of_increment
        doc.no_of_year_for_increment = self.no_of_year_for_increment

        doc.designation = self.new_designation
        doc.employee_id =self.new_employee_id
        doc.grade = self.new_grade
        doc.ministry_agency= self.new_ministry_agency
        doc.department = self.new_department
        doc.tenant_section = self.new_tenant_section
        doc.mobile_no = self.new_mobile_number

        doc.floor_area = self.floor_area
        doc.rate_per_sq_ft = self.rate_per_sq_ft
        doc.rent_amount= self.rent_amount
        doc.security_deposit = self.security_deposit
        doc.receipt_no = self.receipt_no
        doc.receipt_date = self.receipt_date
        doc.initial_allotment_date = self.initial_allotment_date
        doc.allocated_date = self.allocated_date
        doc.m_start_date = self.m_start_date
        doc.m_end_date = self.m_end_date
        doc.house_no = self.house_no
        doc.sale_price = self.sale_price
        doc.from_date = self.from_date
        doc.area = self.area
        doc.security_deposit_pilot = self.security_deposit_pilot
        doc.to_date = self.to_date
        doc.repayment_period = self.repayment_period
        doc.original_monthly_instalment = self.original_monthly_instalment
        doc.family_details = self.family_details

		# Need to make this a child table
        doc.transferred_from = "{cid} : {name}".format(cid=self.cid, name=self.tenant_name)
        doc.transferred_date = self.transfer_date

        doc.submit()