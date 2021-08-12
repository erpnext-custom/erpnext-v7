# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = get_columns(filters), get_data(filters)
	return columns, data

def get_data(filters):
	cond = get_condidion(filters)
	if filters.show_aggregate:
		return frappe.db.sql("""
			SELECT `group`,coal_raising_type,tire,
				sum(no_of_labours) as no_of_labours,
				sum(product_qty) as product_qty,
				sum(machine_hours) as machine_hours,
				sum(amount) as amount,
				sum(machine_payable) as machine_payable,
				sum(grand_amount) as grand_amount,
				sum(penalty_amount) as penalty_amount
			FROM `tabProduction` 
			WHERE docstatus = 1
			AND branch = '{}' 
			AND posting_date between '{}'
			AND '{}'
			{} 
			AND (tire = '' OR tire is not null) 
			AND (coal_raising_type != '' or coal_raising_type is not null)
			group by `group`, coal_raising_type
		""".format(filters.branch,filters.from_date,filters.to_date,cond),as_dict=1)

	return frappe.db.sql("""
		SELECT 
			name as reference,posting_date,coal_raising_type, 
			`group`,tire, no_of_labours,machine_hours,
			product_qty,amount,machine_payable,
			grand_amount, penalty_amount
		FROM `tabProduction`
		WHERE docstatus = 1
		AND branch = '{}' 
		AND posting_date between '{}'
		AND '{}'
		{}
		""".format(filters.branch,filters.from_date,filters.to_date,cond),as_dict=1)

def get_condidion(filters=None):
	cond = ''
	if filters.from_date > filters.to_date:
		frappe.throw('From Date cannot be after To Date')
	if filters.coal_raising_type:
		cond += " AND coal_raising_type ='{}'".format(filters.coal_raising_type)
	if filters.group:
		cond += " AND `group` ='{}' ".format(filters.group)
	if filters.tire:
		cond += " AND tire = '{}' ".format(filters.tire)
	return cond

def get_columns(filters):
	col = []
	if not filters.show_aggregate:
		col += [
		{
			'fieldname':'reference',
			'fieldtype':'Link',
			'label':'Reference',
			'options':'Production',
			'width':110
		},
		{
			'fieldname':'posting_date',
			'fieldtype':'Date',
			'label':'Posting Date',
			'width':100
		}]

	col += [
		{
			'fieldname':'coal_raising_type',
			'fieldtype':'Data',
			'label':'Coal Raising Type',
			'width':120
		},
		{
			'fieldname':'group',
			'fieldtype':'Link',
			'label':'Group',
			'options':'Departmental Group',
			'width':140
		},
		{
			'fieldname':'tire',
			'fieldtype':'Link',
			'label':'Tire',
			'options':'Tire',
			'width':120
		},
		{
			'fieldname':'no_of_labours',
			'fieldtype':'Float',
			'label':'No. Labours',
			'width':90
		},
		{
			'fieldname':'machine_hours',
			'fieldtype':'Float',
			'label':'Machine Hrs',
			'width':90
		},
		{
			'fieldname':'machine_payable',
			'fieldtype':'Currency',
			'label':'Machine Payable',
			'width':110
		},
		{
			'fieldname':'product_qty',
			'fieldtype':'Float',
			'label':'Quantity',
			'width':90
		},
		{
			'fieldname':'grand_amount',
			'fieldtype':'Currency',
			'label':'Grand Amount',
			'width':120
		},
		{
			'fieldname':'penalty_amount',
			'fieldtype':'Currency',
			'label':'Penalty Amount',
			'width':120
		},
		{
			'fieldname':'amount',
			'fieldtype':'Currency',
			'label':'Net Amount',
			'width':120
		},
	]
	return col