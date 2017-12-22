'''
--------------------------------------------------------------------------------------------------------------------------
Version          Author          CreatedOn          ModifiedOn          Remarks
------------ --------------- ------------------ -------------------  -----------------------------------------------------
2.0		  SHIV		                   28/11/2017         get_user_info method included.
--------------------------------------------------------------------------------------------------------------------------                                                                          
'''

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import msgprint
from frappe.utils import flt, cint
from frappe.utils.data import get_first_day, get_last_day, add_years


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
