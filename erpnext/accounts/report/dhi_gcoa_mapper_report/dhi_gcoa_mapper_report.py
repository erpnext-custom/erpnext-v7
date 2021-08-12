# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = get_cols(filters), get_data(filters)
	return columns, data

def get_data(filters):
    cond = ''
    
    if filters.is_inter_company:
        cond += " AND dm.is_inter_company = 1 "
    if filters.dhi_gcoa_acc:
        cond += " AND dm.account_code = '{}' ".format(filters.dhi_gcoa_acc)
        
    if not filters.map or filters.map == "Mapped":
		return frappe.db.sql('''
							SELECT dm.account_code as dhi_gcoa_acc_code,
								dm.account_name as dhi_gcoa_acc,
								CASE
									WHEN dm.is_inter_company = 1 THEN 'Inter Company'
									ELSE 'None Inter Company'
								END as is_inter_company,
								dmi.account as coa_acc
							FROM `tabDHI GCOA Mapper` dm
							INNER JOIN `tabDHI Mapper Item` dmi ON dm.name = dmi.parent
							{}
							'''.format(cond),as_dict=True)
    else:
		return frappe.db.sql('''
							SELECT dm.account_code as dhi_gcoa_acc_code,
								dm.account_name as dhi_gcoa_acc,
								CASE
									WHEN dm.is_inter_company = 1 THEN 'Inter Company'
									ELSE 'None Inter Company'
								END as is_inter_company
							FROM `tabDHI GCOA` dm
							WHERE dm.account_code NOT IN
       							(select account_code from `tabDHI GCOA Mapper` where account_code = dm.account_code)
							{}
							'''.format(cond),as_dict=True)
def get_cols(filters):
    cols = [
		{
			"fieldname":"dhi_gcoa_acc_code",
			"label":"DHI GCOA Code",
			"fieldtype":"Link",
			"options":"DHI GCOA",
			"width":150
		},
		{
			"fieldname":"dhi_gcoa_acc",
			"label":"DHI GCOA",
			"fieldtype":"Link",
			"options":"DHI GCOA Mapper",
			"width":350
		},
		{
			"fieldname":"is_inter_company",
			"label":"Is Inter Company",
			"fieldtype":"Data",
			"width":150
		}
	]
    if not filters.map or filters.map == "Mapped":
        cols.append({
			"fieldname":"coa_acc",
			"label":"Company Account",
			"fieldtype":"Link",
			"options":"Account",
			"width":400
		})
    return cols