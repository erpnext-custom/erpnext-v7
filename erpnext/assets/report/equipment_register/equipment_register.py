# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt, cstr
from frappe import msgprint, _

def execute(filters=None):
	if not filters: filters = {}

	data = get_data(filters)
	columns = get_columns(data)

	return columns, data

def get_columns(data):
	columns = [
		_("Asset Code") + ":Link/Asset:100",
		 _("Old Asset Code") + "::140",
	        _("Serial No.") + "::120",
		 _("Asset Category") + "::140",
		_("Asset Sub-Category") + "::120",
 		 _("Issued To") + "::140",
	 	 _("Cost Center") + "::120",
	         _("Purchase Date") + "::80",
		 _("Issued Date") + "::80",
		 _("Equipment Code") + ":Link/Equipment:120",
	 	 _("Registration No") + "::90",
	 	 _("Equipment Type") + "::120",
	 	 _("Equipment Model") + "::140",
	 	 _("Chassis No.") + "::140",
	 	_("Engine No.") + "::120",
	         _("Asset Amount") + " :Currency:100",
	 	_("Asset Branch") + "::120",
	 	_("Eqp. Branch") + "::120",
	 	 		 
	]

	return columns

def get_data(filters):
		

	        data = """ SELECT a.name, a.old_asset_code, a.serial_number, a.asset_category, a.asset_sub_category,
 (SELECT employee_name FROM tabEmployee AS emp WHERE emp.name = a.issued_to) AS issuedto, a.cost_center, a.purchase_date, a.presystem_issue_date, e.name, e.equipment_number, e.equipment_type, e.equipment_model,
 e.chassis_number, e.engine_number,
a.gross_purchase_amount, a.branch, e.branch FROM tabAsset a,  tabEquipment e
WHERE a.name = e.asset_code """

		if filters.get("fiscal_year"): 
			data += " and year(a.purchase_date) = {0}".format(filters.fiscal_year)

		if filters.get("company"): 
			data += " and a.company = '{0}'".format(filters.company)
		if filters.get("cost_center"): 
			data += " and a.cost_center = '{0}'".format(filters.cost_center)	

		return frappe.db.sql(data)
