from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import msgprint
from frappe.utils import flt, cint, now, getdate
from frappe.utils.data import get_first_day, get_last_day, add_years, date_diff, today, get_first_day, get_last_day
#from erpnext.hr.hr_custom_functions import get_month_details, get_company_pf, get_employee_gis, get_salary_tax, update_salary_structure
from erpnext.hr.hr_custom_functions import get_month_details, get_salary_tax
import collections
from frappe.model.naming import make_autoname

def submit_dn_20230116():
        counter = 0
        for i in frappe.db.sql("""select * from `tabDelivery Note`
                where name in ('DN22113201','DN22113070','DN22113068','DN22113062',
                'DN22113061','DN22112487','DN22112128','DN22112126',
                'DN22112124','DN22112079','DN22112078','DN22112076',
                'DN22112073','DN22112072','DN22112071','DN22112070',
                'DN22112061','DN22112060','DN22112058','DN22112056',
                'DN22112054','DN22112052','DN22112050','DN22112044',
                'DN22112043','DN22112042','DN22112041','DN22112038',
                'DN22112037','DN22112032','DN22111832','DN22111831',
                'DN22111825','DN22111824','DN22111817','DN22111816',
                'DN22111811','DN22111810','DN22111809','DN22111808',
                'DN22111775','DN22111773','DN22111770','DN22111767',
                'DN22111760','DN22111675','DN22111669','DN22111664',
                'DN22111662','DN22111661','DN22111657','DN22111655',
                'DN22111649','DN22111643','DN22111639','DN22111634',
                'DN22111631','DN22111627','DN22111623','DN22111620',
                'DN22111616','DN22111613','DN22111612','DN22111611',
                'DN22111598','DN22111594','DN22111591','DN22111587',
                'DN22111584','DN22110909','DN22110907','DN22110904',
                'DN22110901','DN22110899','DN22110898','DN22110894',
                'DN22110884','DN22110881','DN22110868','DN22110864',
                'DN22110861','DN22110859','DN22110854','DN22110846',
                'DN22110844','DN22110839','DN22094675','DN22094676',
                'DN22094677','DN22094679','DN22094680','DN22094682',
                'DN22094225','DN22094223','DN22094222','DN22094210',
                'DN22094209','DN22094208','DN22094205','DN22093836',
                'DN22092959','DN22092932')
                order by posting_date""", as_dict=True):
                counter += 1
                print(i.name, i.posting_date, i.docstatus)
                if i.docstatus == 0:
                        try:
                                doc = frappe.get_doc("Delivery NOte", doc.name)
                                doc.submit()
                                frappe.db.commit()
                        except Exception as e:
                                print(str(e))
        frappe.db.commit()

def submit_sr20230114(submit=0):
        counter = 0
        for i in frappe.db.sql("""select name from `tabStock Reconciliation`
                where name in ('SR/000616', 'SR/000617', 'SR/000618', 'SR/000619', 'SR/000621')""", as_dict=True):
                counter += 1
                doc = frappe.get_doc('Stock Reconciliation', i.name)
                print(counter, doc.name, doc.docstatus)
                if submit:
                        try:
                                doc.submit()
                                print 'Submitted successfully...'
                        except Exception, e:
                                print 'ERROR: ', str(e)
                frappe.db.commit()

def submit_sr20230112(submit=0):
	counter = 0
	for i in frappe.db.sql("""select name from `tabStock Reconciliation`
		where name in ('SR/000600','SR/000585','SR/000583','SR/000579',
			'SR/000577','SR/000575','SR/000574','SR/000568',
			'SR/000564','SR/000563','SR/000560','SR/000558',
			'SR/000556','SR/000537','SR/000524','SR/000523',
			'SR/000504-2','SR/000316','SR/000370','SR/000319')""", as_dict=True):
		counter += 1
		doc = frappe.get_doc('Stock Reconciliation', i.name)
		print(counter, doc.name, doc.docstatus)
		if submit:
			try:
				doc.submit()
			except Exception, e:
				print 'ERROR: ', str(e)
			print 'Submitted successfully...'
		frappe.db.commit()

# given by Jamyang & Sangay, NRDCL 2023/01/1
def submit_pr20210511():
	print('Submitting Stock Reconciliation...')
	counter = 0
	for i in frappe.db.sql("""select name from `tabProduction`
		where name in ('PRO210500455', 'PRO210500456')
		and docstatus = 0""", as_dict=True):
		counter += 1
		doc = frappe.get_doc('Production', i.name)
		print counter, doc.name, doc.docstatus, 'Submitting...'
		doc.submit()
		frappe.db.commit()
		print 'Submitted successfully...'

# given by Mani Gyeltshen, NRDCL 2021/06/02
def submit_cancel_pr20210602():
	print('Submitting Production entry...')
	counter = 0
	for i in frappe.db.sql("""select name from `tabProduction`
		where name in ('PRO210600075')
		and docstatus = 0""", as_dict=True):
		counter += 1
		doc = frappe.get_doc('Production', i.name)
		print counter, doc.name, doc.docstatus, 'Submitting...'
                doc.submit()
                frappe.db.commit()
		print 'Submitted successfully...'

	print('Cancelling Production entry...')
	counter = 0
	for i in frappe.db.sql("""select name from `tabProduction`
		where name in ('PRO210500496')
		and docstatus = 1""", as_dict=True):
		counter += 1
		doc = frappe.get_doc('Production', i.name)
		print counter, doc.name, doc.docstatus, 'Submitting...'
                doc.cancel()
                frappe.db.commit()
		print 'Cancelled successfully...'

# given by Mani Gyeltshen, NRDCL 2021/05/11
def submit_pr20210511():
	print('Submitting Stock Reconciliation...')
	counter = 0
	for i in frappe.db.sql("""select name from `tabProduction`
		where name in ('PRO210500455', 'PRO210500456')
		and docstatus = 0""", as_dict=True):
		counter += 1
		doc = frappe.get_doc('Production', i.name)
		print counter, doc.name, doc.docstatus, 'Submitting...'
                doc.submit()
                frappe.db.commit()
		print 'Submitted successfully...'

	print('\nCancelling Stock Reconciliation...')
	counter = 0
	for i in frappe.db.sql("""select name from `tabStock Reconciliation`
		where name in ('SR/000168')
		and docstatus = 1""", as_dict=True):
		counter += 1
		doc = frappe.get_doc('Stock Reconciliation', i.name)
		print counter, doc.name, doc.docstatus, 'Cancelling...'
                doc.cancel()
                frappe.db.commit()
		print 'Submitted successfully...'

# given by Mani Gyeltshen, NRDCL 2021/05/03
def submit_pr20210503():
	print('SUBMIT===>')
	counter = 0
	for i in frappe.db.sql("""select name from `tabProduction`
		where name in ('PRO210500076')
		and docstatus = 0""", as_dict=True):
		counter += 1
		doc = frappe.get_doc('Production', i.name)
		print counter, doc.name, doc.docstatus, 'Submitting...'
                doc.submit()
                frappe.db.commit()
		print 'Submitted successfully...'
	
# given by Mani Gyeltshen, NRDCL 2021/04/15
def submit_pr20210415():
	print('SUBMIT===>')
	counter = 0
	for i in frappe.db.sql("""select name from `tabProduction`
		where name in ('PRO210401031', 'PRO210401032')
		and docstatus = 0""", as_dict=True):
		counter += 1
		doc = frappe.get_doc('Production', i.name)
		print counter, doc.name, doc.docstatus, 'Submitting...'
                doc.submit()
                frappe.db.commit()
		print 'Submitted successfully...'

	print('CANCEL===>')
	counter = 0
	for i in frappe.db.sql("""select name from `tabProduction`
		where name in ('PRO210100246', 'PRO210100250')
		and docstatus = 1""", as_dict=True):
		counter += 1
		doc = frappe.get_doc('Production', i.name)
		print counter, doc.name, doc.docstatus, 'Cancelling...'
                doc.cancel()
                frappe.db.commit()
		print 'Cancelled successfully...'


# given by Mani Gyeltshen, NRDCL 2021/04/08
def submit_pr20210408():
	print('CANCEL===>')
	counter = 0
	for i in frappe.db.sql("""select name from `tabProduction`
		where name in ('PRO210302090')
		and docstatus = 1""", as_dict=True):
		counter += 1
		doc = frappe.get_doc('Production', i.name)
                doc.cancel()
                frappe.db.commit()
		print counter, doc.name, doc.docstatus, 'Cancelling...'
		print 'Cancelled successfully...'

	print('SUBMIT===>')
	counter = 0
	for i in frappe.db.sql("""select name from `tabProduction`
		where name in ('PRO210400416','PRO210400429', 'PRO210400430','PRO210400431','PRO210400432','PRO210400433')
		and docstatus = 0""", as_dict=True):
		counter += 1
		doc = frappe.get_doc('Production', i.name)
                doc.submit()
                frappe.db.commit()
		print counter, doc.name, doc.docstatus, 'Submitting...'
		print 'Submitted successfully...'

# create by SHIV on 2021/04/08
def submit_sr20210408(submit=0):
	counter = 0
	for i in frappe.db.sql("""select name from `tabStock Reconciliation`
		where name in ('SR/000164', 'SR/000168')""", as_dict=True):
		counter += 1
		doc = frappe.get_doc('Stock Reconciliation', i.name)
		print counter, doc.name, doc.docstatus
		if submit:
			try:
				doc.submit()
			except Exception, e:
				print 'ERROR: ', str(e)
			print 'Submitted successfully...'
		frappe.db.commit()

# following method created by SHIV to submit different entries together, 2021/01/05 req.by Birkha
def submit_entries():
	prod = frappe.get_doc("Production", "PRO201100933")
	#prod = frappe.get_doc("Production", "PRO201200741")
	#dn = frappe.get_doc("Delivery Note", "DN20112745-1")
	
	if prod.docstatus == 0:
		print("Production", prod.name, "Submitting...")
		prod.submit()
		frappe.db.commit()
	#if dn.docstatus == 0:
	#	print("Delivery ", dn.name, "Submitting...")
	#	dn.submit()
	#	frappe.db.commit()

# following method created by SHIV to submit DNs given by jamyang 2020/12/22
# temporarily stopped as other transactions needs to be taken care first on priority
def submit_dn(debug=1):
	counter = 0
	for i in frappe.db.sql("""select dn.name from `tabDelivery Note` dn
				where exists(select 1 from temp t where t.name = dn.name)
				and dn.docstatus = 0
				order by dn.posting_date
			""", as_dict=True):
		counter += 1
		doc = frappe.get_doc('Delivery Note', i.name)
		print(now(), counter, doc.name, str(doc.posting_date), doc.docstatus)
		if not debug:
			doc.submit()
			frappe.db.commit()

# Lot list item updatgion, 2020/10/29, Shiv->Kinley Dorji
# bench execute erpnext.temp_patch.create_lot_list_item
def create_lot_list_item():
	for i in frappe.db.get_all("Lot List", "name"):
		print i
		lot = frappe.get_doc("Lot List", i.name)
		row = lot.append("lot_list_items", {})
		row.item_sub_group = lot.item_sub_group
                row.item = lot.item
                row.item_name = frappe.db.get_value("Item", lot.item,"item_name")
                row.t_species = frappe.db.get_value("Item",lot.item,"species")
                row.timber_class = frappe.db.get_value("Timber Species",frappe.db.get_value("Item",lot.item,"species"),"timber_class")
                row.total_volume = lot.total_volume
                row.total_pieces = lot.total_pieces
		row.save(ignore_permissions=True)

def cancel_pr():
        #for a in frappe.db.sql("select name from `tabPurchase Receipt` where name in ('PR20030002','PR20030106')", as_dict=True):
	doc = frappe.get_doc("Purchase Receipt", "PR20030106")
	doc.cancel()
	frappe.db.commit()
	print doc.name, doc.docstatus


def submit_production1():
	counter = 0
	for i in frappe.db.sql("""select name from `tabProduction`
		where name in ('PRO201100110')""", as_dict=True):
		counter += 1
		doc = frappe.get_doc('Production', i.name)
                doc.submit()
                frappe.db.commit()
		print counter, doc.name, doc.docstatus
		print 'Submitted successfully...'
		

# create by SHIV on 2020/10/23
def submit_production(submit=0):
	counter = 0
	for i in frappe.db.sql("""select name from `tabProduction`
		where name in ('PRO200900180-3','PRO201000312','PRO201000313','PRO201000315','PRO201000316')""", as_dict=True):
		counter += 1
		doc = frappe.get_doc('Production', i.name)
		print counter, doc.name, doc.docstatus
		if submit:
			try:
				doc.submit()
			except Exception, e:
				print 'ERROR: ', str(e)
			print 'Submitted successfully...'
		frappe.db.commit()

# create by SHIV on 2020/10/22
def submit_stock_reconciliation(submit=0):
	counter = 0
	for i in frappe.db.sql("""select name from `tabStock Reconciliation`
		where name in ('SR/000110','SR/000154','SR/000153','SR/000085','SR/000086','SR/000112','SR/000113','SR/000156','SR/000157')""", as_dict=True):
		counter += 1
		doc = frappe.get_doc('Stock Reconciliation', i.name)
		print counter, doc.name, doc.docstatus
		if submit:
			try:
				doc.submit()
			except Exception, e:
				print 'ERROR: ', str(e)
			print 'Submitted successfully...'
		frappe.db.commit()

# Created by SHIV on 2019/12/12
def refresh_salary_structures(debug=1):
        counter = 0
        for i in frappe.db.get_all("Salary Structure", "name", {"is_active": "Yes"}):
                counter += 1
                print counter, i.name
                if not debug:
                        doc = frappe.get_doc("Salary Structure", i.name)
                        doc.save()
        
def update_new_payscale_arrears(debug=1):
        counter = 0
        for i in frappe.db.sql("""
                        select sst.name, sr.new_basic, sr.basic_arrears, sr.salary_arrears
                        from
                                `tabSalary Structure` sst,
                                maintenance.salary_revision2019 sr
                        where sst.is_active = 'Yes'
                        and sst.from_date = '2019-12-01'
                        and sr.employee = sst.employee
                        and (ifnull(sr.basic_arrears,0) > 0 or ifnull(sr.salary_arrears,0))
                """, as_dict=True):
                counter += 1
                print counter, i
                if not debug:
                        print 'updating....'
                        doc = frappe.get_doc("Salary Structure", i.name)
                        if flt(i.basic_arrears):
                                row = doc.append("earnings", {})
                                row.salary_component = "Basic Pay Arrears"
                                row.amount          = flt(i.basic_arrears)
                                row.from_date        = "2019-12-01"
                                row.to_date          = "2019-12-31"
                                row.save(ignore_permissions=True)
                        if flt(i.salary_arrears):
                                row = doc.append("earnings", {})
                                row.salary_component = "Salary Arrears"
                                row.amount          = flt(i.salary_arrears)
                                row.from_date        = "2019-12-01"
                                row.to_date          = "2019-12-31"
                                row.save(ignore_permissions=True)                                
                        doc.save()
                        
def update_new_payscale_basic(debug=1):
        counter = 0
        for i in frappe.db.sql("""
                        select sst.name, sr.new_basic, sr.basic_arrears, sr.salary_arrears
                        from
                                `tabSalary Structure` sst,
                                maintenance.salary_revision2019 sr
                        where sst.is_active = 'Yes'
                        and sst.from_date = '2019-12-01'
                        and sr.employee = sst.employee
                """, as_dict=True):
                counter += 1
                print counter, i
                if not debug:
                        print 'updating....'
                        if not frappe.db.exists("Salary Detail", {"parent": i.name, "salary_component": "Basic Pay"}):
                                frappe.throw(_("Basic Pay component not found"))
                        #basic = frappe.get_doc("Salary Detail", {"parent": i.name, "salary_component": "Basic Pay"})
                        #basic.db_set("amount",i.new_basic)
                        doc = frappe.get_doc("Salary Structure", i.name)
                        for j in doc.get('earnings'):
                                if j.salary_component == "Basic Pay":
                                        j.amount = i.new_basic
                                        break
                        doc.save()
        
def update_new_payscale_master(debug=1):
        counter = 0
        for i in frappe.db.get_all("Salary Structure", "name", {"is_active": "Yes", "from_date": "2019-12-01"}):
                counter += 1
                print counter, i
                if not debug:
                        doc = frappe.get_doc("Salary Structure", i.name)
                        doc.ca = 20 if flt(doc.ca) == 23 else doc.ca
                        doc.eligible_for_psa = 0
                        doc.psa = 0
                        doc.save()
                
def create_new_salary_structures(debug=1):
        def duplicate_structure(old_sst):
                old = frappe.get_doc("Salary Structure", old_sst)
                old.is_active   = 'No'
                old.to_date     = '2019-11-30'
                old.save(ignore_permissions=True)
                print 'update old_structure'
                new = {
                        "doctype": "Salary Structure",
                        "employee": old.employee,
                        "is_active": "Yes",
                        "from_date": "2019-12-01",
                        "eligible_for_corporate_allowance": old.eligible_for_corporate_allowance,
                        "ca_method": old.ca_method,
                        "ca": old.ca,
                        "eligible_for_contract_allowance": old.eligible_for_contract_allowance,
                        "contract_allowance_method": old.contract_allowance_method,
                        "contract_allowance": old.contract_allowance,
                        "eligible_for_communication_allowance": old.eligible_for_communication_allowance,
                        "communication_allowance_method": old.communication_allowance_method,
                        "communication_allowance": old.communication_allowance,
                        "eligible_for_fuel_allowances": old.eligible_for_fuel_allowances,
                        "fuel_allowances_method": old.fuel_allowances_method,
                        "fuel_allowances": old.fuel_allowances,
                        "eligible_for_shift": old.eligible_for_shift,
                        "shift_method": old.shift_method,
                        "shift": old.shift,
                        "eligible_for_difficulty": old.eligible_for_difficulty,
                        "difficulty_method": old.difficulty_method,
                        "difficulty": old.difficulty,
                        "eligible_for_high_altitude": old.eligible_for_high_altitude,
                        "high_altitude_method": old.high_altitude_method,
                        "high_altitude": old.high_altitude,
                        "eligible_for_psa": old.eligible_for_psa,
                        "psa_method": old.psa_method,
                        "psa": old.psa,
                        "eligible_for_mpi": old.eligible_for_mpi,
                        "mpi_method": old.mpi_method,
                        "mpi": old.mpi,
                        "eligible_for_deputation": old.eligible_for_deputation,
                        "deputation_method": old.deputation_method,
                        "deputation": old.deputation,
                        "eligible_for_officiating_allowance": old.eligible_for_officiating_allowance,
                        "officiating_allowance_method": old.officiating_allowance_method,
                        "officiating_allowance": old.officiating_allowance,
                        "eligible_for_temporary_transfer_allowance": old.eligible_for_temporary_transfer_allowance,
                        "temporary_transfer_allowance_method": old.temporary_transfer_allowance_method,
                        "temporary_transfer_allowance": old.temporary_transfer_allowance,
                        "eligible_for_scarcity": old.eligible_for_scarcity,
                        "scarcity_method": old.scarcity_method,
                        "scarcity": old.scarcity,
                        "eligible_for_cash_handling": old.eligible_for_cash_handling,
                        "cash_handling_method": old.cash_handling_method,
                        "cash_handling": old.cash_handling,
                        "eligible_for_honorarium": old.eligible_for_honorarium,
                        "honorarium_method": old.honorarium_method,
                        "honorarium": old.honorarium,
                        "eligible_for_pbva": old.eligible_for_pbva,
                        "eligible_for_leave_encashment": old.eligible_for_leave_encashment,
                        "eligible_for_ltc": old.eligible_for_ltc,
                        "eligible_for_overtime_and_payment": old.eligible_for_overtime_and_payment,
                        "eligible_for_sws": old.eligible_for_sws,
                        "eligible_for_gis": old.eligible_for_gis,
                        "eligible_for_pf": old.eligible_for_pf,
                        "eligible_for_health_contribution": old.eligible_for_health_contribution,
                        "eligible_for_bonus": old.eligible_for_annual_bonus,
                }
                # Earnings
                earnings = []
                for i in old.get("earnings"):
                        earnings.append({
                                "salary_component": i.salary_component,
                                "amount": i.amount,
                                "depends_on_lwp": i.depends_on_lwp,
                                "from_date": i.from_date,
                                "to_date": i.to_date,
                                "institution_name": i.institution_name,
                                "reference_type": i.reference_type,
                                "reference_number": i.reference_number,
                                "total_deductible_amount": i.total_deductible_amount,
                                "total_deducted_amount": i.total_deducted_amount,
                                "total_outstanding_amount": i.total_outstanding_amount,
                                "salary_component_type": i.salary_component_type
                        })

                # Deductions
                deductions = []
                for i in old.get("deductions"):
                        deductions.append({
                                "salary_component": i.salary_component,
                                "amount": i.amount,
                                "depends_on_lwp": i.depends_on_lwp,
                                "from_date": i.from_date,
                                "to_date": i.to_date,
                                "institution_name": i.institution_name,
                                "reference_type": i.reference_type,
                                "reference_number": i.reference_number,
                                "total_deductible_amount": i.total_deductible_amount,
                                "total_deducted_amount": i.total_deducted_amount,
                                "total_outstanding_amount": i.total_outstanding_amount,
                                "salary_component_type": i.salary_component_type
                        })

                new.update({"earnings": earnings})
                new.update({"deductions": deductions})
                frappe.get_doc(new).save(ignore_permissions=True)
                return new
        
        counter = 0
        for i in frappe.db.sql("""
                        select ssb.name
                        from
                                maintenance.`tabSalary Structure_bkp20191212` ssb,
                                `tabSalary Structure` sst
                        where ssb.is_active='Yes'
                        and sst.name = ssb.name
                        and sst.is_active = ssb.is_active
                """, as_dict=True):
                counter += 1
                print counter, i
                if not debug:
                        duplicate_structure(i.name)
        
# 2019/05/22 Birkha->Shiv
def cancel_dn():
	#dn = "DN20112745"
	#doc = frappe.get_doc("Delivery Note", "DN19043483")
	#doc = frappe.get_doc("Delivery Note", "DN20031357") #Req on 2020/10/01
	doc = frappe.get_doc("Delivery Note", dn) #Req on 2020/12/16
	print 'Cancelling {}...'.format(dn)
	doc.cancel()
	frappe.db.commit()
	print doc.name, doc.docstatus

# 2019/04/01
def update_production_sle():
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
                sle = frappe.db.sql("select name, item_code, actual_qty from temp_sle where voucher_no = '{0}' order by name".format(i.name), as_dict=True)
                
                if len(voucher) == len(sle):
                        for j in range(len(voucher)):
                                if voucher[j].item_code == sle[j].item_code and abs(voucher[j].qty) == abs(sle[j].actual_qty):
                                        print j, 'PROD', i.name, voucher[j].item_code, voucher[j].idx, voucher[j].tbl, voucher[j].name, voucher[j].qty, 'SLE', sle[j].name, sle[j].item_code, sle[j].idx, sle[j].actual_qty
                                        frappe.db.sql("""
                                                update `tabStock Ledger Entry`
                                                set voucher_detail_no = '{0}'
                                                where name = '{1}'
                                        """.format(voucher[j].name, sle[j].name))                                     
                                else:
                                        frappe.throw(_("Values dont match"))
                else:
                        frappe.throw(_("Lengths dont match"))

                if (counter%500) == 0: 
                        frappe.db.commit()
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
	
# bench execute erpnext.temp_patch.cancel_ssl --args "'2020','01',"
def cancel_ssl(pfiscal_year, pmonth):
	counter = 0
	for s in frappe.db.sql("select name from `tabSalary Slip` where fiscal_year='{0}' and month = '{1}' and docstatus=1".format(pfiscal_year, pmonth), as_dict=True):
		counter += 1
		print counter, s.name
		doc = frappe.get_doc("Salary Slip", s.name)
		doc.cancel()	
	print "Total",counter

def testmail():
        # Test1, trying Delayed TRUE/FALSE
        a = frappe.sendmail(recipients=['siva@bt.bt','sivasankar.k2003@gmail.com'],subject="Mail with Delayed TRUE",message="Delayed FALSE",delayed=True)
        print a,'Delayed TRUE: Mail sent successfully...'
        '''
        a = frappe.sendmail(recipients=['siva@bt.bt'],subject="Mail with Delayed TRUE",message="Delayed FALSE",delayed=True)
        print a,'Delayed TRUE: Mail sent successfully...'
        b = frappe.sendmail(recipients=['siva@bt.bt'],subject="Mail with Delayed FALSE",message="Delayed FALSE",delayed=False)
        print b,'Delayed FALSE: Mail sent successfully...'
        '''
        # Test2, trying bulk emails
        '''
        for i in range(50):
                print i
                frappe.sendmail(recipients=['siva@bt.bt'],subject="Mail with Delayed TRUE",message="Delayed TRUE")
        '''

        # Test3, trying with reference details
        # This doesn't create communication
        '''
        frappe.sendmail(recipients=['siva@bt.bt'],
                    subject='Mail with Delayed TRUE',
                    message='Delayed TRUE',
                    reference_doctype='Customers',
                    reference_name='95591',
                    communication='Email')
        '''

        # Test4, creating communication
        '''
        email.make(
                doctype = 'Customers',
                name = '95591',
                content = 'Communication body',
                subject = 'Communication subject',
                recipients='siva@bt.bt',
                communication_medium='Email',
                send_email=True,
                #send_me_a_copy=True, #Sends a copy to bia@bt.bt
                print_html='<h1>Some more tests</h1>'   #Sends the print_html content as html attachment
        )
        '''

# Shiv 2019/01/24, Due to wrong EL settings under employee group ESP, all ESP employees got
# 30 days EL credited for the year 2019 
def remove_el():
	counter = 0
	for el in frappe.db.sql("select * from `tabLeave Allocation` where leave_type = 'Earned Leave' and from_date = '2019-01-01' and to_date = '2019-12-31'", as_dict=True):
		counter += 1
		print el.employee, el.docstatus, el.leave_type, el.carry_forwarded_leaves, el.new_leaves_allocated, el.total_leaves_allocated
		if el.docstatus == 1:
			doc = frappe.get_doc("Leave Allocation", el.name)
			doc.cancel()
			print 'Cancelled successfully'
		else:
			print 'Unable to cancel. docstatus: {0}'.format(el.docstatus)

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
                                select company, branch, name as employeecd, user_id, 'DES Employee' type
                                 from `tabDES Employee`
                                 where user_id is not null
                                 and exists(select 1
                                                from  `tabUser`
                                                where `tabUser`.name = `tabDES Employee`.user_id)
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

#
# Updating ref_doc in `tabReappropriation Details` for transactions prior to introduction of submit button on "Budget Reappropiation" screen
# 2018/06/27
#
def update_budget_reappropriation():
        print 'Creating a dummy reappropriation'
        doc = frappe.new_doc("Budget Reappropiation")
        doc.from_cost_center = "Gelephu - CDCL"
        doc.to_cost_center = "Gelephu - CDCL"
        doc.fiscal_year = "2018"
        doc.save(ignore_permissions=True)
        doc.submit()

def get_monthly_count(from_date, to_date):
    print from_date, to_date
    mcount = {}
    from_month      = str(from_date)[5:7]
    to_month        = str(to_date)[5:7]
    from_year       = str(from_date)[:4]
    to_year         = str(to_date)[:4]
    from_monthyear  = str(from_year)+str(from_month)
    to_monthyear    = str(to_year)+str(to_month)
    
    for y in range(int(from_year), int(to_year)+1):
        m_start = from_month if str(y) == str(from_year) else '01'
        m_end   = to_month if str(y) == str(to_year) else '12'
                            
	print 'Year:',y                            
        for m in range(int(m_start), int(m_end)+1):
	    print 'Month:',m
            key          = str(y)+(str(m).rjust(2,str('0')))
            m_start_date = key[:4]+'-'+key[4:]+'-01'
            m_start_date = from_date if str(y)+str(m).rjust(2,str('0')) == str(from_year)+str(from_month) else m_start_date
            m_end_date   = to_date if str(y)+str(m).rjust(2,str('0')) == str(to_year)+str(to_month) else get_last_day(m_start_date)
	    print str(y)+str(m),str(from_year)+str(from_month),str(to_year)+str(to_month)
	    print m_start_date, m_end_date
            if mcount.has_key(key):
                mcount[key]['local'] += date_diff(m_end_date, m_start_date)+1
            else:
                mcount[key] = {'local': date_diff(m_end_date, m_start_date)+1, 'claimed': 0}                                                

    print collections.OrderedDict(sorted(mcount.items()))
    for k,v in collections.OrderedDict(sorted(mcount.items())).iteritems():
	print k,v

    keys = [k for k in mcount]
    print keys

    format_strings = ','.join(['%s'] * len(mcount))
    print format_strings
    print "VALUES IN ({0})".format(format_strings) % tuple(keys)

def employee_id_check():
    counter2 = 0
    ylist = frappe.db.sql("select year(date_of_joining) years from `tabEmployee` group by year(date_of_joining) order by years",as_dict=True)
    for y in ylist:
         counter = 0
         elist = frappe.db.sql("select date_of_joining,name,employee_name,earlier_id from `tabEmployee` where year(date_of_joining) = '{0}' order by date_of_joining".format(y.years),as_dict=True)
         for e in elist:
              counter += 1
              if cint(e.name[-3:]) != cint(counter):
		   counter2 += 1
                   print counter2, e.date_of_joining, counter, e.name, e.employee_name, e.earlier_id

def cancel_asset():
    li = frappe.db.sql("select name from `tabAsset` where name between '{0}' and '{1}'".format('ASSET181003692','ASSET181003756'), as_dict=True)	
    for i in li:
         doc = frappe.get_doc("Asset",i.name)
	 try:
	     doc.cancel()
	     print i.name, 'Cancelled successfully...'
         except Exception, e:
             print i.name, 'Something went wrong'

def test123():
    li = frappe.db.get_values("Employee", {"employee_subgroup":"F16"}, ["employee_name","designation","date_of_joining"], as_dict=1)
    print len(li),li
    for i in li:
    	print i

