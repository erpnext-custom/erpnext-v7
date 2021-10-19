# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate, formatdate, cstr

def execute(filters=None):
	validate_filters(filters);
	columns = get_columns();
	queries = construct_query(filters);
	data = get_data(queries, filters);

	return columns, data

def get_data(query, filters=None):
	data = []
	datas = frappe.db.sql(query, (filters.from_date, filters.to_date), as_dict=True);
	for d in datas:
		row = [d.item_code, d.item_name, d.item_group, d.item_sub_group, d.reg_number, d.qty, d.e_name, d.custodian, d.cost_center, d.issued_date, d.amount]
		data.append(row);
	return data

def construct_query(filters=None):
	query = """select id.item_code, id.item_name, (select ig.item_group from `tabItem` ig where ig.name = id.item_code) as item_group, (select isg.item_sub_group from `tabItem` isg where isg.name = id.item_code) as item_sub_group, id.reg_number, id.qty, id.cost_center, (select a.name from tabEmployee a where a.name = id.issued_to) as e_name, (select e.employee_name from tabEmployee as e where e.name = id.issued_to) as custodian, id.issued_date, id.amount 
	from `tabAsset Issue Details` as id where id.docstatus = 1 and id.issued_date between %s and %s
	"""
	
	if filters.from_date and filters.to_date:
		query += " and id.issued_date between '{0}' and '{1}'".format(filters.get('from_date'), filters.get('to_date'))

	if filters.item_code:
		query += " and id.item_code = '{0}'".format(filters.get("item_code"))

	if filters.item_group:
		query += " and exists ( select 1 from `tabItem` where name = id.item_code and item_group = '{0}')".format(filters.get("item_group")) 
	if filters.item_sub_group:
		query += " and exists ( select 1 from `tabItem` where name = id.item_code and item_sub_group = '{0}')".format(filters.get("item_sub_group"))
	
	if filters.cost_center:
		query += " and cost_center = '{0}'".format(filters.get("cost_center"))

	query += " order by id.issued_date asc"
	return query;

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


def get_columns():
	return [
		{
		  "fieldname": "item_code",
		  "label": "Material Code",
		  "fieldtype": "Link",
		  "options": "Item",
		  "width": 100
		},
		{
		  "fieldname": "item_name",
		  "label": "Material Name",
		  "fieldtype": "Data",
		  "width": 150
		},
		{
                  "fieldname": "item_group",
                  "label": "Material Group",
                  "fieldtype": "Link",
                  "options": "Item Group",
                  "width": 170
                },

		{
                  "fieldname": "item_sub_group",
                  "label": "Material Sub Group",
                  "fieldtype": "Link",
                  "options": "Item Sub Group",
                  "width": 170
                },

		{
		  "fieldname": "reg_number",
		  "label": "Registration No",
		  "fieldtype": "Data",
		  "width": 150
		},
		{
		  "fieldname": "qty",
		  "label": "Quantity",
		  "fieldtype": "Data",
		  "width": 100
		},
		{
			"fieldname": "e_name",
			"label": "Employee ID",
			"fieldtype": "Link",
			"options": "Employee",
			"width": 130
		},
		{
		  "fieldname": "issued_to",
		  "label": "Custodian",
		  "fieldtype": "Data",
		  "width": 130
		},
		{
		  "fieldname": "cost_center",
		  "label": "Cost Center",
	      	  "fieldtype": "Link",
	          "options": "Cost Center",
		  "width": 170
		  },
		{
		  "fieldname": "issued_date",
		  "label": "Issued Date",
		  "fieldtype": "Date",
		  "width": 100
		},
		{
		  "fieldname": "amount",
		  "label": "Gross Amount",
		  "fieldtype": "Currency",
		  "width": 200
		}
	]
