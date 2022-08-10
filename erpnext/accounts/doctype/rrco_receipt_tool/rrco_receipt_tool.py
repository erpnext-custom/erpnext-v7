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
		if not self.item and self.purpose == "Purchase Invoices":
			frappe.throw("Atleast one invoice is required to submit this document")
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
					bill_no = ""
					if a.transaction == "Direct Payment":
						bill_no = a.invoice_no
					elif a.transaction == "Leave Encashment":
						employee, employee_name = frappe.db.get_value("Leave Encashment", a.invoice_no, ["employee","employee_name"])
						bill_no = str(employee_name + "(" + a.invoice_no + ")")
					elif a.transaction == "Purchase Invoice":
						bill_no = a.invoice_no

					rrco = frappe.new_doc("RRCO Receipt Entries")
					rrco.purpose = str(self.purpose)
					rrco.supplier = a.party
					rrco.bill_no = bill_no
					rrco.purchase_invoice = a.invoice_no
					rrco.receipt_date = self.tds_receipt_date
					rrco.receipt_number = self.tds_receipt_number
					rrco.cheque_number = self.cheque_number
					rrco.cheque_date = self.cheque_date
					rrco.branch = self.branch
					rrco.rrco_receipt_tool = self.name
					rrco.flags.ignore_permissions = True
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
			rrco.flags.ignore_permissions = True
			rrco.submit()
	
	def get_invoices(self):
		if self.purpose in ["Leave Encashment", "Purchase Invoices","PBVA"]:
			# if not self.branch and not self.tds_rate and not self.from_date and not self.to_date:
			if not self.tds_rate and not self.from_date and not self.to_date:
				frappe.throw("Select the details to retrieve the invoices")
			cond = ''
			cond1 = ''
			if self.branch:
				cond += " AND d.branch = '{}'".format(self.branch)
				cond1 += " AND p.branch = '{}'".format(self.branch)
				cond2 += " AND a.branch = '{}'".format(self.branch)

			if self.purpose == 'Leave Encashment':
				query = """select  "Leave Encashment" as transaction, name, application_date as posting_date, 
    					encashment_amount as invoice_amount, tax_amount, employee as party
						FROM `tabLeave Encashment` AS a WHERE a.docstatus = 1 
						AND a.application_date BETWEEN '{0}' AND '{1}' 
						{2} 
						AND NOT EXISTS (SELECT 1 
									FROM `tabRRCO Receipt Entries` AS b 
									WHERE b.purchase_invoice = a.name)
						AND tax_amount > 0
						""".format(self.from_date, self.to_date, cond2)
			elif self.purpose == 'PBVA':
				query = """select  "PBVA" as transaction, a.name, a.posting_date as posting_date, 
    					b.amount as invoice_amount, b.tax_amount, b.employee as party
						FROM `tabPBVA` AS a, `tabPBVA Details` AS b WHERE a.docstatus = 1
						AND a.name = b.parent
						AND a.fiscal_year = '{0}'
						{1} 
						AND NOT EXISTS (SELECT 1 
									FROM `tabRRCO Receipt Entries` AS b 
									WHERE b.purchase_invoice = a.name)
						AND b.tax_amount > 0
						""".format(self.fiscal_year, cond2)
			else:
				query = """
          				select "Purchase Invoice" as transaction, name, posting_date, 
              			tds_taxable_amount as invoice_amount, tds_amount  as tax_amount, p.supplier as party
						FROM `tabPurchase Invoice` AS p
						WHERE docstatus = 1 AND posting_date BETWEEN '{0}' AND '{1}'
						AND tds_amount > 0
						AND tds_rate = '{2}' {3} 
						AND NOT EXISTS (SELECT 1 
										FROM `tabRRCO Receipt Entries` AS b 
										WHERE b.purchase_invoice = p.name) 
						AND EXISTS (
							select 1
							from `tabTDS Remittance`  as r, `tabTDS Remittance Item` ri
							where r.name = ri.parent
							and r.docstatus = 1
							and ri.invoice_no = p.name
						)
						UNION
						select "Project Invoice" as transaction, name, invoice_date, 
              			tds_taxable_amount as invoice_amount, tds_amount  as tax_amount,  party
						FROM `tabProject Invoice` AS p
						WHERE docstatus = 1 AND invoice_date BETWEEN '{0}' AND '{1}' 
						AND tds_rate = '{2}' {3}
						AND tds_amount > 0
						AND NOT EXISTS (SELECT 1 
										FROM `tabRRCO Receipt Entries` AS b 
										WHERE b.purchase_invoice = p.name) 
						AND EXISTS (
							select 1
							from `tabTDS Remittance`  as r, `tabTDS Remittance Item` ri
							where r.name = ri.parent
							and r.docstatus = 1
							and ri.invoice_no = p.name
						)
						UNION 
						select "Direct Payment" as transaction, d.name, d.posting_date, 
      					di.taxable_amount as invoice_amount, 
                        di.tds_amount as tds_amount, di.party
           				FROM `tabDirect Payment` AS d 
      					LEFT JOIN `tabDirect Payment Item` as di on di.parent = d.name
						WHERE d.docstatus = 1 
						AND d.posting_date BETWEEN '{0}' AND '{1}'
						AND d.tds_percent = '{2}'
						AND d.payment_type = "Payment"
						AND di.tds_amount > 0
						{4} 
						AND NOT EXISTS (SELECT 1 
										FROM `tabRRCO Receipt Entries` AS b 
										WHERE b.purchase_invoice = d.name and b.docstatus = 1)
						AND EXISTS (
							select 1
							from `tabTDS Remittance`  as r, `tabTDS Remittance Item` ri
							where r.name = ri.parent
							and r.docstatus = 1 
       						and ri.invoice_no = d.name
							and ri.party = di.party
						)
						UNION
						select "Mechanical Payment" as transaction, p.name, p.posting_date as invoice_date, 
              			p.payable_amount as invoice_amount, p.tds_amount as tax_amount,  p.supplier as party
						FROM `tabMechanical Payment` AS p
						WHERE p.docstatus = 1 AND p.posting_date BETWEEN '{0}' AND '{1}' 
						AND p.tds_rate = '{2}' {3}
						AND p.tds_amount > 0
						AND NOT EXISTS (SELECT 1 
										FROM `tabRRCO Receipt Entries` AS b 
										WHERE b.purchase_invoice = p.name) 
						AND EXISTS (
							select 1
							from `tabTDS Remittance`  as r, `tabTDS Remittance Item` ri
							where r.name = ri.parent
							and r.docstatus = 1
							and ri.invoice_no = p.name
						)
						UNION
						select "Technical Sanction Bill" as transaction, p.name, p.posting_date as invoice_date, 
              			p.total_amount as invoice_amount, p.tds_amount as tax_amount,  p.party as party
						FROM `tabTechnical Sanction Bill` AS p
						WHERE p.docstatus = 1 AND p.posting_date BETWEEN '{0}' AND '{1}' 
						AND p.tds_percent = '{2}' {3}
						AND p.tds_amount > 0
						AND NOT EXISTS (SELECT 1 
										FROM `tabRRCO Receipt Entries` AS b 
										WHERE b.purchase_invoice = p.name) 
						AND EXISTS (
							select 1
							from `tabTDS Remittance`  as r, `tabTDS Remittance Item` ri
							where r.name = ri.parent
							and r.docstatus = 1
							and ri.invoice_no = p.name
						)
						""".format(self.from_date, self.to_date, self.tds_rate, cond1, cond)

			self.set('item', [])
			for a in frappe.db.sql(query, as_dict=True):
				row = self.append('item', {})
				d = {'transaction': a.transaction, 'invoice_no': a.name, 'invoice_date': a.posting_date, 'invoice_amount': a.invoice_amount, 'tax_amount': a.tax_amount, 'party': a.party}
				row.update(d)
		else:
			if self.item:
				to_remove= []
				for d in self.item:
					to_remove.append(d)
				[self.remove(d) for d in to_remove]