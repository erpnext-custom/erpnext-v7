# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from erpnext.accounts.utils import get_child_cost_centers
from frappe.utils import flt
import frappe

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters) 
	return data, columns



def get_data(filters):
	data = []
        #conditions = get_conditions(filters)
        #group_by = get_group_by(filters)
        #order_by = get_order_by(filters)
	query = frappe.db.sql("""
			select so.name, so.customer, soi.qty, soi.rate, soi.amount, 
			soi.item_code, soi.item_name, so.transaction_date, 
			soi.product_requisition
			from
			`tabSales Order` so, 
			`tabSales Order Item` soi 
			where so.name = soi.parent  and  so.docstatus = 1
		""", as_dict = 1);
	for d in query:
		frappe.msgprint(" name : {0}".format(d.product_requisition))
		#Customer Details
		cust = frappe.db.sql("""
			select customer_id, customer_type, mobile_no from `tabCustomer` where name = '{0}'""".format(d.customer), as_dict =1)[0]
		frappe.msgprint("{0}".format(cust.customer_type))
		#Product Requisition Details
		prd = frappe.db.sql("""
				select pr.applicant_contact, pr.applicant_name, pr.construction_type, pr.current_dzongkha, pr.current_resident, 
				pr.destination_dzongkha, pr.end_date, pr.is_new_customer, pr.location, pr.no_of_story, pr.others, ifnull(pri.qty,0),
				pr.remarks, pr.start_date, pr.tharm from `tabProduct Requisition` pr, `tabProduct Requisition Item` pri  
				where pr.name = pri.parent and 
				pr.name = '{0}'""".format(d.product_requisition), as_dict =1)
		if not prd:
			prd.applicant_contact = prd.applicant_name = prd.construction_type = prd.current_dzongkha = prd.current_resident = \
                        prd.destination_dzongkha = prd.end_date =  prd.is_new_customer = prd.location = prd.no_of_story = prd.others = prd.qty = \
                        prd.remarks =  prd.start_date =  prd.tharm = 0.0

		#Delivery Details
		dnd = frappe.db.sql("""
			select dn.contact_no,dn.drivers_name, dn.transportation_charges, dn.vehicle 
			from `tabDelivery Note` dn, `tabDelivery Note Item` dni
			where dn.name = dni.parent and dni.against_sales_order = '{0}'""".format(d.name), as_dict =1)

		#Sales Invoice Details
		sid = frappe.db.sql("""
			select si.name from `tabSales Invoice` si, `tabSales Invoice Item` sii 
			where si.name = sii.parent and sii.sales_order = '{0}'""".format(d.name), as_dict =1)
		frappe.msgprint("{0}".format(prd.qty))
		data.append((d.name, d.customer, d.customer, cust.customer_type, cust.customer_id, cust.mobile_no, d.item_name, prd.qty, d.qty, 
		'flt(prd.qty - d.qty)', d.rate, d.amount, 'sid.name', 'prd.destination_dzongkha', 'prd.tharm', 'prd.construction_type', 'prd.start_date, prd.end_date', d.transaction_date, 'prd.location', 'dnd.vehicle', 'capavity', 'total', 'dnd.drivers_name', 'dnd.contact_no', 'prd.current_resident', 'prd.current_dzongkha', 'prd.no_of_story', 'dnd.transportation_charges', 'total_tc', 'total_tc_amount'))
		return tuple(data)
	 
'''def get_group_by(filters):
        if filters.show_aggregate:
                group_by = " group by branch, location, item_sub_group"
        else:
                group_by = ""

        return group_by

def get_order_by(filters):
        return " order by region, location, item_group, item_sub_group"

def get_conditions(filters):
        if not filters.cost_center:
                return " and pe.docstatus = 10"

        all_ccs = get_child_cost_centers(filters.cost_center)
        if not all_ccs:
                return " and pe.docstatus = 10"

        all_branch = [str("DUMMY")]
        for a in all_ccs:
                branch = frappe.db.sql("select name from tabBranch where cost_center = %s", a, as_dict=1)
                if branch:
                        all_branch.append(str(branch[0].name))

        condition = " and pe.branch in {0} ".format(tuple(all_branch))

        if filters.timber_type != "All":
                condition += " and pe.timber_type = '{0}'".format(filters.timber_type)

        if filters.location:
                condition += " and pe.location = '{0}'".format(filters.location)	


        if filters.item_group:
                condition += " and pe.item_group = '{0}'".format(filters.item_group)

        if filters.item_sub_group:
                condition += " and pe.item_sub_group = '{0}'".format(filters.item_sub_group)

        if filters.item:
                condition += " and pe.item_code = '{0}'".format(filters.item)

        if filters.from_date and filters.to_date:
                condition += " and pe.posting_date between '{0}' and '{1}'".format(filters.from_date, filters.to_date)

        if filters.timber_species:
                condition += " and pe.timber_species = '{0}'".format(filters.timber_species)

        if filters.timber_class:
                condition += " and pe.timber_class = '{0}'".format(filters.timber_class)

        if filters.warehouse:
                condition += " and pe.warehouse = '{0}'".format(filters.warehouse)

        return condition'''

def get_columns(filters):
	columns = [
		{ "fieldname": "serial_no", "label": "Sales Order", "fieldtype": "Link", "options": "Sales Order","width": 120},
		{ "fieldname": "customer", "label": "Customer", "fieldtype": "Link", "options": "Customer", "width": 120},
		{ "fieldname": "customer_name", "label": "Customer Name", "fieldtype": "data", "width": 120},
		{ "fieldname": "customer_type",	"label": "Customer Type", "fieldtype": "data","width": 100},
		{ "fieldname": "customer_id","label": "Customer ID/Word Order No.", "fieldtype": "data", "width": 100},
		{ "fieldname": "customer_contact", "label": "Customer Contact No.", "fieldtype": "data", "width": 100},
		{ "fieldname": "material",  "label": "Material", "fieldtype": "data", "width": 100},
		{ "fieldname": "quantity_req", "label": "Quantity Required", "fieldtype": "Float", "width": 100},
		{ "fieldname": "quantity_appr", "label": "Quantity Approved","fieldtype": "Float", "width": 100},
		{ "fieldname": "balance_qty", "label": "Balance Quantity", "fieldtype": "Float", "width": 100},
		{ "fieldname": "rate", "label": "Rate", "fieldtype": "Float", "width": 100},
		{ "fieldname": "amount",  "label": "Amount", "fieldtype": "Float","width": 100},
		{ "fieldname": "invoice_no", "label": "Money Receipt No","fieldtype": "data","width": 100},
		{ "fieldname": "destinaiton_dzo", "label": "Destination Dzongkha","fieldtype": "data","width": 100},
		{ "fieldname": "plot_thram", "label": "Plot/Tharm No.","fieldtype": "data","width": 100},
		{ "fieldname": "construction_type",  "label": "Construction Type", "fieldtype": "data",  "width": 100},
		{ "fieldname": "construction_start_date", "label": "Construction Start Date","fieldtype": "date", "width": 100},
		{ "fieldname": "construction_end_date", "label": "Construction End Date", "fieldtype": "date", "width": 100},
		{ "fieldname": "posting_date",  "label": "Current Date", "fieldtype": "date","width": 100},
		{ "fieldname": "location", "label": "Location", "fieldtype": "data","width": 100},
		{ "fieldname": "vehicle_no", "label": "Vehicle No.", "fieldtype": "data", "width": 100},
		{ "fieldname": "vehicle_capacity", "label": "Vehicle Capacity","fieldtype": "data",  "width": 100},
		{ "fieldname": "v_total",  "label": "Total", "fieldtype": "Float",  "width": 100},
		{ "fieldname": "drivers_name", "label": "Drivers Name", "fieldtype": "data", "width": 100},
		{ "fieldname": "drivers_contact", "label": "Drivers Contact", "fieldtype": "data", "width": 100},
		{ "fieldname": "current_residential_address", "label": "Current Residential Address", "fieldtype": "data", "width": 100},
		{ "fieldname": "current_residential_dzo", "label": "Current Residential Dzongkhag", "fieldtype": "data","width": 100},
		{ "fieldname": "no_of_story",  "label": "No Of Story", "fieldtype": "data", "width": 100 },
		{ "fieldname": "transportation_charges", "label": "Transportation Charges", "fieldtype": "Currency", "width": 100},
		{ "fieldname": "total_transportation_cost", "label": "Total Transportation Cost", "fieldtype": "Currenncy","width": 100},
		{ "fieldname": "total_amount", "label": "Total Amount", "fieldtype": "Currency", "width": 100}
	]

	if filters.item_group == "Timber Products":
		columns.insert(4, {
			"fieldname": "timber_class",
			"label": "Class",
			"fieldtype": "Link",
			"options": "Timber Class",
			"width": 100
		})
		columns.insert(5, {
			"fieldname": "timber_species",
			"label": "Species",
			"fieldtype": "Link",
			"options": "Timber Species",
			"width": 100
		})
		columns.insert(6, {
			"fieldname": "timber_type",
			"label": "Type",
			"fieldtype": "Data",
			"width": 100
		})
	
	return columns

