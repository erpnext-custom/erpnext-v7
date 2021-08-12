// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Coal Raising Report"] = {
	"filters": [
		{
			'fieldname':'branch',
			'fieldtype':'Link',
			'label':__('Branch'),
			'options':'Branch',
			'reqd':1
		},
		{
			'fieldname':'from_date',
			'fieldtype':'Date',
			'label':__('From Date'),
			'default':frappe.datetime.month_start(),
			'reqd':1
		},
		{
			'fieldname':'to_date',
			'fieldtype':'Date',
			'label':__('To Date'),
			'default':frappe.datetime.month_end(),
			'reqd':1
		},
		{
			'fieldname':'coal_raising_type',
			'fieldtype':'Select',
			'label':__('Coal Raising Type'),
			'options':['','Manual','Machine Sharing','SMCL Machine'],
		},
		{
			'fieldname':'group',
			'fieldtype':'Link',
			'label':__('Group'),
			'options':'Departmental Group'
		},
		{
			'fieldname':'tire',
			'fieldtype':'Link',
			'label':__('Tire'),
			'options':'Tire'
		},
		{
			'fieldname':'show_aggregate',
			'fieldtype':'Check',
			'label':__('Show Aggregate Data')
		}
	]
}
