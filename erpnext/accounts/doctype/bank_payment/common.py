
from __future__ import unicode_literals
import frappe
from frappe import _
# from frappe.utils import cint, flt, now, nowtime, get_bench_path,get_site_path, touch_file, getdate, get_datetime
@frappe.whitelist()
def get_account_by_branch_set_query(doctype, txt, searchfield, start, page_len,filters):
	if not filters.get("branch"):
		frappe.msgprint(_("Please select <b>Paid From Branch</b> first"))
	data = []
	data = frappe.db.sql("""
    	SELECT 
     		a.name, 
       		a.bank_name, 
         	a.bank_branch, 
          	a.bank_account_type, 
           	a.bank_account_no
		FROM `tabAccount` a
			WHERE a.bank_name is NOT NULL
			AND a.bank_branch is NOT NULL
			AND a.bank_account_type is NOT NULL
			AND a.bank_account_no is NOT NULL
			AND 
   				(EXISTS 
       				(SELECT 1
						FROM `tabBranch` b 
						INNER JOIN `tabBranch Bank Account` ba 
						ON b.name = ba.parent
						WHERE b.name = '{0}'
						AND ba.account = a.name)
					OR 
					EXISTS (SELECT 1
						FROM `tabBranch` 
						WHERE name = "{0}"
						AND {1} = a.name)
				)
	""".format(filters.get("branch"), filters.get("account_type")))

	if filters.get("branch") and not data:
		expense_bank_account = frappe.db.get_value("Branch", filters.get("branch"), filters.get("account_type"))
		if not expense_bank_account:
			frappe.msgprint(_("Default <b>Expense Bank Account</b> is not set for this branch"))
		else:
			account = frappe.db.get("Account", expense_bank_account)
			if not account.bank_name:
				frappe.msgprint(_('<b>Bank Name</b> is not set for {}').format(frappe.get_desk_link("Account", expense_bank_account)))
			elif not account.bank_branch:
				frappe.msgprint(_("""<b>Bank Account's Branch</b> is not set for {} """).format(frappe.get_desk_link("Account", expense_bank_account)))
			elif not account.bank_account_no:
				frappe.msgprint(_('<b>Bank Account No.</b> is not set for {}').format(frappe.get_desk_link("Account", expense_bank_account)))
			elif not account.bank_account_type:
				frappe.msgprint(_('<b>Bank Account Type</b> is not set for {}').format(frappe.get_desk_link("Account", expense_bank_account)))
	return data

@frappe.whitelist()
def get_account_by_branch_frappe_call(branch, account_type):
	if not branch:
		frappe.msgprint(_("Please select <b>Paid From Branch</b> first"))
	data = []
	data = frappe.db.sql("""
    	SELECT 
     		a.name, 
       		a.bank_name, 
         	a.bank_branch, 
          	a.bank_account_type, 
           	a.bank_account_no
		FROM `tabAccount` a
			WHERE a.bank_name is NOT NULL
			AND a.bank_branch is NOT NULL
			AND a.bank_account_type is NOT NULL
			AND a.bank_account_no is NOT NULL
			AND 
   				(EXISTS 
       				(SELECT 1
						FROM `tabBranch` b 
						INNER JOIN `tabBranch Bank Account` ba 
						ON b.name = ba.parent
						WHERE b.name = '{0}'
						AND ba.account = a.name)
					OR 
					EXISTS (SELECT 1
						FROM `tabBranch` 
						WHERE name = "{0}"
						AND {1} = a.name)
				)
	""".format(branch, account_type))

	if branch and not data:
		expense_bank_account = frappe.db.get_value("Branch", branch, account_type)
		if not expense_bank_account:
			frappe.msgprint(_("Default <b>Expense Bank Account</b> is not set for this branch"))
		else:
			account = frappe.db.get("Account", expense_bank_account)
			if not account.bank_name:
				frappe.msgprint(_('<b>Bank Name</b> is not set for {}').format(frappe.get_desk_link("Account", expense_bank_account)))
			elif not account.bank_branch:
				frappe.msgprint(_("""<b>Bank Account's Branch</b> is not set for {} """).format(frappe.get_desk_link("Account", expense_bank_account)))
			elif not account.bank_account_no:
				frappe.msgprint(_('<b>Bank Account No.</b> is not set for {}').format(frappe.get_desk_link("Account", expense_bank_account)))
			elif not account.bank_account_type:
				frappe.msgprint(_('<b>Bank Account Type</b> is not set for {}').format(frappe.get_desk_link("Account", expense_bank_account)))
	return data