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

class UploadAttendanceOthers(Document):
	pass

@frappe.whitelist()
def get_template():
	if not frappe.has_permission("MR Attendance", "create"):
		raise frappe.PermissionError

	args = frappe.local.form_dict
	w = UnicodeWriter()
	w = add_header(w, args)
	w = add_data(w, args)

	# write out response as a type csv
	frappe.response['result'] = cstr(w.getvalue())
	frappe.response['type'] = 'csv'
	frappe.response['doctype'] = "MR Attendance"

def add_header(w, args):
	status = ", ".join((frappe.get_meta("MR Attendance").get_field("status").options or "").strip().split("\n"))
	w.writerow(["Notes:"])
	w.writerow(["Please do not change the template headings"])
	w.writerow(["Status should be P if Present"])
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
	#existing_attendance_records = get_existing_attendance_records(args)
	#for date in dates:
	for e in employees:
		#existing_attendance = {}
		#if existing_attendance_records \
		#	and tuple([date, employee.name]) in existing_attendance_records:
		#		existing_attendance = existing_attendance_records[tuple([date, employee.name])]
		row = [
			#existing_attendance and existing_attendance.name or "",
			#employee.name, employee.employee_name, date,
			#existing_attendance and existing_attendance.status or "", employee.company,
			#existing_attendance and existing_attendance.naming_series or get_naming_series(),
			e.branch, e.cost_center, e.etype, "\'"+str(e.name)+"\'", e.person_name, args.fiscal_year, args.month
		]
		w.writerow(row)
	return w

def get_dates(args):
	"""get list of dates in between from date and to date"""
	no_of_days = date_diff(add_days(args["to_date"], 1), args["from_date"])
	dates = [add_days(args["from_date"], i) for i in range(0, no_of_days)]
	return dates

def get_active_employees(args):
	employees = frappe.db.sql("""select "MR" as etype, name, person_name, branch, cost_center
		from `tabMuster Roll Employee` where docstatus < 2 and status = 'Active' and branch =%(branch)s UNION
		select "GEP" as etype, name, person_name, branch, cost_center
		from `tabGEP Employee` where docstatus < 2 and status = 'Active' and branch = %(branch)s""", {"branch": args.branch}, as_dict=1)
	return employees

def get_existing_attendance_records(args):
	attendance = frappe.db.sql("""select name, att_date, employee, status, naming_series
		from `tabAttendance` where att_date between %s and %s and docstatus < 2""",
		(args["from_date"], args["to_date"]), as_dict=1)

	existing_attendance = {}
	for att in attendance:
		existing_attendance[tuple([att.att_date, att.employee])] = att

	return existing_attendance

def get_naming_series():
	series = frappe.get_meta("Attendance").get_field("naming_series").options.strip().split("\n")
	if not series:
		frappe.throw(_("Please setup numbering series for Attendance via Setup > Numbering Series"))
	return series[0]


@frappe.whitelist()
def upload():
	if not frappe.has_permission("MR Attendance", "create"):
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
			for j in range(8, len(row)):
				doc = frappe.new_doc("MR Attendance")
				doc.branch = row[0]
				doc.cost_center = row[1]
				if str(row[2]) == "MR":
					doc.employee_type = "Muster Roll Employee"
				elif str(row[2]) == "GEP":
					doc.employee_type = "GEP Employee"
				doc.employee = str(row[3]).strip('\'')
				
				month = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"].index(row[6]) + 1	
				month = str(month) if cint(month) > 9 else str("0" + str(month))
				day = str(j) if cint(j) > 9 else str("0" + str(j))
				doc.date = str(row[5]) + '-' + str(month) + '-' + str(day)
				if str(row[j -1]) == "P":
					doc.status = "Present"
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
