# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import cint, cstr, flt, fmt_money, formatdate, nowtime, getdate

class LotList(Document):
	def validate(self):
		# if self.items:
		# 	self.calculate_vol()
		self.set_missing_values()
		i_group_check = total_volume = 0
		for d in self.lot_list_items:
			item_group = frappe.db.get_value("Item",d.item,"item_group")
			if item_group != "Timber Products":
				i_group_check += 1
			else:
				total_volume += flt(d.total_volume)

		if i_group_check != 0:
			frappe.throw("Lot List can only be created for Timber Products")
		
		self.total_volume = total_volume



		self.lot_no = self.name
		

	def on_submit(self):
		pass
	
	def set_missing_values(self):
		for d in self.lot_list_items:
			if d.item and not d.item_name:
				d.item_name = frappe.db.get_value("Item",d.item,"item_name")
				d.item_sub_group = frappe.db.get_value("Item",d.item,"item_sub_group")
				timber_species = frappe.db.get_value("Item",d.item,"species")
				if timber_species:
					d.t_species = timber_species
					d.timber_class = frappe.db.get_value("Timber Species",d.t_species,"timber_class")

	# def calculate_vol(self):
		# total_vol=0.0
		# count = 0
		# for item in self.items:
		# 	in_inches = 0
		# 	if self.item_sub_group == "Sawn" or self.item_sub_group == "Block" or self.item_sub_group == "Field Sawn":
		# 		item.volume = ((flt(item.length) * flt(item.girth) * flt(item.height)) / 144) * item.number_pieces
		# 	else:
		# 		f = str(item.girth).split(".")
		# 		girth_in_inches = cint(f[0]) * 12
		# 		if len(f) > 1:
		# 			if cint(f[1]) > 11:
		# 				frappe.throw("Inches should be smaller than 12 on row {0}".format(item.idx))
		# 			girth_in_inches += cint(f[1])
				
		# 		item.volume = flt(flt(flt(girth_in_inches * girth_in_inches) * flt(item.length)) / 1809.56) * flt(item.number_pieces) 
					
		# 	total_vol += flt(item.volume)
		# 	count += int(item.number_pieces)
		# if self.auto_calculate:
		# 	self.total_volume = total_vol

		# self.total_pieces = count
	
	def get_item_details(self, item=None):
		data = []
		for d in frappe.db.sql("select item_name, item_sub_group, species, case when species != \"\" then (select ts.timber_class from `tabTimber Species` ts where ts.species = i.species) end as timber_class from `tabItem` i where i.name = '{0}'".format(item),as_dict = True):
			data.append({"item_name": d.item_name, "item_sub_group":d.item_sub_group, "species":d.species, "timber_class":d.timber_class})
		return data	

	def get_warehouse(doctype=None, txt=None, searchfield=None, start=None, page_len=None, filters=None):
		if not filters.get("branch"):
			frappe.throw("Please Select Branch First")
		return frappe.db.sql("select parent from `tabWarehouse Branch` where branch = {0}".format(filters.get("branch")))
@frappe.whitelist()
def make_sales_order(source_name, target_doc=None):
	def set_missing_values(source, target):
		pass

	def update_item(source, target, source_parent):
		target.warehouse = source_parent.warehouse
		sub_group = frappe.db.get_value("Item", source.item, "item_sub_group")
		lot_check = frappe.db.get_value("Item Sub Group", sub_group, "lot_check")
		target.item_name = frappe.db.get_value("Item", source.item, "item_name")
		target.stock_uom = frappe.db.get_value("Item", source.item, "stock_uom")
		target.business_activity = frappe.db.get_value("Item", source.item, "business_activity")
		
		if lot_check:
			if source.total_volume < 0:
				frappe.msgprint("Not available volume under the selected Lot")
			else:
				target.qty = source.total_volume
				target.stock_qty = source.total_volume


	target_doc = get_mapped_doc("Lot List", source_name, {
                "Lot List": {
                        "doctype": "Sales Order",
                        "field_map": {
				"branch": "branch",
				"posting_date":"po_date",
				# "currency": "price_list_currency"
                #         },
                #         "validation": {
                #                 "docstatus": ["=", 1]
                #         }
						}
                },
                "Lot List Details": {
                        "doctype": "Sales Order Item",
                        "field_map": [
								["parent", "lot_number"],
                                ["item", "item_code"],
                                ["total_volume", "balance"],
								["total_pieces", "total_pieces"]
                        ],
						"postprocess": update_item,
                },
    }, target_doc, set_missing_values)

	return target_doc

@frappe.whitelist()
def make_stock_entry(source_name, target_doc=None):
	def set_missing_values(source, target):
		pass

	def update_item(source, target, source_parent):
		target.s_warehouse = source_parent.warehouse
		sub_group = frappe.db.get_value("Item", source.item, "item_sub_group")
		lot_check = frappe.db.get_value("Item Sub Group", sub_group, "lot_check")
		target.item_name = frappe.db.get_value("Item", source.item, "item_name")
		target.stock_uom = frappe.db.get_value("Item", source.item, "stock_uom")
		target.uom = frappe.db.get_value("Item", source.item, "stock_uom")
		if lot_check:
			if source.total_volume < 0:
				frappe.msgprint("Not available volume under the selected Lot")
			else:
				target.qty = source.total_volume


	target_doc = get_mapped_doc("Lot List", source_name, {
                "Lot List": {
                        "doctype": "Stock Entry",
                        "field_map": {
				"branch": "branch",
				"posting_date":"po_date",
				# "currency": "price_list_currency"
                #         },
                #         "validation": {
                #                 "docstatus": ["=", 1]
                #         }
						}
                },
                "Lot List Details": {
                        "doctype": "Stock Entry Detail",
                        "field_map": [
								["parent", "lot_number"],
                                ["item", "item_code"],
                                ["total_volume", "qty"],
                                ["total_volume", "transfer_qty"],
                        ],
						"postprocess": update_item,
                },
    }, target_doc, set_missing_values)

	return target_doc

@frappe.whitelist()
def get_lot_list(doctype=None, txt=None, searchfield=None, start=None, page_len=None, filters=None):
	cond = ""
	if filters.get("branch"):
		cond += " and l.branch = '{0}'".format(filters.get("branch"))
	else:
		frappe.throw("Please select Branch first")

	return frappe.db.sql("""
		select name from `tabLot List` l
		where (l.sales_order is NULL or l.sales_order = "")
        and (l.stock_entry is NULL or l.stock_entry = "")
		and (l.production is NULL or l.production = "")
		and l.docstatus = 1
		and not exists(select 1
				from `tabLot Allotment Lots` la
				where la.lot_number = l.name
				and la.docstatus != 2)
		and `{key}` LIKE %(txt)s {cond}
		order by name limit %(start)s, %(page_len)s
		""".format(key=searchfield, cond=cond), {
			'txt': '%' + txt + '%',
			'start': start, 'page_len': page_len
		})

@frappe.whitelist()
def get_la_lot_list(doctype=None, txt=None, searchfield=None, start=None, page_len=None, filters=None):
	if not filters.get("branch"):
		frappe.throw("Please Select Branch First")

	return frappe.db.sql("""
		select name from `tabLot List` l
		where l.branch = '{}' and (l.sales_order is NULL or l.sales_order = "")
        and (l.stock_entry is NULL or l.stock_entry = "")
		and (l.production is NULL or l.production = "")
		and l.docstatus = 1
		and not exists(select 1
				from `tabLot Allotment Lots` la
				where la.lot_number = l.name
				and la.docstatus != 2)
		""".format(filters.get("branch")))
