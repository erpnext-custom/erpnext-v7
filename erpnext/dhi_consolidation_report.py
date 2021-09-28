import frappe
from frappe.utils import getdate, datetime, nowdate, flt
from erpnext.accounts.report.consolidation_report.consolidation_report import get_data, get_value
# from erpnext.accounts.report.gcoa_wise_report.gcoa_wise_report import create_transaction

@frappe.whitelist(allow_guest=True)
def dhi_consolidation_report():
    filters = {}
    filters['is_inter_company'] = ''
    return get_value(filters,'Yes')

# @frappe.whitelist()
# def create_transaction(filters=None,data = None):
#     frappe.msgprint('str')
#     total = 0
#     if not data:
#         filters = {}
#         filters['from_date'] = filters.from_date
#         filters['to_date'] = filters.to_date
#         data = get_data(filters)
        
#     doc = frappe.new_doc('Consolidation Transaction')
#         doc.from_date = filters.from_date
#         doc.to_date = filters.to_date
        
#     for d in data:
#         total += flt(d.amount)
#         doc.items.append(d)
        
#     doc.total_amount = total
#     doc.save(ignore_permissions=True)
    
@frappe.whitelist()
def auto_creation():
    filters = {}
    filters['from_date'] = getdate(frappe.defaults.get_user_default("year_start_date"))
    filters['to_date'] = getdate('2021-08-30')
    filters['is_inter_company'] = ''
    create_transaction(filters,[])
