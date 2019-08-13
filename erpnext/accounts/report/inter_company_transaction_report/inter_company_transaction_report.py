# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, msgprint
from frappe.utils import flt
from frappe.utils import formatdate
from operator import itemgetter, attrgetter

def execute(filters=None):
	if not filters: filters = {}

	columns = get_columns(filters)
	data = get_data(filters)

	return columns, data


def get_columns(filters):
	columns = [_("Reference") + ":Data:100", _("Reference No") + ":Dynamic Link/"+_("Reference")+":100", 
	_("Sales Inv. No.") + ":Data:100", _("Sales Inv. Date") + ":Date:100", _("Sales Amount") + ":Currency:90", _("Received") + ":Currency:90", _("Receivable") + ":Currency:90", 
	_("Payment Inv. No") + ":Data:100", _("Inv. Date") + ":Date:100", _("Payment Amount") + ":Currency:90", _("Paid") + ":Currency:90", _("Payable") + ":Currency:90",
	_("Advance Received") + ":Currency:90", _("Rec. Adjusted") + ":Currency:90", _("Rec. Balance") + ":Currency:90",
	_("Advance Paid") + ":Currency:90", _("Pay. Adjusted") + ":Currency:90", _("Pay. Balance") + ":Currency:90"]
	return columns

def get_data(filters):
	record = []
	data = []

	if filters.get("party"):
		sql1 = "SELECT  name, invoice_no, invoice_date, posting_date, amount, is_advance, payment_type \
		FROM `tabDirect Payment` where posting_date between \'" + str(filters.start_date) + "\' \
		and \'" + str(filters.end_date) + "\' and  party =  \'" + str(filters.party) + "\' \
		and docstatus = '1'"
	#	frappe.msgprint("{0}".format(sql1))
		if filters.get("branch"):
			sql1 += " and branch = \'" + str(filters.branch) + "\'"

		query1 = frappe.db.sql(sql1,as_dict = 1)
		
		for rev in query1:
			if rev.is_advance == 1:
				if rev.payment_type == "Payment":
					row = ['Direct Payment',rev.name,'','','','','', rev.invoice_no, rev.invoice_date, '', '','', '', '','', rev.amount, rev.amount, 0,rev.posting_date]
				elif rev.payment_type == "Receive":
					row = ['Direct Payment',rev.name, rev.invoice_no, rev.invoice_date, '', '', '', '', '','',0,0, rev.amount,'','','','','',rev.posting_date]
			else:
				if rev.payment_type == "Payment":
					row = ['Direct Payment', rev.name, '','','','','', rev.invoice_no, rev.inovice_date, rev.amount, rev.amount,0,'','','','','','',rev.posting_date]
				elif rev.payment_type == "Receive":
					row = ['Direct Payment',rev.name, rev.invoice_no, rev.invoice_date, rev.amount, rev.amount, 0, '','','','','','','','','','','',rev.posting_date]
			record.append(row)

		sql2 = "SELECT name, bill_no, posting_date, grand_total, outstanding_amount FROM `tabPurchase Invoice` \
		WHERE supplier = \'" + str(filters.party) + "\' and \
		posting_date BETWEEN \'" + str(filters.start_date) + "\' and \'" + str(filters.end_date) + "\' \
		and docstatus = '1'"
		
		if filters.get("branch"):
			sql2 += " and branch = \'" + str(filters.branch) + "\'"

		query2 = frappe.db.sql(sql2,as_dict = 1)

		for dtl in query2:
			if dtl.outstanding_amount > 0:
				paid_amt = flt(dtl.grand_total) - flt(dtl.outstanding_amount)
				row = ['Purchase Invoice', dtl.name,'','','','','', dtl.bill_no, dtl.posting_date, dtl.grand_total, paid_amt, dtl.outstanding_amount, '', '','','', '','', dtl.posting_date]
			else:
				row = ['Purchase Invoice',dtl.name,'','','','','', dtl.bill_no, dtl.posting_date, dtl.grand_total, dtl.grand_total, 0,'','','','','','',dtl.posting_date]
			record.append(row)


		sql3 = "SELECT name, posting_date, grand_total, outstanding_amount \
		FROM `tabSales Invoice` WHERE  docstatus = '1' and customer = \'" + str(filters.party) + "\' \
		and posting_date BETWEEN \'" + str(filters.start_date) + "\' and \'" + str(filters.end_date) + "\'"
		if filters.get("branch"):
			sql3 += " and branch = \'" + str(filters.branch) + "\'"

		query3 = frappe.db.sql(sql3,as_dict=1)

		for dt in query3:
			if dt.outstanding_amount > 0:
				received_amt = flt(dt.grand_total) - flt(dt.outstanding_amount)
				row = ['Sales Invoice',dt.name, dt.name, dt.posting_date, dt.grand_total, received_amt, dt.outstanding_amount, '','','','','','', '', '','','', '',dt.posting_date,]
			else:
				row = ['Sales Invoice',dt.name, dt.name, dt.posting_date, dt.grand_total, dt.grand_total, 0, '','','','','','', '', '','','', '',dt.posting_date,]
			record.append(row)

		sql4 = "SELECT name, posting_date, total_invoice_amount, advance_amount, outstanding_amount \
		FROM `tabHire Charge Invoice` WHERE docstatus = '1' and customer = \'" + str(filters.party) + "\' \
		and posting_date BETWEEN \'" + str(filters.start_date) + "\' and \'" + str(filters.end_date) + "\'"

		if filters.get("branch"):
			sql4 += " and branch = \'" + str(filters.branch) + "\'"

		query4 = frappe.db.sql(sql4, as_dict=1)

		for dl in query4:
			if dl.outstanding_amount > 0:
				received_amt = flt(dl.total_invoice_amount) - flt(dl.outstanding_amount)
				row = ['Hire Charge Invoice',dl.name, dl.name, dl.posting_date, dl.total_invoice_amount, received_amt, dl.outstanding_amount, '','','','','','', '', '','','', '',dl.posting_date]
			else:
				row = ['Hire Charge Invoice',dl.name, dl.name, dl.posting_date, dl.total_invoice_amount, dl.total_invoice_amount, 0, '','','','','','', '', '','','', '',dl.posting_date]
			record.append(row)

		sql5 = "SELECT name, invoice_date, gross_invoice_amount, total_received_amount, total_balance_amount \
			FROM `tabProject Invoice` WHERE docstatus = '1' and customer = \'" + str(filters.party) + "\' \
			and invoice_date BETWEEN \'" + str(filters.start_date) + "\' and \'" + str(filters.end_date) + "\'"

		if filters.get("branch"):
			sql5 += " and branch = \'" + str(filters.branch) + "\'"

		query5 = frappe.db.sql(sql5, as_dict=1)
		
		for pd in query5:
			if pd.total_balance_amount > 0 :
				row = ['Project Invoice',pd.name, pd.name, pd.invoice_date, pd.gross_invoice_amount, pd.total_received_amount, pd.total_balance_amount, '','','','','','', '', '','','', '',pd.invoice_date]
			else:
				row = ['Project Invoice',pd.name, pd.name, pd.invoice_date, pd.gross_invoice_amount, pd.gross_invoice_amount, 0, '','','','','','', '', '','','', '',pd.invoice_date]
			record.append(row)

		sql6 = "SELECT name, posting_date, total_amount, outstanding_amount \
		FROM `tabJob Card` WHERE docstatus = '1' and customer = \'" + str(filters.party) + "\' \
		and posting_date BETWEEN \'" + str(filters.start_date) + "\' and \'" + str(filters.end_date) + "\'"

		if filters.get("branch"):
			sql5 += " and branch = \'" + str(filters.branch) + "\'"

		query6 = frappe.db.sql(sql6, as_dict=1)

		for jd in query6:
			if jd.outstanding_amount > 0:
				received_amt = flt(jd.total_amount) - flt(jd.outstanding_amount)
				row = ['Job Card',jd.name, jd.name, jd.posting_date, jd.total_amount, received_amt, jd.outstanding_amount, '','','','','','', '', '','','', '',jd.posting_date]
			else:
				row = ['Job Card',jd.name, jd.name, jd.posting_date, jd.total_amount, jd.total_amount, 0, '','','','','','', '', '','','', '',jd.posting_date]
			record.append(row)

	record = sorted(record, key=itemgetter(18))

	return record
