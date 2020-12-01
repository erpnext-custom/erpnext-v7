# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt, cstr
from frappe import msgprint, _

def execute(filters=None):
	if not filters: filters = {}

	data = get_data(filters)
	columns = get_columns(filters)

	return columns, data

def get_columns(filters):
	columns = [
		_("Equipment Code") + ":Link/Equipment:120",
	 	_("Registration No") + "::90",
	 	_("Equipment Type") + "::120",
	 	_("Equipment Model") + "::140",
	 	_("Branch") + "::120",
		_("Belongs To") + "::120"		 
	]
	if filters.get("owner") == 'Own':
		columns.append(_("Employee") + ":Link/Employee:120")
		columns.append(_("Employee Name") + "::120")
	return columns

def get_data(filters):
	equipment_query = frappe.db.sql(""" select e.name, e.equipment_number, e.equipment_type, e.equipment_model, e.owned_by from `tabEquipment` e 
			where 1 = 1 and e.not_cdcl = 1""".format(owner))

	other_asset_query = frappe.db.sql(""" select a.name, a.asset_name, a.brand, a.model, a.owned_by from `tabAsset Others` a where 1 = 1""")

	data = list(equipment_query) + list(other_asset_query)

	
	return frappe.db.sql(data)
