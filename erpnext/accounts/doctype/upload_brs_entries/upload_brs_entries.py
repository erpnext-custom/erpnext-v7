# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr, add_days, date_diff
from frappe import _
from frappe.utils.csvutils import UnicodeWriter
from frappe.model.document import Document

class UploadBRSEntries(Document):
	pass

@frappe.whitelist()
def get_template():
	if not frappe.has_permission("BRS Entries", "create"):
		raise frappe.PermissionError

	args = frappe.local.form_dict

	w = UnicodeWriter()
	w = add_header(w)

	# write out response as a type csv
	frappe.response['result'] = cstr(w.getvalue())
	frappe.response['type'] = 'csv'
	frappe.response['doctype'] = "BRS Entries"

def add_header(w):
	w.writerow(["Notes:"])
	w.writerow(["Please DO NOT change the template headings"])
	w.writerow([""])
	w.writerow(["Cheque No", "Amount", "Clearing Date"])
	return w

@frappe.whitelist()
def upload():
	if not frappe.has_permission("BRS Entries", "create"):
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
		d["doctype"] = "BRS Entries"

		try:
			check_record(d)
			ret.append(import_doc(d, "BRS Entries", 1, row_idx, submit=True))
		except Exception, e:
			error = True
			ret.append('Error for row (#%d) %s : %s' % (row_idx,
				len(row)>1 and row[1] or "", cstr(e)))
			frappe.errprint(frappe.get_traceback())

	if error:
		frappe.db.rollback()
	else:
		frappe.db.commit()
	return {"messages": ret, "error": error}
