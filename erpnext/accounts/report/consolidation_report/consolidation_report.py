# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt

def execute(filters=None):
	filter = {}
	# filter['from_date'] = filters.from_date
	# filter['to_date'] = filters.to_date
	filter['is_inter_company'] = filters.is_inter_company
	columns, data = get_columns(), get_value(filter,'No')
	return columns, data

def get_value(filters,from_rest_api=None):
    cond = ''
    if filters['is_inter_company'] == 'Yes':
        cond += ' and interco != "I_NONE"'
    d = frappe.db.sql('''
                      select name 
						from `tabConsolidation Transaction` 
						order by to_date desc, creation desc limit 1;
                      ''',as_dict=True)
    if not d:
        return
    parent_name = d[0].name
    query = '''
				SELECT
				account_code, account,
				entity, segment, flow,
				interco, time, opening_dr, 
				opening_cr,debit, credit,
				amount
				FROM `tabConsolidation Transaction Item` where parent = '{}'
				{}
				'''.format(parent_name,cond)
    if from_rest_api == 'Yes': 
    	return frappe.db.sql(query,as_dict=1) 
    elif from_rest_api == 'No':
    	return frappe.db.sql(query)
def get_data(filters):
	# return filters
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
			val, c, de, amt, o_dr, o_cr = payable_receivable_amount(gcoa,d,filters)
			data += val
		elif not d.doc_company:
			val, cr, de, amt, o_dr, o_cr = other_expense_amount(gcoa,d,filters)
			data += val
		
	data1 = merge_duplicate(data)
	return data1

def non_inter_company(gcoa,filters):
	data, credit, debit, amount, opening_dr, opening_cr = [], 0, 0, 0, 0, 0
	for d in get_coa(gcoa.account_name):
		c, de, a, o_cr, o_dr = 0, 0, 0, 0, 0
		if d.account_type in ['Payable','Receivable'] and not d.doc_company:
			val, c, de, a, o_dr, o_cr = payable_receivable_amount(gcoa,d,filters)
   
		elif not d.doc_company:
			val, c, de, a, o_dr, o_cr = other_expense_amount(gcoa,d,filters)
		credit += flt(c)
		debit += flt(de)
		amount += flt(a)
		opening_cr += flt(o_cr)
		opening_dr += flt(o_dr)

	if credit or debit or amount:
		data.append(create_non_inter_compay_row(opening_dr, opening_cr, gcoa.account_code, gcoa.account_name, filters, credit, debit, amount))
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
					new_data[i]["opening_debit"] += flt(d["opening_debit"])
					new_data[i]["opening_credit"] += flt(d["opening_credit"])
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

# for Purchase invoice where tempoary gl is booked
def other_expense_amount(gcoa,coa,filters):
	value, debit, credit, amount, opening_dr, opening_cr = [], 0, 0, 0, 0, 0

	for a in frappe.db.sql("""
			select sum(credit) as credit, sum(debit) as debit, 
			consolidation_party_type as party_type,
			consolidation_party as party
			from `tabGL Entry` where posting_date between '{0}' and '{1}' 
			and (exact_expense_acc = '{2}' or account = '{2}') 
			and (credit is not null or debit is not null) 
			and voucher_type not in ('Stock Entry','Purchase Receipt','Stock Reconciliation','Issue POL','Asset Movement','Bulk Asset Transfer','Equipment POL Transfer')
			group by consolidation_party
			""".format(filters['from_date'],filters['to_date'],coa.account),as_dict=True):
		if (a.credit or a.debit) :
			dhi_company_code, cond, dr, cr = '', '', 0, 0
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
	
			if a.party_type == 'Supplier':
				dhi_company_code = frappe.db.get_value('Supplier',{'name':a.party,'inter_company':1,'disabled':0},['company_code'])
			else:
				dhi_company_code = frappe.db.get_value('Customer',{'name':a.party,'inter_company':1,'disabled':0},['company_code'])
	
			if dhi_company_code and gcoa.is_inter_company :
				row = {}
				row = cerate_inter_compay_row(dr, cr, gcoa.account_code, gcoa.account_name, coa.root_type, dhi_company_code, filters, a)
				value.append(row)
			elif not dhi_company_code and not gcoa.is_inter_company :
				opening_dr += flt(dr)
				opening_cr += flt(cr)
				debit += flt(a.debit)
				credit += flt(a.credit)
				amount += flt(flt(a.debit) + flt(dr)) - flt(flt(a.credit)+flt(cr)) if coa.root_type in ['Asset','Expense'] else flt(flt(a.credit)+flt(cr)) - flt(flt(a.debit) + flt(dr))
	
	if gcoa.is_inter_company:
		return value, 0, 0, 0, 0, 0
	else:
		return [], credit, debit, amount, opening_dr, opening_cr

# for gl selected for particular doc company
def get_doc_company_amount(gcoa,coa,filters):
	value, debit, credit, amount, opening_dr, opening_cr = [], 0, 0, 0, 0, 0

	for a in frappe.db.sql("""
			select sum(credit) as credit, sum(debit) as debit
			from `tabGL Entry` where posting_date between '{0}' and '{1}' 
			and (account = '{2}' or exact_expense_acc = '{2}') 
			and (credit is not null or debit is not null)
			and voucher_type not in ('Stock Entry','Purchase Receipt','Stock Reconciliation','Issue POL','Asset Movement','Bulk Asset Transfer','Equipment POL Transfer')
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
			'account':gcoa.account_name,
			'account_code':gcoa.account_code,
			'entity':doc.entity,
			'segment':doc.segment,
			'flow':doc.flow,
			'interco':'I_'+coa.doc_company,
			'time':str(filters['from_date']) + ' to '+ str(filters['to_date']),
			'debit':debit,
			'credit':credit,
			'amount': amount
		})
	return value

# applicable for payable and Receivable
def payable_receivable_amount(gcoa,coa,filters):
	value = []
	query = ''
	debit = credit = amount = opening_dr = opening_cr = 0

	query = """
			select sum(gl.credit) as credit,sum(gl.debit) as debit, gl.party,gl.party_type
			from `tabGL Entry` as gl where gl.posting_date between '{0}' and '{1}' 
			and gl.account = '{2}' 
			and (gl.party is not null and gl.party != '')
			and (gl.credit is not null or gl.debit is not null) 
			and voucher_type not in ('Stock Entry','Purchase Receipt','Stock Reconciliation','Issue POL','Asset Movement','Bulk Asset Transfer','Equipment POL Transfer')
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
			if gcoa.is_inter_company:
				if a.party_type == 'Supplier':
					dhi_company_code = frappe.db.get_value('Supplier',{'name':a.party,'inter_company':1,'disabled':0},['company_code'])
				else:
					dhi_company_code = frappe.db.get_value('Customer',{'name':a.party,'inter_company':1,'disabled':0},['company_code'])
			if dhi_company_code and gcoa.is_inter_company:
				row = {}
				row = cerate_inter_compay_row(dr, cr, gcoa.account_code, gcoa.account_name, coa.root_type, dhi_company_code, filters, a)
				value.append(row)
			elif not dhi_company_code and not gcoa.is_inter_company:
				opening_dr += flt(dr)
				opening_cr += flt(cr)
				debit += flt(a.debit)
				credit += flt(a.credit)
				amount += flt(flt(a.debit) + flt(dr)) - flt( flt(a.credit) + flt(cr)) if coa.root_type in ['Asset','Expense'] else flt(flt(a.credit) + flt(cr)) - flt( flt(a.debit) + flt(dr))

	if gcoa.is_inter_company:
		return value, 0, 0, 0, 0, 0
	else:
		return [], credit, debit, amount, opening_dr, opening_cr

def create_non_inter_compay_row(opening_debit, opening_credit, account_code, account_name, filters, credit, debit,amount) :
	doc = frappe.get_doc('DHI Setting')
	row = {}
	row = {
			'opening_debit':opening_debit,
			'opening_credit':opening_credit,
			'account_code':account_code,
			'account':account_name,
			'entity':doc.entity,
			'segment':doc.segment,
			'flow':doc.flow,
			'interco':doc.interco,
			'time':str(filters['from_date']) + ' to '+ str(filters['to_date']),
			'debit':debit,
			'credit':credit,
			'amount':amount
			}
	return row


def cerate_inter_compay_row(opening_debit,opening_credit, account_code,account_name,root_type,company_code,filters,data=None) :
	# frappe.msgprint(str(data))
	doc = frappe.get_doc('DHI Setting')
	row = {}
	row = {
			'opening_debit':opening_debit,
			'opening_credit':opening_credit,
			'account_code':account_code,
			'account':account_name,
			'entity':doc.entity,
			'segment':doc.segment,
			'flow':doc.flow,
			'interco':'I_'+str(company_code),
			'time':str(filters['from_date']) + ' to '+ str(filters['to_date']),
			'debit':data.debit,
			'credit':data.credit,
			'amount': flt(flt(data.debit) + flt(opening_debit)) - flt(flt(data.credit)+flt(opening_credit)) if root_type in ['Asset','Expense'] else flt(flt(data.credit)+flt(opening_credit)) - flt(flt(data.debit)+flt(opening_debit))
	}
	return row
def create_transaction(filters=None,data = None):
	total = 0
	if not data:
		data = get_data(filters)
		
	doc = frappe.new_doc('Consolidation Transaction')
	doc.from_date = filters['from_date']
	doc.to_date = filters['to_date']
	doc.set('items',[])
	for d in data:
		total += flt(d['amount'])
		row = doc.append('items',{})
		row.update(d)
	doc.save(ignore_permissions=True)
	doc.submit()

		

def get_columns():
	return [
		{
			"fieldname":"account_code",
			"label":"Account Code",
			"fieldtype":"Data",
			"width":100
		},
		{
			"fieldname":"account",
			"label":"Account",
			"fieldtype":"Link",
			"options":"DHI GCOA Mapper",
			"width":200
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
			"fieldtype":"Currency",
			"width":150
		},
		{
			"fieldname":"opening_credit",
			"label":"Opening(Cr)",
			"fieldtype":"Currency",
			"width":150
		},
		{
			"fieldname":"debit",
			"label":"Debit",
			"fieldtype":"Currency",
			"width":150
		},
		{
			"fieldname":"credit",
			"label":"Credit",
			"fieldtype":"Currency",
			"width":150
		},
		{
			"fieldname":"amount",
			"label":"Amount",
			"fieldtype":"Currency",
			"width":150
		},
	]

