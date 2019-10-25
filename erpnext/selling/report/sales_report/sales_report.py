# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from erpnext.accounts.utils import get_child_cost_centers
from frappe.utils import flt
import frappe
from frappe import _

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_data(filters):
	data = []
	cond = get_conditions(filters)
	qty, group, amount = get_group_by(filters)
	#frappe.msgprint("{0} and {1}".format(qty, group))
	order_by = get_order_by(filters)
	query = frappe.db.sql("""select *from 
	(select so.name as so_name , so.customer, so.customer_name, so.branch, soi.qty as qty_approved, soi.delivered_qty, soi.rate, soi.item_code, 
	soi.name as soi_name, soi.item_name, soi.item_group,
	so.transaction_date from
        `tabSales Order` so,  `tabSales Order Item` soi where so.name = soi.parent and so.docstatus = 1 {0}) as so_detail
	inner join
	(select dn.name, dni.so_detail as dni_name, 
	dni.name as dni_detail, dni.against_sales_invoice from `tabDelivery Note` dn, `tabDelivery Note Item` dni
        where dn.name = dni.parent and dn.docstatus =1) as dn_detail
	on so_detail.soi_name = dn_detail.dni_name
	inner join
	(select si.name, sii.dn_detail, (select item_sub_group from tabItem where item_code = sii.item_code group by item_sub_group) as item_sub, sii.sales_order, sii.delivery_note, {1} as sii_qty, sii.rate as sii_rate, {3} as sii_amount  from `tabSales Invoice` si, `tabSales Invoice Item` sii where si.name = sii.parent and si.docstatus =1 {2}) 
	as si_detail
	on dn_detail.dni_detail = si_detail.dn_detail""".format(cond, qty, group, amount), as_dict = True)
	agg_qty = agg_amount = qty = rate = amount =  qty_required  = qty_approved = balance_qty = delivered_qty = 0.0
	row = {}
	for d in query:
		#customer detail
		cust = get_customer(filter, d.customer)
		row = {
			"sales_order": d.so_name, "posting_date": d.transaction_date, "customer": cust.name, "customer_name": cust.customer_name, 
			"customer_type": cust.customer_type, "customer_id": cust.customer_id, "customer_contact": cust.mobile_no, 
			"item_code": d.item_code, "item_name": d.item_name, "qty_approved": flt(d.qty_approved),
			"qty": flt(d.sii_qty),  "rate": flt(d.sii_rate),  "amount": flt(d.sii_amount), "receipt_no": d.name, 
			"delivered_qty": flt(d.sii_qty), "agg_qty": flt(d.sii_qty),
			"agg_amount": flt(d.sii_amount), "agg_branch": d.branch, "item_sub_group": d.item_sub
			}
		data.append(row)
		agg_amount += flt(d.sii_amount)
		qty +=  flt(d.sii_qty)  
		rate +=  flt(d.sii_rate)
		amount += flt(d.sii_amount)
		qty_approved += flt(d.qty_approved)
		delivered_qty =+ flt(d.sii_qty)
		balance_qty += flt(d.qty_approved) - flt(d.sii_qty)
		row = { "agg_qty": agg_qty, "agg_amount": agg_amount, "qty": qty, "rate": rate, "amount": amount, 
		"qty_approved": qty_approved, "qty_required": qty_required, "qty_approved": qty_approved, "delivered_qty": delivered_qty,
                "balance_qty":  balance_qty, "agg_branch": "'Total'", "sales_order": "'Total'"}
	data.append(row)
	return tuple(data)

def get_customer(filters, cond):
	return frappe.db.sql("""
                        select name, customer_type, mobile_no, customer_name, customer_id from `tabCustomer` where name = "{0}"
			""".format(cond), as_dict =1)[0]

def get_group_by(filters):
	group_by = " "
	qty = 'sii.qty'
	amount = 'sii.amount'
	if filters.group_by == 'Sales Order':
		group_by = " group by sii.sales_order"
		qty = " sum(sii.qty)"
		amount = " sum(sii.amount)"
	if filters.aggregate:
		group_by = " group by item_sub, si.branch"
		qty = " sum(sii.qty)"
		amount = " sum(sii.amount)"
	return qty, group_by, amount

def get_order_by(filters):
	return " order by so.name"

def get_conditions(filters):
	if not filters.cost_center:
		return " and so.docstatus = 10"
	all_ccs = get_child_cost_centers(filters.cost_center)
	if not all_ccs:
		return " and so.docstatus = 10"

	all_branch = [str("DUMMY")]
	for a in all_ccs:
		branch = frappe.db.sql("select name from tabBranch where cost_center = %s", a, as_dict=1)
		if branch:
			all_branch.append(str(branch[0].name))
	condition = " and so.branch in {0} ".format(tuple(all_branch))
	if filters.from_date and filters.to_date:
        	condition += " and so.transaction_date between '{0}' and '{1}'".format(filters.from_date, filters.to_date)

	if filters.warehouse:
                condition += " and soi.warehouse = '{0}'".format(filters.warehouse)

	if filters.item_group:
		 condition += " and soi.item_group = '{0}'".format(filters.item_group)

	if filters.item:
		condition += " and soi.item_code = '{0}'".format(filters.item)

	if filters.item_sub_group:
		condition += " and '{0}' in (select item_sub_group from `tabItem` where name = soi.item_code)".format(filters.item_sub_group)
	
	return condition




def get_columns(filters):
	columns = [
		{
		  "fieldname": "sales_order",
		  "label": "Sales Order",
		  "fieldtype": "Link",
		  "options": "Sales Order",
		  "width": 100
		},
		{
                  "fieldname": "posting_date",
                  "label": "SO Date",
                  "fieldtype": "Date",
                  "width": 90
                },
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
                  "width": 125
                },
		{
		  "fieldname": "customer",
		  "label": "Customer Name",
		  "fieldtype": "Link",
          	  "options": "Customer",
		  "width": 140
		},
		{
		  "fieldname": "customer_type",
		  "label": "Customer Type",
		  "fieldtype": "Data",
		  "width": 140
		},
        	{	
		  "fieldname": "customer_id",
		  "label": "Customer ID/Work Permit",
		  "fieldtype": "Data",
		  "width": 150
		},
		{
		  "fieldname": "customer_contact",
		  "label": "Customer Contact",
		  "fieldtype": "Data",
		  "width": 120
		},	
			
		{
                  "fieldname": "qty",
                  "label": "Invoiced Qty",
                  "fieldtype": "Float",
                  "width": 90
                },

                {
                  "fieldname": "rate",
                  "label": "Rate",
                  "fieldtype": "Float",
                  "width": 70
                },
                {
                  "fieldname": "amount",
                  "label": "Amount",
                  "fieldtype": "Currency",
                  "width": 110
                },
	]

	if filters.group_by == 'Delivery Note':
		columns.insert(11,{
                  "fieldname": "receipt_no",
                  "label": "Sales Invoice No",
                  "fieldtype": "Link",
                  "options": "Sales Invoice",
                  "width": 120
                })

	if filters.aggregate == 1:
		columns = [
		{
                  "fieldname": "agg_branch",
                  "label": "Branch",
                  "fieldtype": "data",
                  "width": 100
                },
		{
                  "fieldname": "item_sub_group",
                  "label": "Item Sub Group",
                  "fieldtype": "data",
                  "width": 100
                },
                {
                  "fieldname": "qty",
                  "label": "Sales Qty",
                  "fieldtype": "Float",
                  "width": 90
                },
                {
                  "fieldname": "agg_amount",
                  "label": "Amount",
                  "fieldtype": "Currency",
                  "width": 100
                }
		]

	return columns
