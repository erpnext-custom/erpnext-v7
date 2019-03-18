from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import msgprint
from frappe.utils import flt, cint
from frappe.utils.data import get_first_day, get_last_day, add_years, getdate, nowdate, add_days
from erpnext.custom_utils import get_branch_cc

def update_stock_entries():
	counter = 0
	for i in frappe.db.sql("""
			select name, posting_date,purpose,owner 
			from `tabStock Entry` 
			where posting_date between '2019-02-01' and '2019-02-28' 
			and docstatus=0
			and purpose = 'Material Transfer'
			and owner = 'dorji2392@bt.bt'
			order by posting_date, name
		""", as_dict=True):
		counter += 1
		print counter, i.name, i.posting_date, i.purpose, i.owner
		try:
			doc = frappe.get_doc("Stock Entry", i.name)
			doc.submit()
			frappe.db.commit()
		except Exception, e:
			print 'ERROR',i.name,e
			frappe.db.rollback()

def cancel_salary_slips():
        fiscal_year = '2019'
        month   = '01'
        counter = 0

        for ssl in frappe.db.sql("select name from `tabSalary Slip` where fiscal_year='{0}' and month = '{1}' and docstatus=1".format(fiscal_year,month), as_dict=True):
                counter += 1
                print counter, ssl.name
                doc = frappe.get_doc("Salary Slip", ssl.name)
                doc.cancel()
##
# Post casual leave on the first day of every month
##
def post_casual_leaves():
        start = getdate('2019-01-01')
        end   = getdate('2019-12-31')

        employees = frappe.db.sql("select name, employee_name from `tabEmployee` where status = 'Active' and employment_type in (\'Regular employees\', \'Contract\')", as_dict=True)
        for e in employees:
                la = frappe.new_doc("Leave Allocation")
                la.employee = e.name
                la.employee_name = e.employee_name
                la.leave_type = "Casual Leave"
                la.from_date = str(start)
                la.to_date = str(end)
                la.carry_forward = cint(0)
                la.new_leaves_allocated = flt(10)
                la.submit()

def update_emp_cc():
	for a in frappe.db.sql("select name, branch from tabEmployee", as_dict=1):
		#if not get_branch_cc(a.branch):
		print(str(a.name) + " ==> " + str(a.branch))
		frappe.db.sql("update tabEmployee set cost_center = %s where name = %s", (get_branch_cc(a.branch), a.name))

def move_asset_movement():
        ams = frappe.db.sql("select name, transaction_date from `tabAsset Movement`", as_dict=True)
        for a in ams:
                frappe.db.sql("update `tabAsset Movement` set posting_date = %s where name = %s", (a.transaction_date, a.name))

def adjust_budget_po():
	for a in frappe.db.sql("select name, status from `tabPurchase Order` where status = 'Closed' and transaction_date > '2017-12-31' and docstatus = 1", as_dict=1):
		print(str(a.name) + " ==> " + str(a.status))
		doc = frappe.get_doc("Purchase Order", a.name)
		doc.adjust_commit_budget(a.status)

def cancel_dn():
	sis = frappe.db.sql("select name, posting_date from `tabSales Invoice` where posting_date > '2017-12-31' and docstatus = 1;", as_dict=True)
	for s in sis:
		print(s.name)
		doc = frappe.get_doc("Sales Invoice", s.name)
		doc.cancel()
	frappe.db.commit()
	dns = frappe.db.sql("select name from `tabDelivery Note` where posting_date > %s and docstatus = 1", ('2017-12-31'), as_dict=True)
	for a in dns:
		print(a.name)
		doc = frappe.get_doc("Delivery Note", a.name)
		doc.cancel()

def update_ss():
	empl = frappe.db.sql("select name from `tabEmployee`", as_dict=True)
	for emp in empl:
		e = frappe.get_doc("Employee", emp.name)
		ss_name = frappe.db.sql("select name from `tabSalary Structure` where is_active = 'Yes' and employee = %s", (emp.name), as_dict=True)
		for a in ss_name:
			ss = frappe.get_doc("Salary Structure", a.name)
			ss.db_set("branch", e.branch)
			ss.db_set("department", e.department)
			ss.db_set("division", e.division)
			ss.db_set("section", e.section)
			ss.db_set("designation", e.designation)

def assign_date_ta():
	tas = frappe.db.sql("select name from `tabTravel Authorization` where travel_claim is null", as_dict=True)
	for ta in tas:
		taa = frappe.db.sql("select name, date from `tabTravel Authorization Item` where parent = %s order by date desc limit 1", (str(ta.name)), as_dict=True)
		doc = frappe.get_doc("Travel Authorization", ta.name)
		doc.db_set('end_date_auth', taa[0].date)
		print(str(ta.name) + " ==> " + str(taa[0].date) + "  ==> " + str(doc.end_date_auth))

def adjust_leave_encashment():
	les = frappe.db.sql("select name, encashed_days, employee from `tabLeave Encashment` where docstatus = 1 and application_date between %s and %s", ('2017-01-01', '2017-12-31'), as_dict=True)
	for le in les:
		print(str(le.name))
		allocation = frappe.db.sql("select name, to_date from `tabLeave Allocation` where docstatus = 1 and employee = %s and leave_type = 'Earned Leave' order by to_date desc limit 1", (le.employee), as_dict=True)
		obj = frappe.get_doc("Leave Allocation", allocation[0].name)
		obj.db_set("leave_encashment", le.name)
		obj.db_set("encashed_days", (le.encashed_days))
		obj.db_set("total_leaves_allocated", (flt(obj.total_leaves_allocated) - flt(le.encashed_days)))


##
# Post earned leave on the first day of every month
##
def post_earned_leaves():
	date = add_years(frappe.utils.nowdate(), 1)
	start = get_first_day(date);
	end = get_last_day(date);
	
	employees = frappe.db.sql("select name, employee_name from `tabEmployee` where status = 'Active' and employment_type in (\'Regular employees\', \'Contract\')", as_dict=True)
	for e in employees:
		la = frappe.new_doc("Leave Allocation")
		la.employee = e.name
		la.employee_name = e.employee_name
		la.leave_type = "Casual Leave"
		la.from_date = str(start)
		la.to_date = str(end)
		la.carry_forward = cint(0)
		la.new_leaves_allocated = flt(10)
		la.submit()
		
#Create asset received entries for asset balance
def createAssetEntries():
	frappe.db.sql("delete from `tabAsset Received Entries`")
	receipts = frappe.db.sql("select pr.posting_date, pr.name, pri.item_code, pri.qty from `tabPurchase Receipt` pr,  `tabPurchase Receipt Item` pri  where pr.docstatus = 1 and pri.docstatus = 1 and pri.parent = pr.name", as_dict=True)
	for a in receipts:
		item_group = frappe.db.get_value("Item", a.item_code, "item_group")
		if item_group and item_group == "Fixed Asset":
			ae = frappe.new_doc("Asset Received Entries")
			ae.item_code = a.item_code
			ae.qty = a.qty
			ae.received_date = a.posting_date
			ae.ref_doc = a.name
			ae.submit()

# create consumed and committed budget
def budget():
	deleteExisting()
	commitBudget();
	consumeBudget();
	adjustBudgetJE()

def deleteExisting():
	print("Deleting existing data")
	frappe.db.sql("delete from `tabCommitted Budget`")
	frappe.db.sql("delete from `tabConsumed Budget`")

##
# Commit Budget
##
def commitBudget():
	print("Committing budgets from PO")
	orders = frappe.db.sql("select name from `tabPurchase Order` where docstatus = 1", as_dict=True)
	for a in orders:
		order = frappe.get_doc("Purchase Order", a['name'])
		for item in order.get("items"):
			account_type = frappe.db.get_value("Account", item.budget_account, "account_type")
			if account_type in ("Fixed Asset", "Expense Account"):
				consume = frappe.get_doc({
					"doctype": "Committed Budget",
					"account": item.budget_account,
					"cost_center": item.cost_center,
					"po_no": order.name,
					"po_date": order.transaction_date,
					"amount": item.amount,
					"item_code": item.item_code,
					"date": frappe.utils.nowdate()})
				consume.submit()


##
# Commit Budget
##
def adjustBudgetJE():
	print("Committing and consuming from JE")
	entries = frappe.db.sql("select name from `tabGL Entry` where voucher_type='Journal Entry' and (against_voucher_type != 'Asset' or against_voucher_type is null)", as_dict=True)
	for a in entries:
		gl = frappe.get_doc("GL Entry", a['name'])
		account_type = frappe.db.get_value("Account", gl.account, "account_type")
		
		if account_type in ("Fixed Asset", "Expense Account"):
			commit = frappe.get_doc({
					"doctype": "Committed Budget",
					"account": gl.account,
					"cost_center": gl.cost_center,
					"po_no": gl.voucher_no,
					"po_date": gl.posting_date,
					"amount": gl.debit - gl.credit,
					"item_code": "",
					"date": frappe.utils.nowdate()})
			commit.submit()
			
			consume = frappe.get_doc({
					"doctype": "Consumed Budget",
					"account": gl.account,
					"cost_center": gl.cost_center,
					"po_no": gl.voucher_no,
					"po_date": gl.posting_date,
					"amount": gl.debit - gl.credit,
					"item_code": "",
					"com_ref": gl.voucher_no,
					"date": frappe.utils.nowdate()})
			consume.submit()

##
# Commit Budget
##
def consumeBudget():
	print("Consuming budgets from PI")
	invoices = frappe.db.sql("select name from `tabPurchase Invoice` where docstatus = 1", as_dict=True)
	for a in invoices:
		invoice = frappe.get_doc("Purchase Invoice", a['name'])
		for item in invoice.get("items"):
			expense, cost_center = frappe.db.get_value("Purchase Order Item", {"item_code": item.item_code, "cost_center": item.cost_center, "parent": item.purchase_order, "docstatus": 1}, ["budget_account", "cost_center"])
			if expense:
				account_type = frappe.db.get_value("Account", expense, "account_type")
				if account_type in ("Fixed Asset", "Expense Account"):
					po_date = frappe.db.get_value("Purchase Order", item.purchase_order, "transaction_date")
					consume = frappe.get_doc({
						"doctype": "Consumed Budget",
						"account": expense,
						"cost_center": item.cost_center,
						"po_no": invoice.name,
						"po_date": po_date,
						"amount": item.amount,
						"item_code": item.item_code,
						"com_ref": item.purchase_order,
						"date": frappe.utils.nowdate()})
					consume.submit()
	

##
# Update presystem date
##
def updateDate():
	import csv
	with open('/home/frappe/emines/sites/emines.smcl.bt/public/files/myasset.csv', 'rb') as f:
		reader = csv.reader(f)
		mylist = list(reader)
		for i in mylist:
			asset = frappe.get_doc("Asset", i[0])
			asset.db_set("presystem_issue_date", i[1])
			
		print ("DONE")
##
# Sets the initials of autoname for PO, PR, SO, SI, PI, etc
##
def moveConToCom():
	pass
	consumed = frappe.get_all("Consumed Budget")
	to = len(consumed)
	i = 0
	for a in consumed:
		i = i + 1
		d = frappe.get_doc("Consumed Budget", a.name)
		obj = frappe.get_doc({
				"doctype": "Committed Budget",
				"account": d.account,
				"cost_center": d.cost_center,
				"po_no": d.po_no,
				"po_date": d.po_date,
				"amount": d.amount,
				"item_code": d.item_code,
				"date": d.date
			})
		obj.submit()
		d.delete();
		print(str(i * 100 / to))
	print("DONE")

def createConsumed():
	con = frappe.db.sql("select pe.name as name, per.reference_name as pi from `tabPayment Entry Reference` per, `tabPayment Entry` pe where per.parent = pe.name and pe.docstatus = 1 and per.reference_doctype = 'Purchase Invoice' and pe.posting_date between '2017-01-01' and '2017-12-31'", as_dict=True)
	for a in con:
		items = frappe.db.sql("select item_code, cost_center, purchase_order, amount from `tabPurchase Invoice Item`  where docstatus = 1 and parent = \'" + str(a.pi) + "\'", as_dict=True)
		for i in items:
			#con = frappe.db.sql("select name, po_no, amount, docstatus from `tabCommitted Budget` where po_no = \'" + i.purchase_order + "\' and item_code = \'" + i.item_code + "\' and cost_center = \'" + i.cost_center + "\'")
			con = frappe.db.sql("select name, po_no, amount, account from `tabCommitted Budget` where po_no = \'" + i.purchase_order + "\' and item_code = \'" + i.item_code + "\' and cost_center = \'" + i.cost_center + "\' and amount = \'" + str(i.amount) + "\'")
			print(str(a.name))
			if con:
				print(str(con))
			else:
				print("NOT FOUND")
			#print(str(i.purchase_order) + " / " + str(i.item_code) + " / " + str(i.amount))

# Ver 2.0 Begins, added by SHIV
# This method updates all the employees branches in user permissions
def update_branch_permission():
        for e in frappe.db.sql("select name, branch, user_id from `tabEmployee` where status = 'Active' and ifnull(user_id,'x') != 'x'",as_dict=True):
                print e.name, e.branch, e.user_id
                frappe.permissions.add_user_permission("Branch", e.branch, e.user_id)
