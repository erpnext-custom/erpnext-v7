from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import msgprint
from frappe.utils import flt, cint
from frappe.utils.data import get_first_day, get_last_day, add_years, getdate, nowdate, add_days
from erpnext.custom_utils import get_branch_cc

def update_item_name():
	for a in frappe.db.sql("select item_code, item_name, name from `tabSales Invoice Item` where warehouse = 'Dzungdi Warehouse Plant 2 - SMCL'", as_dict=True):
		i_name = frappe.db.get_value("Item", a.item_code, "item_name")
		if a.item_name != i_name:
			frappe.db.sql("update `tabSales Invoice Item` set item_name = '{}' where name = '{}'".format(i_name, a.name))
			print("Item Name " + a.item_name + " Changed to " + i_name )


#addded bank name and bank account name in overtime application and updated for previous transactions (Tashi)
def update_ot():
	for ot in frappe.db.sql("select name, employee from `tabOvertime Application` where docstatus <= 1", as_dict = 1):
		doc = frappe.get_doc("Employee", ot.employee)
		frappe.db.sql("update `tabOvertime Application` set bank_name = '{0}', bank_no = {1} where name = '{2}'".format(doc.bank_name, doc.bank_ac_no, ot.name))
		print doc.bank_name
	
def update_ss():
	count = 1
	for a in frappe.db.sql(" select name from `tabSalary Structure` where is_active = 'Yes'", as_dict = 1):
		doc = frappe.get_doc("Salary Structure", a.name)
		count += 1
		doc.save(ignore_permissions = True)
		print a.name, count
		print "hi"

def pol_update():
	for a in frappe.db.sql(" select pol from `tabHSD Payment Item` where parent = 'HSDP2002007'", as_dict = 1):
		frappe.db.sql("update `tabPOL` set paid_amount = '' where name = '{0}'".format(a.pol))

def get_asset_issue():
	#for a in frappe.db.sql("select name from tabAsset where purchase_date > '2018-12-31' and docstatus = 1", as_dict=1):
	for a in frappe.db.sql("select name, asset_category as ac, gross_purchase_amount as gross from tabAsset where docstatus = 1", as_dict=1):
		for b in frappe.db.sql("select je.name from `tabJournal Entry` je, `tabJournal Entry Account` jea where je.name = jea.parent and jea.reference_name = %s and je.docstatus = 2", a.name, as_dict=1):
			print str(a.name) + " > " + str(b.name) + " = " + str(a.gross) + " : " + str(a.ac)

def get_asset_issue_1():
	#for a in frappe.db.sql("select name from tabAsset where purchase_date > '2018-12-31' and docstatus = 1", as_dict=1):
	for a in frappe.db.sql("select name, asset_category as ac, gross_purchase_amount as gross from tabAsset where docstatus = 1 and purchase_date > '2018-12-31'", as_dict=1):
		gls = frappe.db.sql("select je.name from `tabJournal Entry` je, `tabJournal Entry Account` jea where je.name = jea.parent and jea.reference_name = %s and je.docstatus = 2", a.name, as_dict=1)
		if not gls:
			print str(a.name) + " > " + str(a.gross) + " : " + str(a.ac)
def update_basic():
        count = 1
        for ss in frappe.db.sql(""" select p.name, c.amount, p.employee from `tabSalary Slip` p, `tabSalary Detail` c where c.parent = p.name and 
                                p.fiscal_year = '2019' and p.month = 12 and p.docstatus = 1 and c.salary_component = 'Basic Pay'""", as_dict =1):
                count += 1
                doc = frappe.get_doc("Salary Structure", {"employee": ss.employee, "is_active": 'Yes'})
                frappe.db.sql(""" update `tabSalary Detail` set amount = {0} where parent  = '{1}' and salary_component = 'Basic Pay'
                        """.format(ss.amount, doc.name))
                #doc.save()
                print ss.employee, ss.amount, doc.name, count



def update_sals():
        count = 1
        for ss in frappe.db.sql(""" select name from `tabSalary Structure` where is_active = 'Yes'""", as_dict =1):
                doc = frappe.get_doc("Salary Structure", ss.name)
                doc.save()
                count += 1
                print ss.name, count



def update_po():
	#p.transaction_date >= '2019-07-01'
        count = 0
        for po in frappe.db.sql(""" select p.name, p.transaction_date, c.budget_account, c.cost_center, c.amount, c.item_code, 
                        p.transaction_date from `tabPurchase Order` p, `tabPurchase Order Item` c 
                        where p.name = c.parent and p.docstatus = 1 and p.name = 'PO19100014'""", as_dict = 1):
                if not frappe.db.exists("Committed Budget", {"po_no": po.name,  "po_date": po.transaction_date, "amount": po.amount, "item_code": po.item_code, "account" : po.budget_account}):
                        count += 1
                        bud_obj = frappe.get_doc({
                                "doctype": "Committed Budget",
                                "account": po.budget_account,
                                "cost_center": po.cost_center,
                                "po_no": po.name,
                                "po_date": po.transaction_date,
                                "amount": po.amount,
                                "item_code": po.item_code,
                                "date": po.transaction_date
                                })
                        bud_obj.submit()
                        print po.name, count

def update_com_budget():
        count = 1
        for a in frappe.db.sql("select po_no, amount, account, cost_center, com_ref, item_code, po_date, date from `tabConsumed Budget` where docstatus = 1 and po_date >= '2019-07-01'", as_dict =1):

                frappe.db.sql("""update `tabCommitted Budget` com set consumed = 1 where com.po_no = '{0}' and com.amount =  {1} and com.account = '{2}' and com.cost_center = '{3}' and com.item_code = '{4}' and com.po_date = '{5}' and com.date != '{6}'""".format(a.com_ref, a.amount, a.account, a.cost_center, a.item_code, a.po_date, a.date))

		'''frappe.db.sql("""update `tabCommitted Budget` com set consumed = 1 where com.po_no = '{0}' and com.amount =  {1} and com.account = '{2}' and com.cost_center = '{3}'""".format(a.po_no, a.amount, a.account, a.cost_center))
		print a.po_no
                count += 1
                frappe.db.sql("""update `tabCommitted Budget` com set consumed = 1 where com.po_no = '{0}' and com.amount =  {1} and com.account = '{2}' and com.cost_center = '{3}' and com.po_no = '{4}' and com.date = '{5}'""".format(a.po_no, a.amount, a.account, a.cost_center, a.com_ref, a.date))
		
		frappei.db.sql("""update `tabCommitted Budget` com set consumed = 1 where com.po_no = '{0}' and com.amount =  {1} and com.account = '{2}' and com.cost_center = '{3}' and com.item_code = '{4}' and com.po_date = '{5}'""".format(a.com_ref, a.amount, a.account, a.cost_center, a.item_code, a.po_date))
		'''
		count += 1
		print a.po_no, count




def update_sst():
	count = 0
        for a in frappe.db.sql(""" select s.name from `tabSalary Structure` s, `tabSalary Detail` d where s.name = d.parent and s.is_active = 'Yes'
                        and d.salary_component = 'PF' and d.amount > 0""", as_dict =1):
                doc = frappe.get_doc("Salary Structure", a.name)
                count += 1
		doc.save()
                print count, doc.name



	'''def update_se():
        for a in frappe.db.sql("select name, equipment from `tabStock Entry` where purpose = 'Material Transfer' and docstatus = 1", as_dict =1):
                if a.equipment:
                        equipment_type = frappe.get_doc("Equipment", a.equipment).equipment_type
                        frappe.db.sql(" update `tabStock Entry` set equipment_type = '{0}' where name = '{1}'".format(equipment_type, a.name))
                print a.i

name, a.equipment


def check_trans_pay():
	for a in frappe.db.sql("select a.name, a.equipment, b.reference_type as rt, b.reference_name as rn, b.reference_row as rr  from `tabTransporter Payment` a, `tabTransporter Payment Item` b  where a.name = b.parent and a.docstatus = 1", as_dict=1):
		if a.rt == "Production":
			eq = frappe.db.get_value("Production Product Item", a.rr, "equipment")
		elif a.rt == "Stock Entry":
			eq = frappe.db.get_value("Stock Entry", a.rn, "equipment")
		else:
			eq = None
		if a.equipment != eq:
			print(a.name)'''

def update_empdetail():
	for a in frappe.db.sql(" select employee, name from `tabSalary Structure` ", as_dict =1):
		emp = frappe.get_doc("Employee", a.employee)
		print(a.name, a.employee)
		frappe.db.sql(""" update `tabSalary Structure` set employee_group = '{0}', employee_grade = '{1}' 
				where  name = '{2}'""".format(emp.employee_group, emp.employee_subgroup, a.name))


def save_salary_structure():
	for a in frappe.db.sql(""" select name from `tabSalary Structure` where is_active = 'Yes'""", as_dict =1):
		doc = frappe.get_doc("Salary Structure", a.name)
		print(a.name)
		doc.save()


def update_rrco_entries():
	import re
	pi = '^PI'
	dp = '^DP'
	bill_name = ''
	for a in frappe.db.sql("select name, purchase_invoice from `tabRRCO Receipt Entries`", as_dict =1):
		if a.purchase_invoice:
			print(a.name, a.purchase_invoice)
			if re.match(pi, str(a.purchase_invoice)):
				doc  = frappe.get_doc("Purchase Invoice", a.purchase_invoice)
				bill_name = doc.bill_no
				supp = doc.supplier
				frappe.db.sql(""" update `tabRRCO Receipt Entries` set bill_no = '{0}', 
					purpose = 'Purchase Invoices', supplier ='{2}'  where name = '{1}'""".format(bill_name, a.name, supp))
			if re.match(dp, str(a.purchase_invoice)):
				doc  = frappe.get_doc("Direct Payment", a.purchase_invoice)
				bill_name = doc.name
				supp = doc.party
				frappe.db.sql(""" update `tabRRCO Receipt Entries` set bill_no = '{0}', 
					purpose = 'Purchase Invoices', supplier = '{2}'  where name = '{1}'""".format(bill_name, a.name, supp))

def update_production_20190225():
	num = 0
	for a in frappe.db.sql("select a.name, a.posting_date from tabProduction a where docstatus = 1 and not exists (select 1 from  `tabGL Entry` b where b.voucher_no = a.name) order by a.posting_date asc, a.posting_time asc", as_dict=1):
		print(a.name)
		doc = frappe.get_doc("Production", a.name)
		doc.make_products_gl_entry()
		doc.make_raw_material_gl_entry()
		num = num + 1
		if num % 20 == 0:
			frappe.db.commit()
	frappe.db.commit() 


def update_pol_1():
	num = 0
	for a in frappe.db.sql("select name from tabPOL p where docstatus = 1 and exists (select 1 from `tabStock Ledger Entry` where voucher_no = p.name)", as_dict=1):
		frappe.db.sql("update tabPOL set docstatus = 0 where name = %s", a.name)
		frappe.db.sql("delete from `tabGL Entry` where voucher_no = %s", a.name)
		frappe.db.sql("delete from `tabStock Ledger Entry` where voucher_no = %s", a.name)
		print(a.name)
		doc = frappe.get_doc("POL", a.name)
		doc.submit()
		num = num + 1
		if num % 100 == 0:
			print("Committing....")
			frappe.db.commit()
	frappe.db.commit()


def cancel_prod_1():
	for a in frappe.db.sql("select name from tabProduction where docstatus in (0, 1)", as_dict=1):
		print(a.name)
		frappe.db.sql("delete from `tabStock Ledger Entry` where voucher_no = %s", a.name)
		frappe.db.sql("delete from `tabGL Entry` where voucher_no = %s", a.name)
		frappe.db.sql("update tabProduction set docstatus = 2 where name = %s", a.name)

def cancel_st_1():
	for a in frappe.db.sql("select a.posting_date, a.name, b.name as child, purpose from `tabStock Entry` a, `tabStock Entry Detail` b where a.name = b.parent and b.item_code in ('300017', '300018') and a.docstatus in (0, 1) order by timestamp(a.posting_date, a.posting_time) DESC", as_dict=1):
		print(a.name)
		frappe.db.sql("delete from `tabStock Ledger Entry` where voucher_no = %s", a.name)
		frappe.db.sql("delete from `tabGL Entry` where voucher_no = %s", a.name)
		frappe.db.sql("update `tabStock Entry` set docstatus = 2 where name = %s", a.name)
		frappe.db.sql("update `tabStock Entry Detail` set docstatus = 2 where name = %s", a.child)
		frappe.db.commit()


def cancel_dn_1():
	for a in frappe.db.sql("select a.posting_date, a.name, b.name as child from `tabDelivery Note` a, `tabDelivery Note Item` b where a.name = b.parent and b.item_code in ('300017', '300018') and a.docstatus in (0, 1) order by timestamp(a.posting_date, a.posting_time) DESC", as_dict=1):
		print(a.name)
		frappe.db.sql("delete from `tabStock Ledger Entry` where voucher_no = %s", a.name)
		frappe.db.sql("delete from `tabGL Entry` where voucher_no = %s", a.name)
		frappe.db.sql("update `tabDelivery Note` set docstatus = 2 where name = %s", a.name)
		frappe.db.sql("update `tabDelivery Note Item` set docstatus = 2 where name = %s", a.child)
		frappe.db.commit()

def cancel_si_draft():
	for a in frappe.db.sql("select parent, name from `tabSales Invoice Item` where item_code in ('300017', '300018') and docstatus = 0", as_dict=1):
		print(a.name)
	#	frappe.db.sql("update `tabSales Invoice` set docstatus = 2 where name = %s", a.name)
		frappe.db.sql("update `tabSales Invoice Item` set docstatus = 2 where name = %s", a.name)
		frappe.db.commit()

		
def cancel_si():
	for a in frappe.db.sql("select parent as name from `tabSales Invoice Item` where item_code in ('300017', '300018') and docstatus = 1", as_dict=1):
		print(a.name)
		doc = frappe.get_doc("Sales Invoice", a.name)
		doc.cancel()
		frappe.db.commit()


def cancel_production():
	for a in frappe.db.sql("select name from tabProduction where docstatus = 1 order by timestamp(posting_date, posting_time) DESC", as_dict=1):
		print(a.name)
		doc = frappe.get_doc("Production", a.name)
		doc.cancel()
		frappe.db.commit()

def check_asset_dep():
        for a in frappe.db.sql("select name, asset_category, opening_accumulated_depreciation as oad from tabAsset where docstatus = 1 and status not in ('Scrapped', 'Sold') order by asset_category", as_dict=1):
		dep_ds = frappe.db.sql("select accumulated_depreciation_amount as ada from `tabDepreciation Schedule` where parent = %s and journal_entry is not null order by schedule_date desc limit 1", a.name, as_dict=1)
		if dep_ds:
			dep_ds = flt(dep_ds[0]['ada'])
		else:
			dep_ds = 0

		dep_acc = frappe.db.get_value("Asset Category Account", {"parent": a.asset_category}, "depreciation_expense_account")
		dep_gl = frappe.db.sql("select sum(debit) as gl from `tabGL Entry` where account = %s and against_voucher = %s group by against_voucher", (dep_acc, a.name), as_dict=1)
		if dep_gl:
			dep_gl = flt(dep_gl[0]['gl'])
		else:
			dep_gl = 0
		
		if dep_ds > 0:
			dep_ds = dep_ds - flt(a.oad)
		dep_ds = round(dep_ds, 2)
		if dep_ds != dep_gl:
			dif =  dep_ds - dep_gl
			if dif > 0.2 or dif < -0.2:
				print(str(a.name) + " : " + str(a.asset_category) + " ==> " + str(dep_ds) + " / " + str(dep_gl))

def get_diff_asset():
	for a in frappe.db.sql("select name, asset_category, asset_account from tabAsset where docstatus = 1", as_dict=1):
		as_acc = frappe.db.get_value("Asset Category Account", {"parent": a.asset_category}, "fixed_asset_account")
		if as_acc != a.asset_account:
			print(str(a.name) + "   :  " + str(as_acc) + "  ==> " + str(a.asset_account))

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
		"""if not get_branch_cc(a.branch):
			print(str(a.name) + " ==> " + str(a.branch))
		"""
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
