from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import msgprint
from frappe.utils import flt, cint, now
from frappe.utils.data import get_first_day, get_last_day, add_years
from erpnext.hr.hr_custom_functions import get_month_details, get_company_pf, get_employee_gis, get_salary_tax, update_salary_structure

def adjust_leave_encashment():
        les = frappe.db.sql("select name, encashed_days, employee from `tabLeave Encashment` where docstatus = 1 and application_date between %s and %s", ('2017-01-01', '2017-12-31'), as_dict=True)
        for le in les:
                print(str(le.name))
                allocation = frappe.db.sql("select name, to_date from `tabLeave Allocation` where docstatus = 1 and employee = %s and leave_type = 'Earned Leave' order by to_date desc limit 1", (le.employee), as_dict=True)
                obj = frappe.get_doc("Leave Allocation", allocation[0].name)
                obj.db_set("leave_encashment", le.name)
                obj.db_set("encashed_days", (le.encashed_days))
                obj.db_set("total_leaves_allocated", (flt(obj.total_leaves_allocated) - flt(le.encashed_days)))

def get_date():
	print(now())
def update_ss():
	sss = frappe.db.sql("select name from `tabSalary Structure`", as_dict=True)
	for ss in sss:
		doc = frappe.get_doc("Salary Structure", ss)
		doc.save()

def update_customer():
	ccs = frappe.db.sql("select name from `tabCost Center` where is_group != 1", as_dict=True)
	for cc in ccs:
		obj = frappe.get_doc("Cost Center", cc)
		print(cc)
		obj.save()

def update_employee():
	emp_list = frappe.db.sql("select name from tabEmployee", as_dict=True)
	for emp in emp_list:
		print(emp.name)
		edoc = frappe.get_doc("Employee", emp)
		branch = frappe.db.get_value("Cost Center", edoc.cost_center, "branch")
		if branch:
			edoc.branch = branch
			edoc.save()
		else:
			frappe.throw("No branch for " + str(edoc.cost_center) + " for " + str(emp))

def give_admin_access():
	reports = frappe.db.sql("select name from tabReport", as_dict=True)
	for r in reports:
		role = frappe.new_doc("Report Role")
		role.parent = r.name
		role.parenttype = "Report"
		role.parentfield = "roles"
		role.role = "Administrator"
		role.save()		

def save_equipments():
	for a in frappe.db.sql("select name from tabEquipment", as_dict=True):
		doc = frappe.get_doc("Equipment", a.name)
		print(str(a))
		doc.save()

def submit_ss():
	ss = frappe.db.sql("select name from `tabSalary Structure`", as_dict=True)
	for s in ss:
		doc = frappe.get_doc("Salary Structure", s.name)
		for a in doc.earnings:
			if a.salary_component == "Basic Pay":
				print(str(doc.employee) + " ==> " + str(a.amount))
				update_salary_structure(doc.employee, flt(a.amount), s.name)
				break
		#doc.save()

def create_users():
	emp = frappe.db.sql("select name, company_email from tabEmployee where status = 'Active'", as_dict=True)
	if emp:
		for e in emp:
			print(str(e.name))
			doc = frappe.new_doc("User")
			doc.enabled = 1
			doc.email = e.company_email
			doc.first_name = "Test"
			doc.new_password = "CDCL!2017"
			doc.save()
		
			role = frappe.new_doc("UserRole")
			role.parent = doc.name
			role.role = "Employee"
			role.parenttype = "User"
			role.save()
			doc.save()
			em = frappe.get_doc("Employee", e.name)	
			em.user_id = doc.name
			em.save()
		print("DONE")

def submit_assets():
	list = frappe.db.sql("select name from tabAsset where docstatus = 0", as_dict=True)
	if list:
		num = 0
		for a in list:
			num = num + 1
			doc = frappe.get_doc("Asset", a.name)
			doc.submit()
			print(str(a.name))
			if cint(num) % 100 == 0:
				frappe.db.commit()
		print("DONE")

def give_permission():
	users = frappe.db.sql("select name from tabUser", as_dict=True)
	for u in users:
		if u.name in ['admins@cdcl.bt', 'proco@cdcl.bt', 'accounts@cdcl.bt', 'project@cdcl.bt', 'maintenance@cdcl.bt', 'fleet@cdcl.bt', 'sales@cdcl.bt','stock@cdcl.bt', 'hr@cdcl.bt','tashi.dorji775@bt.bt', 'sonam.zangmo@bt.bt', 'siva@bt.bt', 'jigme@bt.bt', 'dorji2392@bt.bt', 'sangay.dorji2695@bt.bt', 'lhendrup.dorji@bt.bt']:
			for branch in frappe.db.sql("select name from tabBranch", as_dict=True):
				#if branch == 'Lingmethang':
				frappe.permissions.add_user_permission("Branch", branch.name, u.name)
			print("DONE")	
		print(str(u))

##
# Post earned leave on the first day of every month
##
def post_earned_leaves():
	date = add_years(frappe.utils.nowdate(), 1)
	start = get_first_day(date);
	end = get_last_day(date);
	
	employees = frappe.db.sql("select name, employee_name from `tabEmployee` where status = 'Active' and employment_type in (\'Regular\', \'Contract\')", as_dict=True)
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
