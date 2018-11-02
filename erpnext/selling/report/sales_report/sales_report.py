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
	order_by = get_order_by(filters)

	query = frappe.db.sql(""" select* from (select *from 
	(select so.name as so_name , so.customer, soi.qty as qty_approved, soi.rate, soi.amount, soi.item_code, soi.name as soi_name,
 			soi.item_name, so.transaction_date, soi.product_requisition from
                        `tabSales Order` so, 
                        `tabSales Order Item` soi
                        where so.name = soi.parent and so.docstatus = 1 {0} {2}) as so_detail
	inner join
	(select dn.name, dn.contact_no, dn.drivers_name, dn.transportation_charges, dn.vehicle, dni.location, dni.so_detail as dni_name, 
	dni.name as dni_detail, dni.against_sales_invoice
                        from `tabDelivery Note` dn,
                        `tabDelivery Note Item` dni
                        where dn.name = dni.parent and dn.docstatus =1 {1}) as dn_detail
	on so_detail.soi_name = dn_detail.dni_name) as dt
	inner join
	(select si.name, sii.dn_detail  from `tabSales Invoice` si, `tabSales Invoice Item` sii 
                        where si.name = sii.parent and si.docstatus =1) as si_detail
	on dt.dni_detail = si_detail.dn_detail""".format(cond, dni_loc, order_by), as_dict = True, debug = True)
	for d in query:
		#customer detail
		cust = get_customer(filter, d.customer)
		#frappe.msgprint("{0}".format(cust.name))
		row = {
			"sales_order": d.so_name, "posting_date": d.transaction_date, "customer": cust.name, "customer_name": cust.customer_name, 
			"customer_type": cust.customer_type, "customer_id": cust.customer_id, "customer_contact": cust.mobile_no, 
			"item_code": d.item_code, "item_name": d.item_name, "qty_approved": d.qty_approved, "rate": d.rate, 
			"amount": d.amount, "receipt_no": d.name, "vehicle_no": d.vehicle, "drivers_name": d.drivers_name, 
			"drivers_contact": d.contact_no, "total_transportation_charges": d.transportation_charges
			}
		

		if filters.item_group == 'Timber Products':
			tim = get_timber_detail(filters, d.item_code) 
			#frappe.msgprint("{0}".format(tim.spc))
			row["timber_class"] = tim.timber_class
			row["timber_species"] = tim.spc
			row["timber_type"] = tim.timber_type

		if d.product_requisition and filters.item_group == 'Mineral Products':
			pr = get_prod_req(filters, d.product_requisition)
			#frappe.msgprint("{0}".format(d.product_requisition))
			frappe.msgprint("{0}, {1}".format(pr.applicant_name, pr.end_date))
			row["qty_required"] = pr.qty_required,
			row["balance_qty"] = flt(d.qty_approved) - flt(pr.qty_required),
			row["dest_dzongkha"] = pr.destination_dzongkha,
			row["plot"] = pr.tharm,
			row["construction_type"] = pr.construction_type,
			row["cons_start_date"] = pr.start_date,
			row["cons_end_date"] = pr.end_date,
			row["location"] = pr.location,
			row["current_address"] = pr.current_resident,
			row["current_dzo"] = pr.current_dzongkha,
			row["no_of_story"] = pr.no_of_story,
			row["applicant_name"] = pr.applicant_name,

		data.append(row)
	return data

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
                        select name, customer_type, mobile_no, customer_name, customer_id from `tabCustomer` where customer_name = '{0}'
			""".format(cond), as_dict =1)[0]

def get_group_by(filters):
	if filters.show_aggregate:
		group_by = " group by so.branch, pri.item_code"
	else:
		group_by = ""
	return group_by

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
	'''item_cond = ' and 1 = 1'
	if filters.item_group:
		 += " and pe.item_group = '{0}'".format(filters.item_group)

	if filters.item_sub_group:
		condition += " and pe.item_sub_group = '{0}'".format(filters.item_sub_group)

	if filters.item:
		condition += " and pe.item_code = '{0}'".format(filters.item)

	if filters.timber_species:
		condition += " and pe.timber_species = '{0}'".format(filters.timber_species)

	if filters.timber_class:
		condition += " and pe.timber_class = '{0}'".format(filters.timber_class)

	if filters.warehouse:
		condition += " and pe.warehouse = '{0}'".format(filters.warehouse)'''
	return condition




def get_columns(filters):
	columns = [
		{
		  "fieldname": "sales_order",
		  "label": "Sales Order",
		  "fieldtype": "Link",
		  "options": "Sales Order",
		  "width": 150
		},
		{
                  "fieldname": "posting_date",
                  "label": "SO Date",
                  "fieldtype": "Date",
                  "width": 100
                },
		{
		  "fieldname": "customer",
		  "label": "Customer",
		  "fieldtype": "Link",
          	"options": "Customer",
		  "width": 100
		},
		{
		  "fieldname": "customer_name",
		  "label": "Customer Name",
		  "fieldtype": "Data",
		  "width": 100
		},
		{
		  "fieldname": "customer_type",
		  "label": "Customer Type",
		  "fieldtype": "Data",
		  "width": 100
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
		  "width": 150
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
		  "width": 100
		},
		
		{
		  "fieldname": "qty_approved",
		  "label": "Qty Approved",
		  "fieldtype": "Data",
		  "width": 90
		},
		
		{
		  "fieldname": "rate",
		  "label": "Rate",
		  "fieldtype": "Data",
		  "width": 150
		},
		{
		  "fieldname": "amount",
		  "label": "Amount",
		  "fieldtype": "Currency",
		  "width": 150
		},
		{
		  "fieldname": "receipt_no",
		  "label": "Money Receipt No",
		  "fieldtype": "Link",
		  "options": "Sales Invoice",
		  "width": 100
		},
		
		{
		  "fieldname": "vehicle_no",
		  "label": "Vehicle No",
		  "fieldtype": "Data",
		  "width": 100
		},
		{
		  "fieldname": "drivers_name",
		  "label": "Drivers Name",
		  "fieldtype": "Data",
		  "width": 150
		},
		{
		  "fieldname": "drivers_contact",
		  "label": "Drivers Contact",
		  "fieldtype": "Data",
		  "width": 150
		},	
		{
		  "fieldname": "total_transportation_charges",
		  "label": "Total Transportation Charges",
		  "fieldtype": "Data",
		  "width": 150
		}
	]

    	if filters.item_group == "Timber Products":
		columns.insert(9, {
			"fieldname": "timber_class",
			"label": "Class",
			"fieldtype": "Link",
			"options": "Timber Class",
			"width": 100
		})
		columns.insert(10, {
			"fieldname": "timber_species",
			"label": "Species",
			"fieldtype": "Link",
			"options": "Timber Species",
			"width": 100
		})
		columns.insert(11, {
			"fieldname": "timber_type",
			"label": "Type",
			"fieldtype": "Data",
			"width": 100
		})

    	if filters.item_group == "Mineral Products":
        	columns.insert(7, {
		  "fieldname": "qty_required",
		  "label": "Qty Required",
		  "fieldtype": "Data",
		  "width": 100
		})
        	columns.insert(9,{
		  "fieldname": "balance_qty",
		  "label": "Balance Qty",
		  "fieldtype": "Data",
		  "width": 90
		})
        	columns.insert(10,{
		  "fieldname": "dest_dzongkha",
		  "label": "Destination Dzongkha",
		  "fieldtype": "Data",
		  "width": 100
		})
		columns.insert(11, {
		  "fieldname": "plot",
		  "label": "Plot/Tharm No",
		  "fieldtype": "Data",
		  "width": 100
		})
		columns.insert(12, {
		  "fieldname": "construction_type",
		  "label": "Construction Type",
		  "fieldtype": "Data",
		  "width": 150
		})
		columns.insert(13, {
		  "fieldname": "cons_start_date",
		  "label": "Construction Start Date",
		  "fieldtype": "Date",
		  "width": 150
		})
		columns.insert(14, {
		  "fieldname": "cons_end_date",
		  "label": "Construction End Date",
		  "fieldtype": "Date",
		  "width": 200
		})
		columns.insert(15, {
		  "fieldname": "location",
		  "label": "Location",
		  "fieldtype": "Data",
		  "width": 100
		})
        	columns.insert(16, {	
		  "fieldname": "current_address",
		  "label": "Current Residential Address",
		  "fieldtype": "Data",
		  "width": 150
		})
		columns.insert(17, {
		  "fieldname": "current_dzo",
		  "label": "Current Residential Dzongkha",
		  "fieldtype": "Data",
		  "width": 150
		})
		columns.insert(18, {
		  "fieldname": "no_of_story",
		  "label": "No Of Story",
		  "fieldtype": "Data",
		  "width": 150
		})
	return columns
