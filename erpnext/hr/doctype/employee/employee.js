// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

cur_frm.add_fetch("branch", "cost_center", "cost_center")
frappe.provide("erpnext.hr");
erpnext.hr.EmployeeController = frappe.ui.form.Controller.extend({
	setup: function() {
		this.frm.fields_dict.user_id.get_query = function(doc, cdt, cdn) {
			return { query:"frappe.core.doctype.user.user.user_query"} }
		this.frm.fields_dict.reports_to.get_query = function(doc, cdt, cdn) {
			return { query: "erpnext.controllers.queries.employee_query"} }
	},

	onload: function() {
		this.frm.set_query("leave_approver", "leave_approvers", function(doc) {
			return {
				query:"erpnext.hr.doctype.employee_leave_approver.employee_leave_approver.get_approvers",
				filters:{
					user: doc.user_id
				}
			}
		});
	},

	refresh: function() {
		var me = this;
		erpnext.toggle_naming_series();
	},

	date_of_birth: function() {
		return cur_frm.call({
			method: "get_retirement_date",
			args: {date_of_birth: this.frm.doc.date_of_birth}
		});
	},

	salutation: function() {
		if(this.frm.doc.salutation) {
			this.frm.set_value("gender", {
				"Mr": "Male",
				"Ms": "Female"
			}[this.frm.doc.salutation]);
		}
	},

	make_salary_structure: function(btn) {
		frappe.model.open_mapped_doc({
			method: "erpnext.hr.doctype.employee.employee.make_salary_structure",
			frm: cur_frm
		});
	}
});
cur_frm.cscript = new erpnext.hr.EmployeeController({frm: cur_frm});

//Custom Scripts
// Ver 20160703.1 Added by SSK
cur_frm.fields_dict['department'].get_query = function(doc, dt, dn) {
       return {
               filters:{"branch1": doc.branch}
       }
}

cur_frm.fields_dict['division'].get_query = function(doc, dt, dn) {
       return {
               //filters:{"dpt_name": doc.department} // Ver20160703.1 commented by SSK
               filters:{"dpt_name": doc.department, "branch": doc.branch} //Ver20160703.1 Added by SSK
       }
}

cur_frm.fields_dict['section'].get_query = function(doc, dt, dn) {
       return {
               //filters:{"d_name": doc.division} //Ver20160703.1 commented by SSK
               filters:{"d_name": doc.division, "dpt_name": doc.department, "branch": doc.branch} //Ver20160703.1 added by SSK
       }
}

cur_frm.fields_dict['employee_subgroup'].get_query = function(doc, dt, dn) {
       return {
               filters:{"employee_group": doc.employee_group}
       }
}

cur_frm.fields_dict['designation'].get_query = function(doc, dt, dn) {
       return {
               filters:{"employee_subgroup": doc.employee_subgroup}
       }
}
