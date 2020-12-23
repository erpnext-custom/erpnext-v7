# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

from frappe import _

def execute(filters=None):
        if not filters: filters = {}

        data = get_data(filters)
        columns = get_columns(filters)

        return columns, data

def get_columns(filters):
        columns = [
                _("Code") + ":Link/Equipment:120",
                _("Name") + "::90",
                _("Type") + "::120",
                _("Model") + "::140",
		_("Branch") + ":Link/Branch:120",
                _("Owner By") + ":Link/Supplier:120",
		_("Custodian") + ":Link/Employee:120"
        ]
        return columns

def get_data(filters):
        
	eqp_query = """ select e.name, e.equipment_number, e.equipment_type, e.equipment_model, e.branch, e.owned_by, e.current_operator 
                        from `tabEquipment` e 
                        where 1 = 1 and e.not_cdcl = 1"""

	ast_query = """ select a.name, a.asset_name, a.brand, a.model, a.branch, a.owned_by, a.issued_to from `tabAsset Others` a where 1 = 1"""
	if filters.get("branch"):
		eqp_query += " and e.branch = '{0}'".format(filters.get("branch"))
		ast_query += " and a.branch = '{0}'".format(filters.get("branch"))

	if filters.get("owner"):
		eqp_query += " and e.owned_by = '{0}'".format(filters.get("owner"))
		ast_query += " and a.owned_by = '{0}'".format(filters.get("owner"))

	if filters.get("custodian"):
		eqp_query += " and e.current_operator = '{0}'".format(filters.get("custodian"))
		ast_query += " and a.issued_to = '{0}'".format(filters.get("custodian"))			
	equipment_data = frappe.db.sql(eqp_query)
	asset_data = frappe.db.sql(ast_query)

	data = list(equipment_data) + list(asset_data)
        return data
	
