from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe import msgprint
from frappe.utils import flt, cint, now, nowdate, getdate, get_datetime,now_datetime
from frappe.utils.data import date_diff, add_days, get_first_day, get_last_day, add_years
#from erpnext.hr.hr_custom_functions import get_month_details, get_company_pf, get_employee_gis, get_salary_tax, update_salary_structure
from erpnext.hr.hr_custom_functions import get_month_details, get_salary_tax
from datetime import timedelta, date
from erpnext.custom_utils import get_branch_cc, get_branch_warehouse
from erpnext.accounts.utils import make_asset_transfer_gl
from datetime import datetime
import os
import subprocess

def get_stats():
        filename = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = '/home/kinley/erp/logs/stats/top'+filename+'.log'
        values  = []
        
        with open(filename, "w") as outfile:
                subprocess.call("top -b -n1", shell=True, stdout=outfile)

        with open(filename) as infile:
                counter = 0
                start   = 999
                
                for line in infile:
                        counter += 1
                        record   = ()
                        if counter > start:
                                record = tuple([
                                        str(filename).strip(),
                                        line[:5].strip(),
                                        line[5:14].strip(),
                                        line[14:18].strip(),
                                        line[18:22].strip(),
                                        line[22:30].strip(),
                                        line[30:37].strip(),
                                        line[37:44].strip(),
                                        line[44:46].strip(),
                                        line[46:52].strip(),
                                        line[52:57].strip(),
                                        line[57:67].strip(),
                                        line[67:len(line)].strip(),
                                        str(frappe.session.user).strip(),
                                        str(now_datetime()).strip()
                                ])
                                values.append(str(record))
                        else:
                                if line[:5].strip() == "PID":
                                        start = counter
        if len(values) > 0:
                qry = """
                        insert into maintenance.stats(filename,pid,user,pr,ni,virt,res,shr,s,
                                cpu,mem,time,command,owner,creation)
                        values {0}
                """

                try:
                        sql = qry.format(",".join(values))
                        frappe.db.sql(sql)
                except Exception, e:
                        frappe.throw(_("{0}").format(str(e)))
        print filename

def adjust_pr_entry():
	for a in frappe.db.sql("select name from `tabPurchase Receipt` where name in ('PRCO18110243', 'PRCO18070032')", as_dict=1):
		print(str(a.name))
		frappe.db.sql("delete from `tabGL Entry` where voucher_no = %s", a.name)
		doc = frappe.get_doc("Purchase Receipt", a.name)
		doc.make_gl_entries()

	"""for a in frappe.db.sql("select distinct parent from `tabPurchase Receipt Item` where parent in ('PRCO18050290', 'PRCO18110238')", as_dict=1):
		print(str(a.parent))
		frappe.db.sql("delete from `tabGL Entry` where voucher_no = %s", a.parent)
		doc = frappe.get_doc("Purchase Receipt", a.parent)
		doc.make_gl_entries()"""

def adjust_se_entry():
	for a in frappe.db.sql("select distinct parent from `tabStock Entry Detail` where parent in ('PRCO18050290','SEMI18060781','SEMT18060017','PRCO18070032','PRCO18110238','PRCO18110243','SEMI18121376','SEMI18121378','SEMI18121380')", as_dict=1):
		print(str(a.parent))
		frappe.db.sql("delete from `tabGL Entry` where voucher_no = %s", a.parent)
		doc = frappe.get_doc("Stock Entry", a.parent)
		doc.make_gl_entries()

def update_increments_jan2019():
	err_count = 0
	for i in frappe.db.sql("select * from maintenance.update_increments where ifnull(flag,0) = 0", as_dict=True):
		if not frappe.db.exists("Salary Increment", {'fiscal_year': '2019', 'month': '01', 'employee': i.employee}):
			err_count += 1
			print i.sno, i.employee, i.remarks, i.increment_amount, i.flag

	if err_count:
		print 'ERROR: Unable to update increments due to above listed employees not having increments.'
		return False

	# Updating increments
	for i in frappe.db.sql("select * from maintenance.update_increments where ifnull(flag,0) = 0", as_dict=True):
		doc = frappe.get_doc("Salary Increment", {'fiscal_year': '2019', 'month': '01', 'employee': i.employee, 'docstatus': 0})
		print doc.name
		if i.remarks == "NO_INCREMENT":
			try:
				doc.remarks = 'No increment as per the excel sheet provided in ticket#1265'
				doc.increment = 0
				doc.new_basic = flt(doc.old_basic)
				doc.save()
				frappe.db.sql("update maintenance.update_increments set flag=1 where employee='{0}'".format(i.employee))
				print i.employee,'NO_INCREMENT'
			except Exception, e:
				print i
				frappe.throw(_("ERROR: While updating for NO_INCREMENT. {0}").format(e))
		elif i.remarks == "PRORATED":
			try:
				doc.remarks = 'Prorated as per the excel sheet provided in ticket#1265'
				doc.increment = flt(i.increment_amount)
				doc.new_basic = flt(doc.old_basic)+flt(i.increment_amount)
				doc.save()
				frappe.db.sql("update maintenance.update_increments set flag=1 where employee='{0}'".format(i.employee))
				print i.employee,'PRORATED'
			except Exception, e:
				print i
				frappe.throw(_("ERROR: While updating for PRORATED. {0}").format(e))
		else:
			print i
			frappe.throw(_("No matching record found for the excel sheet records provided"))

def update_consumed_budget_direct_payment():
        ml = frappe.db.sql("select p.name as name, p.posting_date as posting_date, p.cost_center as cost_center, p.debit_account as budget_account, p.amount as amount  from `tabDirect Payment` p where p.payment_type='payment' and journal_entry == "" p.name not in (select po_no from `tabConsumed Budget`)", as_dict=1)
        for a in ml:
                dc = frappe.new_doc("Committed Budget")
                dc.account = a.budget_account
                dc.cost_center = a.cost_center
                dc.po_no = a.name
                dc.po_date = a.posting_date
                dc.amount = a.amount
                dc.poi_name = a.name
                dc.date = a.posting_date
                dc.flags.ignore_permissions=1
                dc.submit()

                cb = frappe.new_doc("Consumed Budget")
                cb.account = a.budget_account
                cb.cost_center = a.cost_center
                cb.po_no = a.name
                cb.po_date = a.posting_date
                cb.amount = a.amount
                cb.pii_name = a.name,
                cb.com_ref = dc.name,
                cb.date = a.posting_date
                cb.flags.ignore_permissions=1
                cb.submit()
			
def update_consumed_budget():
        ml = frappe.db.sql("select p.name as name, p.posting_date as posting_date, p.cost_center as cost_center, i.budget_account as budget_account, i.amount as amount  from `tabImprest Recoup` p, `tabImprest Recoup Item` i where p.name = i.parent and p.docstatus = 1 and p.name not in (select po_no from `tabConsumed Budget`)", as_dict=1)
        for a in ml:
                dc = frappe.new_doc("Committed Budget")
                dc.account = a.budget_account
                dc.cost_center = a.cost_center
                dc.po_no = a.name
                dc.po_date = a.posting_date
                dc.amount = a.amount
                dc.poi_name = a.name
                dc.date = a.posting_date
                dc.flags.ignore_permissions=1
                dc.submit()

                cb = frappe.new_doc("Consumed Budget")
                cb.account = a.budget_account
                cb.cost_center = a.cost_center
                cb.po_no = a.name
                cb.po_date = a.posting_date
                cb.amount = a.amount
                cb.pii_name = a.name,
                cb.com_ref = dc.name,
                cb.date = a.posting_date
                cb.flags.ignore_permissions=1
                cb.submit()


def test():
	print("IN TEST")

def update_dp_gl():
        for a in frappe.db.sql("select name, posting_date from `tabDirect Payment` where docstatus = 1", as_dict=1):
                for b in frappe.db.sql("select name, posting_date from `tabGL Entry` where voucher_no = %s", a.name, as_dict=1):
                        if b.posting_date != a.posting_date:
                                print(str(a.name) + " : " + str(a.posting_date) + " to " + str(b.posting_date))
				frappe.db.sql("update `tabGL Entry` set posting_date = %s where name = %s", (a.posting_date, b.name))

def adjust_asset_sale():
	for a in frappe.db.sql("select name, branch from `tabSales Invoice` where naming_series = 'Fixed Asset' and docstatus = 1 and posting_date > '2018-01-01'", as_dict=1):
		gl = None
		gls = frappe.db.sql("select name from `tabGL Entry` where voucher_no = %s and account = 'Gain or Loss on Sale of Asset - CDCL'", a.name, as_dict=1)
		if gls:
			gl = gls[0].name
		if gl:
			cc = get_branch_cc(a.branch)
			print(str(a.name) + " : " + str(gl) + " ==> " + str(cc))
			frappe.db.sql("update `tabGL Entry` set cost_center = %s where name = %s", (cc, gl))

def adjust_budget_po():
        for a in frappe.db.sql("select name, status from `tabPurchase Order` where status = 'Closed' and transaction_date > '2017-12-31' and docstatus = 1", as_dict=1):
                print(str(a.name) + " ==> " + str(a.status))
                doc = frappe.get_doc("Purchase Order", a.name)
                doc.adjust_commit_budget(a.status)

def cancel_bdr():
	#for a in frappe.db.sql("select name from `tabBreak Down Report` b where b.docstatus = 1 and b.date < '2018-12-01' and not exists (select 1 from `tabJob Card` j where j.break_down_report = b.name);", as_dict=1):
	for a in frappe.db.sql("select name from `tabBreak Down Report` b where b.docstatus = 1 and b.date < '2018-12-01' and not exists (select 1 from `tabJob Card` j where j.break_down_report = b.name and j.docstatus in (0, 1));", as_dict=1):
		print(str(a.name))
		doc = frappe.get_doc("Break Down Report", a.name)
		doc.cancel()

"""def restore_jc():
	for a in frappe.db.sql("select a.name, b.stock_entry from `tabJob Card` a, `tabJob Card Item` b where a.name = b.parent and a.docstatus = 1 and b.stock_entry is not null group by b.stock_entry", as_dict=1):
		print(str(a.name) + " ==> " + str(a.stock_entry))
		frappe.db.sql("update `tabStock Entry` set job_card = %s where name = %s", (a.name, a.stock_entry))

def repost_stock_gl():
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


def update_sst_payment_methods():
        counter = 0
        for i in frappe.db.sql("select * from `tabSalary Component` where field_value is not null", as_dict=True):
                counter += 1
                print counter, i.name
                frappe.db.sql("""
                        update `tabSalary Structure`
                        set {0} = '{1}'
                """.format(i.field_method, i.payment_method))

        frappe.db.sql("update `tabSalary Structure` set temporary_transfer_allowance_method = 'Percent' where ifnull(temporary_transfer_allowance,0) > 0 and ifnull(lumpsum_temp_transfer_amount,0) = 0")
        frappe.db.sql("update `tabSalary Structure` set temporary_transfer_allowance_method = 'Lumpsum' where ifnull(temporary_transfer_allowance,0) = 0 and ifnull(lumpsum_temp_transfer_amount,0) > 0;");
        print 'Done updating.....'

