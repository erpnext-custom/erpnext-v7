# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = get_cols(filters), get_data(filters)
	return columns, data

def get_data(filters):
	cond = ''
	data = []
	if filters.is_inter_company:
		cond += " where is_inter_company = 1 "
	if filters.dhi_gcoa_acc:
		cond += " where account_code = '{}' ".format(filters.dhi_gcoa_acc)
	if filters.is_inter_company and filters.dhi_gcoa_acc:
		cond = " where where is_inter_company = 1 and account_code = '{}' ".format(filters.dhi_gcoa_acc)
	
	if not filters.map or filters.map.strip() == "GCOA Mapped":
		for d in frappe.db.sql('''
						 SELECT
							account_code as dhi_gcoa_acc_code,
								account_name as dhi_gcoa_acc,
								CASE
									WHEN is_inter_company = 1 THEN 'Inter Company'
									ELSE 'None Inter Company'
								END as is_inter_company
						 FROM `tabDHI GCOA Mapper` {}
						 '''.format(cond),as_dict=True):
			val = frappe.db.sql('''
					   SELECT account as coa_acc,
							'{}' as dhi_gcoa_acc,
							'{}' as dhi_gcoa_acc_code,
							'{}' as is_inter_company
					   FROM `tabDHI Mapper Item` WHERE parent = '{}'
					   '''.format(d.dhi_gcoa_acc,d.dhi_gcoa_acc_code,d.is_inter_company,d.dhi_gcoa_acc),as_dict=1)
			data += val
	elif filters.map.strip() == "COA Unmapped":
		data = frappe.db.sql('''
						SELECT name as coa_acc
						FROM `tabAccount` a
						WHERE NOT EXISTS (	select 1 from `tabDHI Mapper Item` where account = a.name)
						AND a.is_group != 1
						 ''',as_dict=1)
	return data
	
def get_cols(filters):

	if not filters.map or filters.map.strip() == "GCOA Mapped":
			cols = [{"fieldname":"dhi_gcoa_acc_code","label":"DHI GCOA Code","fieldtype":"Link","options":"DHI GCOA","width":120,},
		{"fieldname":"dhi_gcoa_acc","label":"DHI Group Chart Of Account","fieldtype":"Link","options":"DHI GCOA Mapper","width":250,},
		{"fieldname":"is_inter_company","label":"Is Inter Company","fieldtype":"Data","width":150},
		{"fieldname":"coa_acc","label":"Company Chart Of Account","fieldtype":"Link","options":"Account","width":400}
	]
	elif filters.map.strip() == "COA Unmapped":
		cols = [{"fieldname":"coa_acc","label":"Company Chart Of Account","fieldtype":"Link","options":"Account","width":400}]
	return cols