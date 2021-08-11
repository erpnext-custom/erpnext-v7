# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt

def execute(filters=None):
	filter = {}
	# frappe.msgprint(str(filters))
	filter['from_date'] = filters.from_date
	filter['to_date'] = filters.to_date
	filter['is_inter_company'] = filters.is_inter_company
	
	columns, data = get_columns(), get_data(filter)
	return columns, data

def get_data(filters):
	data, cond = [], ''
	if filters['is_inter_company'] == 'Yes':
		cond += ' WHERE is_inter_company = 1 '
	elif filters['is_inter_company'] == 'No':
		cond += ' WHERE is_inter_company = 0 '
	for d in frappe.db.sql('''
						SELECT account_name, account_code, is_inter_company
						FROM `tabDHI GCOA Mapper` {}
						'''.format(cond),as_dict=True):
		if d.is_inter_company:
			data += inter_company(d,filters)
		else:
			data += non_inter_company(d,filters)
   
	return data

def inter_company(gcoa,filters):
	data = []
	for d in get_coa(gcoa.account_name):
		if d.doc_company and gcoa.is_inter_company :
			data += get_doc_company_amount(gcoa,d,filters)
		elif d.account_type in ['Payable','Receivable'] and not d.doc_company:
			val, c, de, amt = payable_receivable_amount(gcoa,d,filters)
			data += val
		elif not d.doc_company:
			val, cr, de, amt = other_expense_amount(gcoa,d,filters)
			data += val
		
	data1 = merge_duplicate(data)
	return data1

def non_inter_company(gcoa,filters):
	data, credit, debit, amount = [], 0, 0, 0
	for d in get_coa(gcoa.account_name):
		if d.account_type in ['Payable','Receivable'] and not d.doc_company:
			c, de, a = 0, 0, 0
			val, c, de, a = payable_receivable_amount(gcoa,d,filters)
			credit += flt(c)
			debit += flt(de)
			amount += flt(a)
		elif not d.doc_company:
			c, de, a = 0, 0, 0
			val, c, de, a = other_expense_amount(gcoa,d,filters)
			credit += flt(c)
			debit += flt(de)
			amount += flt(a)
	if credit or debit or amount:
		data.append(create_non_inter_compay_row(gcoa.account_code,gcoa.account_name,filters,credit,debit,amount))
	return data

def merge_duplicate(data):
	new_data = []
	for d in data:
		if len(data) == 0 :
			new_data.append(d)
		else:
			no_duplicate = True
			for i, item in enumerate(new_data):
				if item["interco"] == d["interco"]:
					new_data[i]["amount"] += flt(d["amount"])
					new_data[i]["credit"] += flt(d["credit"])
					new_data[i]["debit"] += flt(d["debit"])
					no_duplicate = False
					break
			if no_duplicate:
				new_data.append(d)
	
	return new_data
		
def get_coa(gcoa_account_name):
	return frappe.db.sql('''
						 SELECT account, account_type,
						   root_type, doc_company
						FROM `tabDHI Mapper Item`
						WHERE parent = '{}'
						 '''.format(gcoa_account_name),as_dict = True)
 
# for Purchase invoice where tempoary gl is booked
def other_expense_amount(gcoa,coa,filters):
	value, debit, credit, amount = [], 0, 0, 0

	for a in frappe.db.sql("""
			select sum(credit) as credit, sum(debit) as debit, 
			consolidation_party_type as party_type,
			consolidation_party as party
			from `tabGL Entry` where posting_date between '{0}' and '{1}' 
			and (exact_expense_acc = '{2}' or account = '{2}') 
			and (credit is not null or debit is not null) 
			and voucher_type not in ('Stock Entry','Purchase Receipt','Stock Reconciliation','Imprest Recoup','Issue POL','Asset Movement','Bulk Asset Transfer','Equipment POL Transfer','Period Closing Voucher','TDS Remittance')
			group by consolidation_party
			""".format(filters['from_date'],filters['to_date'],coa.account),as_dict=True):
		if (a.credit or a.debit) and a.party_type :
			dhi_company_code =''
			# if gcoa.is_inter_company:
				# frappe.msgprint(str(a))
			if a.party_type == 'Supplier':
				dhi_company_code = frappe.db.get_value('Supplier',{'name':a.party,'inter_company':1},['company_code'])
			else:
				dhi_company_code = frappe.db.get_value('Customer',{'name':a.party,'inter_company':1},['company_code'])
	
			if dhi_company_code and gcoa.is_inter_company :
				row = {}
				row = cerate_inter_compay_row(gcoa.account_code,gcoa.account_name,coa.root_type,dhi_company_code,filters,a)
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
			elif not dhi_company_code and not gcoa.is_inter_company :
				debit += flt(a.debit)
				credit += flt(a.credit)
				amount += flt(a.debit) - flt(a.credit) if coa.root_type in ['Asset','Expense'] else flt(a.credit) - flt(a.debit)
	
	if gcoa.is_inter_company:
		return value, 0, 0, 0
	else:
		return [], credit, debit, amount

# for gl selected for particular doc company
def get_doc_company_amount(gcoa,coa,filters):
	# frappe.msgprint(str(d))
	value, debit, credit, amount = [], 0, 0, 0
	for a in frappe.db.sql("""
			select sum(credit) as credit, sum(debit) as debit
			from `tabGL Entry` where posting_date between '{0}' and '{1}' 
			and (account = '{2}' or exact_expense_acc = '{2}') 
			and (credit is not null or debit is not null)
			and voucher_type not in ('Stock Entry','Purchase Receipt','Stock Reconciliation','Imprest Recoup','Issue POL','Asset Movement','Bulk Asset Transfer','Equipment POL Transfer','Period Closing Voucher','TDS Remittance')
			""".format(filters['from_date'],filters['to_date'],coa.account),as_dict=True):
		debit += flt(a.debit)
		credit += flt(a.credit)
		amount += flt(a.debit) - flt(a.credit) if coa.root_type in ['Asset','Expense'] else flt(a.credit) - flt(a.debit)

	if debit or credit:
		doc = frappe.get_doc('DHI Setting')
		row = {}
		value.append({
			'account_code':gcoa.account_code,
			'account':gcoa.account_name,
			'entity':doc.entity,
			'segment':doc.segment,
			'flow':doc.flow,
			'interco':'I_'+coa.doc_company,
			'time':filters['from_date'] + ' to '+filters['to_date'],
			'debit':debit,
			'credit':credit,
			'amount': amount
		})
	return value

# applicable for payable and Receivable
def payable_receivable_amount(gcoa,coa,filters):
	value = []
	debit, credit,amount, query = 0,0,0,''
	query = """
			select sum(gl.credit) as credit,sum(gl.debit) as debit, gl.party,gl.party_type
			from `tabGL Entry` as gl where gl.posting_date between '{0}' and '{1}' 
			and gl.account = '{2}' 
			and (gl.party is not null and gl.party != '')
			and (gl.credit is not null or gl.debit is not null) 
			and voucher_type not in ('Stock Entry','Purchase Receipt','Stock Reconciliation','Imprest Recoup','Issue POL','Asset Movement','Bulk Asset Transfer','Equipment POL Transfer','Period Closing Voucher','TDS Remittance')
			group by party
			""".format(filters['from_date'],filters['to_date'],coa.account)
   
	for a in frappe.db.sql(query,as_dict=True) :
		# frappe.msgprint(str(a))
		if (a.credit or a.debit) and a.party_type :
			dhi_company_code =''
			if gcoa.is_inter_company:
				if a.party_type == 'Supplier':
					dhi_company_code = frappe.db.get_value('Supplier',{'name':a.party,'inter_company':1},['company_code'])
				else:
					dhi_company_code = frappe.db.get_value('Customer',{'name':a.party,'inter_company':1},['company_code'])
			if dhi_company_code and gcoa.is_inter_company:
				# frappe.msgprint(str(dhi_company_code))
				row = {}
				row = cerate_inter_compay_row(gcoa.account_code,gcoa.account_name,coa.root_type,dhi_company_code,filters,a)
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
			elif not dhi_company_code and not gcoa.is_inter_company:
				debit += flt(a.debit)
				credit += flt(a.credit)
				amount += flt(a.debit) - flt(a.credit) if coa.root_type in ['Asset','Expense'] else flt(a.credit) - flt(a.debit)
	if gcoa.is_inter_company:
		return value, 0, 0, 0
	else:
		return [], credit, debit, amount

def create_non_inter_compay_row(account_code,account_name,filters,credit,debit,amount) :
	doc = frappe.get_doc('DHI Setting')
	row = {}
	# frappe.msgprint(str(doc.interco))
	row = {
			'account_code':account_code,
			'account':account_name,
			'entity':doc.entity,
			'segment':doc.segment,
			'flow':doc.flow,
			'interco':doc.interco,
			'time':filters['from_date']+' to '+filters['to_date'],
			'debit':debit,
			'credit':credit,
			'amount':amount
			}
	return row


def cerate_inter_compay_row(account_code,account_name,root_type,company_code,filters,data=None) :
	# frappe.msgprint(str(data))
	doc = frappe.get_doc('DHI Setting')
	row = {}
	row = {
			'account_code':account_code,
			'account':account_name,
			'entity':doc.entity,
			'segment':doc.segment,
			'flow':doc.flow,
			'interco':'I_'+str(company_code),
			'time':filters['from_date'] + ' to '+filters['to_date'],
			'debit':data.debit,
			'credit':data.credit,
			'amount': flt(data.debit) - flt(data.credit) if root_type in ['Asset','Expense'] else flt(data.credit) - flt(data.debit)
	}
	return row

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
			"width":300
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
 
# @frappe.whitelist()
def try_data(filters):
	return filters