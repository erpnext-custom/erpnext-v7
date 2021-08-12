# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt

def execute(filters=None):
	columns, data = get_columns(), get_data(filters)
	return columns, data

def get_data(filters):
	data = []
	for d in frappe.db.sql("""
		SELECT account_code, 
			account_name,
			is_inter_company
		FROM `tabDHI GCOA Mapper`
		""",as_dict=True):
		data += get_value(d.account_code,d.account_name,d.is_inter_company,filters)
	# frappe.msgprint(format(data))
	return data

def get_value(account_code,account_name,is_inter_company,filters):
	value = []
	debit = 0
	credit = 0
	amount = 0
	doc = frappe.get_doc('DHI Setting')
	for d in frappe.db.sql("""
			SELECT account 
			FROM `tabDHI Mapper Item`
			WHERE parent = '{}'
		""".format(account_name),as_dict=True):
		for t in frappe.db.sql("""
			SELECT DISTINCT(party) as party, party_type
			FROM `tabGL Entry`
			WHERE account = '{}' 
			AND posting_date BETWEEN '{}' 
			AND '{}'
		""".format(d.account,filters.from_date,filters.to_date),as_dict=True):

			if t.party_type in ['Supplier','Customer'] or not t.party_type :
				company_code = ''
				if t.party_type == 'Supplier':
					company_code = frappe.db.get_value('Supplier',{'name':t.party}, ['company_code'])
				elif t.party_type == 'Customer':
					company_code = frappe.db.get_value('Customer',{'name':t.party}, ['company_code'])

				data = frappe.db.sql("""
							SELECT SUM(debit) as debit, SUM(credit) as credit
							FROM `tabGL Entry`
							WHERE account = '{}' 
							AND posting_date BETWEEN '{}' 
							AND '{}'
							AND party_type ='{}'
							AND party ='{}'
						""".format(d.account,filters.from_date,filters.to_date,t.party_type,t.party),as_dict=True)

				root_type = frappe.db.get_value('Account',d.account,['root_type'])
				
				if company_code and (not filters.is_inter_company or filters.is_inter_company == 'Yes') :
					value.append({
						'account_code':account_code,
						'account':account_name,
						'entity':doc.entity,
						'segment':doc.segment,
						'flow':doc.flow,
						'interco':'I_'+company_code,
						'time':filters.from_date+' to '+filters.to_date,
						'debit':data[0].debit,
						'credit':data[0].credit,
						'amount': flt(data[0].debit) - flt(data[0].credit) if root_type in ['Asset','Expense'] else flt(data[0].credit) - flt(data[0].debit)
					})
				elif root_type in ['Asset','Expense']:
					amount += flt(data[0].debit) - flt(data[0].credit)
					debit += flt(data[0].debit)
					credit += flt(data[0].credit)
				else:
					amount += flt(data[0].credit) - flt(data[0].debit)
					debit += flt(data[0].debit)
					credit += flt(data[0].credit)

	if not filters.is_inter_company or filters.is_inter_company == 'No':
		if not is_inter_company:
			value.append({
							'account_code':account_code,
							'account':account_name,
							'entity':doc.entity,
							'segment':doc.segment,
							'flow':doc.flow,
							'interco':doc.interco,
							'time':filters.from_date+' to '+filters.to_date,
							'debit':debit,
							'credit':credit,
							'amount':amount
						})
	
	
	return value

def get_columns():
	return [
		{
			"fieldname":"account_code",
			"label":"Account",
			"fieldtype":"Link",
			"options":"DHI GCOA Mapper",
			"width":100
		},
		{
			"fieldname":"account",
			"label":"Description",
			"fieldtype":"Link",
			"options":"DHI GCOA Mapper",
			"width":180
		},
		{
			"fieldname":"entity",
			"label":"Entity",
			"fieldtype":"Data",
			"width":60
		},
		{
			"fieldname":"segment",
			"label":"Segment",
			"fieldtype":"Data",
			"width":60
		},
		{
			"fieldname":"flow",
			"label":"Flow",
			"fieldtype":"Data",
			"width":80
		},
		{
			"fieldname":"interco",
			"label":"Interco",
			"fieldtype":"Data",
			"width":60
		},
		{
			"fieldname":"time",
			"label":"Time",
			"fieldtype":"Data",
			"width":160
		},
		{
			"fieldname":"debit",
			"label":"Debit",
			"fieldtype":"Float",
			"width":120
		},
		{
			"fieldname":"credit",
			"label":"Credit",
			"fieldtype":"Float",
			"width":120
		},
		{
			"fieldname":"amount",
			"label":"Amount",
			"fieldtype":"Float",
			"width":120
		},
	]