import frappe, ast

@frappe.whitelist()
def submit_assets(assets_list):
	"""
	Submits all the assets_list present in the list
	assets_list is in string form, which is converted to list later
	"""
	# frappe.msgprint("length: {}".format(len(assets_list)))
	if len(assets_list) < 3:
		frappe.throw("Please select the assets to submit")
	
	# converting string to list obj
	assets_list = ast.literal_eval(assets_list)
	
	no_error = True
	for i in assets_list:
		try:			
			doc = frappe.get_doc("Asset", i)
			if doc.docstatus == 0:
				doc.submit()
			else:
				frappe.msgprint("This document is already submitted or cancelled: " + i)
		except:
			no_error = False
			frappe.msgprint("Error in Asset: " + i)
			# throwing again so its not validated
			frappe.throw('Validation Error. <b>None submitted</b>')
			
	if no_error:
		frappe.msgprint("Success.\nPlease refresh the page.")
		