# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

'''
------------------------------------------------------------------------------------------------------------------------------------------
Version          Author         Ticket#           CreatedOn          ModifiedOn          Remarks
------------ --------------- --------------- ------------------ -------------------  -----------------------------------------------------
3.0               SHIV		                   28/01/2019                          Original Version
------------------------------------------------------------------------------------------------------------------------------------------                                                                          
'''

from __future__ import unicode_literals
import frappe
from frappe import _
from erpnext.hr.doctype.approver_settings.approver_settings import get_final_approver
from erpnext.hr.hr_custom_functions import get_officiating_employee

def validate_workflow_states(doc):
	approver_field = {
			"Salary Advance": ["advance_approver","advance_approver_name","advance_approver_designation"],
			"Leave Application": ["leave_approver","leave_approver_name"],
			"Travel Authorization": ["supervisor",""],
			"Travel Claim": ["supervisor",""],
			"Employee Benefits": ["benefit_approver","benefit_approver_name"],
                        "Request EL Allocation": ["approver", "approver_name"],
			"Overtime Authorization": ["approver", "approver_name"],
			"Overtime Claim": ["approver", "approver_name"],
			"Leave Encashment": ["approver", "approver_name"],
			"Material Request": ["approver","approver_name"],
	}
	
	if not approver_field.has_key(doc.doctype) or not frappe.db.exists("Workflow", {"document_type": doc.doctype, "is_active": 1}):
		return
	document_approver = approver_field[doc.doctype]
	login_user        = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, ["user_id","employee_name","designation","name"])
	if doc.doctype in ["Material Request"]:
		# needed so that non-employees like admin cannot create MR 
		# added by phuntsho on Feb 3 2021
		if not login_user: 
			frappe.throw("You do not have permission to create MR!")
		owner        = frappe.db.get_value("Employee", {"user_id": doc.owner}, ["user_id","employee_name","designation","name"])
		employee          = frappe.db.get_value("Employee", owner[3], ["user_id","employee_name","designation","name"])
		reports_to        = frappe.db.get_value("Employee", frappe.db.get_value("Employee", owner[3], "reports_to"), ["user_id","employee_name","designation","name"])
	else:
		employee          = frappe.db.get_value("Employee", doc.employee, ["user_id","employee_name","designation","name"])
		reports_to        = frappe.db.get_value("Employee", frappe.db.get_value("Employee", doc.employee, "reports_to"), ["user_id","employee_name","designation","name"])

	final_approver    = frappe.db.get_value("Employee", {"user_id": get_final_approver(doc.branch)}, ["user_id","employee_name","designation","name"])
	workflow_state    = doc.get("workflow_state").lower()
	
	if not login_user:
		frappe.throw("{0} is not added as the employee".format(frappe.session.user))

	if doc.doctype == "Salary Advance":
		#CEO is set as the approver for Salary Advance.
		''' employee --> final_approver(branch)/reports_to(final_approver(branch)) '''
		if workflow_state == "Waiting CEO Approval".lower():
			advance_doc  = frappe.get_doc("Employee", {"designation": 'Chief Executive Officer', "status": 'Active'})
			vars(doc)[document_approver[0]] = advance_doc.user_id
			vars(doc)[document_approver[1]] = advance_doc.employee_name
			vars(doc)[document_approver[2]] = advance_doc.designation
			officiating = get_officiating_employee(advance_doc.name)
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, ["user_id","employee_name","designation","name"])
				vars(doc)[document_approver[0]] = officiating[0] if officiating else document_approver[0]
				vars(doc)[document_approver[1]] = officiating[1] if officiating else document_approver[1]
				vars(doc)[document_approver[2]] = officiating[2] if officiating else document_approver[2]
			
			if "HR Manager" not in frappe.get_roles(frappe.session.user):
				frappe.throw(_("Only HR Manager role can approve."))
		elif workflow_state == "Approved".lower():
			if doc.get(document_approver[0]) != frappe.session.user:
					frappe.throw(_("Only <b>{0}, {1}</b> can approve this application").format(doc.get(document_approver[1]),doc.get(document_approver[1])), title="Invalid Operation")
		elif workflow_state == "Rejected".lower():
				if doc.get(document_approver[0]) and doc.get(document_approver[0]) != frappe.session.user:
						if workflow_state != doc.get_db_value("workflow_state"):
								frappe.throw(_("Only <b>{0}, {1}</b> can reject this application").format(doc.get(document_approver[1]),doc.get(document_approver[1])), title="Invalid Operation")
		else:
				pass
						
	elif doc.doctype == "Material Request":
		if doc.approver and doc.approver != frappe.session.user:
			frappe.throw(_("Only the approver <b>{0}</b> allowed to verify or approve this document").format(doc.approver), title="Invalid Operation")

		if workflow_state == "Waiting Supervisor Approval".lower():
			if "MR GM" in frappe.get_roles(frappe.session.user): 
				# MR GM should be able to edit only if MR is submitted by Manager
				if (doc.owner != frappe.session.user) and "MR Manager" not in frappe.get_roles(doc.owner):
					frappe.throw("MR GM is not allowed to save the document during this workflow state.")
					
			officiating = get_officiating_employee(reports_to[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, ["user_id","employee_name","designation","name"])
			
			vars(doc)[document_approver[0]] = officiating[0] if officiating else reports_to[0]
			vars(doc)[document_approver[1]] = officiating[1] if officiating else reports_to[1]
			
		elif workflow_state == "Verified By Supervisor".lower():
			officiating = get_officiating_employee(final_approver[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, ["user_id","employee_name","designation","name"])
			vars(doc)[document_approver[0]] = officiating[0] if officiating else final_approver[0]
			vars(doc)[document_approver[1]] = officiating[1] if officiating else final_approver[1]
		elif workflow_state == "Approved":
			doc.docstatus = 1

	elif doc.doctype == "Request EL Allocation":
		hr_user = frappe.db.get_single_value("HR Settings", "hr_approver")
		hr_approver = frappe.db.get_value("Employee", hr_user, ["user_id","employee_name","designation","name"])
		if workflow_state == "Draft".lower():
			vars(doc)[document_approver[0]] = employee[0]
			vars(doc)[document_approver[1]] = employee[1]
		elif workflow_state == "Waiting Approval".lower():
			if doc.get(document_approver[0]) != frappe.session.user:
				frappe.throw("Only {0} is allowed to process this application ".format(doc.get(document_approver[0])))
			officiating = get_officiating_employee(hr_approver[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, ["user_id","employee_name","designation","name"])
			vars(doc)[document_approver[0]] = officiating[0] if officiating else hr_approver[0]
			vars(doc)[document_approver[1]] = officiating[1] if officiating else hr_approver[1]
		elif workflow_state == "Waiting Supervisor Approval".lower():
			if employee[0] == final_approver[0]:
				officiating = get_officiating_employee(hr_approver[3])
				if officiating:
					officiating = frappe.db.get_value("Employee", officiating[0].officiate, ["user_id","employee_name","designation","name"])
				vars(doc)[document_approver[0]] = officiating[0] if officiating else hr_approver[0]
				vars(doc)[document_approver[1]] = officiating[1] if officiating else hr_approver[1]

			else:
				officiating = get_officiating_employee(final_approver[3])
				if officiating:
					officiating = frappe.db.get_value("Employee", officiating[0].officiate, ["user_id","employee_name","designation","name"])
				vars(doc)[document_approver[0]] = officiating[0] if officiating else final_approver[0]
				vars(doc)[document_approver[1]] = officiating[1] if officiating else final_approver[1]

		elif workflow_state == "Approved".lower():
			if doc.get(document_approver[0]) != frappe.session.user:
				frappe.throw(_("Only <b>{0}, {1}</b> can approve this application").format(doc.get(document_approver[1]),doc.get(document_approver[1])), title="Invalid Operation")
		elif workflow_state == "Rejected".lower():
			if doc.get(document_approver[0]) and doc.get(document_approver[0]) != frappe.session.user:
				if workflow_state != doc.get_db_value("workflow_state"):
					frappe.throw(_("Only <b>{0}, {1}</b> can reject this application").format(doc.get(document_approver[1]),doc.get(document_approver[1])), title="Invalid Operation")
		else:
			pass

	elif doc.doctype == "Leave Encashment":
		if workflow_state == "Waiting Approval".lower():
			hr_user = frappe.db.get_single_value("HR Settings", "hr_approver")
			hr_approver = frappe.db.get_value("Employee", hr_user, ["user_id","employee_name","designation","name"])
			officiating = get_officiating_employee(hr_approver[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, ["user_id","employee_name","designation","name"])
			vars(doc)[document_approver[0]] = officiating[0] if officiating else hr_approver[0]
			vars(doc)[document_approver[1]] = officiating[1] if officiating else hr_approver[1]

		elif workflow_state == "Approved".lower():
			if frappe.session.user != doc.approver:
				frappe.throw("Only '{0}' is allowed to Approved the Leave Encashment".format(doc.approver))
			if doc.docstatus == 0 and workflow_state == "Approved":
				doc.workflow_state = "Waiting Approval"
		

	elif doc.doctype in ["Overtime Claim","Overtime Authorization"]:
		hr_user = frappe.db.get_single_value("HR Settings", "hr_approver")
		hr_approver = frappe.db.get_value("Employee", hr_user, ["user_id","employee_name","designation","name"])
		
		if workflow_state == "Draft".lower():
			vars(doc)[document_approver[0]] = employee[0]
			vars(doc)[document_approver[1]] = employee[1]

		elif workflow_state == "Approved".lower():
			if  doc.approver != frappe.session.user:
				frappe.throw("Only {0} can only approve Overtime Application".format(doc.approver))
			if final_approver[0] != doc.approver and employee[0] != final_approver[0]:
				frappe.throw("Only {0} can approve your Overtime Application".format(frappe.bold(final_approver[0])))
			#doc.status= "Approved"
			if doc.doctype == "Overtime Claim":
				officiating = get_officiating_employee(hr_approver[3])
				if officiating:
					officiating = frappe.db.get_value("Employee", officiating[0].officiate, ["user_id","employee_name","designation","name"])
				vars(doc)[document_approver[0]] = officiating[0] if officiating else hr_approver[0]
				vars(doc)[document_approver[1]] = officiating[1] if officiating else hr_approver[1]

		elif workflow_state == "Claimed".lower():
			if  hr_approver[0] != frappe.session.user:
				frappe.throw("Only {0} can verify payment for  Overtime Application".format(hr_approver[0]))

		if workflow_state == "Waiting Supervisor Approval".lower():
			officiating = get_officiating_employee(reports_to[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, ["user_id","employee_name","designation","name"])
			vars(doc)[document_approver[0]] = officiating[0] if officiating else reports_to[0]
			vars(doc)[document_approver[1]] = officiating[1] if officiating else reports_to[1]

			if doc.approver == employee[0]:
				frappe.throw("Overtime Application submitter {0} cannot be the supervisor ".format(doc.approver))
		elif workflow_state == "Verified By Supervisor".lower():
			if  doc.approver != frappe.session.user:
				frappe.throw("Only {0} can submit the leave application".format(doc.approver))
			if final_approver[0] != employee[0]:
				officiating = get_officiating_employee(final_approver[3])
				if officiating:
					officiating = frappe.db.get_value("Employee", officiating[0].officiate, ["user_id","employee_name","designation","name"])
				vars(doc)[document_approver[0]] = officiating[0] if officiating else final_approver[0]
				vars(doc)[document_approver[1]] = officiating[1] if officiating else final_approver[1]
		elif workflow_state == "Rejected".lower():
			if doc.approver != frappe.session.user:
				frappe.throw("Only {0} can Reject this application".format(doc.approver), title="Operation not permitted")
			else:
				if workflow_state == "Rejected".lower():
					doc.status = "Rejected"
				vars(doc)[document_approver[0]] = reports_to[0]
				vars(doc)[document_approver[1]] = reports_to[1]

		elif workflow_state == "Cancelled".lower():
			if frappe.session.user not in (doc.approver,"Administrator"):
				frappe.throw(_("Only Overtime approver <b>{0}</b> ( {1} ) can cancel this document.").format(doc.approver_name, doc.approver), title="Operation not permitted")		

	elif doc.doctype == "Employee Benefits":
		hr_user = frappe.db.get_single_value("HR Settings", "hr_approver")
		hr_approver = frappe.db.get_value("Employee", hr_user, ["user_id","employee_name","designation","name"])

		if workflow_state == "Draft".lower():
			if doc.purpose == "Separation":
				if not "HR User" in frappe.get_roles(frappe.session.user):
					frappe.throw("Only HR user with role HR User can create the employee benefit with purpose Separation")

			vars(doc)[document_approver[0]] = frappe.session.user
			login_user        = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, ["user_id","employee_name","designation","name"])
		  	vars(doc)[document_approver[1]] = login_user[1]
		elif workflow_state == "Waiting Approval".lower():
			if doc.purpose == "Separation":
				if not "HR User" in frappe.get_roles(frappe.session.user):
					frappe.throw("Only HR user with role HR User can create the employee benefit with purpose Separation")
				officiating = get_officiating_employee(hr_approver[3])
				if officiating:
					officiating = frappe.db.get_value("Employee", officiating[0].officiate, ["user_id","employee_name","designation","name"])

				vars(doc)[document_approver[0]] = officiating[0] if officiating else hr_approver[0]
				vars(doc)[document_approver[1]] = officiating[1] if officiating else hr_approver[1]
			else:
				# If employee is RM|HR Manager, it will look for Officiating, else it will go their Supervisor
				if employee[0] == final_approver[0]:
					officiating = get_officiating_employee(reports_to[3])
					if officiating:
						officiating = frappe.db.get_value("Employee", officiating[0].officiate, ["user_id","employee_name","designation","name"])
					vars(doc)[document_approver[0]] = officiating[0] if officiating else reports_to[0]
					vars(doc)[document_approver[1]] = officiating[1] if officiating else reports_to[1]
				else:
					officiating = get_officiating_employee(final_approver[3])
					if officiating:
						officiating = frappe.db.get_value("Employee", officiating[0].officiate, ["user_id","employee_name","designation","name"])
					vars(doc)[document_approver[0]] = officiating[0] if officiating else final_approver[0]
					vars(doc)[document_approver[1]] = officiating[1] if officiating else final_approver[1]
		elif workflow_state == "Approved".lower():
			if doc.docstatus == 0 and doc.workflow_state == "Approved":
				doc.workflow_state = "Waiting Approval"
			if doc.get(document_approver[0]) != frappe.session.user:
				frappe.throw(_("Only <b>{0}, {1}</b> can approve this application").format(doc.get(document_approver[0]),doc.get(document_approver[1])), title="Invalid Operation")
		elif workflow_state == "Rejected".lower():
			if doc.get(document_approver[0]) and doc.get(document_approver[0]) != frappe.session.user:
				if workflow_state != doc.get_db_value("workflow_state"):
					frappe.throw(_("Only <b>{0}, {1}</b> can reject this application").format(doc.get(document_approver[0]),doc.get(document_approver[1])), title="Invalid Operation")
		else:
			pass

	elif doc.doctype == "Leave Application":
		hr_user = frappe.db.get_single_value("HR Settings", "hr_approver")
		hr_approver = frappe.db.get_value("Employee", hr_user, ["user_id","employee_name","designation","name"])
		if workflow_state == "Draft".lower():
			vars(doc)[document_approver[0]] = employee[0]
			vars(doc)[document_approver[1]] = employee[1]

		elif workflow_state == "Waiting CEO Approval".lower():
			if doc.leave_type != "Medical Leave":
				frappe.throw("You can only forward Medical Leaves")

		elif workflow_state == "Approved".lower():
			if doc.leave_type == "Medical Leave":
				if "CEO" not in frappe.get_roles(frappe.session.user) and doc.leave_type == "Medical Leave":
					frappe.throw("Only CEO is be allowed to approve Medical Leaves ") 
				if doc.docstatus == 0 and workflow_state == "Appproved":
					doc.workflow_state = "Waiting CEO Approval"
			else:
				if  doc.leave_approver != frappe.session.user:
					frappe.throw("Only {0} can submit the leave application".format(doc.leave_approver))

				if doc.docstatus == 0 and workflow_state == "Appproved":
					doc.workflow_state = "Verified By Supervisor"

				# Checking of Final Approval have assinged an Officiating
				officiating = get_officiating_employee(final_approver[3])
				if officiating:
					final_approver = frappe.db.get_value("Employee", officiating[0].officiate, ["user_id","employee_name","designation","name"])
				if final_approver[0] != doc.leave_approver and employee[0] != final_approver[0]:
					frappe.throw("Only {0} can approve your leave application".format(frappe.bold(final_approver[0])))

			#Change employment status in  Employee Master -- Author: Thukten Dendup<thukten.dendup@bt.bt>
			doc.status= "Approved"
			emp_status = frappe.db.get_value("Leave Type", doc.leave_type, ["check_employment_status","employment_status"])
			if emp_status[0] and emp_status[1]:
				emp = frappe.get_doc("Employee", doc.employee)
				emp.employment_status = emp_status[1]
				emp.save(ignore_permissions = True)

		elif workflow_state == "Waiting Supervisor Approval".lower():
			officiating = get_officiating_employee(reports_to[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, ["user_id","employee_name","designation","name"])
			vars(doc)[document_approver[0]] = officiating[0] if officiating else reports_to[0]
			vars(doc)[document_approver[1]] = officiating[1] if officiating else reports_to[1]
			if doc.leave_approver == employee[0]:
				frappe.throw("Leave Application submitter {0} cannot be the supervisor ".format(doc.leave_approver))

		elif workflow_state == "Verified By Supervisor".lower():
			if  doc.leave_approver != frappe.session.user:
				frappe.throw("Only {0} can submit the leave application".format(doc.leave_approver))

			#Check for GM's Leaves as it will be verified and approved by GM's Supervisor(CEO)
			#Employee's beside GM will be approved by HoD(GM)
			if final_approver[0] != employee[0]:
				officiating = get_officiating_employee(final_approver[3])
				if officiating:
					officiating = frappe.db.get_value("Employee", officiating[0].officiate, ["user_id","employee_name","designation","name"])
				vars(doc)[document_approver[0]] = officiating[0] if officiating else final_approver[0]
				vars(doc)[document_approver[1]] = officiating[1] if officiating else final_approver[1]

		elif workflow_state in ['Rejected', 'Rejected By Supervisor']:
			if workflow_state == "Rejected".lower():
				doc.status = "Rejected"

			vars(doc)[document_approver[0]] = reports_to[0]
			vars(doc)[document_approver[1]] = reports_to[1]

		elif workflow_state == "Cancelled".lower():
			if frappe.session.user not in (doc.leave_approver,"Administrator"):
				frappe.throw(_("Only leave approver <b>{0}</b> ( {1} ) can cancel this document.").format(doc.leave_approver_name, doc.leave_approver), title="Operation not permitted")

	elif doc.doctype == "Travel Authorization":
		if workflow_state == "Draft".lower():
			vars(doc)[document_approver[0]] = employee[0]

		elif workflow_state == "Waiting Supervisor Approval".lower():
			officiating = get_officiating_employee(reports_to[3])
			# employee's supervisor's officiate is if himself, get supervisor of his supervisor. Jai 19 July 2022 else take supervisor's officiate 
			if officiating[0].officiate == employee[0]:
				officiating = frappe.db.get_value("Employee", frappe.db.get_value("Employee", reports_to[3], "reports_to"), ["user_id","employee_name","designation","name"])
			else:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, ["user_id","employee_name","designation","name"])
			vars(doc)[document_approver[0]] = officiating[0] if officiating else reports_to[0]
			
			if doc.supervisor == employee[0]:
				frappe.throw("Travel Authorization submitter {0} cannot be the supervisor ".format(doc.supervisor))
			
		elif workflow_state == "Approved".lower():
			if doc.supervisor != frappe.session.user:
				frappe.throw("Only {0} can Approve the Travel Authorization".format(doc.supervisor))
			if employee[0] == doc.supervisor:
				frappe.throw("Not allowed to approve his/her own Travel Authorization")
			if doc.docstatus == 0 and workflow_state == "Approved":
				doc.workflow_state = "Verified By Supervisor"

		elif workflow_state == "Verified By Supervisor".lower():
			if doc.supervisor != frappe.session.user:
				frappe.throw("Only {0} can submit the Travel Authorization".format(doc.supervisor))
			officiating = get_officiating_employee(final_approver[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, ["user_id","employee_name","designation","name"])
			vars(doc)[document_approver[0]] = officiating[0] if officiating else final_approver[0]
			vars(doc)[document_approver[1]] = officiating[1] if officiating else final_approver[1]
		
		elif workflow_state in ['Rejected', 'Rejected By Supervisor']:
			if workflow_state == "Rejected".lower():
				doc.status = "Rejected"
			vars(doc)[document_approver[0]] = reports_to[0]

	elif doc.doctype == "Travel Claim":
		if workflow_state == "Waiting Approval".lower():
			hr_user = frappe.db.get_single_value("HR Settings", "hr_approver")
			hr_approver = frappe.db.get_value("Employee", hr_user, ["user_id","employee_name","designation","name"])
			officiating = get_officiating_employee(hr_approver[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, ["user_id","employee_name","designation","name"])
			vars(doc)[document_approver[0]] = officiating[0] if officiating else hr_approver[0]
			vars(doc)[document_approver[1]] = officiating[1] if officiating else hr_approver[1]

		if workflow_state == "Claimed".lower():
			if frappe.session.user != doc.supervisor:
				frappe.throw("Only '{0}' is allowed to Approved the Travel Claim".format(doc.supervisor))
			if doc.docstatus == 0 and workflow_state == "Claimed":
				doc.workflow_state = "Waiting Approval"
		
	else:
		pass
