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


# /home/frappe/erp bench execute erpnext.custom_patch.grant_permission_all_test
def grant_permission_all_test():
        emp_list = frappe.db.sql("""
                                 select company, branch, name as employeecd, user_id, 'Employee' type
                                 from `tabEmployee`
                                 where user_id is not null
                                 and exists(select 1
                                                from  `tabUser`
                                                where `tabUser`.name = `tabEmployee`.user_id)
                                and name = 'CDCL0403003'
                        """, as_dict=1)

        for emp in emp_list:
                # From Employee Master
                frappe.permissions.remove_user_permission("Company", emp.company, emp.user_id)
                frappe.permissions.remove_user_permission("Branch", emp.branch, emp.user_id)

                frappe.permissions.add_user_permission("Company", emp.company, emp.user_id)
                frappe.permissions.add_user_permission("Branch", emp.branch, emp.user_id)

                frappe.permissions.remove_user_permission(emp.type, emp.employeecd, emp.user_id)
                frappe.permissions.add_user_permission(emp.type, emp.employeecd, emp.user_id)
                
                # From Assign Branch 
                ba = frappe.db.sql("""
                                select branch
                                from `tabBranch Item`
                                where exists(select 1
                                               from `tabAssign Branch`
                                               where `tabAssign Branch`.name = `tabBranch Item`.parent
                                               and   `tabAssign Branch`.user = '{0}')
                        """.format(emp.user_id), as_dict=1)
                

                for a in ba:
                        frappe.permissions.remove_user_permission("Branch", a.branch, emp.user_id)
                        frappe.permissions.add_user_permission("Branch", a.branch, emp.user_id)


def grant_permission_all():
        emp_list = frappe.db.sql("""
                                 select company, branch, name as employeecd, user_id, 'Employee' type
                                 from `tabEmployee`
                                 where user_id is not null
                                 and exists(select 1
                                                from  `tabUser`
                                                where `tabUser`.name = `tabEmployee`.user_id)
                                union all
                                select company, branch, name as employeecd, user_id, 'GEP Employee' type
                                 from `tabGEP Employee`
                                 where user_id is not null
                                 and exists(select 1
                                                from  `tabUser`
                                                where `tabUser`.name = `tabGEP Employee`.user_id)
                                union all
                                select company, branch, name as employeecd, user_id, 'Muster Roll Employee' type
                                 from `tabMuster Roll Employee`
                                 where user_id is not null
                                 and exists(select 1
                                                from  `tabUser`
                                                where `tabUser`.name = `tabMuster Roll Employee`.user_id)
                        """, as_dict=1)

        for emp in emp_list:
                # From Employee Master
                frappe.permissions.remove_user_permission("Company", emp.company, emp.user_id)
                frappe.permissions.remove_user_permission("Branch", emp.branch, emp.user_id)

                frappe.permissions.add_user_permission("Company", emp.company, emp.user_id)
                frappe.permissions.add_user_permission("Branch", emp.branch, emp.user_id)

                frappe.permissions.remove_user_permission(emp.type, emp.employeecd, emp.user_id)
                frappe.permissions.add_user_permission(emp.type, emp.employeecd, emp.user_id)
                                                
                # From Assign Branch 
                ba = frappe.db.sql("""
                                select branch
                                from `tabBranch Item`
                                where exists(select 1
                                               from `tabAssign Branch`
                                               where `tabAssign Branch`.name = `tabBranch Item`.parent
                                               and   `tabAssign Branch`.user = '{0}')
                        """.format(emp.user_id), as_dict=1)
                

                for a in ba:
                        frappe.permissions.remove_user_permission("Branch", a.branch, emp.user_id)
                        frappe.permissions.add_user_permission("Branch", a.branch, emp.user_id)

def remove_memelakha_entries():
	# This is done after manually crosschecking, everything is ok
	il = frappe.db.sql("""
		select a.name, b.item_code, count(*), sum(b.qty)
		from `tabStock Entry` a, `tabStock Entry Detail` b
		where a.branch = 'Memelakha Asphalt Plant' 
		and b.parent = a.name
		and a.job_card is null
		and a.name not in ('SECO17100009')
		and a.purpose = 'Material Issue'
		and lower(title) not like '%asphalt%'
		group by a.name, b.item_code
		order by a.name, b.item_code;
		""", as_dict=1)
	
	counter = 0

	for i in il:
		counter += 1
		idoc = frappe.get_doc("Stock Entry", i.name)
		print counter, idoc.name, idoc.docstatus

# 25/12/2017 SHIV, It is observed that parent cost_centers are used in the transaction which is wrong
def check_for_cc_group_entries():
        ex = ['Cost Center','Attendance Tool Others','Budget Reappropriation Tool','Project Overtime Tool', 'Supplementary Budget Tool']

        li = frappe.db.sql("""
                        select g.doctype, g.fieldname, g.table_name
                        from (
                        
                                select
                                        parent as doctype,
                                        fieldname,
                                        'tabDocField' as table_name
                                from `tabDocField` 
                                where (
                                        (fieldtype = 'Link' and options = 'Cost Center')
                                        or
                                        (lower(fieldname) like '%cost%center%' and fieldtype in ('Data','Dynamic Link','Small Text','Long Text','Read Only', 'Text'))
                                        )
                                union all
                                select
                                        dt as doctype,
                                        fieldname,
                                        'tabCustom Field' as table_name
                                from `tabCustom Field` 
                                where (
                                        (fieldtype = 'Link' and options = 'Cost Center')
                                        or
                                        (lower(fieldname) like '%cost%center%' and fieldtype in ('Data','Dynamic Link','Small Text','Long Text','Read Only', 'Text'))
                                        )
                        ) as g
                        where g.doctype not in ({0})
                """.format("'"+"','".join(ex)+"'"), as_dict=1)

        for i in li:
                no_of_rec = 0
                
                counts = frappe.db.sql("""
                                select a.{1} cc, count(*) counts
                                from `tab{0}` as a
                                where a.{1} is not null
                                and exists(select 1
                                                from `tabCost Center` as b
                                                where b.name = a.{1}
                                                and b.is_group = 1)
                                group by a.{1}
                """.format(i.doctype, i.fieldname), as_dict=1)

                '''
                if counts:
                        if counts[0].counts > 0:
                                no_of_rec = counts[0].counts
                                print i.doctype+" ("+i.fieldname+") : "+str(no_of_rec)
                '''

                for c in counts:
                        print i.doctype.ljust(50,' ')+str(":"), c.cc, c.counts
                

# 2018/06/06, Hap Dorji, Sotck Reconciliation entry didn't take effect on stock balance report for SR/000041
# /home/frappe/erp bench execute erpnext.temp_patch.update_stock_reconciliation
def update_stock_reconciliation():
        items = frappe.db.sql("""
                select *
                from `tabStock Ledger Entry`
                where voucher_type = 'Stock Reconciliation'
                and voucher_no = 'SR/000041'
                and docstatus < 2
                order by posting_date, posting_time
        """, as_dict=1)

        upd_counter = 0
        for i in items:
                diff = 0
                prev = frappe.db.sql("""
                        select *
                        from `tabStock Ledger Entry`
                        where warehouse = '{0}'
                        and item_code = '{1}'
                        and posting_date <= '{2}'
                        and posting_time < '{3}'
                        and docstatus < 2
                        order by posting_date desc, posting_time desc
                        limit 1
                """.format(i.warehouse, i.item_code, i.posting_date, i.posting_time), as_dict=1)

                if prev:
                        diff = flt(i.stock_value,5)-flt(prev[0].stock_value,5)
                        print 'F',i.item_code, i.stock_value, prev[0].stock_value, flt(i.stock_value_difference,5), flt(diff,5)
                else:
                        diff = i.stock_value
                        print 'N',i.item_code, i.stock_value, flt(i.stock_value_difference,5), flt(diff,5)

                if flt(i.stock_value_difference,5) != flt(diff,5):
                        print 'updading...'
                        frappe.db.sql("""
                                update `tabStock Ledger Entry`
                                set stock_value_difference = {0}
                                where name = '{1}'
                        """.format(diff, i.name))
                        upd_counter += 1

        print 'Total No.of rows updated: ',upd_counter
