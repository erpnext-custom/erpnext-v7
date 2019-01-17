# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns = get_columns(filters)
	query = get_query(filters)
	data = get_data(query, filters)
	cond = get_conditions(filters)
	return columns, data
def get_data(query, filters):
	data = []
	for d in frappe.db.sql(query, as_dict =1):
		row = [d.pr_name, d.pr_branch, d.pr_creation, d.pr_posting, d.pr_docstatus, d.pr_owner, d.pr_is_allotment, d.pr_cons_type, \
			d.so_name, d.so_creation, d.so_posting_date, d.so_status, d.so_owner, d.dn_name, d.dn_creation, d.dn_posting, d.dn_owner,\
			d.dn_status, d.si_name, d.si_creation, d.si_posting, d.si_owner, d.si_status, d.pe_name, d.pe_creation, d.pe_posting,\
			d.pe_owner,d.pe_status]  
		data.append(row)
	return data

def get_conditions(filters):
        conditions = ""
        if filters.get("month"):
                month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
                        "Dec"].index(filters["month"]) + 1
                filters["month"] = month
                conditions += " and month(pr.creation) = '{0}'".format(filters["month"])
        '''if filters.get("fiscal_year"): conditions += " and year(mr.creation) = {0}".format(filters.get("fiscal_year"))
        if filters.get("cost_center"): conditions += " and mr.branch =  '{0}'".format(filters.get("cost_center"))
        conditions += " and mr.workflow_state  != 'Cancelled'"
        conditions += " and case when rq.status IS NOT NULL then rq.status != 'Cancelled' else 1 =1 end"
        conditions += " and case when po.docstatus IS NOT NULL then po.docstatus != 2 else 1 =1 end"
        conditions += " and case when pr.status IS NOT NULL then pr.status != 'Cancelled' else 1 =1 end"
        conditions += " and case when pi.docstatus IS NOT NULL then pi.docstatus != 2 else 1 =1 end"
        #and ifnull(1 =1, pi.docstatus != 2)"'''
        return conditions


def get_query(filters):
	#conditions = get_conditions(filters)
	query = """
	select *from 
	(select 
		pr.name as pr_name, pr.branch as pr_branch, pr.creation as pr_creation, pr.posting_date as pr_posting, 
		pr.docstatus as pr_docstatus, pr.owner as pr_owner, pr.is_allotment as pr_is_allotment, pr.construction_type  as pr_cons_type
		from `tabProduct Requisition` pr, `tabProduct Requisition Item` pri  where pr.name = pri.parent) as pr_detail
    	left join
	(select 
		so.name as so_name , so.creation as so_creation, so.transaction_date as so_posting_date, so.docstatus so_status, so.owner as so_owner,		      so.po_no as so_po, soi.name as soi_name
		from `tabSales Order` so,  `tabSales Order Item` soi where so.name = soi.parent) as so_detail
	on pr_detail.pr_name = so_detail.so_po
    	left join
	(select 
		dn.name as dn_name, dn.creation as dn_creation, dn.posting_date as dn_posting, dn.owner as dn_owner, dn.docstatus as dn_status,
		dni.name as dni_detail, dni.so_detail as dni_name
    		from `tabDelivery Note` dn, `tabDelivery Note Item` dni where dn.name = dni.parent) as dn_detail
	on so_detail.soi_name = dn_detail.dni_name
	left join
	(select 
		si.name as si_name, si.creation as si_creation, si.posting_date as si_posting, si.docstatus as si_status, si.owner as si_owner, sii.dn_detail
    		from `tabSales Invoice` si, `tabSales Invoice Item` sii where si.name = sii.parent) as si_detail
	on dn_detail.dni_detail = si_detail.dn_detail
    	left join
   	(select 
		pe.name as pe_name, pe.creation as pe_creation, pe.posting_date as pe_posting, pe.docstatus as pe_status, pe.owner as pe_owner, per.reference_name 
    		from `tabPayment Entry` pe, `tabPayment Entry Reference` per where pe.name = per.parent) as pe_detail
    	on si_detail.si_name = pe_detail.reference_name"""
	return query


def get_status(pr_status, so_status, dn_status, si_status, pe_status):
	if pr_status == so_status == dn_status == si_status == pe_status == 0:
		return "Draft"
	if pr_status == so_status == dn_status == si_status == pe_status == 2:
		return "Cancelled"
	if pr_status == so_status == dn_status == si_status == pe_status == 1:
		return "Submitted"
	
def get_columns(filters):
        cols = [
                ("PR Name") + ":Link/Product Requisition:120",
		("Branch") + ":Link/Branch:160",
		("PR Create Date") + ":Date:100",
                ("PR Submit Date") + ":Date:110",
                ("PR Status") + ":Data:100",
		("PR Owner") + ":Link/User:140",
		("Is Allotment") + ":Data:100",
                ("Construction Type") + ":Data:120",

                ("SO Name") + ":Link/Sales Order:100",
                ("SO Creation Date") + ":Data:100",
		("SO Submit Date") + ":Date:100",
		("SO Status") + ":Data:100",
		("SO Owner") + ":Data:100",

                ("DN Name") + ":Link/Delivery Note:100",
		("DN Creation Date") + ":Date:100",
		("DN Submit Date") + ":Date:100",
                ("DN Owner") + ":Data:100",
		("DN Status") + ":Data:140",
		       
		("SI Name") + ":Link/Sales Invoice:140",
                ("SI Creation Date") + ":Date:140",
                ("SI Submit Date") + ":Date:100",
                ("SI Owner") + ":Data:100",
                ("SI Status") + ":Data:100",

		("PE Name") + ":Link/Payment Entry:140",
		("PE Creation Date") + ":Date:100",
		("PE Submit Date") + ":Date:100",
		("PE Owner") + ":Data:100",
		("PE Status") + ":Data:100",

        ]
        return cols

