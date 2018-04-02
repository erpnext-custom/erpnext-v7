from frappe.utils import flt

@frappe.whitelist()
def get_employee_details():
	emps = frappe.db.sql("select count(1) as number, branch from tabEmployee where status = 'Active' group by branch")

	emp = []
	emp_count = []
	for a in emps:
		emp.append(a.branch)
		emp_count.append(a.number)

	return [emp, emp_count]
		
