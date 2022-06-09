# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe

from frappe import _

def get_context(context):
	context.no_cache = 1
	context.show_sidebar = True

	if not (frappe.form_dict.doctype and frappe.form_dict.name):
		frappe.throw(_("Not Permitted"), frappe.PermissionError)
		return

	context.doc = frappe.get_doc(frappe.form_dict.doctype, frappe.form_dict.name)
	if hasattr(context.doc, "set_indicator"):
		context.doc.set_indicator()

	context.parents = frappe.form_dict.parents
	context.payment_ref = frappe.db.get_value("Payment Request", 
		{"reference_name": frappe.form_dict.name}, "name")
	
	context.enabled_checkout = frappe.get_doc("Shopping Cart Settings").enable_checkout
			
	if context.doc and not context.doc.has_website_permission("read"):
		frappe.throw(_("Not Permitted"), frappe.PermissionError)
