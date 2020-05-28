# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cint, flt, now, add_days, add_to_date, get_datetime
from frappe.model.document import Document
from erpnext.crm_utils import get_branch_rate, get_branch_location, get_vehicles, get_limit_details
from erpnext.crm_api import init_payment
from frappe.core.doctype.user.user import send_sms

class CustomerOrder(Document):
	def validate(self):
		self.check_for_duplicates()
		self.get_site_details()
		self.get_item_details()
		self.update_item_rate()
		self.validate_transportation()
		self.update_payable_amount()
		self.validate_quantity_limits()
		self.update_user_details()

	def before_submit(self):
		self.posting_date = now()

	def on_submit(self):
		self.update_site()
		self.make_sales_order()
		self.sendsms()

	def on_cancel(self):
		self.update_site()

	def check_for_duplicates(self):
		if frappe.db.sql("""select count(*) from `tabCustomer Order` where user = "{}" and site = "{}" 
			and docstatus = 0 and name != "{}" """.format(self.user, self.site, self.name))[0][0]:
			frappe.throw(_("New orders not allowed as you already have unpaid order(s). Please complete the payment/cancel the previous order(s)"))

	def update_user_details(self):
		if frappe.db.exists("User Account", self.user):
			doc = frappe.get_doc("User Account", self.user)
			self.full_name = doc.full_name
			self.mobile_no = doc.mobile_no
			self.alternate_mobile_no = doc.alternate_mobile_no

	def sendsms(self,msg=None):
		if self.docstatus == 1:
			msg = "Your order for {0} is placed successfully. Tran Ref No {1}".\
				format(str(self.item_name)+", Quantity "+str(self.total_quantity)+" "+str(self.uom),self.name)

		mobile_no = frappe.db.get_value("User", self.user, "mobile_no")
		if mobile_no:
			send_sms(mobile_no, msg)

	def initiate_payment(self):
		if self.bank_code and self.bank_account:
			init_payment(self.name, self.bank_code, self.bank_account, flt(self.total_balance_amount))

	def validate_quantity_limits(self):
		# quantity validations
		if not flt(self.total_quantity):
			frappe.throw(_("Total Quantity cannot be empty"))

		self.site_item_name 	= None
		self.total_available_quantity = None
		limits 			= get_limit_details(self.site, self.branch, self.item)
		if limits:
			self.site_item_name = limits.site_item_name
			self.total_available_quantity = flt(limits.total_available_quantity)
		if flt(self.total_quantity) > flt(self.total_available_quantity):
			frappe.throw(_("You have crossed your overall quota by quantity {0} {1}")\
				.format(flt(self.total_quantity)-flt(self.total_available_quantity), self.uom),title="Insufficient Balance")

		if 'has_limit' in limits:
			limits 		= limits.has_limit
			self.order_limit_type = limits.limit_type
			if limits.limit_type == "Quantity":
				balance 			= 0
				self.daily_quantity_limit 	= 0
				self.daily_available_quantity	= 0
				self.weekly_quantity_limit 	= 0
				self.weekly_available_quantity	= 0
				self.monthly_quantity_limit 	= 0
				self.monthly_available_quantity	= 0
				self.yearly_quantity_limit 	= 0
				self.yearly_available_quantity	= 0
				if flt(limits.daily_quantity_limit):
					balance = flt(limits.daily_quantity_limit)-flt(limits.daily_ordered_quantity)
					self.daily_quantity_limit 	= flt(limits.daily_quantity_limit)
					self.daily_available_quantity 	= flt(balance)
					if flt(balance) < flt(self.total_quantity):
						frappe.throw(_("You have crossed your daily quota by quantity {0} {1}")\
							.format(flt(self.total_quantity)-flt(balance), self.uom),title="Insufficient Balance")
				if flt(limits.weekly_quantity_limit):
					balance = flt(limits.weekly_quantity_limit)-flt(limits.weekly_ordered_quantity)
					self.weekly_quantity_limit 	= flt(limits.weekly_quantity_limit)
					self.weekly_available_quantity 	= flt(balance)
					if flt(balance) < flt(self.total_quantity):
						frappe.throw(_("You have crossed your weekly quota by quantity {0} {1}")\
							.format(flt(self.total_quantity)-flt(balance), self.uom),title="Insufficient Balance")
				if flt(limits.monthly_quantity_limit):
					balance = flt(limits.monthly_quantity_limit)-flt(limits.monthly_ordered_quantity)
					self.monthly_quantity_limit 	= flt(limits.monthly_quantity_limit)
					self.monthly_available_quantity = flt(balance)
					if flt(balance) < flt(self.total_quantity):
						frappe.throw(_("You have crossed your monthly quota by quantity {0} {1}")\
							.format(flt(self.total_quantity)-flt(balance), self.uom),title="Insufficient Balance")
				if flt(limits.yearly_quantity_limit):
					balance = flt(limits.yearly_quantity_limit)-flt(limits.yearly_ordered_quantity)
					self.yearly_quantity_limit 	= flt(limits.yearly_quantity_limit)
					self.yearly_available_quantity 	= flt(balance)
					if flt(balance) < flt(self.total_quantity):
						frappe.throw(_("You have crossed your yearly quota by quantity {0} {1}")\
							.format(flt(self.total_quantity)-flt(balance), self.uom),title="Insufficient Balance")
			elif limits.limit_type == "Truck Loads":
				balance 			= 0
				self.daily_quantity_limit_count 	= 0
				self.daily_available_quantity_count	= 0
				self.weekly_quantity_limit_count 	= 0
				self.weekly_available_quantity_count	= 0
				self.monthly_quantity_limit_count 	= 0
				self.monthly_available_quantity_count	= 0
				self.yearly_quantity_limit_count 	= 0
				self.yearly_available_quantity_count	= 0
				if flt(limits.daily_quantity_limit_count):
					balance = flt(limits.daily_quantity_limit_count)-flt(limits.daily_ordered_quantity_count)
					self.daily_quantity_limit_count 	= flt(limits.daily_quantity_limit_count)
					self.daily_available_quantity_count 	= flt(balance)
					if flt(balance) < flt(self.noof_truck_load):
						frappe.throw(_("You have crossed your daily quota by {0} truck load(s)")\
							.format(flt(self.noof_truck_load)-flt(balance)),title="Insufficient Balance")
				if flt(limits.weekly_quantity_limit_count):
					balance = flt(limits.weekly_quantity_limit_count)-flt(limits.weekly_ordered_quantity_count)
					self.weekly_quantity_limit_count 	= flt(limits.weekly_quantity_limit_count)
					self.weekly_available_quantity_count 	= flt(balance)
					if flt(balance) < flt(self.noof_truck_load):
						frappe.throw(_("You have crossed your weekly quota by {0} truck load(s)")\
							.format(flt(self.noof_truck_load)-flt(balance)),title="Insufficient Balance")
				if flt(limits.monthly_quantity_limit_count):
					balance = flt(limits.monthly_quantity_limit_count)-flt(limits.monthly_ordered_quantity_count)
					self.monthly_quantity_limit_count 	= flt(limits.monthly_quantity_limit_count)
					self.monthly_available_quantity_count   = flt(balance)
					if flt(balance) < flt(self.noof_truck_load):
						frappe.throw(_("You have crossed your monthly quota by {0} truck load(s)")\
							.format(flt(self.noof_truck_load)-flt(balance)),title="Insufficient Balance")
				if flt(limits.yearly_quantity_limit_count):
					balance = flt(limits.yearly_quantity_limit_count)-flt(limits.yearly_ordered_quantity_count)
					self.yearly_quantity_limit_count 	= flt(limits.yearly_quantity_limit_count)
					self.yearly_available_quantity_count 	= flt(balance)
					if flt(balance) < flt(self.noof_truck_load):
						frappe.throw(_("You have crossed your yearly quota by {0} truck load(s)")\
							.format(flt(self.noof_truck_load)-flt(balance)),title="Insufficient Balance")

	def get_item_details(self):
		if not self.item:
			frappe.throw(_("Item is mandatory"))

		item = frappe.get_doc("Item", self.item)
		self.item_name		= item.item_name
		self.item_sub_group 	= item.item_sub_group
		self.uom		= item.stock_uom
		
		self.total_available_quantity = 0
		if frappe.db.exists("Site Item", {"parent": self.site, "item_sub_group": self.item_sub_group}):
			doc = frappe.get_doc("Site Item", {"parent": self.site, "item_sub_group": self.item_sub_group})
			self.site_item_name     = doc.name
			self.total_available_quantity = flt(doc.balance_quantity)
		else:
			frappe.throw(_("Material {0} not found under Site").format(self.item_sub_group))

	def update_site(self):
		""" update Site Item quantity """
		#if self.approval_status == "Rejected":
		#	return
		#elif self.approval_status == "Pending":
		#	frappe.throw(_("Request cannot be submitted in <b>Pending</b> status"))
	
		doc = frappe.get_doc("Site Item", {"parent": self.site, "item_sub_group": self.item_sub_group})
		total_quantity = -1*flt(self.total_quantity) if self.docstatus == 2 else flt(self.total_quantity)
		doc.ordered_quantity = flt(doc.ordered_quantity) + flt(total_quantity)
		doc.balance_quantity = flt(doc.expected_quantity) + flt(doc.extended_quantity) - flt(doc.ordered_quantity)
		doc.save(ignore_permissions=True)

		'''
		# update available_balance for all orders in draft mode
		for i in frappe.get_all('Customer Order', fields=["name"], filters={'user': self.user, 'item_sub_group': self.item_sub_group, 'docstatus': 0}):
			co = frappe.get_doc('Customer Order': i.name)
			co.balance_quantity = flt(doc.balance_quantity)
			co.save(ignore_permissions=True)
		'''

	def update_distance(self):
		distance = 0
		if self.transport_mode == "Common Pool":
			distance = frappe.db.get_value("Site Distance", {"parent":self.site,"item":self.item,"branch":self.branch}, "distance")
			self.distance = flt(distance) 
			if not flt(distance):
				frappe.throw(_("Distance not available between {0} and site location").format(self.branch))

	def make_sales_order(self):
		if frappe.db.exists("Site Type", {"name": self.site_type, "payment_required": 1}) \
			and not frappe.db.exists("Customer Payment", {"customer_order": self.name, "docstatus": 1}):
			frappe.throw(_("You need to make payment first to place the order"))

		item = frappe.get_doc("Item", self.item)
		wh = frappe.db.get_value("CRM Branch Setting", {"branch": self.branch}, "default_warehouse")
		if not wh:
			frappe.throw(_("Default warehouse is not linked for the branch {0}").format(self.branch))

		if frappe.db.exists("Business Activity", item.item_sub_group):
			business_activity = item.item_sub_group
		else:
			business_activity = frappe.db.get_value("Business Activity", {"is_default": 1})

		doc = frappe.get_doc({
				"doctype": "Sales Order",
				"branch": self.branch,
				"site": self.site,
				"customer_order": self.name,
				"title": "Sale of {0}({2}) via {1}".format(self.item_sub_group, self.name, self.transport_mode),	
				"naming_series": item.item_group,
				"customer": self.customer,
				"transaction_date": now(),
				"order_type": "Sales",
				"currency": "BTN",
				"conversion_rate": 1,
				"price_list_currency": "BTN",
				"plc_conversion_rate": 1,
				"rate_template": self.transportation_rate if self.transport_mode == "Common Pool" else None,
				"total_distance": flt(self.distance) if self.transport_mode == "Common Pool" else 0,
				"transportation_charges": self.total_transportation_rate if self.transport_mode == "Common Pool" else None,
				"transportation_rate": self.transport_rate if self.transport_mode == "Common Pool" else None,
				"total_quantity": self.total_quantity if self.transport_mode == "Common Pool" else None,	
				"delivery_date": add_days(now(), cint(self.lead_time)),
				"items": [{
					"item_code": self.item,
					"item_name": self.item_name,
					"price_template": self.selling_price,
					"qty": flt(self.total_quantity),
					"rate": flt(self.item_rate),
					"warehouse": wh,
					"business_activity": business_activity
				}]
			})
		doc.save(ignore_permissions=True)
		doc.submit()
		self.db_set("sales_order", doc.name)

	def get_site_details(self):
		if not self.site:
			frappe.throw(_("Please select a Site first"))
		doc = frappe.get_doc("Site", self.site) 
		self.site_type	= doc.site_type
		self.latitude	= doc.latitude
		self.longitude	= doc.longitude
		self.dzongkhag	= doc.dzongkhag
		self.plot_no	= doc.plot_no
		self.site_location	= doc.location

		if not frappe.db.exists("Customer", {"customer_id": self.user}):
			frappe.throw(_("Customer account not found"))
		self.customer = frappe.db.get_value("Customer", {"customer_id": self.user})

	def validate_transportation(self):
		noof_truck_load = 0
		if not self.transport_mode:
			frappe.throw(_("Please select preferred Transport Mode"))
		elif self.transport_mode == "Common Pool":
			if not flt(self.transport_rate):
				frappe.throw(_("Transportation Rate is not defined for {0}").format(self.branch))

			for i in self.get("pool_vehicles"):
				if flt(i.noof_truck_load) < 0:
					frappe.throw(_("Row#{0}: No.of Truck Loads cannot be a negative value").format(i.idx))
				noof_truck_load += flt(i.noof_truck_load)
		elif self.transport_mode == "Others":
			for i in self.get("pool_vehicles"):
				if flt(i.noof_truck_load) < 0:
					frappe.throw(_("Row#{0}: No.of Truck Loads cannot be a negative value").format(i.idx))
				noof_truck_load += flt(i.noof_truck_load)
		else:
			#get_vehicles(self.user, self.site, self.transport_mode)
			for i in self.get("vehicles"):
				if self.transport_mode == "Private Pool":
					if not cint(frappe.db.get_value("Site", self.site, "allow_private_pool")):
						frappe.throw(_("Private Pool transportation is not permitted for this site"))
					if not frappe.db.exists("Site Private Pool", {"parent": self.site, "vehicle": i.vehicle}):
						frappe.throw(_("Row#{0}: Vehicle {1} is not registered as private pool for site {2}")\
							.format(i.idx,i.vehicle,self.site))

				if self.transport_mode == "Self Owned Transport":
					if not frappe.db.exists("Vehicle", {"user": self.user, "name": i.vehicle}):
						frappe.throw(_("Row#{0}: Vehicle {1} is not registered under your account").format(i.idx,i.vehicle))

				if flt(i.noof_truck_load) < 0:
					frappe.throw(_("Row#{0}: No.of Truck Loads cannot be a negative value for vehicle {1}").format(i.idx,i.vehicle))
				noof_truck_load += flt(i.noof_truck_load)

			if self.transport_mode == "Self Owned Transport" and not frappe.db.exists("Vehicle", {"user": self.user}):
				frappe.throw(_("No vehicle found under your account. Please register your vehicle first"))
			if not self.get("vehicles"):
				frappe.throw(_("You need to select atleast one vehicle for {}").format(self.transport_mode))
		self.noof_truck_load = flt(noof_truck_load)

	def update_item_rate(self):
		''' update item_rate based on selected branch '''
		if not self.branch:
			frappe.throw(_("Material Source Branch is mandatory"))
		elif not self.item:
			frappe.throw(_("Material is mandatory"))
		elif not self.location:
			frappe.throw(_("Material Source Location is mandatory"))

		# get branch details
		item = get_branch_rate(site=self.site, branch=self.branch, item=self.item)
		if item:
			self.lead_time 		 = item[0].lead_time
			self.has_common_pool	 = item[0].has_common_pool
			self.transportation_rate = item[0].tr_name
			self.transport_rate 	 = item[0].tr_rate
			self.distance		 = item[0].distance
		else:
			self.lead_time 		 = 0
			self.has_common_pool	 = 0
			self.transportation_rate = None
			self.transport_rate 	 = 0
			self.distance		 = 0

		# get location based rate details
		item = get_branch_location(site=self.site, item=self.item, branch=self.branch, location=self.location)
		if item:
			self.selling_price = None
			if len(item) > 1:
				for i in item:
					if i.location:
						self.location = i.location
						self.selling_price = i.selling_price
						self.item_rate = i.item_rate
						break
			if not self.selling_price:
				self.location	   = item[0].location
				self.selling_price = item[0].selling_price
				self.item_rate 	   = item[0].item_rate
		else:
			self.selling_price	 = None
			self.item_rate 		 = 0

		if not self.selling_price:
			frappe.throw(_("Selling Price not available"))
		if not self.transport_mode:
			frappe.throw(_("Please choose a Transport Mode"))
		if not cint(self.has_common_pool) and self.transport_mode == "Common Pool":
			frappe.throw(_("Selected Warehouse does not offer transportation facility. Choose another Warehouse \
				or consider using Self Owned Transport"))

	def update_payable_amount(self):
		''' update total payable amount '''
		import math
		tbl = self.get("pool_vehicles") if self.transport_mode in("Common Pool","Others") else self.get("vehicles")
		total_quantity   	  = 0
		total_transportation_rate = 0


		for i in tbl:
			i.quantity	  = flt(i.vehicle_capacity) * flt(i.noof_truck_load)
			total_quantity	 += i.quantity

		if self.transport_mode == "Common Pool":
			total_transportation_rate = flt(self.distance) * flt(total_quantity) * flt(self.transport_rate) 

		self.total_quantity  	   	= total_quantity
		self.total_item_rate 	  	= flt(total_quantity) * flt(self.item_rate)
		self.total_transportation_rate	= flt(total_transportation_rate) 
		self.total_payable_amount  	= flt(flt(self.total_item_rate) + flt(self.total_transportation_rate),2)
		#if flt(self.total_payable_amount,2) - math.floor(flt(self.total_payable_amount,2)) != 0.50:
		#	self.total_payable_amount = round(self.total_payable_amount)

		self.total_balance_amount	= flt(self.total_payable_amount,2)
