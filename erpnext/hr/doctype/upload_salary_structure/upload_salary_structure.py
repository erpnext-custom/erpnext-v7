# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt, cstr, add_days, date_diff, nowdate
from frappe import _
from frappe.utils.csvutils import UnicodeWriter
from frappe.model.document import Document
from erpnext.hr.hr_custom_functions import get_employee_gis, get_salary_tax, get_company_pf 

class UploadSalaryStructure(Document):
	pass

@frappe.whitelist()
def get_template():
	if not frappe.has_permission("Salary Structure", "create"):
		raise frappe.PermissionError

	args = frappe.local.form_dict

	w = UnicodeWriter()
	w = add_header(w)

	# write out response as a type csv
	frappe.response['result'] = cstr(w.getvalue())
	frappe.response['type'] = 'csv'
	frappe.response['doctype'] = "Salary Structure"

def add_header(w):
	w.writerow(["Notes:"])
	w.writerow(["Please DO NOT change the template headings"])
	w.writerow([""])
	w.writerow(["Employee", "Employee Name", "Basic", "Corporate", "Contract", "Communication", "Fuel", "Underground", "Shift", "PSA", "PDA", "Deputation", "Officiating", "Scarcity", "Difficulty", "High Altitude", "Cash Handling", "Component 1", "Amount 1", "Scheme 1", "Bank 1", "Number 1",  "Component 2", "Amount 2", "Scheme 2", "Bank 2", "Number 2", "Component 3", "Amount 3", "Scheme 3", "Bank 3", "Number 3"])
	return w

@frappe.whitelist()
def upload():
	if not frappe.has_permission("Salary Structure", "create"):
		raise frappe.PermissionError

	from frappe.utils.csvutils import read_csv_content_from_uploaded_file
	from frappe.modules import scrub

	rows = read_csv_content_from_uploaded_file()
	rows = filter(lambda x: x and any(x), rows)
	if not rows:
		msg = [_("Please select a csv file")]
		return {"messages": msg, "error": msg}

	#Columns located at 4th row
	columns = [scrub(f) for f in rows[2]]
	ret = []
	error = False

	from frappe.utils.csvutils import check_record, import_doc

	
	for i, row in enumerate(rows[3:]):
		if not row: continue
		row_idx = i + 3
		d = frappe._dict(zip(columns, row))
		try:
			ear = ded = 0
			sws_amount = flt(frappe.db.get_value("Salary Component", "SWS", "default_amount"))
			doc = frappe.new_doc("Salary Structure")
			if d.employee:
				emp = frappe.get_doc("Employee", d.employee)
				doc.employee = d.employee
				doc.is_active = 'Yes'
				doc.from_date = nowdate()
				if d.basic:
					doc.append("earnings",{"salary_component": "Basic Pay", "amount": flt(d.basic)})
					ear += flt(d.basic)	
				else:
					frappe.throw("No Basic Pay record on row " + str(row_idx))
				if d.corporate:
					doc.eligible_for_corporate_allowance = 1
					doc.ca = d.corporate
					amount = flt(d.basic) * 0.01 * flt(d.corporate)
					doc.append("earnings",{"salary_component": "Corporate Allowance", "amount": amount})	
					ear += flt(amount)	
				if d.contract:
					doc.eligible_for_contract_allowance = 1
					doc.contract_allowance = d.contract
					amount = flt(d.basic) * 0.01 * flt(d.contract)
					doc.append("earnings",{"salary_component": "Contract Allowance", "amount": amount})	
					ear += flt(amount)	
				if d.communication:
					doc.eligible_for_communication_allowance = 1
					doc.communication_allowance = d.communication
					amount = flt(d.communication)
					doc.append("earnings",{"salary_component": "Communication Allowance", "amount": amount})
					ear += amount	
				if d.fuel:
					doc.eligible_fuel_allowances = 1
					doc.fuel_allowances = d.fuel
					amount = flt(d.fuel)
					doc.append("earnings",{"salary_component": "Fuel Allowance", "amount": amount})
					ear += amount	
				if d.underground:
					doc.eligible_for_underground = 1
					doc.underground = d.underground
					amount = flt(d.basic) * 0.01 * flt(d.underground)
					doc.append("earnings",{"salary_component": "Underground Allowance", "amount": amount})	
					ear += amount	
				if d.shift:
					doc.eligible_for_shift = 1
					doc.shift = d.shift
					amount = flt(d.basic) * 0.01 * flt(d.shift)
					doc.append("earnings",{"salary_component": "Shift Allowance", "amount": amount})	
					ear += amount	
				if d.psa:
					doc.eligible_for_psa = 1
					doc.psa = d.psa
					amount = flt(d.basic) * 0.01 * flt(d.psa)
					doc.append("earnings",{"salary_component": "PSA", "amount": amount})	
					ear += amount	
				if d.pda:
					doc.eligible_for_pda = 1
					doc.psa = d.pda
					amount = flt(d.basic) * 0.01 * flt(d.pda)
					doc.append("earnings",{"salary_component": "PDA", "amount": amount})	
					ear += amount	
				if d.deputation:
					doc.eligible_for_deputation = 1
					doc.deputation = d.deputation
					amount = flt(d.basic) * 0.01 * flt(d.deputation)
					doc.append("earnings",{"salary_component": "Deputation Allowance", "amount": amount})	
					ear += amount	
				if d.officiating:
					doc.eligible_for_officiating = 1
					doc.officiating = d.officiating
					amount = flt(d.basic) * 0.01 * flt(d.officiating)
					doc.append("earnings",{"salary_component": "Officiating Allowance", "amount": amount})	
					ear += amount	
				if d.scarcity:
					doc.eligible_for_scarcity = 1
					doc.scarcity = d.scarcity
					amount = flt(d.basic) * 0.01 * flt(d.scarcity)
					doc.append("earnings",{"salary_component": "Scarcity Allowance", "amount": amount})	
					ear += amount	
				if d.difficulty:
					doc.eligible_for_difficulty = 1
					doc.difficulty = d.difficulty
					amount = flt(d.difficulty)
					doc.append("earnings",{"salary_component": "Dificult Area Allowance", "amount": amount})
					ear += amount	
				if d.high_altitude:
					doc.eligible_for_high_altitude = 1
					doc.high_altitude = d.high_altitude
					amount = flt(d.high_altitude)
					doc.append("earnings",{"salary_component": "High Altitude Allowance", "amount": amount})
					ear += amount	
				if d.cash_handling:
					doc.eligible_for_cash_handling = 1
					doc.cash_handling = d.cash_handling
					amount = flt(d.cash_handling)
					doc.append("earnings",{"salary_component": "Cash Handling Allowance", "amount": amount})
					ear += amount	

				if d.amount_1:
					if d.bank_1 and d.scheme_1 and d.component_1 and d.number_1:
						doc.append("deductions",{"salary_component": str(d.component_1), "amount": flt(d.amount_1), "institution_name": str(d.bank_1), "reference_type": str(d.scheme_1), "reference_number": str(d.number_1)})	
						ded += flt(d.amount_1)

				if d.amount_2:
					if d.bank_2 and d.scheme_2 and d.component_2 and d.number_2:
						doc.append("deductions",{"salary_component": str(d.component_2), "amount": flt(d.amount_2), "institution_name": str(d.bank_2), "reference_type": str(d.scheme_2), "reference_number": str(d.number_2)})	
						ded += flt(d.amount_2)

				if d.amount_3:
					if d.bank_3 and d.scheme_3 and d.component_3 and d.number_3:
						doc.append("deductions",{"salary_component": str(d.component_3), "amount": flt(d.amount_3), "institution_name": str(d.bank_3), "reference_type": str(d.scheme_3), "reference_number": str(d.number_3)})	
						ded += flt(d.amount_3)

				doc.append("deductions",{"salary_component": "SWS", "amount": sws_amount})	
				ded += sws_amount
				
				if not emp.employee_subgroup:
					frappe.throw("No Grade assigned to " + str(emp.employee_name))
				gis_amount = flt(frappe.db.get_value("Employee Grade", emp.employee_subgroup, "gis"))
				doc.append("deductions",{"salary_component": "Group Insurance Scheme", "amount": gis_amount})	
				ded += gis_amount

				ded_percent = get_company_pf()
				pf_amount = flt(d.basic) * 0.01 * flt(ded_percent[0][0])
				doc.append("deductions",{"salary_component": "PF", "amount": pf_amount})	
				ded += pf_amount
				
				health_amount = flt(ear) * 0.01 * flt(ded_percent[0][2])
				doc.append("deductions",{"salary_component": "Health Contribution", "amount": health_amount})	
				ded += health_amount
				
				tax_gross = flt(ear) - flt(pf_amount) - flt(gis_amount)
				if d.communication:
					tax_gross -= (0.5 * flt(d.communication))
				tax_amount = get_salary_tax(tax_gross)
				doc.append("deductions",{"salary_component": "Salary Tax", "amount": tax_amount})	
				ded += tax_amount
				
				doc.total_earning = flt(ear)
				doc.total_deduction = flt(ded)
				doc.net_pay = flt(ear) - flt(ded)
				doc.insert()
			else:
				frappe.throw("No employee record on row " + str(row_idx))
			
			ret.append("Salary Structure created for " + str(d.employee))
		except Exception, e:
			error = True
			ret.append('Error for row (#%d) ' % (row_idx))
			ret.append(str(frappe.get_traceback()))
			frappe.errprint(frappe.get_traceback())
		
	return {"messages": ret, "error": error}

 
