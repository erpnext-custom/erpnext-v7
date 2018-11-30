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
	if filters.location:
                dni_loc = " and dni.location = '{0}'".format(filters.location)
	else:
		dni_loc = " and 1 =1"

	cond = get_conditions(filters)
	qty, group = get_group_by(filters)
	#frappe.msgprint("so {0}, {1}".format(qty, group))
	order_by = get_order_by(filters)
	query = frappe.db.sql("""select *from 
	(select so.name as so_name , so.customer, so.customer_name, so.branch, soi.qty as qty_approved, soi.delivered_qty, soi.rate, soi.item_code, 
	soi.name as soi_name, soi.item_name, soi.item_group,
	so.transaction_date, soi.product_requisition from
        `tabSales Order` so,  `tabSales Order Item` soi where so.name = soi.parent and so.docstatus = 1 {0}) as so_detail
	inner join
	(select dn.name, dn.contact_no, dn.drivers_name, dn.transportation_charges, dn.vehicle, dni.location, dni.so_detail as dni_name, 
	dni.name as dni_detail, dni.against_sales_invoice from `tabDelivery Note` dn, `tabDelivery Note Item` dni
        where dn.name = dni.parent and dn.docstatus =1) as dn_detail
	on so_detail.soi_name = dn_detail.dni_name
	inner join
	(select si.name, sii.dn_detail, (select item_sub_group from tabItem where item_code = sii.item_code group by item_sub_group) as item_sub, sii.sales_order, sii.delivery_note, {2} as sii_qty, sii.rate as sii_rate, sii.amount as sii_amount  from `tabSales Invoice` si, `tabSales Invoice Item` sii where si.name = sii.parent and si.docstatus =1 {3}) 
	as si_detail
	on dn_detail.dni_detail = si_detail.dn_detail""".format(cond, dni_loc, qty, group), as_dict = True)
	agg_qty = agg_amount = qty = rate = amount =  qty_required  = qty_approved = balance_qty = delivered_qty = transportation_charges = 0.0
	row = {}
	for d in query:
		#customer detail
		cust = get_customer(filter, d.customer)
		row = {
			"sales_order": d.so_name, "posting_date": d.transaction_date, "customer": cust.name, "customer_name": cust.customer_name, 
			"customer_type": cust.customer_type, "customer_id": cust.customer_id, "customer_contact": cust.mobile_no, 
			"item_code": d.item_code, "item_name": d.item_name, "qty_approved": flt(d.qty_approved),
			"qty": flt(d.sii_qty),  "rate": flt(d.sii_rate),  "amount": flt(d.sii_qty) * flt(d.sii_rate), "receipt_no": d.name, 
			"delivered_qty": flt(d.sii_qty), "vehicle_no": d.vehicle, "drivers_name": d.drivers_name, 
			"drivers_contact": d.contact_no, "transportation_charges": d.transportation_charges, "agg_qty": flt(d.sii_qty),
			"agg_amount": flt(d.sii_amount), "agg_branch": d.branch, "agg_location": d.location, "item_sub_group": d.item_sub
			}	

		spec = frappe.db.get_value("Item", d.item_code, "species")
                if filters.item_group == 'Timber Products' and spec != None:
			tim = get_timber_detail(filters, d.item_code) 
			row["timber_class"] = tim.timber_class
			row["timber_species"] = tim.spc
			row["timber_type"] = tim.timber_type

		if d.product_requisition and filters.item_group == 'Mineral Products':
			pr = get_prod_req(filters, d.product_requisition)
			row["applicant_name"] = pr.applicant_name,
			row["qty_required"] = flt(pr.qty_required),
			row["balance_qty"] = flt(d.qty_approved) - flt(d.delivered_qty),
			row["dest_dzongkha"] = pr.destination_dzongkha,
			row["plot"] = pr.tharm,
			row["construction_type"] = pr.construction_type,
			row["cons_start_date"] = pr.start_date,
			row["cons_end_date"] = pr.end_date,
			row["location"] = pr.location,
			row["current_address"] = pr.current_resident,
			row["current_dzo"] = pr.current_dzongkha,
			row["no_of_story"] = pr.no_of_story
			qty_required += flt(pr.qty_required)
		data.append(row)
		agg_qty += flt(d.sii_qty)
		agg_amount += flt(d.sii_amount)
		qty +=  flt(d.sii_qty)  
		rate +=  flt(d.sii_rate)
		amount += flt(d.sii_qty) * flt(d.sii_rate)
		qty_approved += flt(d.qty_approved)
		delivered_qty =+ flt(d.sii_qty)
		balance_qty += flt(d.qty_approved) - flt(d.sii_qty)
		transportation_charges += flt(d.transportation_charges)
		row = { "agg_qty": agg_qty, "agg_amount": agg_amount, "qty": qty, "rate": rate, "amount": amount, 
		"qty_approved": qty_approved, "qty_required": qty_required, "qty_approved": qty_approved, "delivered_qty": delivered_qty,
                "balance_qty":  balance_qty, "transportation_charges": transportation_charges, "agg_branch": "'Total'", "sales_order": "'Total'"}
	data.append(row)
	return tuple(data)

def get_timber_detail(filters, cond):
	return frappe.db.sql(""" select i.item_code, i.item_group, ts.species as spc, ts.timber_type, ts.timber_class
		from `tabItem` i, `tabTimber Species` ts where i.item_group = 'Timber Products' and ts.species = i.species 
		and i.item_code = '{0}'""".format(cond), as_dict =1)[0]

def get_prod_req(filters, cond):
		return frappe.db.sql(""" select pr.applicant_contact, pr.applicant_name, pr.construction_type, pr.current_dzongkha, 
			pr.current_resident, pr.destination_dzongkha, pr.end_date, pr.is_new_customer, pr.location, pr.no_of_story, pr.others, pri.qty 			as qty_required,pr.remarks, pr.start_date, pr.tharm from `tabProduct Requisition` pr, `tabProduct Requisition Item` pri 
		where pr.name = pri.parent and pri.name = '{0}'""".format(cond), as_dict =1)[0]

def get_customer(filters, cond):
	return frappe.db.sql("""
                        select name, customer_type, mobile_no, customer_name, customer_id from `tabCustomer` where name = '{0}'
			""".format(cond), as_dict =1)[0]

def get_group_by(filters):
	group_by = " "
	qty = 'sii.qty'
	if filters.group_by == 'Sales Order':
		group_by = " group by sii.sales_order"
		qty = " sum(sii.qty)"
	if filters.aggrigate:
		group_by = " group by item_sub, si.branch"
		qty = " sum(sii.qty)"
	return qty, group_by

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

	if filters.timber_species:
		condition += """ and '{0}' in (select ts.species from `tabItem` i, `tabTimber Species` ts where ts.species = i.species  
                and i.item_code = soi.item_code)""".format(filters.timber_species)

	if filters.timber_class:
		condition += """ and '{0}' in (select ts.timber_class from `tabItem` i, `tabTimber Species` ts where ts.species = i.species 
                and i.item_code = soi.item_code)""".format(filters.timber_class)
	'''if filters.timber_type == 'All':
		condition += " and 1 = 1"'''
	
	if filters.timber_type != 'All':
		condition += """ and '{0}' in (select ts.timber_type from `tabItem` i, `tabTimber Species` ts where ts.species = i.species 
                and i.item_code = soi.item_code)""".format(filters.timber_type)
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

	if filters.group_by == 'Delivery Note' and filters.item_group == 'Mineral Products':
		 columns.insert(8,{
                  "fieldname": "vehicle_no",
                  "label": "Vehicle No",
                  "fieldtype": "Data",
                  "width": 100
                 })
                 columns.insert(9,{
                  "fieldname": "drivers_name",
                  "label": "Drivers Name",
                  "fieldtype": "Data",
                  "width": 130
                 })
                 columns.insert(10, {
                  "fieldname": "drivers_contact",
                  "label": "Drivers Contact",
                  "fieldtype": "Data",
                  "width": 130
                 })
                 columns.insert(11, {
                  "fieldname": "transportation_charges",
                  "label": "Transportation Charges",
                  "fieldtype": "Currency",
                  "width": 150
                 })

    	if filters.item_group == "Timber Products":
		columns.insert(4, {
			"fieldname": "timber_class",
			"label": "Timber Class",
			"fieldtype": "Link",
			"options": "Timber Class",
			"width": 100
		})
		columns.insert(5, {
			"fieldname": "timber_species",
			"label": "Timber Species",
			"fieldtype": "Link",
			"options": "Timber Species",
			"width": 100
		})
		columns.insert(6, {
			"fieldname": "timber_type",
			"label": "Timber Type",
			"fieldtype": "Data",
			"width": 100
		})

    	if filters.item_group == "Mineral Products":
		columns.insert(8, {
		  "fieldname": "applicant_name",
		  "label": "Applicant Name",
		  "fieldtype": "Data",
		  "width": 130
                })
		columns.insert(9, {
                  "fieldname": "construction_type",
                  "label": "Construction Type",
                  "fieldtype": "Data",
                  "width": 130
                })
                columns.insert(10, {
                  "fieldname": "cons_start_date",
                  "label": "Construction Start Date",
                  "fieldtype": "Date",
                  "width": 150
                })
                columns.insert(11, {
                  "fieldname": "cons_end_date",
                  "label": "Construction End Date",
                  "fieldtype": "Date",
                  "width": 150
                })
		columns.insert(12, {
                  "fieldname": "location",
                  "label": "Location",
                  "fieldtype": "Data",
                  "width": 100
                })
		columns.insert(13, {
                  "fieldname": "plot",
                  "label": "Plot/Tharm No",
                  "fieldtype": "Data",
                  "width": 100
                })
        	columns.insert(14, {
		  "fieldname": "qty_required",
		  "label": "Qty Required",
		  "fieldtype": "Data",
		  "width": 90
		})
		columns.insert(15, {
                  "fieldname": "qty_approved",
                  "label": "Qty Approved",
                  "fieldtype": "Data",
                  "width": 90
                })
		columns.insert(16,{
                  "fieldname": "delivered_qty",
                  "label": "Delivered Qty",
                  "fieldtype": "Data",
                  "width": 90
                })
		columns.insert(17,{
                  "fieldname": "balance_qty",
                  "label": "Balance Qty",
                  "fieldtype": "Data",
                  "width": 90
                })
        	columns.insert(18,{
		  "fieldname": "dest_dzongkha",
		  "label": "Destination Dzongkha",
		  "fieldtype": "Data",
		  "width": 150
		})
        	columns.insert(19, {	
		  "fieldname": "current_address",
		  "label": "Current Residential Address",
		  "fieldtype": "Data",
		  "width": 150
		})
		columns.insert(20, {
		  "fieldname": "current_dzo",
		  "label": "Current Residential Dzongkha",
		  "fieldtype": "Data",
		  "width": 150
		})
		columns.insert(21, {
		  "fieldname": "no_of_story",
		  "label": "No Of Story",
		  "fieldtype": "Data",
		  "width": 100
		})
		
	if filters.aggrigate == 1:
		columns = [
		{
                  "fieldname": "agg_branch",
                  "label": "Branch",
                  "fieldtype": "data",
                  "width": 100
                },
		{
                  "fieldname": "agg_location",
                  "label": "Location",
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
                  "fieldname": "agg_qty",
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
