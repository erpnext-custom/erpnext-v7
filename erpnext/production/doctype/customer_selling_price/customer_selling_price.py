# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt, cint

class CustomerSellingPrice(Document):
	def validate(self):
		self.check_sp_rate()
		self.check_duplicate_settings()
	
	def check_sp_rate(self):
		for a in self.item_rates:
			if not flt(a.selling_price) > 0:
				frappe.throw("Selling Rate should be greater than 0 for <b>" + str(a.particular) + "</b>")

			if a.price_based_on == "Item":
				a.item_name = frappe.db.get_value("Item", a.particular, "item_name")
				a.timber_type = None
				a.item_sub_group = None
			else:
				a.item_name = None

	def check_duplicate_settings(self):
		item_list = []
		for a in self.item_rates:
			rate_dtl = str(str(a.particular) + "/" + str(a.timber_type) + "/" + str(a.item_sub_group) + "/" + str(a.location))
			if rate_dtl in item_list:
				frappe.throw("<b>"+str(a.particular) + ", " + str(a.item_name) + "</b> already defined more than once with the same locations<b>")
			item_list.append(rate_dtl)

		#Check customer and branch duplicate	
		for a in frappe.db.sql("""select b.branch, b.name 
								from `tabCustomer Selling Price` b 
								where b.name != %s 
								and b.branch = %s
								and (%s between b.from_date and b.to_date 
									or %s between b.from_date and b.to_date 
									or (%s > b.from_date and %s < b.to_date) 
									or (%s < b.from_date and %s > b.to_date)
									)
								and b.customer = %s
								""", (self.name, self.branch, self.from_date, self.to_date, self.from_date, self.to_date, self.from_date, self.to_date, self.customer), as_dict=1):
			#check for Item duplicate
			doc = frappe.get_doc("Customer Selling Price", a.name)
			for b in doc.item_rates:
				if str(b.particular) + "/" + str(b.timber_type) + "/" + str(b.item_sub_group) + "/" + str(b.location) in item_list:
					if b.timber_type and b.item_sub_group:
						frappe.throw("<b>"+str(b.particular) + "/" + str(b.timber_type) + "/" + str(b.item_sub_group)+ "</b> already defined for the same period in <b>"+str(frappe.get_desk_link(self.doctype, a.name))+"</b>")
					else:
						frappe.throw("<b>"+str(b.particular) + "</b> already defined for Customer <b>"+ str(self.customer) +"</b> the same period in <b>"+str(frappe.get_desk_link(self.doctype, a.name))+"</b>")

@frappe.whitelist()
def get_customer_selling_rate(price_list, branch, item_code, transaction_date, location, customer):
	if not branch or not item_code or not transaction_date:
		frappe.throw("Select Item Code or Branch or Posting Date")
	cond = ""
	rate = 0.00
	if location != "NA":
		cond += "AND location = '{}'".format(location)

		rate = frappe.db.sql(""" select selling_price as rate 
							from `tabSelling Price Rate` 
							where parent = '{0}' 
							and particular = '{1}' 
							{2} 
						""".format(price_list, item_code, cond), as_dict =1)
	if not rate:
		rate = frappe.db.sql(""" select selling_price as rate 
								from `tabSelling Price Rate` 
								where parent = '{0}' 
								and particular = '{1}' 
								and (location is NULL or location = '') 
							""".format(price_list, item_code), as_dict =1)
	if not rate:
		rate = frappe.db.sql(""" select selling_price as rate 
								from `tabSelling Price Rate` 
								where parent = '{0}' 
								and particular = '{1}'
							""".format(price_list, item_code), as_dict =1)		
	if not rate:
		species = frappe.db.get_value("Item", item_code, "species")
		if species:
			item_sub_group = frappe.db.get_value("Item", item_code, "item_sub_group")
			timber_class, timber_type = frappe.db.get_value("Timber Species", species, ["timber_class", "timber_type"])
			rate = frappe.db.sql("""select selling_price as rate 
									from `tabSelling Price Rate` 
									where parent = '{0}' 
									and particular = '{1}' 
									and timber_type = '{2}' 
									and item_sub_group = '{3}' 
									'{4}'""".format(price_list, timber_class, timber_type, item_sub_group, cond), as_dict =1)
			if not rate:
				rate = frappe.db.sql(""" select selling_price as rate 
										from `tabSelling Price Rate` 
										where parent = '{0}' 
										and particular = '{1}' 
										and timber_type = '{2}' 
										and item_sub_group = '{3}' 
										and (location is NULL or location = '' )
									""".format(price_list, timber_class, timber_type, item_sub_group), as_dict =1)
	return rate and flt(rate[0].rate) or 0.0
