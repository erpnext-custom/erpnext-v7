# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = get_columns(filters), get_data(filters)
	return columns, data

def get_data(filters):
	validate_filters(filters)
	cond = get_conditions(filters)

	return frappe.db.sql("""select dn.posting_date, "Delivery Note" voucher_type,
				dn.name as voucher_no, dpe.ledger_posted_on, ifnull(dpe.status,'Pending') status
			from `tabDelivery Note` dn
			left join `tabDeferred Posting Entry` dpe on dpe.voucher_no = dn.name
			where dn.posting_date between '{from_date}' and '{to_date}'
			and dn.docstatus = 1
			and (
				exists(select 1 from `tabDeferred Posting Entry` dpe2
					where dpe2.voucher_no = dn.name {cond})
				or
				not exists(select 1 from `tabStock Ledger Entry` sle
				where sle.voucher_type = "Delivery Note"
				and sle.voucher_no = dn.name)
			)
		""".format(from_date=filters.from_date, to_date=filters.to_date, cond=cond))

def validate_filters(filters):
	if filters.to_date < filters.from_date:
		frappe.throw(_("<b>From Date</b> should be earlier to <b>To Date</b>"))

def get_conditions(filters):
	cond = ""
	if filters.status:
		cond = "and dpe2.status = '{}'".format(filters.status)
	return cond

def get_columns(filters):
	return [
		{
			"fieldname": "posting_date",
			"label": "Posting Date",
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "voucher_type",
			"label": "Voucher Type",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "voucher_no",
			"label": "Voucher No",
			"fieldtype": "Dynamic Link",
			"options": "voucher_type",
			"width": 150
		},
		{
			"fieldname": "ledger_posted_on",
			"label": "Last Tried On",
			"fieldtype": "Date",
			"width": 150
		},
		{
			"fieldname": "status",
			"label": "Posting Status",
			"fieldtype": "Data",
			"width": 100
		}
	]