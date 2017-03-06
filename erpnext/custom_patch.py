from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import msgprint
##
# Sets the initials of autoname for PO, PR, SO, SI, PI, etc
##
def moveConToCom():
	pass
	consumed = frappe.get_all("Consumed Budget")
	to = len(consumed)
	i = 0
	for a in consumed:
		i = i + 1
		d = frappe.get_doc("Consumed Budget", a.name)
		obj = frappe.get_doc({
				"doctype": "Committed Budget",
				"account": d.account,
				"cost_center": d.cost_center,
				"po_no": d.po_no,
				"po_date": d.po_date,
				"amount": d.amount,
				"item_code": d.item_code,
				"date": d.date
			})
		obj.submit()
		d.delete();
		print(str(i * 100 / to))
	print("DONE")

def createConsumed():
	con = frappe.db.sql("select pe.name as name, per.reference_name as pi from `tabPayment Entry Reference` per, `tabPayment Entry` pe where per.parent = pe.name and pe.docstatus = 1 and per.reference_doctype = 'Purchase Invoice' and pe.posting_date between '2017-01-01' and '2017-12-31'", as_dict=True)
	for a in con:
		items = frappe.db.sql("select item_code, cost_center, purchase_order, amount from `tabPurchase Invoice Item`  where docstatus = 1 and parent = \'" + str(a.pi) + "\'", as_dict=True)
		for i in items:
			#con = frappe.db.sql("select name, po_no, amount, docstatus from `tabCommitted Budget` where po_no = \'" + i.purchase_order + "\' and item_code = \'" + i.item_code + "\' and cost_center = \'" + i.cost_center + "\'")
			con = frappe.db.sql("select name, po_no, amount, account from `tabCommitted Budget` where po_no = \'" + i.purchase_order + "\' and item_code = \'" + i.item_code + "\' and cost_center = \'" + i.cost_center + "\' and amount = \'" + str(i.amount) + "\'")
			print(str(a.name))
			if con:
				print(str(con))
			else:
				print("NOT FOUND")
			#print(str(i.purchase_order) + " / " + str(i.item_code) + " / " + str(i.amount))
