# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt, datetime
from frappe.core.doctype.user.user import send_sms
import re

class LotAllotment(Document):
	def autoname(self):
		naming_abbr = ""
		now = ""
		year = ""
		month = ""
		if self.allotment_type == "Direct Allotment":
			naming_abbr = "DALL"
		elif self.allotment_type == "Monthly Allotment":
			naming_abbr = "MALL"
		now = datetime.datetime.now()
		year = datetime.datetime.strftime((now),"%y")
		month = datetime.datetime.strftime((now),"%m")
		naming_code = naming_abbr+year+month
		pname = frappe.db.sql("select name from `tabLot Allotment` where name like '{}%' order by name desc limit 1".format(naming_code),as_dict=True)
		if not pname:
			self.name = naming_code+"00001"
		else:
			num=[]
			num = [int(s) for s in re.findall(r"\d+",pname[0].name)]  	
			self.name = naming_abbr+str(num[0]+1)

	def validate(self):
		self.check_duplicates()
		self.calculate_amount()
	
	def on_submit(self):
		self.sendsms()

	def check_duplicates(self):
		entries = []
		for d in self.lot_list_lot:
			entries.append(d.lot_number)
		n_dup = set(entries)
		
		if len(entries) != len(n_dup):
			frappe.throw("There cannot be duplicate lot list allotment")
		
	def sendsms(self,msg=None):
		if self.docstatus == 1:
			lots = []
			for d in self.lot_list_lot:
				lots.append(d.lot_number)
			msg = "Dear Customer, Timber Lot Number(s) {0} Are Alloted To Your Site {2}. Tran Ref No {1}.".format(tuple(lots),self.name, self.site)
		mobile_no = frappe.db.get_value("User", self.customer_id, "mobile_no")
		if mobile_no:
			send_sms(mobile_no, msg)


	def calculate_amount(self):
		discount = additional = pieces = volume = total = 0
		for d in self.lot_list_lot	:
			d.payable_amount = d.discount = d.additional = d.pieces = d.total_amount = 0
			for i in self.lot_list_details:
				if i.lot_number == d.lot_number:
					# d.discount += i.discount_amount * i.total_volume
					# d.additional += i.additional_cost * i.total_volume
					d.pieces += int(i.total_pieces)
					d.payable_amount += i.amount
					d.total_amount += i.amount

			if d.discount > 0:
				if d.discount < 0:
					frappe.throw("Discount Amount Cannot Be Greater Than The Actual Amount")
				d.payable_amount -= d.discount
			if d.additional > 0:
				d.payable_amount += d.additional

		for d in self.lot_list_details:
			pieces += int(d.total_pieces)
			volume += d.total_volume
			# discount   += d.discount_amount * d.total_volume
			# additional += d.additional_cost * d.total_volume
			total += d.amount

		self.total_payable = total

		if self.additional_cost != 0:
			self.total_payable += self.additional_cost
			
		if self.discount_amount != 0:
			self.total_payable -= self.discount_amount
		
		if self.challan_cost:
			self.total_payable += self.challan_cost
		
		self.total_amount = total
		self.total_volume = volume
		self.total_pieces = pieces


	def get_lot_list_detail(self, lot_number = None, posting_date = None):
		data = []
		price_template = []
		lot_list_details = frappe.db.sql("""
			select b.parent, branch, location, b.item, b.item_name, b.item_sub_group, b.total_volume, b.total_pieces from `tabLot List Details` b, `tabLot List` a where a.name = b.parent and b.parent = '{0}'
		""".format(lot_number), as_dict=True)

		for a in lot_list_details:
			price_template = self.get_price_template(a.branch, a.location, a.item, posting_date)
			if price_template:
				data.append({"branch": a.branch, "location": a.location, "lot_number": a.parent, "item": a.item, "item_name": a.item_name, "item_sub_group": a.item_sub_group, "total_volume": flt(a.total_volume), "total_pieces": a.total_pieces, "parent": price_template[0]['parent'], "selling_price":flt(price_template[0]['selling_price'])})
			
			else:
				data.append({"branch": a.branch, "location": a.location, "lot_number": a.parent, "item": a.item, "item_name": a.item_name, "item_sub_group": a.item_sub_group, "total_volume": flt(a.total_volume), "total_pieces": a.total_pieces})
		
		return data
	
	#get price template automatically from lot details pulled in above method Kinley Dorji
	def get_price_template(self, branch, location, item, posting_date):
		data = []
		price_template = ""
		if location != None:
			price_template = frappe.db.sql("""select a.parent, b.selling_price from `tabSelling Price Branch` a, `tabSelling Price Rate` b
			where a.parent = b.parent and a.branch = '{0}' and b.location = '{1}' and b.particular = '{2}'
			and exists (select 1 from `tabSelling Price` where name = a.parent and '{3}' between from_date and to_date) group by a.parent
			""".format(branch, location, item, posting_date), as_dict = True)

		if not price_template:
			price_template = frappe.db.sql(""" select a.parent, b.selling_price from `tabSelling Price Branch` a, `tabSelling Price Rate` b where a.parent = b.parent and a.branch = '{0}' and b.particular = '{1}' and exists (select 1 from `tabSelling Price` where name = a.parent and '{2}' between from_date and to_date) group by a.parent""".format(branch, item, posting_date), as_dict =True)
			item_group = frappe.db.get_value("Item", item, "item_group")
			if not price_template and item_group == 'Timber Products':
				item_species = frappe.db.get_value("Item", item, "species")
				if not item_species:
					return
				else:
					timber_class, timber_type = frappe.db.get_value("Timber Species", item_species, ["timber_class", "timber_type"])
					item_sub_group = frappe.db.get_value("Item", item, "item_sub_group")
					if location != None:
						price_template = frappe.db.sql(""" select a.parent, b.selling_price  from `tabSelling Price Branch` a, `tabSelling Price Rate` b where a.parent = b.parent and a.branch = '{0}' and b.location = '{1}' and b.particular = '{2}' and b.timber_type = '{3}' and b.item_sub_group = '{5}' and exists (select 1 from `tabSelling Price` where name = a.parent and '{4}' between from_date and to_date) group by a.parent""".format(branch, location, timber_class, timber_type, posting_date, item_sub_group), as_dict =True)
					if not price_template:
						price_template = frappe.db.sql(""" select a.parent, b.selling_price  from `tabSelling Price Branch` a, `tabSelling Price Rate` b where a.parent = b.parent and a.branch = '{0}' and b.particular = '{1}' and b.timber_type = '{2}' and b.item_sub_group = '{4}' and exists (select 1 from `tabSelling Price` where name = a.parent and '{3}' between from_date and to_date) and (b.location is NULL or b.location = '') group by a.parent""".format(branch, timber_class, timber_type, posting_date, item_sub_group), as_dict = True)
		if price_template:
			for a in price_template:
				data.append({"parent": a.parent, "selling_price": flt(a.selling_price)})
		else:
			frappe.throw("Rate for Item: <b> '{0}' </b> Is Not Defined In Selling Price List, Please Define The Rate".format(item))
		return data