from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import msgprint
from frappe.utils import flt, cint
from frappe.utils.data import get_first_day, get_last_day, add_years, getdate, nowdate, add_days
from erpnext.custom_utils import get_branch_cc

# update SWSS for all the Salary Structures, by SHIV on 2021/02/17
def update_swss_for_all_salary_structures(debug=1):
        count = 0
        for i in frappe.get_all("Salary Structure", {"is_active": "Yes"}):
                count += 1
                print(count,i.name)
                if not debug:
                        doc = frappe.get_doc("Salary Structure", i.name)
                        doc.save(ignore_permissions=True)
        frappe.db.commit()

# adjustment for stock balance issue of 2019, by SHIV on 2021/02/16
def adjust_stock_20210216():
	doc = frappe.new_doc("Stock Ledger Entry")
	doc.item_code = '100908'
	doc.warehouse = 'Khothakpa Consumable Warehouse - SMCL'
	doc.posting_date = '2019-12-31'
	doc.posting_time = '23:56:14'
	doc.voucher_type = 'Purchase Receipt'
	doc.voucher_no = 'PR19110060'
	doc.actual_qty = -6
	doc.stock_uom = 'No'
	doc.valuation_rate = 17685.04
	doc.stock_value_difference = -106110.24
	doc.company = 'State Mining Corporation Ltd'
	doc.fiscal_year = '2019'
	doc.save(ignore_permissions=True)
	print(doc.name)
	frappe.db.commit()

def submit_sr20210208_2():
	for i in frappe.db.sql("select * from `tabStock Reconciliation` where name in ('SR/000054', 'SR/000053') order by name desc", as_dict=True):
		print(i.name, i.docstatus)
		if i.docstatus == 0:
			doc = frappe.get_doc("Stock Reconciliation", i.name)
			doc.submit()
		frappe.db.commit()

def submit_sr20210208():
	for i in frappe.db.sql("select * from `tabStock Reconciliation` where name in ('SR/000051', 'SR/000053') order by name", as_dict=True):
		print(i.name, i.docstatus)
		if i.docstatus == 0:
			doc = frappe.get_doc("Stock Reconciliation", i.name)
			doc.submit()
		frappe.db.commit()

def cancel_sr20210202():
	doc = frappe.get_doc("Stock Reconciliation", "SR/000048")
	doc.cancel()
	frappe.db.commit()

def submit_sr20210202():
	doc = frappe.get_doc("Stock Reconciliation", "SR/000052")
	doc.submit()
	frappe.db.commit()

# adjustment for stock balance issue of 2019, by SHIV on 2021/01/11
def adjust_stock_2019():
	doc = frappe.new_doc("Stock Ledger Entry")
	doc.item_code = '300018'
	doc.warehouse = 'Khothagpa Gypsum Mines - SMCL'
	doc.posting_date = '2019-12-31'
	doc.posting_time = '23:56:14'
	doc.voucher_type = 'Stock Reconciliation'
	doc.voucher_no = 'SR/000036'
	doc.stock_uom = 'MT'
	doc.valuation_rate = 1265.90
	doc.stock_value_difference = -17556.28
	doc.company = 'State Mining Corporation Ltd'
	doc.fiscal_year = '2019'
	doc.save(ignore_permissions=True)
	print(doc.name)
	frappe.db.commit()

# submitting backdated production entry, by SHIV on 2020/07/13
# time bench execute erpnext.temp_patch.submit_production --args "[''],1,"
def submit_production(pr_list=[], debug=1):
	for i in pr_list:
		print(i)
		doc = frappe.get_doc('Production', i)
		if debug:
			print(i, doc.docstatus)
		else:
			if doc.docstatus == 0:
				doc.submit()
				frappe.db.commit()
				print('Submitted successfully')
			else:
				print('Cannot submit records with docstatus: {}'.format(doc.docstatus))

# bench execute erpnext.temp_patch.cancel_sr --args "['SR/000035'],1,"
def cancel_sr(sr_list=[], debug=1):
	#for i in ('SR/000033', 'SR/000035', 'SR/000036'):
	for i in sr_list:
		print(i)
		doc = frappe.get_doc('Stock Reconciliation', i)
		if debug:
			print(i, doc.docstatus)
		else:
			if doc.docstatus == 1:
				doc.cancel()
				frappe.db.commit()
				print('Submitted successfully')
			else:
				print('Cannot submit records with docstatus: {}'.format(doc.docstatus))

# bench execute erpnext.temp_patch.submit_sr --args "['SR/000035-1'],1,"
def submit_sr(sr_list=[], debug=1):
	#for i in ('SR/000033', 'SR/000035', 'SR/000036'):
	for i in sr_list:
		print(i)
		doc = frappe.get_doc('Stock Reconciliation', i)
		if debug:
			print(i, doc.docstatus)
		else:
			if doc.docstatus == 0:
				doc.submit()
				frappe.db.commit()
				print('Submitted successfully')
			else:
				print('Cannot submit records with docstatus: {}'.format(doc.docstatus))

# back dated production entries 2019/07/02
def backdate_production():
	query = """
	select name, posting_date, posting_time, docstatus
	from `tabProduction`
	where name in ('PRO190700055','PRO190700054','PRO190700038','PRO190700053','PRO190700052',
	'PRO190700051','PRO190700050','PRO190700049','PRO190700048','PRO190700047',
	'PRO190700046','PRO190700045','PRO190700044','PRO190700043')
	and docstatus = 0
	order by posting_date, posting_time
	"""
	for i in frappe.db.sql(query, as_dict=True):
		print i
		doc = frappe.get_doc("Production", i.name)
		doc.submit()
		frappe.db.commit()

# Following method created by SHIV on 2019/04/15
# This method is created to update deduction details for Feb-2019 and Mar-2019 salary slips
def update_ssl_final():
        counter = 0
        for i in frappe.db.sql("select * from maintenance.sd_update where fiscal_year='2019' and month='03' order by creation", as_dict=True):
                counter += 1
                print counter,i.fiscal_year, i.month, i.qry
                frappe.db.sql(i.qry)
        frappe.db.commit()
                
def update_ssl_deductions():
        src_year  = "2019"
        src_month = "02"
        dest_year = "2019"
        dest_month= "03"
        qry = """
                select
                        ss.name, ss.employee, ss.fiscal_year, ss.month,
                        sd.name sd_name,
                        sd.salary_component,
                        sd.amount,
                        sd.institution_name,
                        sd.reference_type,
                        sd.reference_number,
                        sd.total_deductible_amount,
                        sd.total_deducted_amount,
                        sd.total_outstanding_amount,
                        sd.salary_component_type,
                        sd.ref_docname
                from `tabSalary Slip` ss, `tabSalary Detail` sd
                where ss.docstatus = 1
                {cond}
                and sd.parent = ss.name
                and sd.parentfield = 'deductions'
                order by ss.name
        """
        cond = "and ss.fiscal_year = '{fiscal_year}' and ss.month = '{month}'".format(fiscal_year=src_year, month=src_month)
        counter = log_single = log_multiple = log_notfound = 0
        
        for i in frappe.db.sql(qry.format(cond=cond), as_dict = True):
                counter += 1
                info = []
                amounts = []

                if i.get("institution_name"):
                        info.append("institution_name = '{0}'".format(i.get("institution_name")))
                if i.get("reference_type"):
                        info.append("reference_type = '{0}'".format(i.get("reference_type")))
                if i.get("reference_number"):
                        info.append("reference_number = '{0}'".format(i.get("reference_number")))
                if i.get("total_deductible_amount"):
                        info.append("total_deductible_amount = {0}".format(i.get("total_deductible_amount")))
                if i.get("total_deducted_amount"):
                        amounts.append("total_deducted_amount = {0}".format(flt(i.get("total_deducted_amount"))+flt(i.get("amount"))))
                if i.get("total_outstanding_amount"):
                        amounts.append("total_outstanding_amount = '{0}'".format(flt(i.get("total_outstanding_amount"))-flt(i.get("amount"))))
                if i.get("salary_component_type"):
                        info.append("salary_component_type = '{0}'".format(i.get("salary_component_type")))
                if i.get("ref_docname"):
                        info.append("ref_docname = '{0}'".format(i.get("ref_docname")))

                if info or amounts:
                        update_qry = []
                        cond = """
                                and ss.fiscal_year = '{fiscal_year}'
                                and ss.month = '{month}'
                                and ss.employee = '{employee}'
                                and sd.salary_component = '{salary_component}'
                        """.format(fiscal_year=dest_year, month=dest_month, employee=i.employee, salary_component=i.salary_component)
                        ssl = frappe.db.sql(qry.format(cond=cond), as_dict=True)
                        if len(ssl) > 1:
                                cond = """
                                        and ss.fiscal_year = '{fiscal_year}'
                                        and ss.month = '{month}'
                                        and ss.employee = '{employee}'
                                        and sd.salary_component = '{salary_component}'
                                        and sd.amount = {amount}
                                """.format(fiscal_year=dest_year, month=dest_month, employee=i.employee, salary_component=i.salary_component, amount=flt(i.amount))
                                ssl2 = frappe.db.sql(qry.format(cond=cond), as_dict=True)
                                if len(ssl2) > 1:
                                        print 'MULTIPLE SSL2',counter,i.name,i.sd_name,i.salary_component,i.amount,i.institution_name,i.reference_type,i.reference_number,i.total_deductible_amount,i.total_deducted_amount,i.total_outstanding_amount,i.salary_component_type,i.ref_docname
                                        log_multiple += 1
                                elif len(ssl2) == 1:
                                        log_single += 1
                                        if info:
                                                update_qry.append("update `tabSalary Detail` set " + ",".join(info)+" where name='{0}';".format(ssl2[0].sd_name))
                                        if amounts:
                                                update_qry.append("update `tabSalary Detail` set " + ",".join(amounts)+" where name='{0}';".format(ssl2[0].sd_name))
                                                update_qry.append("update `tabSalary Detail` set " + ",".join(amounts)+" where name='{0}';".format(i.ref_docname))
                                else:
                                        print 'NOT FOUND SSL2',counter,i.name,i.sd_name,i.salary_component,i.amount,i.institution_name,i.reference_type,i.reference_number,i.total_deductible_amount,i.total_deducted_amount,i.total_outstanding_amount,i.salary_component_type,i.ref_docname
                                        log_notfound += 1
                        elif len(ssl) == 1:
                                log_single += 1
                                if info:
                                        update_qry.append("update `tabSalary Detail` set " + ",".join(info)+" where name='{0}';".format(ssl[0].sd_name))
                                if amounts:
                                        update_qry.append("update `tabSalary Detail` set " + ",".join(amounts)+" where name='{0}';".format(ssl[0].sd_name))
                                        update_qry.append("update `tabSalary Detail` set " + ",".join(amounts)+" where name='{0}';".format(i.ref_docname))
                        else:
                                print 'NOT FOUND',counter,i.name,i.sd_name,i.salary_component,i.amount,i.institution_name,i.reference_type,i.reference_number,i.total_deductible_amount,i.total_deducted_amount,i.total_outstanding_amount,i.salary_component_type,i.ref_docname
                                log_notfound += 1

                        for uq in update_qry:
                                frappe.db.sql('insert into maintenance.sd_update values("{0}","{1}","{2}",{3})'.format(dest_year,dest_month,uq,"now()"))
                        
        print 'MULTIPLE',log_multiple,'SINGLE',log_single,'NOTFOUND',log_notfound
        frappe.db.commit()
                
# 2019/04/01
def update_production_sle(update="No"):
        counter = 0
        for i in frappe.db.sql("select name from temp_pro order by name", as_dict=True):
                counter += 1
                print counter, i.name
                voucher = frappe.db.sql("""
                                        select *
                                        from
                                                (select 'APPI' as tbl, name, item_code, qty, idx
                                                from `tabProduction Product Item`
                                                where parent = '{0}' order by idx) x
                                        union all
                                        select *
                                        from
                                                (select 'BPMI' tbl, name, item_code, qty, idx
                                                from `tabProduction Material Item`
                                                where parent = '{0}' order by idx) y
                                        order by tbl, idx
                                """.format(i.name), as_dict=True)
                sle = frappe.db.sql("select * from temp_sle where voucher_no = '{0}' order by name".format(i.name), as_dict=True)
                
                if len(voucher) == len(sle):
                        for j in range(len(voucher)):
                                if voucher[j].item_code == sle[j].item_code and abs(voucher[j].qty) == abs(sle[j].actual_qty):
                                        print j, 'PROD', i.name, voucher[j].item_code, voucher[j].idx, voucher[j].tbl, voucher[j].name, voucher[j].qty, 'SLE', sle[j].name, sle[j].item_code, sle[j].voucher_detail_no, sle[j].idx, sle[j].actual_qty
                                        if update.lower() == "yes":
                                                frappe.db.sql("""
                                                        update `tabStock Ledger Entry`
                                                        set voucher_detail_no = '{0}'
                                                        where name = '{1}'
                                                """.format(voucher[j].name, sle[j].name))                                     
                                else:
                                        frappe.throw(_("Values dont match"))
                else:
                        frappe.throw(_("Lengths dont match"))

                if (counter%100) == 0 and update.lower() == "yes":
                        counter = 0
                        frappe.db.commit()
        frappe.db.commit()
                
# Following method created by SHIV on 2020/10/06
def make_gl_for_dn(post=0):
	counter = 0
	for i in frappe.db.sql("""select name from `tabDelivery Note`
		where name in ('DN19092718','DN19100773','DN19100774','DN19100775',
				'DN19100904','DN19100905','DN19100906','DN19100918',
				'DN19102603','DN19102604','DN19102605','DN19110002',
				'DN19110041','DN19110043','DN19110146','DN19110530',
				'DN19110531','DN19110533','DN19110534','DN19110535',
				'DN19110908','DN19110909','DN19110910','DN19111110',
				'DN19111113','DN19120203','DN19120204','DN19120205',
				'DN19120206','DN19120254','DN19120256','DN19120332',
				'DN19120435','DN19120615','DN19120616','DN19120618'
				)
		""", as_dict=True):
		counter += 1
		print counter, i.name
		if post:
			print '\tdeleting gl...'
			frappe.db.sql("delete from `tabGL Entry` where voucher_type = 'Delivery Note' and voucher_no= '{}'".format(i.name))
			print '\tposting gl...'
			doc = frappe.get_doc("Delivery Note", i.name)
			doc.make_gl_entries(repost_future_gle=False)
	frappe.db.commit()

def production_gl():
	qry = """
	select name
	from `tabProduction` p
	where p.docstatus = 1 
	and not exists(select 1
			from `tabGL Entry` g
			where g.voucher_type = 'Production' 
			and g.voucher_no = p.name)
	order by name
	"""
	counter = 0
	for i in frappe.db.sql(qry, as_dict=True):
		counter += 1
		print counter, i.name
		doc = frappe.get_doc("Production", i.name)
		doc.make_gl_entries(repost_future_gle=False)
	frappe.db.commit()

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
        month   = '04'
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
