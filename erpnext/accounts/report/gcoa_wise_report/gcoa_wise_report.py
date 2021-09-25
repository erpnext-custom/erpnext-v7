# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe.utils import getdate, datetime, nowdate, flt

def execute(filters=None):
	filter = {}
	filter['from_date'] = filters.from_date
	filter['to_date'] = filters.to_date
	filter['gcoa_name'] = filters.gcoa_name
	columns = get_columns()
	data = get_data(filter,True)
	return columns, data

def get_data(filters,is_for_report=None):
	data, amount, o_cr, o_dr, cr, dr = [], 0, 0, 0, 0, 0
 
	is_inter_company = frappe.db.get_value('DHI GCOA Mapper',filters['gcoa_name'],['is_inter_company'])
	
	for d in get_coa(filters['gcoa_name']):
		val, amt, op_dr, op_cr, dr1, cr1 = [], 0, 0, 0, 0, 0
		if d.doc_company :
			val, amt, op_dr, op_cr, dr1, cr1  = get_doc_company_amount(d,filters)
		elif d.account_type in ['Payable','Receivable'] and not d.doc_company:
			val, amt, op_dr, op_cr, dr1, cr1 = payable_receivable_amount(is_inter_company,d,filters)
		elif not d.doc_company:
			val, amt, op_dr, op_cr, dr1, cr1 = other_expense_amount(is_inter_company,d,filters)
   
		data += val
		amount += flt(amt)
		o_cr += op_cr
		o_dr += op_dr
		cr += cr1
		dr += dr1
	if not is_inter_company:
		row = create_non_inter_compay_row(o_dr, o_cr,'Total',filters,cr,dr,amount)
		data.append(row)
	if is_for_report and is_inter_company:
		t = dr = cr = de = c = 0
		for d in data:
			t += flt(d['amount'])
			dr += flt(d['opening_debit'])
			cr += flt(d['opening_credit'])
			de += flt(d['debit'])
			c += flt(d['credit'])
		row = create_non_inter_compay_row(dr, cr,'Total',filters,c,de,t)
		data.append(row)
	return data

# for gl selected for particular doc company
def get_doc_company_amount(coa,filters):
	value, debit, credit, amount, opening_dr,opening_cr = [], 0, 0, 0, 0, 0
 
	for a in frappe.db.sql("""
			select sum(credit) as credit, sum(debit) as debit
			from `tabGL Entry`  where posting_date between "{0}" and "{1}" 
			and (account = "{2}" or exact_expense_acc = "{2}") 
			and (credit is not null or debit is not null)
			and voucher_type not in ('Stock Entry','Purchase Receipt','Stock Reconciliation','Issue POL','Asset Movement','Bulk Asset Transfer','Equipment POL Transfer','Period Closing Voucher','TDS Remittance')
			""".format(filters['from_date'],filters['to_date'],coa.account),as_dict=True):
	  
		a['opening_dr'] = a['opening_cr'] = 0

		if coa.root_type in ['Asset','Liability','Equity']:
			query = '''
				select sum(credit) as opening_credit,sum(debit) as opening_debit from `tabGL Entry`
				where posting_date < "{0}"
				and account = "{1}" or exact_expense_acc = "{1}"
					'''.format(filters['from_date'], coa.account)
			a['opening_dr'], a['opening_cr'] = get_opening_balance(query)

		opening_dr += flt(a.opening_dr)
		opening_cr += flt(a.opening_cr)
		debit += flt(a.debit)
		credit += flt(a.credit)
		amount += flt(flt(a.debit) + flt(a.opening_dr)) - flt(flt(a.credit) + flt(a.opening_cr)) if coa.root_type in ['Asset','Expense'] else flt(flt(a.credit) + flt(a.opening_cr)) - flt(flt(a.debit) + flt(a.opening_dr))

	if debit or credit:
		doc = frappe.get_doc('DHI Setting')
		row = {}
		value.append({
			'opening_debit':opening_dr,
			'opening_credit':opening_cr,
			'account':coa.account,
			'entity':doc.entity,
			'segment':doc.segment,
			'flow':doc.flow,
			'interco':'I_'+coa.doc_company,
			'time':str(filters['from_date']) + ' to '+str(filters['to_date']),
			'debit':debit,
			'credit':credit,
			'amount': amount
		})
	return value, amount, 0, 0, 0, 0

# for Purchase invoice where tempoary gl is booked
def other_expense_amount(is_inter_company,coa,filters):
	value, debit, credit, amount, opening_dr, opening_cr, amt = [], 0, 0, 0, 0, 0, 0
 
	for a in frappe.db.sql("""
			select sum(credit) as credit, sum(debit) as debit, 
			consolidation_party_type as party_type,
			consolidation_party as party
			from `tabGL Entry` where posting_date between "{0}" and "{1}" 
			and (account = "{2}" or exact_expense_acc = "{2}") 
			and (credit is not null or debit is not null) 
			and voucher_type not in ('Stock Entry','Purchase Receipt','Stock Reconciliation','Issue POL','Asset Movement','Bulk Asset Transfer','Equipment POL Transfer')
			group by consolidation_party
			""".format(filters['from_date'],filters['to_date'],coa.account),as_dict=True):
		if (a.credit or a.debit) :
			cond, dr, cr = '', 0, 0
			if a.party:
				cond += ' consolidation_party = "{}" '.format(a.party)
			else:
				cond += ' consolidation_party is null '

			q = '''
				select sum(debit) as opening_debit, sum(credit) as opening_credit
				from `tabGL Entry` where {0}
				and (account = "{1}" or exact_expense_acc = "{1}") 
				and posting_date < "{2}"
				'''.format(cond,coa.account,filters['from_date'])
	
			if coa.root_type in ['Asset','Liability','Equity']:
				dr, cr = get_opening_balance(q)
   
			dhi_company_code =''
			if a.party_type == 'Supplier':
				dhi_company_code = frappe.db.get_value('Supplier',{'name':a.party,'inter_company':1,'disabled':0},['company_code'])
			else:
				dhi_company_code = frappe.db.get_value('Customer',{'name':a.party,'inter_company':1,'disabled':0},['company_code'])
	
			if dhi_company_code and is_inter_company :
				row = {}
				row = cerate_inter_compay_row(dr, cr, coa.account, coa.root_type, dhi_company_code, filters, a)
				if len(value) > 0:
					is_new_row = True
					for i, val in enumerate(value):
						if val["interco"] == row["interco"]:
							value["opening_debit"] += flt(row["opening_debit"])
							value["opening_credit"] += flt(row["opening_credit"])
							value[i]["amount"] += flt(row["amount"])
							value[i]["credit"] += flt(row["credit"])
							value[i]["debit"] += flt(row["debit"])
							amt += flt(row["amount"])
							is_new_row = False
							break
					if is_new_row:
						amt += flt(row["amount"])
						value.append(row)
				else:
					amt += flt(row["amount"])
					value.append(row)
			elif not dhi_company_code and not is_inter_company:
				opening_dr += flt(dr)
				opening_cr += flt(cr)
				debit += flt(a.debit)
				credit += flt(a.credit)
				amount += flt(flt(a.debit) + flt(dr)) - flt(flt(a.credit)+flt(cr)) if coa.root_type in ['Asset','Expense'] else flt(flt(a.credit)+flt(cr)) - flt(flt(a.debit) + flt(dr))
	
	if debit or credit or amount:
		amt += flt(amount)
		value.append(create_non_inter_compay_row(opening_dr, opening_cr,coa.account,filters,credit,debit,amount))
	return value, amt, opening_dr, opening_cr, debit, credit

# applicable for payable and Receivable
def payable_receivable_amount(is_inter_company,coa,filters):
	value = []
	debit, credit,amount, query,opening_dr, opening_cr, amt = 0,0,0,'',0,0, 0
	query = """
			select sum(gl.credit) as credit, sum(gl.debit) as debit, gl.party, gl.party_type
			from `tabGL Entry` as gl where gl.posting_date between "{0}" and "{1}" 
			and gl.account = "{2}" 
			and (gl.party is not null and gl.party != '')
			and (gl.credit is not null or gl.debit is not null) 
			and voucher_type not in ('Stock Entry','Purchase Receipt','Stock Reconciliation','Issue POL','Asset Movement','Bulk Asset Transfer','Equipment POL Transfer','Period Closing Voucher','TDS Remittance')
			group by party
			""".format(filters['from_date'],filters['to_date'],coa.account)
	for a in frappe.db.sql(query,as_dict=True) :
		dr = cr = 0
		if coa.root_type in ['Asset','Liability','Equity']:		
			q = '''
				select sum(debit) as opening_debit, sum(credit) as opening_credit
				from `tabGL Entry` where party = "{}" and account = "{}" and posting_date < "{}"
				'''.format(a.party,coa.account,filters['from_date'])
			dr, cr = get_opening_balance(q)
  
		if (a.credit or a.debit) and a.party_type :
			
			dhi_company_code =''
			if a.party_type == 'Supplier':
				dhi_company_code = frappe.db.get_value('Supplier',{'name':a.party,'inter_company':1,'disabled':0},['company_code'])
			else:
				dhi_company_code = frappe.db.get_value('Customer',{'name':a.party,'inter_company':1,'disabled':0},['company_code'])
			if dhi_company_code and is_inter_company:
				row = {}
				row = cerate_inter_compay_row(dr, cr, coa.account, coa.root_type, dhi_company_code, filters, a)
				if len(value) > 0:
					is_new_row = True
					for i, val in enumerate(value):
						if val["interco"] == row["interco"]:
							value[i]["opening_debit"] += flt(row["opening_debit"])
							value[i]["opening_credit"] += flt(row["opening_credit"])
							value[i]["amount"] += flt(row["amount"])
							value[i]["credit"] += flt(row["credit"])
							value[i]["debit"] += flt(row["debit"])
							amt += flt(row["amount"])
							is_new_row = False
							break
					if is_new_row:
						amt += flt(row["amount"])
						value.append(row)
				else:
					amt += flt(row["amount"])
					value.append(row)
			elif not dhi_company_code and not is_inter_company:
				opening_dr += flt(dr)
				opening_cr += flt(cr)
				debit += flt(a.debit)
				credit += flt(a.credit)
				amount += flt(flt(a.debit) + flt(dr)) - flt( flt(a.credit) + flt(cr)) if coa.root_type in ['Asset','Expense'] else flt(flt(a.credit) + flt(cr)) - flt( flt(a.debit) + flt(dr))
	if debit or credit or amount:
		amt += flt(amount)
		value.append(create_non_inter_compay_row(opening_dr, opening_cr, coa.account,filters,credit,debit,amount))
	return value, amt, opening_dr, opening_cr, debit, credit


def get_coa(gcoa_account_name):
	return frappe.db.sql('''
						 SELECT account, account_type,
						   root_type, doc_company
						FROM `tabDHI Mapper Item`
						WHERE parent = '{}'
						 '''.format(gcoa_account_name),as_dict = True)

# fetch opening bal
def get_opening_balance(query):
	opening_bal = frappe.db.sql(query,as_dict= True)
	if not opening_bal:
		return 0, 0
	
	credit, debit = opening_bal[0].opening_credit, opening_bal[0].opening_debit
	
	if flt(debit) > flt(credit):
		debit = flt(debit) - flt(credit)
		credit = 0
	elif flt(credit) > flt(debit):
		credit = flt(credit) - flt(debit)
		debit = 0
	elif flt(debit) == flt(credit):
		credit = debit = 0
	return debit, credit

def create_non_inter_compay_row(opening_debit, opening_credit,account_name,filters,credit,debit,amount) :
	doc = frappe.get_doc('DHI Setting')
	row = {}
	row = {
			'opening_debit':opening_debit,
			'opening_credit':opening_credit,
			'account':account_name,
			'entity':doc.entity,
			'segment':doc.segment,
			'flow':doc.flow,
			'interco':doc.interco,
			'time':str(filters['from_date']) + ' to ' + str(filters['to_date']),
			'debit':debit,
			'credit':credit,
			'amount':amount
			}
	return row


def cerate_inter_compay_row(opening_debit, opening_credit, account_name, root_type,company_code,filters,data=None) :
	doc = frappe.get_doc('DHI Setting')
	row = {}
	row = {
			'opening_debit':opening_debit,
			'opening_credit':opening_credit,
			'account':account_name,
			'entity':doc.entity,
			'segment':doc.segment,
			'flow':doc.flow,
			'interco':'I_'+str(company_code),
			'time':str(filters['from_date']) + ' to '+str(filters['to_date']),
			'debit': data.debit,
			'credit': data.credit,
			'amount': flt(flt(data.debit) + flt(opening_debit)) - flt(flt(data.credit) + flt(opening_credit)) if root_type in ['Asset','Expense'] else flt(flt(data.credit) + flt(opening_credit)) - flt(flt(data.debit) + flt(opening_debit))
	}
	return row

def create_transaction():
	filters = {}
	filters['from_date'] = getdate(frappe.defaults.get_user_default("year_start_date"))
	filters['to_date'] = nowdate()
	filters['is_inter_company'] = ''
	doc = frappe.new_doc('Consolidation Transaction')
	doc.from_date = filters['from_date']
	doc.to_date = filters['to_date']
	doc.set('items',[])
 
	for d in frappe.db.sql('''
				SELECT account_name, account_code, is_inter_company
				FROM `tabDHI GCOA Mapper`
				''',as_dict=True):
		filters['gcoa_name'] = d.account_name
		data = get_data(filters,False)
		if not d.is_inter_company and data:
			row1 = data[len(data)-1]
			if row1['amount']:
				row = doc.append('items',{})
				row.account = d.account_name
				row.account_code= d.account_code
				row.amount = row1['amount']
				row.opening_dr = row1['opening_debit']
				row.opening_cr = row1['opening_credit']
				row.debit = row1['debit']
				row.credit = row1['credit']
				row.entity = row1['entity']
				row.segment = row1['segment']
				row.flow = row1['flow']
				row.interco = row1['interco']
				row.time = row1['time']
		else:
			for a in data:
				if a['amount']:
					row = doc.append('items',{})
					row.account = d.account_name
					row.account_code = d.account_code
					row.amount = a['amount']
					row.opening_dr = a['opening_debit']
					row.opening_cr = a['opening_credit']
					row.debit = a['debit']
					row.credit = a['credit']
					row.entity = a['entity']
					row.segment = a['segment']
					row.flow = a['flow']
					row.interco = a['interco']
					row.time = a['time']
	doc.save(ignore_permissions=True)
	doc.submit()
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
			"fieldname":"opening_debit",
			"label":"Opening(Dr)",
			"fieldtype":"Float",
			"width":100
		},
		{
			"fieldname":"opening_credit",
			"label":"Opening(Cr)",
			"fieldtype":"Float",
			"width":100
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
