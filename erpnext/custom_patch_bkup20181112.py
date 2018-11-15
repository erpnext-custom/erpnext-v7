from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import msgprint
from frappe.utils import flt, cint, now, nowdate, getdate, get_datetime
from frappe.utils.data import date_diff, add_days, get_first_day, get_last_day, add_years
from erpnext.hr.hr_custom_functions import get_month_details, get_company_pf, get_employee_gis, get_salary_tax, update_salary_structure
from datetime import timedelta, date
from erpnext.custom_utils import get_branch_cc, get_branch_warehouse
from erpnext.accounts.utils import make_asset_transfer_gl

def test():
	print("IN TEST")

def restore_jc():
	for a in frappe.db.sql("select a.name, b.stock_entry from `tabJob Card` a, `tabJob Card Item` b where a.name = b.parent and a.docstatus = 1 and b.stock_entry is not null group by b.stock_entry", as_dict=1):
		print(str(a.name) + " ==> " + str(a.stock_entry))
		frappe.db.sql("update `tabStock Entry` set job_card = %s where name = %s", (a.name, a.stock_entry))

"""def repost_stock_gl():
	sr = frappe.db.sql("select a.name from `tabStock Reconciliation` a, `tabStock Reconciliation Item` b where a.name = b.parent and b.item_code = '100452' and a.docstatus = 1", as_dict=1)
	for a in sr:
		print(a.name)
		self = frappe.get_doc("Stock Reconciliation", a.name)
		posting_date = str(get_datetime(str(self.posting_date) + ' ' + str(self.posting_time)))
                for b in self.items:
                        self.repost_issue_pol(b, posting_date)
		frappe.db.commit()

def check_pol_gl():
	for a in frappe.db.sql("select p.name from tabPOL p, `tabJournal Entry` b where p.jv = b.name and p.docstatus = 1 and b.docstatus = 2 and p.posting_date > '2017-12-31'", as_dict=1):
		print(str(a.name))

def link_pol_je():
	docs = frappe.db.sql("select je.reference_name, je.parent from `tabJournal Entry Account` je, tabPOL p where p.name = je.reference_name and je.docstatus = 1 and je.reference_name is not null", as_dict=1)
	for d in docs:
		frappe.db.sql("update tabPOL set jv = %s where name = %s", (d.parent, d.reference_name))
		print(str(d.reference_name) + " ==> " + str(d.parent))
"""

