# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr, add_days, date_diff, cint, flt
from frappe import _
from frappe.utils.csvutils import UnicodeWriter
from frappe.model.document import Document
from calendar import monthrange

class UploadOvertimeEntries(Document):
	pass

@frappe.whitelist()
def get_template():
	if not frappe.has_permission("Overtime Entry", "create"):
		raise frappe.PermissionError

	args = frappe.local.form_dict
	w = UnicodeWriter()
	w = add_header(w, args)
	w = add_data(w, args)

	# write out response as a type csv
	frappe.response['result'] = cstr(w.getvalue())
	frappe.response['type'] = 'csv'
	frappe.response['doctype'] = "Overtime Entry"

def add_header(w, args):
	w.writerow(["Notes:"])
	w.writerow(["Please do not change the template headings"])
	w.writerow(["Number of hours should be Integers"])
	hd = ["Branch", "Cost Center", "Employee Type", "Employee ID", "Employee Name", "Year", "Month"]

	month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
		"Dec"].index(args.month) + 1

	total_days = monthrange(cint(args.fiscal_year), month)[1]
	for day in range(cint(total_days)):
		hd.append(str(day + 1))	

	w.writerow(hd)
	return w

def add_data(w, args):
	#dates = get_dates(args)
	employees = get_active_employees(args)
	for e in employees:
		row = [
			e.branch, e.cost_center, e.etype, "\'"+str(e.name)+"\'", e.person_name, args.fiscal_year, args.month
		]
		w.writerow(row)
	return w

def get_active_employees(args):
	employees = frappe.db.sql("""select "MR" as etype, name, person_name, branch, cost_center
		from `tabMuster Roll Employee` where docstatus < 2 and status = 'Active' and branch =%(branch)s UNION
		select "GEP" as etype, name, person_name, branch, cost_center
		from `tabGEP Employee` where docstatus < 2 and status = 'Active' and branch = %(branch)s""", {"branch": args.branch}, as_dict=1)
	return employees

@frappe.whitelist()
def upload():			
	if not frappe.has_permission("Overtime Entry", "create"):
		raise frappe.PermissionError

	from frappe.utils.csvutils import read_csv_content_from_uploaded_file
	from frappe.modules import scrub

	rows = read_csv_content_from_uploaded_file()
	rows = filter(lambda x: x and any(x), rows)
	if not rows:
		msg = [_("Please select a csv file")]
		return {"messages": msg, "error": msg}
	columns = [scrub(f) for f in rows[3]]
	ret = []
	error = False

	from frappe.utils.csvutils import check_record, import_doc

	for i, row in enumerate(rows[4:]):
		if not row: continue
		try:
			row_idx = i + 4
			for j in range(8, len(row) + 1):
                                month = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"].index(row[6]) + 1
                                month = str(month) if cint(month) > 9 else str("0" + str(month))
                                day   = str(cint(j) - 7) if cint(j) > 9 else str("0" + str(cint(j) - 7))

                                old = frappe.db.get_value("Overtime Entry", {"number":str(row[3]).strip('\''), "date": str(row[5]) + '-' + str(month) + '-' + str(day), "docstatus": 1}, ["docstatus","name","number_of_hours"], as_dict=1)

                                '''
                                if old:
                                        doc = frappe.get_doc("Overtime Entry", old.name)
                                        doc.db_set('number_of_hours', flt(row[j-1]))
                                else:
                                '''
                                
                                if not old and row[j-1]:
                                        doc = frappe.new_doc("Overtime Entry")
					doc.branch          = row[0]
                                        doc.cost_center     = row[1]
                                        doc.number          = str(row[3]).strip('\'')
                                        doc.date            = str(row[5]) + '-' + str(month) + '-' + str(day)
                                        doc.number_of_hours = flt(row[j -1])
                                        
                                        if str(row[2]) == "MR":
                                                doc.employee_type = "Muster Roll Employee"
                                        elif str(row[2]) == "GEP":
                                                doc.employee_type = "GEP Employee"
                                                
                                        doc.submit()
		except Exception, e:
			error = True
			ret.append('Error for row (#%d) %s : %s' % (row_idx,
				len(row)>1 and row[4] or "", cstr(e)))
			frappe.errprint(frappe.get_traceback())

	if error:
		frappe.db.rollback()
	else:
		frappe.db.commit()
	return {"messages": ret, "error": error}
