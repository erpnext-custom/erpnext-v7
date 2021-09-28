from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import msgprint
from frappe.utils import flt, cint
from frappe.utils.data import get_first_day, get_last_day, add_years, getdate, nowdate, add_days
from erpnext.custom_utils import get_branch_cc
import csv

def update_ss():
	count = 1
	for a in frappe.db.sql("select name from `tabSalary Structure` where is_active = 'Yes' and branch = 'Chunaikhola Dolomite Mine'", as_dict = 1):
		doc = frappe.get_doc("Salary Structure", a.name)
		count += 1
		doc.save(ignore_permissions = True)
		print(a.name)

def get_eme_payment():
	for d in frappe.db.sql("""
		SELECT ep.equipment_type,ep.name
			FROM 
				(SELECT DISTINCT(epi.equipment_type), 
					ep.branch,ep.posting_date, ep.name
			FROM `tabEME Payment` ep, `tabEME Payment Item` epi 
			WHERE epi.parent = ep.name and  ep.name = 'EP210400007') ep
	""",as_dict = True):
		# print(d.equipment_type,d.name)
		data = frappe.db.sql("""
			SELECT COUNT(*) from
				(select distinct equipment_no  
					from `tabEME Payment Item` 
				where parent = '{0}' and equipment_type='{1}') c
		""".format(d.name,d.equipment_type))
		print(data)



def copy_direct_payment():
	for d in frappe.db.sql("""
	select name,
		amount,
		taxable_amount,
		tds_amount,
		net_amount,
		supplier,
		party_type,
		party,
		owner,
		parentfield,
		parenttype
	from `tabDirect Payment` 
	where posting_date between '2020-01-01' and '2020-12-31'
	""",as_dict=True):
		frappe.db.sql("""
		INSERT INTO `tabDirect Payment Item` (amount,tds_amount,taxable_amount,net_amount,party_type,party,parent,owner,parentfield,parenttype) 
			values('{}','{}','{}','{}',
			'{}','{}','{}','{}','{}','{}')
		""".format(d.amount,d.tds_amount,d.taxable_amount,d.net_amount,d.party_type,d.party,d.name,d.owner,d.parentfield,d.parenttype))

def copy_to_production_entry():
	i = 0
	for d in frappe.db.sql("""
		select 
			name,
			transportation_amount,
			qty,
			transportation_rate,
			item_code,
			ref_doc,
			transportation_rate * qty as amount,
			equipment_number
		from `tabProduction Entry`
		where (transportation_rate * qty ) != transportation_amount
	""",as_dict= True):
		frappe.db.sql("""
				UPDATE
					`tabProduction Entry`
				SET 
					transportation_amount = '{}'
				WHERE 
					name = '{}' 
				""".format(d.amount,d.name))
		i+=1
		print(d.name,d.equipment_number,d.ref_doc,d.item_code,d.transportation_amount,d.transportation_rate,d.qty,d.amount)
	print(i)
	# for d in frappe.db.sql("""
	# 		select 
	# 			p.rate,
	# 			p.name,
	# 			p.equipment_number,
	# 			p.amount,
	# 			pe.transportation_amount,
	# 			pe.name as entry_name,
	# 			p.item_code,
	# 			pe.qty,
	# 			p.rate
	# 		from 
	# 		(
	# 			SELECT
	# 				p.to_warehouse,
	# 				pi.rate,
	# 				pi.qty,
	# 				pi.amount,
	# 				pi.item_code,
	# 				p.name,
	# 				pi.equipment_number
	# 			FROM
	# 				`tabProduction` p
	# 			INNER JOIN 
	# 				`tabProduction Product Item` pi 
	# 			ON p.name = pi.parent
	# 			WHERE pi.parent = p.name
	# 			and p.docstatus = 1 and (pi.equipment_number !="" or pi.equipment_number IS NOT NULL)
	# 		) p 
	# 		INNER JOIN `tabProduction Entry` pe
	# 		on pe.ref_doc = p.name 
	# 		where pe.ref_doc = p.name
	# 		and	p.amount != pe.transportation_amount 
	# 		and p.item_code = pe.item_code 
	# 		and p.equipment_number = pe.equipment_number 
	# 		and p.qty = pe.qty 
	# 		and p.rate = pe.transportation_rate 
	# 		and ( p.qty *  p.rate != pe.transportation_amount)
	# 	""",as_dict=True):
	# 	frappe.db.sql("""
	# 			UPDATE
	# 				`tabProduction Entry`
	# 			SET 
	# 				transportation_amount = '{}'
	# 			WHERE 
	# 				name = '{}' 
	# 			AND ref_doc = '{}'
	# 			AND item_code = '{}' 
	# 			AND equipment_number ='{}' 
	# 			AND qty = '{}' 
	# 			AND transportation_rate = '{}'
	# 			""".format(d.amount, d.entry_name,d.name,d.item_code,d.equipment_number,d.qty,d.rate))
	# 	i += 1
		
# (348.66, u'PRO210102060', u'BP-2-A9129', 342.72, u'PRODE210104294', u'300034')
# (346.14, u'PRO210102060', u'BP-2-A9129', 342.72, u'PRODE210104294', u'300034')
# (354.78, u'PRO210102060', u'BP-2-A9129', 342.72, u'PRODE210104294', u'300034')
# (342.36, u'PRO210102060', u'BP-2-A9129', 342.72, u'PRODE210104294', u'300034')
# (341.46, u'PRO210102060', u'BP-2-A9129', 342.72, u'PRODE210104294', u'300034')
# (345.24, u'PRO210102060', u'BP-2-A9129', 342.72, u'PRODE210104294', u'300034')
# (346.14, u'PRO210102060', u'BP-2-A9129', 342.72, u'PRODE210104294', u'300034')
# (348.66, u'PRO210102060', u'BP-2-A9129', 342.72, u'PRODE210104294', u'300034')
# (348.66, u'PRO210102060', u'BP-2-A9129', 342.72, u'PRODE210104295', u'300034')
	# i = 1
	# for a in frappe.db.sql("""
	# 		SELECT
	# 			p.to_warehouse,
	# 			pi.rate,
	# 			pi.amount,
	# 			pi.item_code,
	# 			p.name,
	# 			pi.equipment_number
	# 		FROM
	# 			`tabProduction` p
	# 		INNER JOIN 
	# 			`tabProduction Product Item` pi 
	# 		ON p.name = pi.parent
	# 		WHERE pi.parent = p.name
	# 		and p.transfer = 1 and p.docstatus = 1 and (pi.equipment_number !="" or pi.equipment_number IS NOT NULL)
	# 		and p.posting_date > '2021-01-01'
	# 	""",as_dict=True):
	# 	if frappe.db.exists("Production Entry", {"ref_doc":a.name, "item_code": a.item_code, "equipment_number": a.equipment_number}):
	# 		doc = frappe.get_doc("Production Entry", {"ref_doc":a.name, "item_code": a.item_code, "equipment_number": a.equipment_number})
	# 		frappe.db.sql("""
	# 			UPDATE
	# 				`tabProduction Entry`
	# 			SET 
	# 				transfer_to_warehouse='{}',
	# 				transportation_rate = '{}',
	# 				transportation_amount = '{}'
	# 			WHERE 
	# 				name = '{}'
	# 			""".format(a.to_warehouse, a.rate, a.amount, doc.name))
	# 		print("SL: " + str(i) + "PE : " + str(doc.name) + " Amount " + str(a.amount) + "Rate: " + str(a.rate) + "to_warehouse : " + str(a.to_warehouse))
	# 		i+=1
	# 	else:
	# 		print("Doest not exists : " + a.name )	
			
def equipment_number_update():
	for a in frappe.db.sql("""
		SELECT 
			name,
			equipment_number
		FROM `tabProduction Entry`
		WHERE equipment_number = ' BP-1-A1423.'
		""",as_dict=True):
		frappe.db.sql("""
		UPDATE `tabProduction Entry` SET equipment_number = 'BP-1-A1423' WHERE name = '{}'
		""".format(a.name))
	
def logbook_total_hour_update():
	for a in frappe.db.sql("""
		SELECT 
			l.name, l.total_hours, (SELECT sum(i.hours) FROM `tabLogbook Item` i WHERE i.parent = l.name) as hours
		FROM `tabLogbook` l
		WHERE 
			l.branch='Khothakpa Gypsum Mine' AND l.posting_date between '2021-06-01' AND '2021-06-20' AND 
			l.equipment_type='Tipper(Mining)' AND l.total_hours != (SELECT sum(i.hours) FROM `tabLogbook Item` i WHERE i.parent = l.name)
		""",as_dict=True):

		frappe.db.sql("""
        UPDATE `tabLogbook` set total_hours = '{}' WHERE name = '{}'
		""".format(a.hours,a.name))
		print("HI 1998")

def remove_gl_party():
	i  = 1
	for a in frappe.db.sql("""select g.name, g.party, g.party_type, g.account, a.account_type
						from `tabGL Entry` g, `tabAccount` a 
						where g.account = a.name and 
						a.account_type NOT IN ('Receivable', 'Payable')
						and length(g.party) > 0
						""", as_dict=True):
		#frappe.db.sql("update `tabGL Entry` set party = '', party_type = '' where name = '{}'".format(a.name))
		#frappe.db.commit()
		print("Done" + str(i) + " | " +str(a.name) +" | " + str(a.account) + " | " + str(a.party) + "|"+ str(a.account_type))
		i+=1

def copy_issue_to_employee():
	for a in frappe.db.sql("""
		SELECT 
			name, issued_to
		FROM 
			`tabStock Entry Detail`
		""",as_dict=True):
		if 'EMP/' in str(a.issued_to):
			frappe.db.sql("""
				UPDATE
					`tabStock Entry Detail`
				SET 
					issued_to_employee = '{0}'
				WHERE 
					name = '{1}'
			""".format(a.issued_to,a.name))
		elif 'EQUIP' in str(a.issued_to):
			frappe.db.sql("""
				UPDATE
					`tabStock Entry Detail`
				SET 
					issued_to_equipment = '{0}'
				WHERE 
					name = '{1}'
			""".format(a.issued_to,a.name))

def update_ot_jv():
	i = 0
	for a in frappe.db.sql("""select name, payment_jv, posting_date
				from `tabOvertime Application` 
				where (payment_jv is NOT NULL or payment_jv !='') 
				and posting_date between '2021-01-01' and '2021-02-11'""", as_dict=True):
		if frappe.db.exists("Journal Entry", a.payment_jv):
			doc = frappe.get_doc("Journal Entry", a.payment_jv)
			'''
			if doc.docstatus == 1:
				frappe.db.sql("delete from `tabGL Entry` where voucher_no = '{}'".format(a.payment_jv))
			frappe.db.sql("delete from `tabJournal Entry` where name ='{}'".format(a.payment_jv))
			frappe.db.sql("delete from `tabJournal Entry Account` where parent='{}'".format(a.payment_jv))
			frappe.db.sql("update `tabOvertime Application` set payment_jv='' where name ='{}'".format(a.name))
			frappe.db.commit()
			'''
			i+=1
			print(str(i) + " JV :" + a.payment_jv + " Docstatus : " + str(doc.docstatus) + " posting_date : " + str(doc.posting_date))
		else:
			print("Does not exisit" + str(i) + " JV :" + str(a.payment_jv) + " Name: " + str(a.name))


def update_transportation_se():
	for a in frappe.db.sql("""
						Select 
						name, 
						equipment, 
						equipment_number,
						equipment_type,
						weight_slip_no,
						gross_vehicle_weight,
						tyre_weight,
						pol_slip_no, 
						equipment_model,
						transporter_name,
						vehicle_dispatch_date_and_time,
						project,
						remarks,
						customers,
						location,
						rate_base_on_distance,
						distance,
						transportation_rate,
						unloading_by from `tabStock Entry` 
						where (equipment !='' OR equipment is NOT NULL) 
						and transport_payment_done = 0""", as_dict=True):
		child_count = 0
		for b in frappe.db.sql("select count(*) as count from `tabStock Entry Detail` where parent = '{}'".format(a.name), as_dict=True):
			child_count = b.count
		if child_count == 1:
			frappe.db.sql("""
				UPDATE `tabStock Entry Detail` 
				SET equipment = '{0}',
				equipment_number = '{1}',
				equipment_type = '{2}',
				weight_slip_no = '{3}',
				gross_vehicle_weight = '{4}',
				tyre_weight = {5},
				pol_slip_no = '{6}',
				equipment_model ='{7}',
				transporter_name = '{8}',
				vehicle_dispatch_date_and_time='{9}',
				project='{10}',
				customers='{11}',
				location='{12}',
				rate_base_on_distance='{13}',
				distance='{14}',
				transportation_rate={15},
				unloading_by='{16}'
				WHERE parent = '{17}'
			""".format(a.equipment,a.equipment_number,a.equipment_type,a.weight_slip_no,
			a.gross_vehicle_weight,a.tyre_weight,a.pol_slip_no,a.equipment_model,
			a.transporter_name,a.vehicle_dispatch_date_and_time,a.project,
			a.customers,a.location,a.rate_base_on_distance,a.distance,a.transportation_rate,a.unloading_by,a.name))

# bench execute erpnext.custom_patch.update_transportation_se
# following method created by SHIV on 2021/01/28 to remove expired salary advance entries
def remove_expired_salary_advance(submit=0):
	expiry_date = "2020-12-31"
	salary_component = "Salary Advance Deductions"

	li = frappe.db.sql("""
		SELECT sd.name salary_detail, sst.name salary_structure, sst.employee, 
			sst.employee_name, sd.from_date, sd.to_date, sd.amount
		FROM `tabSalary Detail` sd, `tabSalary Structure` sst, `tabEmployee` e
		WHERE sst.is_active = 'Yes'
		AND e.name = sst.employee
		AND sd.parent = sst.name
		AND sd.salary_component = '{salary_component}'
		AND sd.parentfield = 'deductions'
		AND (
				(sd.to_date IS NOT NULL AND sd.to_date <= '{expiry_date}' )
				OR
				(sd.amount = 0)
			)
		AND EXISTS(SELECT 1
				FROM tmp_sa t
				WHERE t.employee = sst.employee)
		ORDER BY sst.employee
	""".format(expiry_date = expiry_date, salary_component = salary_component), as_dict=True)

	counter = 0
	for i in li:
		counter += 1
		print counter, i.salary_detail, i.employee, i.salary_structure, i.from_date, i.to_date, i.amount, i.employee_name

		# create backup record
		if submit:
			frappe.db.sql("insert into `tabSalary Detail Backup` select * from `tabSalary Detail` where name = '{}'".format(i.salary_detail))
			frappe.db.sql("delete from `tabSalary Detail` where name = '{}'".format(i.salary_detail))
			sst = frappe.get_doc("Salary Structure", i.salary_structure)
			sst.save(ignore_permissions=True)
			frappe.db.commit()

def pass_eme_payment():
	for a in frappe.db.sql("select name from `tabEME Payment` where docstatus = 1", as_dict=1):
		doc = frappe.get_doc("EME Payment", a.name)
		doc.update_general_ledger()

def eme_eqp_update():
	for a in frappe.db.sql("select name, equipment from `tabEME Payment Item`", as_dict=1):
		doc = frappe.get_doc("Equipment", a.equipment)
		frappe.db.sql("update `tabEME Payment Item` set equipment_type = '{0}' where name = '{1}'".format(doc.equipment_type, a.name))

def eme_update_trans():
	for e in frappe.db.sql("select name from tabEquipment where branch = 'Tshophangma'", as_dict=1):
		print("Equipment {0}".format(e.name))
		for h in frappe.db.sql("select name from `tabEquipment Hiring Form` where equipment = '{0}'".format(e.name), as_dict=1):
			frappe.db.sql("update `tabEquipment Hiring Form` set branch = 'Tshophangma' where name = '{0}'".format(h.name))

		for l in frappe.db.sql("select name from `tabLogbook` where equipment = '{0}'".format(e.name), as_dict=1):
			frappe.db.sql("update `tabLogbook` set branch = 'Tshophangma' where name = '{0}'".format(l.name))
			

def eme_check():
	for a in frappe.db.sql("select branch, name, equipment from `tabLogbook` where docstatus = 1", as_dict=1):
		#print("Checking {0}".format(a.name))
		branch = frappe.get_doc("Branch", a.branch)
		if branch.is_disabled:
			print("{0} branch is disabled".format(a.name) )
		ep = frappe.get_doc("Equipment", a.equipment)
		if ep.is_disabled:
			print("{0} equipment is disabled".format(a.name) )
		if ep.branch != a.branch:
			print("{0} different".format(a.name) )

def update_order():
	for a in frappe.db.sql("select name from `tabExpense Head`", as_dict=1):
		doc = frappe.get_doc("Expense Head", a.name)
		doc.db_set("order_index", doc.order)

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

# def update_ss():
# 	empl = frappe.db.sql("select name from `tabEmployee`", as_dict=True)
# 	for emp in empl:
# 		e = frappe.get_doc("Employee", emp.name)
# 		ss_name = frappe.db.sql("select name from `tabSalary Structure` where is_active = 'Yes' and employee = %s", (emp.name), as_dict=True)
# 		for a in ss_name:
# 			ss = frappe.get_doc("Salary Structure", a.name)
# 			ss.db_set("branch", e.branch)
# 			ss.db_set("department", e.department)
# 			ss.db_set("division", e.division)
# 			ss.db_set("section", e.section)
# 			ss.db_set("designation", e.designation)

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

def update_item_sub_group(): 
	with open("/home/frappe/erp/apps/erpnext/erpnext/3_Purchase___Stores_Vo_81.csv") as f:
		reader = csv.reader(f)
		mylist = list(reader)
		for i in mylist:
			frappe.db.sql("""update `tabItem` set item_sub_group = '{}' where name = '{}' """.format(i[5], i[2]))
			print("SRNO: {} ".format(i[0]))
			# 	print("DONE FOR ITEM: {}  --- mgroup: {} -----msubgroup: {} ".format(i[2], i[4], i[5]))

def update_salary_structure():
	ss = frappe.get_all("Salary Structure", {'is_active': 'Yes'})
	print(ss)
	count = 1
	for a in ss:
		d = frappe.get_doc("Salary Structure", a.name)
		d.save()
		print(d)
		print(count)
		count += 1

def update_nppf_agency_code():
	emp = frappe.db.sql("SELECT employment_type from `tabEmployee` where status = 'Active'", as_dict=True)

	c1 = c2 = 0
	for e in emp:
		if e.employment_type == 'ESP':
			frappe.db.sql("update `tabEmployee` set nppf_agency_code = 'CES0000020' where employment_type='ESP'")
			c2 += 1
		elif e.employment_type == 'Contract' or e.employment_type == 'Regular employees':
			frappe.db.sql("update `tabEmployee` set nppf_agency_code = 'CGC0000067' where (employment_type='Contract' or employment_type='Regular employees')")
			c1 += 1
		
 	print(c1)
	print(c2)

def update_bank_branch_and_account_type():
	emp = frappe.db.sql(" SELECT name from `tabEmployee` where status = 'active'", as_dict=True)

	for e in emp:
		frappe.db.sql("update `tabEmployee` set bank_branch = 'Samtse Branch - BOBL', bank_account_type='Savings' where name = %s", e.name)
		print(e.name)

