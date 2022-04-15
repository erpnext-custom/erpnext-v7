import frappe
from frappe.utils import getdate, datetime, nowdate, flt
from erpnext.accounts.report.consolidation_report.consolidation_report import get_data, get_value
# from erpnext.accounts.report.gcoa_wise_report.gcoa_wise_report import create_transaction

@frappe.whitelist(allow_guest=True)
def dhi_consolidation_report():
    filters = {}
    filters['is_inter_company'] = ''
    return get_value(filters,'Yes')
