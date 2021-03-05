# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
'''
------------------------------------------------------------------------------------------------------------------------------------------
Version          Author         Ticket#           CreatedOn          ModifiedOn          Remarks
------------ --------------- --------------- ------------------ -------------------  -----------------------------------------------------
1.0.190401       SHIV		                                     2019/04/01         Refined process for making SL and GL entries
------------------------------------------------------------------------------------------------------------------------------------------                                                                          
'''

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, cstr, flt, fmt_money, formatdate, nowtime, getdate
from erpnext.accounts.utils import get_fiscal_year
from erpnext.custom_utils import check_future_date, get_branch_cc, prepare_gl, prepare_sl, get_settings_value
from erpnext.controllers.stock_controller import StockController
from erpnext.stock.utils import get_stock_balance

class Production(StockController):
	def validate(self):
		check_future_date(self.posting_date)
		self.check_cop()
		self.validate_data()
		self.validate_warehouse()
		self.validate_supplier()
		self.validate_items()
		self.validate_posting_time()
		self.validate_transportation()
		self.validate_raw_material_product_qty()

	def validate_data(self):
		if self.production_type == "Adhoc" and not self.adhoc_production:
			frappe.throw("Select Adhoc Production to Proceed")
		if self.production_type == "Planned":
			self.adhoc_production = None
		if self.work_type == "Private" and not self.supplier:
			frappe.throw("Contractor is Mandatory if work type is private")

	def validate_warehouse(self):
		self.validate_warehouse_branch(self.warehouse, self.branch)

	def validate_supplier(self):
                if self.work_type == "Private" and not self.supplier:
                        frappe.throw("Supplier Is Mandiatory For Production Carried Out By Others")

	def validate_items(self):
		prod_items = self.get_production_items()
		for item in self.get("raw_materials"):
			if item.item_code not in prod_items:
				frappe.throw(_("{0} is not a Production Item").format(item.item_code))
			if flt(item.qty) <= 0:
				frappe.throw(_("Quantity for <b>{0}</b> cannot be zero or less").format(item.item_code))

                        """ ++++++++++ Ver 1.0.190401 Begins ++++++++++ """
                        # Following code added by SHIV on 2019/04/01
                        item.cost_center = self.cost_center
                        item.warehouse = self.warehouse
                        item.expense_account = get_expense_account(self.company, item.item_code)
                        """ ++++++++++ Ver 1.0.190401 Ends ++++++++++++ """

		for item in self.get("items"):
			item.production_type = self.production_type
			item.item_name, item.item_group = frappe.db.get_value("Item", item.item_code, ["item_name", "item_group"])

			if item.item_code not in prod_items:
				frappe.throw(_("{0} is not a Production Item").format(item.item_code))
			if flt(item.qty) <= 0:
				frappe.throw(_("Quantity for <b>{0}</b> cannot be zero or less").format(item.item_code))
			if flt(item.cop) <= 0:
				frappe.throw(_("COP for <b>{0}</b> cannot be zero or less").format(item.item_code))
		
			if self.production_type == "Planned":
				continue
			if item.item_sub_group == "Pole" and flt(item.qty_in_no) <= 0:
				frappe.throw("Number of Poles is required for Adhoc Loggings")
			reading_required, par, min_val, max_val = frappe.db.get_value("Item Sub Group", item.item_sub_group, ["reading_required", "reading_parameter", "minimum_value", "maximum_value"])
			if reading_required:
				if not flt(min_val) <= flt(item.reading) <=  flt(max_val):
					frappe.throw("<b>{0}</b> reading should be between {1} and {2} for {3} for Adhoc Production".format(par, frappe.bold(min_val), frappe.bold(max_val), frappe.bold(item.item_code)))
			else:
				item.reading = 0
			
			in_inches = 0
			f = str(item.reading).split(".")
			in_inches = cint(f[0]) * 12
			if len(f) > 1:
				if cint(f[1]) > 11:
					frappe.throw("Inches should be smaller than 12 on row {0}".format(item.idx))
				in_inches += cint(f[1])
			item.reading_inches = in_inches

			""" ++++++++++ Ver 1.0.190401 Begins ++++++++++ """
                        # Following code added by SHIV on 2019/04/01
			item.cost_center = self.cost_center
                        item.warehouse = self.warehouse
                        item.expense_account = get_expense_account(self.company, item.item_code)
                        """ ++++++++++ Ver 1.0.190401 Ends ++++++++++++ """

	def check_cop(self):
		for a in self.items:
			branch = frappe.db.sql("select 1 from `tabCOP Branch` where parent = %s and branch = %s", (a.price_template, self.branch))
			if not branch:
				frappe.throw("Selected COP is not defined for your Branch")

			cop = frappe.db.sql("select cop_amount from `tabCOP Rate Item` where parent = %s and item_code = %s", (a.price_template, a.item_code), as_dict=1)
			if not cop:
				frappe.throw("COP Rate is not defined for your Item")
			a.cop = cop[0].cop_amount
			if flt(a.cop) <= 0:
				frappe.throw("COP Cannot be zero or less")

	def before_submit(self):
		self.assign_default_dummy()
		self.check_cop()

	def on_submit(self):
		""" ++++++++++ Ver 1.0.190401 Begins ++++++++++ """
		# Following lines commented by SHIV on 2019/04/01
		#self.make_products_sl_entry()
		#self.make_products_gl_entry()
		#self.make_raw_material_stock_ledger()
		#self.make_raw_material_gl_entry()

		# Following lines added by SHIV on 2019/04/01 and modified by Thukten on 24/12/2020
		self.update_stock_ledger()
		self.make_gl_entries()

		""" ++++++++++ Ver 1.0.190401 Ends ++++++++++++ """
		self.make_production_entry()

	def on_cancel(self):
		self.assign_default_dummy()
		""" ++++++++++ Ver 1.0.190401 Begins ++++++++++ """
                # Following lines commented by SHIV on 2019/04/01
		#self.make_products_sl_entry()
		#self.make_products_gl_entry()
		#self.make_raw_material_stock_ledger()
		#self.make_raw_material_gl_entry()

                # Following lines added by SHIV on 2019/04/01
		self.update_stock_ledger()
		self.make_gl_entries_on_cancel()
		""" ++++++++++ Ver 1.0.190401 Ends ++++++++++++ """
		
		self.delete_production_entry()

        """ ++++++++++ Ver 1.0.190401 Begins ++++++++++ """
	# update_stock_ledger() method added by SHIV on 2019/04/01
	def update_stock_ledger(self):
		sl_entries = []

		# make sl entries for source warehouse first, then do the target warehouse
		for d in self.get('raw_materials'):
				if cstr(d.warehouse):
						sl_entries.append(self.get_sl_entries(d, {
								"warehouse": cstr(d.warehouse),
								"actual_qty": -1 * flt(d.qty),
								"incoming_rate": 0
						}))
						
		for d in self.get('items'):
				if cstr(d.warehouse):
						sl_entries.append(self.get_sl_entries(d, {
								"warehouse": cstr(d.warehouse),
								"actual_qty": flt(d.qty),
								"incoming_rate": flt(d.cop, 2)
						}))

		if self.transfer:
			if not self.to_warehouse:
				frappe.throw("Receiving warehouse is mandatory while transferring item")
			
			for d in self.get('items'):
				if cstr(d.warehouse):
						sl_entries.append(self.get_sl_entries(d, {
								"warehouse": cstr(d.warehouse),
								"actual_qty": -1 * flt(d.qty),
								"incoming_rate": 0
						}))
						
				if cstr(self.to_warehouse):
						sl_entries.append(self.get_sl_entries(d, {
								"warehouse": cstr(self.to_warehouse),
								"actual_qty": flt(d.qty),
								"incoming_rate": flt(d.cop, 2)
						}))

		if self.docstatus == 2:
				sl_entries.reverse()

		self.make_sl_entries(sl_entries, self.amended_from and 'Yes' or 'No')

        # get_gl_entries() method added by SHIV on 2019/04/01
        def get_gl_entries(self, warehouse_account):
                gl_entries = super(Production, self).get_gl_entries(warehouse_account)
                return gl_entries
        """ ++++++++++ Ver 1.0.190401 Ends ++++++++++++ """
        
	def assign_default_dummy(self):
		self.pol_type = None
		self.stock_uom = None 

	def make_products_sl_entry(self):
		sl_entries = []

		for a in self.items:
			sl_entries.append(prepare_sl(self,
				{
					"stock_uom": a.uom,
					"item_code": a.item_code,
					"actual_qty": a.qty,
					"warehouse": self.warehouse,
					"incoming_rate": flt(a.cop, 2)
				}))

		if sl_entries: 
			if self.docstatus == 2:
				sl_entries.reverse()

			self.make_sl_entries(sl_entries, self.amended_from and 'Yes' or 'No')

	def make_products_gl_entry(self):
		gl_entries = []
		wh_account = frappe.db.get_value("Account", {"account_type": "Stock", "warehouse": self.warehouse}, "name")
		if not wh_account:
			frappe.throw(str(self.warehouse) + " is not linked to any account.")
		expense_account = get_settings_value("Production Account Settings", self.company, "default_production_account")
		if not expense_account:
                        frappe.throw("Setup Default Production Account in Production Account Settings")
			
		for a in self.items:
			amount = flt(a.qty) * flt(a.cop)

			gl_entries.append(
				prepare_gl(self, {"account": wh_account,
						 "debit": flt(amount),
						 "debit_in_account_currency": flt(amount),
						 "cost_center": self.cost_center,
						})
				)

			gl_entries.append(
				prepare_gl(self, {"account": expense_account,
						 "credit": flt(amount),
						 "credit_in_account_currency": flt(amount),
						 "cost_center": self.cost_center,
						})
				)
			
			if self.transfer:
				to_wh_account = frappe.db.get_value("Account", {"account_type": "Stock", "warehouse": self.to_warehouse}, "name")
				frappe.throw("test " + to_wh_account)
				gl_entries.append(
					prepare_gl(self, {"account": to_wh_account,
							"debit": flt(amount),
							"debit_in_account_currency": flt(amount),
							"cost_center": self.cost_center,
							})
					)
				gl_entries.append(
					prepare_gl(self, {"account": wh_account,
							"credit": flt(amount),
							"credit_in_account_currency": flt(amount),
							"cost_center": self.cost_center,
							})
					)	

		if gl_entries:
			from erpnext.accounts.general_ledger import make_gl_entries
			make_gl_entries(gl_entries, cancel=(self.docstatus == 2), update_outstanding="No", merge_entries=True)


	def make_raw_material_stock_ledger(self):
		sl_entries = []

		for a in self.raw_materials:
			sl_entries.append(prepare_sl(self,
				{
					"stock_uom": a.uom,
					"item_code": a.item_code,
					"actual_qty": -1 * flt(a.qty),
					"warehouse": self.warehouse,
					"incoming_rate": 0
				}))

		if sl_entries: 
			if self.docstatus == 2:
				sl_entries.reverse()

			self.make_sl_entries(sl_entries, self.amended_from and 'Yes' or 'No')

	def make_raw_material_gl_entry(self):
		gl_entries = []

		wh_account = frappe.db.get_value("Account", {"account_type": "Stock", "warehouse": self.warehouse}, "name")
		if not wh_account:
			frappe.throw(str(self.warehouse) + " is not linked to any account.")

		for a in self.raw_materials:
			stock_qty, map_rate = get_stock_balance(a.item_code, self.warehouse, self.posting_date, self.posting_time, with_valuation_rate=True)
                        amount = flt(a.qty) * flt(map_rate)

			expense_account = frappe.db.get_value("Item", a.item_code, "expense_account")
			if not expense_account:
				frappe.throw("Set Budget Account in {0}".format(frappe.get_desk_link("Item", a.item_code)))		

			gl_entries.append(
				prepare_gl(self, {"account": wh_account,
						 "credit": flt(amount),
						 "credit_in_account_currency": flt(amount),
						 "cost_center": self.cost_center,
						})
				)

			gl_entries.append(
				prepare_gl(self, {"account": expense_account,
						 "debit": flt(amount),
						 "debit_in_account_currency": flt(amount),
						 "cost_center": self.cost_center,
						})
				)

		if gl_entries:
			from erpnext.accounts.general_ledger import make_gl_entries
			make_gl_entries(gl_entries, cancel=(self.docstatus == 2), update_outstanding="No", merge_entries=True)

	def make_production_entry(self):
		for a in self.items:
			doc = frappe.new_doc("Production Entry")
			doc.flags.ignore_permissions = 1
			doc.item_code = a.item_code
			doc.item_name = a.item_name
			doc.item_group = a.item_group
			doc.qty = a.qty
			doc.uom = a.uom
			doc.cop = a.cop
			doc.company = self.company
			doc.currency = self.currency
			doc.branch = self.branch
			doc.location = self.location
			doc.cost_center = self.cost_center
			doc.warehouse = self.warehouse
			doc.posting_date = str(self.posting_date) + " " + str(self.posting_time)
			doc.ref_doc = self.name
			doc.production_type = self.production_type
			doc.adhoc_production = self.adhoc_production
			doc.equipment_number = a.equipment_number
			doc.equipment_model = a.equipment_model
			doc.transporter_type = frappe.db.get_value("Equipment", a.equipment, "equipment_type")
			doc.unloading_by = a.unloading_by
			doc.group = a.group
			doc.submit()

	def delete_production_entry(self):
		frappe.db.sql("delete from `tabProduction Entry` where ref_doc = %s", self.name)
	
	def get_finish_product(self):
		data = []
		if not self.branch and not self.posting_date:
			frappe.throw("Select branch and posting date to get the products after productions")

		if not self.raw_materials:
			frappe.throw("Please enter a raw material to get the Product")
		else:
			condition = ""
			for a in self.raw_materials:
				raw_material_item = a.item_code
				raw_material_qty = a.qty
				raw_material_unit = a.uom
				item_group = frappe.db.get_value("Item", a.item_code, "item_group")				
				cost_center = a.cost_center
				warehouse = a.warehouse
				expense_account = a.expense_account
				item_type = a.item_type
				if a.item_type:
					condition += " and item_type = '" + str(a.item_type) + "'"
				if a.warehouse:
					condition += " and warehouse = '" + str(a.warehouse) + "'"
		
		if raw_material_item:
			count = 0
			production_seting_code = ""
			for a in frappe.db.sql("""select name 
							from `tabProduction Settings`
							where branch = '{0}' and disable != 1
							and raw_material = '{1}'
							{3}
							and '{2}' between from_date and ifnull(to_date,now())		
				""".format(self.branch, raw_material_item, self.posting_date, condition), as_dict=True):
				count += 1
				production_seting_code = a.name
			
			if count > 1:
				frappe.throw("There are more than 1 production setting for this production parameters")

			if production_seting_code:
				for a in frappe.db.sql("""
						select parameter_type, ratio, item_code, item_name, item_type
						from `tabProduction Settings Item` 
						where parent = '{0}'				
					""".format(production_seting_code), as_dict=True):
					price_template = ""
					cop = ""
					product_qty = 0.00
					for b in frappe.db.sql("""select c.name, b.cop_amount 
						from `tabCost of Production` c, `tabCOP Branch` a, `tabCOP Rate Item` b 
						where c.name = a.parent and c.name = b.parent
						and a.branch = %s 
						and b.item_code = %s 
						and %s between c.from_date and c.to_date
					""",(str(self.branch), str(a.item_code), str(self.posting_date)), as_dict=True):
						price_template = b.name
						cop = b.cop_amount
					if flt(a.ratio) > 0:
						product_qty = (flt(a.ratio) * flt(raw_material_qty))/100
					data.append({
								"parameter_type": a.parameter_type,
								"item_code":a.item_code, 
								"item_name":a.item_name,
								"item_type":a.item_type, 
								"qty": product_qty,
								"uom": raw_material_unit,
								"price_template": price_template,
								"cop": cop,
								"cost_center": cost_center,
								"warehouse": warehouse,
								"expense_account": expense_account,
								"ratio": flt(a.ratio)
								})
				#frappe.msgprint("{}".format(data))
		if data:			
			return data
		else:
			frappe.msgprint("No records in production settings")

	def get_raw_material(self):
		data = []
		if not self.branch and not self.posting_date:
			frappe.throw("Select branch and posting date to get the raw materials")

		if not self.items:
			frappe.throw("Please enter a product to get the raw material")
		else:
			condition = ""
			for a in self.items:
				product_item = a.item_code
				product_qty = a.qty
				product_unit = a.uom				
				cost_center = a.cost_center
				warehouse = a.warehouse
				expense_account = a.expense_account
				item_type = a.item_type
				if a.item_type:
					condition += " and item_type = '" + str(a.item_type) + "'"
				if a.warehouse:
					condition += " and warehouse = '" + str(a.warehouse) + "'"
		
		if product_item:
			count = 0
			production_seting_code = ""
			for a in frappe.db.sql("""select name 
							from `tabProduction Settings`
							where branch = '{0}' and disable != 1
							and product = '{1}'
							{3}
							and '{2}' between from_date and ifnull(to_date,now())		
				""".format(self.branch, product_item, self.posting_date, condition), as_dict=True):
				count += 1
				production_seting_code = a.name
			
			if count > 1:
				frappe.throw("There are more than 1 production setting for this production parameters")

			if production_seting_code:
				for a in frappe.db.sql("""
						select parameter_type, ratio, item_code, item_name, item_type
						from `tabProduction Settings Item` 
						where parent = '{0}'				
				""".format(production_seting_code), as_dict=True):
					raw_material_qty = 0.00
					if flt(a.ratio) > 0:
						raw_material_qty = (flt(a.ratio) * flt(product_qty))/100
					data.append({
								"parameter_type": a.parameter_type,
								"item_code":a.item_code, 
								"item_name":a.item_name, 
								"item_type":a.item_type,
								"qty": raw_material_qty,
								"uom": product_unit,
								"cost_center": cost_center,
								"warehouse": warehouse,
								"expense_account": expense_account,
								})
		if data:			
			return data
		else:
			frappe.msgprint("No records in production settings")

	def validate_raw_material_product_qty(self):
		raw_material_qty = 0.0
		product_item_qty = 0.0
		for a in self.raw_materials:
			raw_material_qty += flt(a.qty)

		for b in self.items:
			product_item_qty += flt(b.qty)

		for c in self.production_waste:
			product_item_qty += flt(c.qty)

		self.raw_material_qty = raw_material_qty
		self.product_qty = product_item_qty
		
		if self.check_raw_material_product_qty:
			if round(self.product_qty,4) > round(self.raw_material_qty,4):
				#frappe.msgprint("product Qty is {} and Raw Material Qty is {} and difference is {}".format(cint(self.product_qty), cint(self.raw_material_qty), diff))
				frappe.throw("Sum of Crushed products should be less than or equivalent to raw materials feed.")

	def validate_transportation(self):
		for d in self.items:
			if not d.transporter_payment_eligible:
				return
			else:
				if not self.transporter_rate_base_on:
					frappe.throw("Please select transporter rate based on Location or Warehouse")

			if not d.equipment:
				frappe.throw("Please Select Equipment or Vehicle for transportation")

			if self.transporter_rate_base_on == "Location":
				rate = 0
				expense_account = 0
				qty = 0
				if not self.distance:
					self.distance = frappe.db.get_value("Location", self.location, "distance")

				if self.distance > 0:
					for a in frappe.db.sql(""" select r.name, d.rate, r.expense_account
											from `tabTransporter Rate` r, `tabTransporter Distance Rate` d 
											where r.name = d.parent
											and '{0}' between r.from_date and r.to_date
											and d.distance = '{1}'
											and r.from_warehouse = '{2}'
											""".format(self.posting_date, self.distance, self.warehouse), as_dict=True):
						rate = a.rate
						expense_account = a.expense_account
						transporter_rate = a.name

				if rate > 0:
					d.rate = rate
					d.transportation_expense_account = expense_account
					d.transporter_rate = transporter_rate
					if d.qty > 0:
						d.amount = flt(d.rate) * flt(d.qty)
					else:
						frappe.throw("Please provide the Quantity")				
				else:
					frappe.throw("Define Transporter Rate for distance {} in Transporter Rate ".format(self.distance))

@frappe.whitelist()
def get_expense_account(company, item):
        expense_account = frappe.db.get_value("Production Account Settings", {"company": company}, "default_production_account")
        if not expense_account:
                expense_account = frappe.db.get_value("Item", item, "expense_account")
        return expense_account
