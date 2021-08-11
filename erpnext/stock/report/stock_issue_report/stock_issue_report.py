# # Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# # For license information, please see license.txt


from __future__ import unicode_literals
import frappe
from frappe.utils import flt, cint,add_days, cstr, flt, getdate, nowdate, rounded, date_diff

def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data


def get_columns(filters):
    cols = [
        ("Date") + ":date:100",
        ("Material Code") + ":data:110",
        ("Material Name")+":data:120",
        ("Material Group")+":data:120",
        ("Material Sub Group")+":data:150",
        ("UoM") + ":data:50",
        ("Qty")+":data:50",
        ("Valuation Rate")+":data:120",
        ("Amount")+":Currency:110",
    ]
    if filters.purpose == "Material Issue" and not filters.accumulate :
        cols.append(("Cost Center")+":data:170")
    if filters.accumulate == 1:
        cols.remove(("Valuation Rate")+":data:120")

    if filters.purpose == "Material Transfer" and not filters.accumulate:
        cols.append(("Warehouse")+":data:170")
        cols.append(("Stock Entry")+":Link/Stock Entry:170")
    return cols

def get_data(filters):
    cond = ''
    if filters.get("warehouse"):
        cond += " AND sed.s_warehouse = \'" + str(filters.warehouse) + "\'"
    if filters.get("from_date") and filters.get("to_date"):
        cond += " AND se.posting_date BETWEEN \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\'"
    data = []
    
    if filters.purpose == 'Material Transfer':
        if  filters.accumulate:
            data =frappe.db.sql("""SELECT se.posting_date, sed.item_code, sed.item_name, 
                    (select item_group from `tabItem` where item_code = sed.item_code ) as item_group ,
                    (select item_sub_group from `tabItem` where item_code = sed.item_code ) as item_sub_group, sed.uom, sum(sed.qty) as qty, 
                    sum(sed.amount) as amount
                FROM `tabStock Entry` se inner join `tabStock Entry Detail` sed
                on se.name = sed.parent 
                where se.docstatus = 1
                and se.purpose = 'Material Transfer'
                and sed.item_code = '{}' {}""".format(filters.item_code, cond))
        else:
            if filters.get("item_code"):
                cond += " AND sed.item_code = \'" + str(filters.item_code) + "\'"
            data = frappe.db.sql("""
                            SELECT se.posting_date, sed.item_code, sed.item_name, 
                                (select item_group from `tabItem` where item_code = sed.item_code ) as item_group ,
                                (select item_sub_group from `tabItem` where item_code = sed.item_code ) as item_sub_group,
                                sed.uom, sed.qty, 
                                sed.valuation_rate, sed.amount
                            FROM `tabStock Entry` se inner join `tabStock Entry Detail` sed
                            on se.name = sed.parent 
                            where se.docstatus = 1 
                            and se.purpose = 'Material Transfer'
                            {} """.format(cond))
                    
    elif filters.purpose == 'Material Issue':
        if  filters.accumulate:
            data =frappe.db.sql("""SELECT se.posting_date, sed.item_code, sed.item_name, 
                    (select item_group from `tabItem` where item_code = sed.item_code ) as item_group ,
                    (select item_sub_group from `tabItem` where item_code = sed.item_code ) as item_sub_group, sed.uom, sum(sed.qty) as qty, 
                    sum(sed.amount) as amount
                FROM `tabStock Entry` se inner join `tabStock Entry Detail` sed
                on se.name = sed.parent 
                where se.docstatus = 1
                and se.purpose = 'Material Issue'
                and sed.item_code = '{}' {}""".format(filters.item_code, cond))
        else:
            if filters.get("item_code"):
                cond += " AND sed.item_code = \'" + str(filters.item_code) + "\'"
            data = frappe.db.sql("""
                            SELECT se.posting_date, sed.item_code, sed.item_name, 
                                (select item_group from `tabItem` where item_code = sed.item_code ) as item_group ,
                                (select item_sub_group from `tabItem` where item_code = sed.item_code ) as item_sub_group,
                                sed.uom, sed.qty, 
                                sed.valuation_rate, sed.amount
                            FROM `tabStock Entry` se inner join `tabStock Entry Detail` sed
                            on se.name = sed.parent 
                            where se.docstatus = 1 
                            and se.purpose = 'Material Issue'
                            {} """.format(cond))
            
            #  if filters.get("item_code"):
            #     cond += " AND sed.item_code = \'" + str(filters.item_code) + "\'"
            # data = """SELECT se.posting_date, sed.item_code, sed.item_name, 
            #     i.item_group, i.item_sub_group, sed.uom, sed.qty, 
            #     sed.valuation_rate,sed.amount, sed.cost_center, se.name 
            # FROM `tabStock Entry` se, `tabStock Entry Detail` sed, `tabItem` i
            # WHERE se.name = sed.parent 
            # AND  se.docstatus = 1 
            # AND se.purpose = 'Material Issue'
            # AND i.name = sed.item_code"""
    
    return data

# from __future__ import unicode_literals
# import frappe
# from frappe.utils import flt, cint,add_days, cstr, flt, getdate, nowdate, rounded, date_diff

# def execute(filters=None):
# 	columns = get_columns(filters)
# 	data = get_data(filters)
# 	return columns, data


# def get_columns(filters):
# 	cols = [
# 		("Date") + ":date:100",
# 		("Material Code") + ":data:110",
# 		("Material Name")+":data:120",
# 		("Material Group")+":data:120",
# 		("Material Sub Group")+":data:150",
# 		("UoM") + ":data:50",
# 		("Qty")+":data:50",
# 		("Valuation Rate")+":data:120",
# 		("Amount")+":Currency:110",
# 	]
# 	if filters.purpose == "Material Issue":
# 		cols.append(("Cost Center")+":data:170")


# 	if filters.purpose == "Material Transfer":
# 		cols.append(("Warehouse")+":data:170")
# 	cols.append(("Stock Entry")+":Link/Stock Entry:170")
# 	return cols

# def get_data(filters):
# 	if filters.purpose == 'Material Transfer':
# 		data = """SELECT se.posting_date, sed.item_code, sed.item_name, 
# 				i.item_group, i.item_sub_group, sed.uom, sed.qty, 
# 				sed.valuation_rate,sed.amount, sed.t_warehouse, se.name 
# 			FROM `tabStock Entry` se, `tabStock Entry Detail` sed, `tabItem` i
# 			WHERE se.name = sed.parent 
# 			AND  se.docstatus = 1 
# 			AND se.purpose = 'Material Transfer'
# 			AND i.name = sed.item_code"""
# 	elif filters.purpose == 'Material Issue':
# 		data = """SELECT se.posting_date, sed.item_code, sed.item_name, 
# 				i.item_group, i.item_sub_group, sed.uom, sed.qty, 
# 				sed.valuation_rate,sed.amount, sed.cost_center, se.name 
# 			FROM `tabStock Entry` se, `tabStock Entry Detail` sed, `tabItem` i
# 			WHERE se.name = sed.parent 
# 			AND  se.docstatus = 1 
# 			AND se.purpose = 'Material Issue'
# 			AND i.name = sed.item_code"""
# 	if filters.get("warehouse"):
# 		data += " AND sed.s_warehouse = \'" + str(filters.warehouse) + "\'"
# 	if filters.get("item_code"):
# 		data += " AND sed.item_code = \'" + str(filters.item_code) + "\'"
# 	if filters.get("from_date") and filters.get("to_date"):
# 		data += " AND se.posting_date BETWEEN \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\'"
# 	return frappe.db.sql(data)

# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

