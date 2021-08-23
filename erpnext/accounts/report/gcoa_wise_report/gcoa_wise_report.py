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
	is_inter_company = frappe.db.get_value('DHI GCOA Mapper',filters.gcoa_name,['is_inter_company'])
	for d in get_coa(filters.gcoa_name):
		if d.doc_company :
			data += get_doc_company_amount(d,filters)
		elif d.account_type in ['Payable','Receivable'] and not d.doc_company:
			data += payable_receivable_amount(is_inter_company,d,filters)
		elif not d.doc_company:
			data += other_expense_amount(is_inter_company,d,filters)
	return data

def get_coa(gcoa_account_name):
	# frappe.msgprint(str(gcoa_account_name))
	return frappe.db.sql('''
						 SELECT account, account_type,
						   root_type, doc_company
						FROM `tabDHI Mapper Item`
						WHERE parent = '{}'
						 '''.format(gcoa_account_name),as_dict = True)


# for gl selected for particular doc company
def get_doc_company_amount(coa,filters):
	# frappe.msgprint(str('doc '))
	value, debit, credit, amount = [], 0, 0, 0
	for a in frappe.db.sql("""
			select sum(credit) as credit, sum(debit) as debit
			from `tabGL Entry` where posting_date between '{0}' and '{1}' 
			and (account = '{2}' or exact_expense_acc = '{2}') 
			and (credit is not null or debit is not null)
			and voucher_type not in ('Stock Entry','Purchase Receipt','Stock Reconciliation','Issue POL','Asset Movement','Bulk Asset Transfer','Equipment POL Transfer','Period Closing Voucher','TDS Remittance')
			""".format(filters.from_date,filters.to_date,coa.account),as_dict=True):
		debit += flt(a.debit)
		credit += flt(a.credit)
		amount += flt(a.debit) - flt(a.credit) if coa.root_type in ['Asset','Expense'] else flt(a.credit) - flt(a.debit)

	if debit or credit:
		doc = frappe.get_doc('DHI Setting')
		row = {}
		value.append({
			'account':coa.account,
			'entity':doc.entity,
			'segment':doc.segment,
			'flow':doc.flow,
			'interco':'I_'+coa.doc_company,
			'time':filters.from_date + ' to '+filters.to_date,
			'debit':debit,
			'credit':credit,
			'amount': amount
		})
	return value

# for Purchase invoice where tempoary gl is booked
def other_expense_amount(is_inter_company,coa,filters):
	value, debit, credit, amount = [], 0, 0, 0
	# frappe.msgprint(str(coa))
	for a in frappe.db.sql("""
			select sum(credit) as credit, sum(debit) as debit, 
			consolidation_party_type as party_type,
			consolidation_party as party
			from `tabGL Entry` where posting_date between '{0}' and '{1}' 
			and (exact_expense_acc = '{2}' or account = '{2}') 
			and (credit is not null or debit is not null) 
			and voucher_type not in ('Stock Entry','Purchase Receipt','Stock Reconciliation','Issue POL','Asset Movement','Bulk Asset Transfer','Equipment POL Transfer','Period Closing Voucher','TDS Remittance')
			group by consolidation_party
			""".format(filters.from_date,filters.to_date,coa.account),as_dict=True):
		if (a.credit or a.debit) and a.party_type :
			dhi_company_code =''
			if a.party_type == 'Supplier':
				dhi_company_code = frappe.db.get_value('Supplier',{'name':a.party,'inter_company':1},['company_code'])
			else:
				dhi_company_code = frappe.db.get_value('Customer',{'name':a.party,'inter_company':1},['company_code'])
	
			if dhi_company_code and is_inter_company :
				row = {}
				row = cerate_inter_compay_row(coa.account,coa.root_type,dhi_company_code,filters,a)
				if len(value) > 0:
					is_new_row = True
					for i, val in enumerate(value):
						if val["interco"] == row["interco"]:
							value[i]["amount"] += flt(row["amount"])
							value[i]["credit"] += flt(row["credit"])
							value[i]["debit"] += flt(row["debit"])
							is_new_row = False
							break
					if is_new_row:
						value.append(row)
				else:
					value.append(row)
			elif not dhi_company_code and not is_inter_company:
				debit += flt(a.debit)
				credit += flt(a.credit)
				amount += flt(a.debit) - flt(a.credit) if coa.root_type in ['Asset','Expense'] else flt(a.credit) - flt(a.debit)
	if debit or credit or amount:
		value.append(create_non_inter_compay_row(coa.account,filters,credit,debit,amount))
	return value
# applicable for payable and Receivable
def payable_receivable_amount(is_inter_company,coa,filters):
	value = []
	debit, credit,amount, query = 0,0,0,''
	# frappe.msgprint('payable and receivale')
	query = """
			select sum(gl.credit) as credit,sum(gl.debit) as debit, gl.party,gl.party_type
			from `tabGL Entry` as gl where gl.posting_date between '{0}' and '{1}' 
			and gl.account = '{2}' 
			and (gl.party is not null and gl.party != '')
			and (gl.credit is not null or gl.debit is not null) 
			and voucher_type not in ('Stock Entry','Purchase Receipt','Stock Reconciliation','Issue POL','Asset Movement','Bulk Asset Transfer','Equipment POL Transfer','Period Closing Voucher','TDS Remittance')
			group by party
			""".format(filters.from_date,filters.to_date,coa.account)
   
	for a in frappe.db.sql(query,as_dict=True) :
		if (a.credit or a.debit) and a.party_type :
			dhi_company_code =''
			# if gcoa.is_inter_company:
			if a.party_type == 'Supplier':
				dhi_company_code = frappe.db.get_value('Supplier',{'name':a.party,'inter_company':1},['company_code'])
			else:
				dhi_company_code = frappe.db.get_value('Customer',{'name':a.party,'inter_company':1},['company_code'])
			if dhi_company_code and is_inter_company:
				# frappe.msgprint(str(dhi_company_code))
				row = {}
				row = cerate_inter_compay_row(coa.account,coa.root_type,dhi_company_code,filters,a)
				if len(value) > 0:
					is_new_row = True
					for i, val in enumerate(value):
						if val["interco"] == row["interco"]:
							value[i]["amount"] += flt(row["amount"])
							value[i]["credit"] += flt(row["credit"])
							value[i]["debit"] += flt(row["debit"])
							is_new_row = False
							break
					if is_new_row:
						value.append(row)
				else:
					value.append(row)
			elif not dhi_company_code and not is_inter_company:
				debit += flt(a.debit)
				credit += flt(a.credit)
				amount += flt(a.debit) - flt(a.credit) if coa.root_type in ['Asset','Expense'] else flt(a.credit) - flt(a.debit)
	if debit or credit or amount:
		value.append(create_non_inter_compay_row(coa.account,filters,credit,debit,amount))
	return value


def create_non_inter_compay_row(account_name,filters,credit,debit,amount) :
	doc = frappe.get_doc('DHI Setting')
	row = {}
	# frappe.msgprint(str(doc.interco))
	row = {
			'account':account_name,
			'entity':doc.entity,
			'segment':doc.segment,
			'flow':doc.flow,
			'interco':doc.interco,
			'time':filters.from_date+' to '+filters.to_date,
			'debit':debit,
			'credit':credit,
			'amount':amount
			}
	return row


def cerate_inter_compay_row(account_name,root_type,company_code,filters,data=None) :
	# frappe.msgprint(str(data))
	doc = frappe.get_doc('DHI Setting')
	row = {}
	row = {
			'account':account_name,
			'entity':doc.entity,
			'segment':doc.segment,
			'flow':doc.flow,
			'interco':'I_'+str(company_code),
			'time':filters.from_date + ' to '+filters.to_date,
			'debit':data.debit,
			'credit':data.credit,
			'amount': flt(data.debit) - flt(data.credit) if root_type in ['Asset','Expense'] else flt(data.credit) - flt(data.debit)
	}
	return row

def get_columns():
	return [
		{
			"fieldname":"account",
			"label":"Account",
			"fieldtype":"Link",
			"options":"Account",
			"width":150
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
			"width":60
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
			"width":100
		},
		{
			"fieldname":"credit",
			"label":"Credit",
			"fieldtype":"Float",
			"width":100
		},
		{
			"fieldname":"amount",
			"label":"Amount",
			"fieldtype":"Float",
			"width":120
		},
	]
