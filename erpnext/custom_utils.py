'''
--------------------------------------------------------------------------------------------------------------------------
Version          Author          CreatedOn          ModifiedOn          Remarks
------------ --------------- ------------------ -------------------  -----------------------------------------------------
2.0		  SHIV		                   28/11/2017         get_user_info method included.
2.0               SHIV                             02/02/2018         added function nvl()
--------------------------------------------------------------------------------------------------------------------------                                                                          
'''

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import msgprint
from frappe.utils import flt, cint
from frappe.utils.data import get_first_day, get_last_day, add_years
from frappe.desk.form.linked_with import get_linked_doctypes, get_linked_docs
from frappe.model.naming import getseries

##
# Rounds to the nearest 5 with precision of 1 by default
##
def round5(x, prec=1, base=0.5):
        return round(base * round(flt(x)/base), prec)

##
# If the document is linked and the linked docstatus is 0 and 1, return the first linked document
##
def check_uncancelled_linked_doc(doctype, docname):
        linked_doctypes = get_linked_doctypes(doctype)
        linked_docs = get_linked_docs(doctype, docname, linked_doctypes)
        for docs in linked_docs:
                for doc in linked_docs[docs]:
                        if doc['docstatus'] < 2:
                                return [docs, doc['name']]
        return 1

def get_year_start_date(date):
	return str(date)[0:4] + "-01-01"

def get_year_end_date(date):
	return str(date)[0:4] + "-12-31"

# Ver 2.0 Begins, following method added by SHIV on 28/11/2017
@frappe.whitelist()
def get_user_info(user=None, employee=None, cost_center=None):
        info = {}
        
	#cost_center,branch = frappe.db.get_value("Employee", {"user_id": user}, ["cost_center", "branch"])

        if employee:
                # Nornal Employee
                cost_center = frappe.db.get_value("Employee", {"name": employee}, "cost_center")
                branch      = frappe.db.get_value("Employee", {"name": employee}, "branch")

                # GEP Employee
                if not cost_center:
                        cost_center = frappe.db.get_value("GEP Employee", {"name": employee}, "cost_center")
                        branch      = frappe.db.get_value("GEP Employee", {"name": employee}, "branch")

                # MR Employee
                if not cost_center:
                        cost_center = frappe.db.get_value("Muster Roll Employee", {"name": employee}, "cost_center")
                        branch      = frappe.db.get_value("Muster Roll Employee", {"name": employee}, "branch")
		
        elif user:
                # Normal Employee
                cost_center = frappe.db.get_value("Employee", {"user_id": user}, "cost_center")
                branch      = frappe.db.get_value("Employee", {"user_id": user}, "branch")

                # GEP Employee
                if not cost_center:
                        cost_center = frappe.db.get_value("GEP Employee", {"user_id": user}, "cost_center")
                        branch      = frappe.db.get_value("GEP Employee", {"user_id": user}, "branch")

                # MR Employee
                if not cost_center:
                        cost_center = frappe.db.get_value("Muster Roll Employee", {"user_id": user}, "cost_center")
                        branch      = frappe.db.get_value("Muster Roll Employee", {"user_id": user}, "branch")
		
	warehouse   = frappe.db.get_value("Cost Center", cost_center, "warehouse")
	approver    = frappe.db.get_value("Approver Item", {"cost_center": cost_center}, "approver")
        customer    = frappe.db.get_value("Customer", {"cost_center": cost_center}, "name")

        info.setdefault('cost_center', cost_center)
        info.setdefault('branch', branch)
        info.setdefault('warehouse', warehouse)
        info.setdefault('approver',approver)
        info.setdefault('customer', customer)
	
	#return [cc, wh, app, cust]
        return info
# Ver 2.0 Ends

##
# Cancelling draft documents
##
@frappe.whitelist()
def cancel_draft_doc(doctype, docname):
        doc = frappe.get_doc(doctype, docname)
        doc.db_set("docstatus", 2)
	if doctype == "Material Request":
		doc.db_set("status", "Cancelled")
		doc.db_set("workflow_state", "Cancelled")
	if doctype == "Travel Claim":
		ta = frappe.db.get_value("Travel Authorization", doc.ta)
		if ta:
			ta.db_set("travel_claim", "")

##
#  nvl() function added by SHIV on 02/02/2018
##
def nvl(val1, val2):
        return val1 if val1 else val2

##
# generate and get the receipt number
##
def generate_receipt_no(doctype, docname, branch, fiscal_year):
	if doctype and docname:
		abbr = frappe.db.get_value("Branch", branch, "abbr")
		if not abbr:
			frappe.throw("Set Branch Abbreviation in Branch Master Record")
		name = str("CDCL/" + str(abbr) + "/" + str(fiscal_year) + "/")
		current = getseries(name, 4)
		doc = frappe.get_doc(doctype, docname)
		doc.db_set("money_receipt_no", current)
		doc.db_set("money_receipt_prefix", name)
		
