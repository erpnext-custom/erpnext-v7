# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate, formatdate, cstr, rounded

def execute(filters=None):
	validate_filters(filters)
        data = get_data(filters)
        columns = get_columns()
        return columns, data

def validate_filters(filters):

        if not filters.fiscal_year:
                frappe.throw(_("Fiscal Year {0} is required").format(filters.fiscal_year))

        fiscal_year = frappe.db.get_value("Fiscal Year", filters.fiscal_year, ["year_start_date", "year_end_date"], as_dict=True)
        if not fiscal_year:
                frappe.throw(_("Fiscal Year {0} does not exist").format(filters.fiscal_year))
        else:
                filters.year_start_date = getdate(fiscal_year.year_start_date)
                filters.year_end_date = getdate(fiscal_year.year_end_date)

        if not filters.from_date:
                filters.from_date = filters.year_start_date

        if not filters.to_date:
                filters.to_date = filters.year_end_date

        filters.from_date = getdate(filters.from_date)
        filters.to_date = getdate(filters.to_date)

        if filters.from_date > filters.to_date:
                frappe.throw(_("From Date cannot be greater than To Date"))

        if (filters.from_date < filters.year_start_date) or (filters.from_date > filters.year_end_date):
                frappe.msgprint(_("From Date should be within the Fiscal Year. Assuming From Date = {0}")\
                        .format(formatdate(filters.year_start_date)))

                filters.from_date = filters.year_start_date

        if (filters.to_date < filters.year_start_date) or (filters.to_date > filters.year_end_date):
                frappe.msgprint(_("To Date should be within the Fiscal Year. Assuming To Date = {0}")\
                        .format(formatdate(filters.year_end_date)))
                filters.to_date = filters.year_end_date


def get_data(filters):

	query = "select status, disposal_date, residual_value, expected_value_after_useful_life, asset_sub_category, asset_status, income_tax_opening_depreciation_amount as iopening, opening_accumulated_depreciation, asset_quantity_, name, asset_name, asset_category, equipment_number, serial_number, old_asset_code, presystem_issue_date,issued_to, (select employee_name from tabEmployee as emp where emp.name = ass.issued_to) as employee_name, (select designation from tabEmployee as emp where emp.name = ass.issued_to) as designation, cost_center, purchase_date, gross_purchase_amount, value_after_depreciation, (select gl.accumulated_depreciation_amount from `tabDepreciation Schedule` as gl where gl.parent = ass.name and gl.schedule_date < \'" + str(filters.from_date) + "\' and gl.docstatus = 1 and gl.journal_entry is not null order by gl.schedule_date desc limit 1) as opening_amount, (select gl.accumulated_depreciation_amount from `tabDepreciation Schedule` as gl where gl.parent = ass.name and gl.schedule_date <= \'" + str(filters.to_date) + "\' and gl.docstatus = 1 and gl.journal_entry is not null order by gl.schedule_date desc limit 1) as depreciation_amount, (select sum(ds.depreciation_income_tax) from `tabDepreciation Schedule` as ds where ds.parent = ass.name and ds.schedule_date between \'" + str(filters.from_date) + "\' and \'" + str(filters.to_date) + "\' and ds.docstatus = 1) as depreciation_income_tax, (select sum(ds.depreciation_income_tax) from `tabDepreciation Schedule` as ds where ds.parent = ass.name and ds.schedule_date < \'" + str(filters.from_date) + "\' and ds.docstatus = 1) as opening_income from tabAsset as ass where ass.docstatus = 1"
        if filters.cost_center:
                query+=" and ass.cost_center = \'" + filters.cost_center + "\'"

        if filters.asset_category:
                query+=" and ass.asset_category = \'" + filters.asset_category + "\'"

        if filters.to_date:
                query += " and ass.purchase_date <= '{0}'".format(filters.to_date)
	asset_data = frappe.db.sql(query, as_dict=True)

        data = []
        if asset_data:
                total_gross = 0.00
                total_actual_dep = 0.00
                total_net = 0.00
                total_opening = 0.00
                total_net_income = 0.00
                total_income = 0.00

                for a in asset_data:
                        """if flt(a.depreciation_amount) >= flt(a.gross_purchase_amount):
                                actual_dep =  flt(a.depreciation_amount) - flt(a.gross_purchase_amount) 
                        else:
                                actual_dep =  flt(a.depreciation_amount)

                        if flt(a.opening_amount) >= flt(a.gross_purchase_amount):
                                opening = flt(a.opening_amount) - flt(a.gross_purchase_amount) + flt(a.opening_accumulated_depreciation)
                        else:
                                opening = flt(a.opening_amount) + flt(a.opening_accumulated_depreciation)
                        """
                        if flt(a.opening_accumulated_depreciation) + flt(a.expected_value_after_useful_life) == flt(a.gross_purchase_amount):
                                actual_dep = 0
                        else:
                                actual_dep =  flt(a.depreciation_amount) - flt(a.opening_amount)
                                if not a.opening_amount:
                                        actual_dep =  flt(a.depreciation_amount) - flt(a.opening_amount) - flt(a.opening_accumulated_depreciation)
                                if not frappe.db.sql("select 1 from `tabDepreciation Schedule` where parent = %s limit 1", a.name):
                                        actual_dep = 0
			if not a.opening_amount:
                                opening = flt(a.opening_accumulated_depreciation)
                        else:
                                opening = flt(a.opening_amount)
                        net_useful_life = flt(a.gross_purchase_amount) - flt(actual_dep) - flt(opening)

                        net_income_tax = flt(a.gross_purchase_amount) - flt(a.iopening) - flt(a.depreciation_income_tax) - flt(a.opening_income)

                        total_gross += flt(a.gross_purchase_amount)
                        total_net += flt(net_useful_life, 3)
                        total_actual_dep += flt(actual_dep, 3)
                        total_income += flt(a.depreciation_income_tax, 3)
                        total_net_income += flt(net_income_tax, 3)
                        total_opening += flt(opening, 3)
			
			row = {
                                "asset_code": a.name,
                                "asset_name": a.asset_name,
                                "serial_number": a.serial_number,
                                "asset_category": a.asset_category,
                                "asset_sub_category": a.asset_sub_category,
                                "issued_to": a.issued_to,
                                "employee_name": a.employee_name,
                                "designation": a.designation,
                                "cost_center": a.cost_center,
                                "date_of_issue": a.purchase_date,
                                "qty": a.asset_quantity_,
                                "amount": a.gross_purchase_amount,
                                "actual_depreciation": flt(actual_dep, 3),
                                "opening": flt(opening, 3),
                                "dep_income_tax": a.depreciation_income_tax,
                                "iopening": flt(a.iopening) + flt(a.opening_income),
                                "net_useful_life": net_useful_life,
                                "net_income_tax": net_income_tax,
                                "old_asset_code": a.old_asset_code,
                                "presystem_issue_date": a.presystem_issue_date,
                                "equipment_number": a.equipment_number,
                                "asset_status": a.asset_status,
                                "residual_value": a.residual_value,
                                "status": a.status,
				"disposal_date": a.disposal_date
                        }
                        data.append(row)
                row = {"amount": flt(total_gross, 3), "actual_depreciation": flt(total_actual_dep, 3), "net_useful_life": flt(total_net, 3), "opening": total_opening, "net_income_tax": total_net_income, "dep_income_tax": total_income}
                data.append(row)

        return data

def get_columns():
        return [
                {
                        "fieldname": "asset_code",
                        "label": _("Asset Code"),
                        "fieldtype": "Link",
                        "options": "Asset",
                        "width": 100
                },
                {
                        "fieldname": "asset_name",
                        "label": _("Asset Name"),
                        "fieldtype": "Data",
                        "width": 200
                },
                {
                        "fieldname": "serial_number",
                        "label": _("Serial Number"),
                        "fieldtype": "Data",
                        "width": 200
                },
                {
                        "fieldname": "asset_category",
                        "label": _("Asset Category"),
                        "fieldtype": "Link",
                        "options":"Asset Category",
                        "width": 200
                },
                {
                        "fieldname": "asset_sub_category",
                        "label": _("Sub Category"),
                        "fieldtype": "Link",
                        "options":"Item Sub Group",
                        "width": 200
                },
		{
                        "fieldname": "issued_to",
                        "label": _("Issued To"),
                        "fieldtype": "Data",
                        "width": 150
                },
                 {
                        "fieldname": "employee_name",
                        "label": _("Employee Name"),
                        "fieldtype": "Data",
                        "width": 150
                },
                 {
                        "fieldname": "designation",
                        "label": _("Designation"),
                        "fieldtype": "Data",
                        "width": 150
                },
                {
                        "fieldname": "cost_center",
                        "label": _("Cost Center"),
                        "fieldtype": "Link",
                        "options": "Cost Center",
                        "width": 130
                },
                 {
                        "fieldname": "qty",
                        "label": _("Quantity"),
                        "fieldtype": "Data",
                        "width": 100
                },
		{
                        "fieldname": "amount",
                        "label": _("Gross Amount"),
                        "fieldtype": "Currency",
                        "width": 120
                },
                {
                        "fieldname": "actual_depreciation",
                        "label": _("Depreciation Amount"),
                        "fieldtype": "Currency",
                        "width": 120
                },
                {
                        "fieldname": "opening",
                        "label": _("Opening Depreciation"),
                        "fieldtype": "Currency",
                        "width": 120
                },
                {
                        "fieldname": "net_useful_life",
                        "label": _("Net Book Value"),
                        "fieldtype": "Currency",
                        "width": 120
                },
                {
                        "fieldname": "iopening",
                        "label": _("Income Open. Dep."),
                        "fieldtype": "Currency",
                        "width": 120
                },
		{
                        "fieldname": "net_income_tax",
                        "label": _("Net Income Tax"),
                        "fieldtype": "Currency",
                        "width": 120
                },
                {
                        "fieldname": "old_asset_code",
                        "label": _("Old Asset Code"),
                        "fieldtype": "Data",
                        "width": 120
                },
                {
                        "fieldname": "presystem_issue_date",
                        "label": _("Original Issue Date"),
                        "fieldtype": "Date",
                        "width": 120
                },
                {
                        "fieldname": "equipment_number",
                        "label": _("Equipment Number"),
                        "fieldtype": "Link",
                        "options": "Equipment",
                        "width": 120
                },
                {
                        "fieldname": "asset_status",
                        "label": _("Asset Status"),
                        "fieldtype": "data",
                        "width": 120
                },
		{
                        "fieldname": "residual_value",
                        "label": _("Residual Value"),
                        "fieldtype": "data",
                        "width": 120
                },
                 {
                        "fieldname": "status",
                        "label": _("Status"),
                        "fieldtype": "data",
                        "width": 120
                },
		{	
			"fieldname": "disposal_date",
			"label": _("Scrapped Date"),
			"fieldtype": "date",
			"width" : 90
		},

        ]

