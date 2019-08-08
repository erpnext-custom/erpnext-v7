# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr, add_days, date_diff, cint, flt, getdate, nowdate
from frappe import _
from frappe.utils.csvutils import UnicodeWriter
from frappe.model.document import Document
from calendar import monthrange

class AttendanceUpload(Document):
	pass

@frappe.whitelist()
def get_template():
	if not frappe.has_permission("Attendance", "create"):
		raise frappe.PermissionError

	args = frappe.local.form_dict
	w = UnicodeWriter()
	w = add_header(w, args)
	w = add_data(w, args)

	# write out response as a type csv
	frappe.response['result'] = cstr(w.getvalue())
	frappe.response['type'] = 'csv'
	frappe.response['doctype'] = "Attendance"

def add_header(w, args):
	status = ", ".join((frappe.get_meta("Attendance").get_field("status").options or "").strip().split("\n"))
	w.writerow(["Notes:"])
	w.writerow(["Please do not change the template headings"])
	w.writerow(["Status should be P if Present, A if Absent"])
	hd = ["Branch","Employment Type", "Employee ID", "Employee Name", "Year", "Month"]

	month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
		"Dec"].index(args.month) + 1

	total_days = monthrange(cint(args.fiscal_year), month)[1]
	for day in range(cint(total_days)):
		hd.append(str(day + 1))	

	w.writerow(hd)
	return w

def add_data(w, args):
        month = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"].index(args.month) + 1
        month = str(month) if cint(month) > 9 else str("0" + str(month))

        total_days = monthrange(cint(args.fiscal_year), cint(month))[1]
        start_date = str(args.fiscal_year) + '-' + str(month) + '-' + str('01')
        end_date   = str(args.fiscal_year) + '-' + str(month) + '-' + str(total_days)
        
	employees = get_active_employees(args)
	loaded     = get_loaded_records(args, start_date, end_date)
	
	for e in employees:
                status = ''
		row = [
			e.branch, e.employment_type, "\'"+str(e.name)+"\'", e.employee_name, args.fiscal_year, args.month
		]
		
		for day in range(cint(total_days)):
			status = loaded.get(e.name, frappe._dict()).get(e.employee_name, frappe._dict()).get(day+1,'')
			row.append(status)
					
		w.writerow(row)
	return w

def get_loaded_records(args, start_date, end_date):
        loaded_list= frappe._dict()

        rl = frappe.db.sql("""
                        select
                                a.employee as employee, a.employee_name as employee_name,
                                day(a.att_date) as day_of_date,
                                case
                                    when a.status = 'Present' then 'P'
                                    when a.status = 'Absent' then 'A'
                                    else a.status
                                end as status
                        from `tabAttendance` as a
			inner join `tabEmployee` as e on a.employee = e.name
                        where e.branch = '{0}'
			and e.employment_type = '{1}'
                        and a.att_date between %s and %s
                        and a.docstatus < 2
                """.format(args.branch, args.employment_type), (start_date, end_date), as_dict=1)

        for r in rl:
                loaded_list.setdefault(r.employee, frappe._dict()).setdefault(r.employee_name, frappe._dict()).setdefault(r.day_of_date,r.status)

        return loaded_list

def get_active_employees(args):        
	employees = frappe.db.sql("""
		select branch, employment_type, name, employee_name  from `tabEmployee`
		where docstatus < 2
                and branch = '{0}'
		and status = "Active"
		and employment_type = '{1}'
		""".format(args.branch, args.employment_type), as_dict=1)

	return employees

@frappe.whitelist()
def upload():
	if not frappe.has_permission("Attendance", "create"):
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

	frappe.msgprint("Started Parsing")
	for i, row in enumerate(rows[4:]):
		if not row: continue
		try:
			row_idx = i + 3
			for j in range(7, len(row) + 1):
                                month = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"].index(row[5]) + 1	
				month = str(month) if cint(month) > 9 else str("0" + str(month))
				day = str(cint(j) - 6) if cint(j) > 9 else str("0" + str(cint(j) - 6))
				status = ''
				
				if str(row[j -1]) in ("P","p"):
                                        status = 'Present'
                                elif str(row[j -1]) in ("A","a"):
                                        status = 'Absent'
                                else:
                                        status = ''
                                        
				frappe.msgprint(str(j))
                                old = frappe.db.get_value("Attendance", {"employee": row[3].strip('\''), "att_date": str(row[4]) + '-' + str(month) + '-' + str(day)}, ["status","name"], as_dict=1)
                                if old:
                                        doc = frappe.get_doc("Attendance", old.name)
                                        doc.db_set('status', status if status in ('Present','Absent') else doc.status)
                                        doc.db_set('branch', row[0])
                                #else:
                                if not old and status in ('Present','Absent'):
                                        doc = frappe.new_doc("Attendance")
                                        doc.status = status
                                        doc.branch = row[0]
                                        doc.employee = str(row[2]).strip('\'')
					doc.employee_name = row[3]
                                        doc.att_date = str(row[4]) + '-' + str(month) + '-' + str(day)
					doc.employment_type = row[1]
                                    	
					#Prevent future dates creation
					if not getdate(doc.att_date) > getdate(nowdate()):
						doc.submit()
		except Exception, e:
			error = True
			ret.append('Error for row (#%d) %s : %s' % (row_idx,
				len(row)>1 and row[3] or "", cstr(e)))
			frappe.errprint(frappe.get_traceback())

	if error:
		frappe.db.rollback()
	else:
		frappe.db.commit()
		frappe.msgprint("DONE")
	return {"messages": ret, "error": error}
