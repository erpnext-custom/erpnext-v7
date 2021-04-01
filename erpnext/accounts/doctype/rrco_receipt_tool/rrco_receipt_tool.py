# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class RRCOReceiptTool(Document):
	def validate(self):		
		self.get_invoices()
		self.validate_data()

	def validate_data(self):
		if self.purpose == "Employee Salary":
			if not self.fiscal_year and not self.month:
				frappe.throw("Fiscal Year and Month values are missing")
			else:
				if frappe.db.exists("RRCO Receipt Entries", {"fiscal_year":self.fiscal_year, "month": self.month}):
					frappe.throw("RRCO Receipt and date has been already assigned for the given month {} and fiscal year {}".format(self.month, self.fiscal_year))

		elif self.purpose in ["PBVA","Annual Bonus"]:
			if not self.fiscal_year:
				frappe.throw("Fiscal Year value is missing")

			if frappe.db.exists("RRCO Receipt Entries", {"fiscal_year":self.fiscal_year, "purpose": self.purpose}):
				frappe.throw("RRCO Receipt and date has been already assigned for {} and fiscal year {}".format(self.purpose, self.fiscal_year))
	
	def on_submit(self):
		self.rrco_receipt_entry()

	def on_cancel(self):
		if frappe.db.exists("RRCO Receipt Entries", {"rrco_receipt_tool": self.name}):
			frappe.db.sql("delete from `tabRRCO Receipt Entries` where rrco_receipt_tool = '{}'".format(self.name))
		else:
			frappe.msgprint("No RRCO Receipt Entries found for this record")

	def rrco_receipt_entry(self):
		if self.purpose in ["Leave Encashment", "Purchase Invoices"]:
			if self.item:
				for a in self.item:
					single_party = 0
					if a.transaction == "Direct Payment":
						single_party, party = frappe.db.get_value("Direct Payment", a.invoice_no, ["single_party_multiple_payments", "party"])
						bill_no = a.invoice_no
					else:
						employee, employee_name = frappe.db.get_value("Leave Encashment", a.invoice_no, ["employee","employee_name"])
						bill_no = str(employee_name + "(" + a.invoice_no + ")")
						party = employee

					if a.transaction == "Direct Payment" and not single_party:
						for b in frappe.db.sql("select party_type, party from `tabDirect Payment Item` where parent = '{}'".format(a.invoice_no), as_dict=True):
							rrco = frappe.new_doc("RRCO Receipt Entries")
							rrco.purpose = str(self.purpose)
							rrco.supplier = b.party
							rrco.bill_no = a.invoice_no
							rrco.purchase_invoice = a.invoice_no
							rrco.receipt_date = self.tds_receipt_date
							rrco.receipt_number = self.tds_receipt_number
							rrco.cheque_number = self.cheque_number
							rrco.cheque_date = self.cheque_date
							rrco.branch = self.branch
							rrco.rrco_receipt_tool = self.name
							rrco.submit()
					else:
						rrco = frappe.new_doc("RRCO Receipt Entries")
						rrco.purpose = str(self.purpose)
						rrco.supplier = party
						rrco.bill_no = bill_no
						rrco.purchase_invoice = a.invoice_no
						rrco.receipt_date = self.tds_receipt_date
						rrco.receipt_number = self.tds_receipt_number
						rrco.cheque_number = self.cheque_number
						rrco.cheque_date = self.cheque_date
						rrco.branch = self.branch
						rrco.rrco_receipt_tool = self.name
						rrco.submit()
						
		elif self.purpose in ["Employee Salary","PBVA","Annual Bonus"]:
			rrco = frappe.new_doc("RRCO Receipt Entries")
			rrco.purpose = str(self.purpose)
			rrco.fiscal_year = str(self.fiscal_year)
			rrco.receipt_date = self.tds_receipt_date
			rrco.receipt_number = str(self.tds_receipt_number)
			rrco.cheque_number = str(self.cheque_number)
			rrco.cheque_date = self.cheque_date
			rrco.rrco_receipt_tool = self.name

			if self.purpose == "Employee Salary":
				rrco.month = str(self.month)
			rrco.submit()
	
	def get_invoices(self):
		if self.purpose in ["Leave Encashment", "Purchase Invoices"]:
			if not self.branch and not self.tds_rate and not self.from_date and not self.to_date:
				frappe.throw("Select the details to retrieve the invoices")

			if self.purpose == 'Leave Encashment':
				query = """select  "Leave Encashment" as transaction, name, application_date as posting_date, encashment_amount as invoice_amount, tax_amount
						FROM `tabLeave Encashment` AS a WHERE a.docstatus = 1 
						AND a.application_date BETWEEN '{0}' AND '{1}' 
						AND a.branch ='{2}' 
						AND NOT EXISTS (SELECT 1 
									FROM `tabRRCO Receipt Entries` AS b 
									WHERE b.purchase_invoice = a.name)
						""".format(self.from_date, self.to_date, self.branch)
			else:
				query = """select "Purchase Invoice" as transaction, name, posting_date, total as invoice_amount, total_taxes_and_charges  as tax_amount
						FROM `tabPurchase Invoice` AS a 
						WHERE docstatus = 1 AND posting_date BETWEEN '{0}' AND '{1}' 
						AND tds_rate = '{2}' 
						AND a.branch = '{3}' 
						AND NOT EXISTS (SELECT 1 
										FROM `tabRRCO Receipt Entries` AS b 
										WHERE b.purchase_invoice = a.name) 
						UNION 
						select "Direct Payment" as transaction, name, posting_date, amount as invoice_amount, tds_amount as tax_amount
						FROM `tabDirect Payment` AS a 
						WHERE docstatus = 1 
						AND posting_date BETWEEN '{0}' AND '{1}'
						AND tds_percent = '{2}' 
						AND a.branch = '{3}' 
						AND NOT EXISTS (SELECT 1 
										FROM `tabRRCO Receipt Entries` AS b 
										WHERE b.purchase_invoice = a.name)
						""".format(self.from_date, self.to_date, self.tds_rate, self.branch)

			self.set('item', [])
			for a in frappe.db.sql(query, as_dict=True):
				row = self.append('item', {})
				d = {'transaction': a.transaction, 'invoice_no': a.name, 'invoice_date': a.posting_date, 'invoice_amount': a.invoice_amount, 'tax_amount': a.tax_amount}
				row.update(d)
		else:
			if self.item:
				to_remove= []
				for d in self.item:
					to_remove.append(d)
				[self.remove(d) for d in to_remove]