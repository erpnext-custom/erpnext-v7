import frappe
from frappe.utils import getdate, datetime, nowdate, flt
from erpnext.accounts.report.consolidation_report.consolidation_report import  get_value
from datetime import datetime, timedelta, date
# from erpnext.accounts.report.gcoa_wise_report.gcoa_wise_report import create_transaction

@frappe.whitelist(allow_guest=True)
def dhi_consolidation_report():
    filters = {}
    filters['is_inter_company'] = ''
    return get_value(filters,'Yes')

