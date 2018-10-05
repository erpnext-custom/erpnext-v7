// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

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
		//cur_frm.set_value("date_of_transfer",frappe.datetime.nowdate());
		//refresh_many(["date_of_transfer"]);
		this.frm.set_indicator_formatter('full_name',
                        function(doc) { return doc.dead ? "red" : "green" })
	},

	refresh: function() {
		var me = this;
		//erpnext.toggle_naming_series();
	},

	date_of_birth: function() {
		return cur_frm.call({
			method: "get_retirement_date",
			args: {date_of_birth: this.frm.doc.date_of_birth, employee_group: this.frm.doc.employee_group}
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
	},

	employment_type: function() {
		/*
		return cur_frm.call({
			method: "get_retirement_date",
			args: {date_of_birth: this.frm.doc.date_of_birth, employment_type: this.frm.doc.employment_type}
		});
		*/
		this.frm.set_value('employee_group',"");
		this.frm.set_query("employee_group", function(doc) {
			return {
				query:"erpnext.hr.doctype.employee.employee.get_employee_groups",
				filters:{
					employment_type: doc.employment_type
				}
			}
		});
	},

	employee_group: function() {
		this.frm.set_value('employee_subgroup',"");
		cur_frm.fields_dict['employee_subgroup'].get_query = function(doc, dt, dn) {
		   return {
				   filters:{"employee_group": doc.employee_group}
		   }
		}
		
		return cur_frm.call({
			method: "get_retirement_date",
			args: {date_of_birth: this.frm.doc.date_of_birth, employee_group: this.frm.doc.employee_group}
		});
	},
	
	cost_center: function(){
		if(!this.frm.doc.__islocal){
			cur_frm.set_value("date_of_transfer",frappe.datetime.nowdate());
			refresh_many(["date_of_transfer"]);
			validate_prev_doc(this.frm,__("Please select date of transfer to new cost center"));		
		}
	},
	
	status: function(){
		this.frm.toggle_reqd(["relieving_date","reason_for_resignation"],(this.frm.doc.status == 'Left' ? 1:0));
	},
	
	branch: function(){
		cur_frm.add_fetch('branch', 'gis_policy_number', 'gis_policy_number');
	},
	
	/*
	department: function(){
		if(!this.frm.doc.__islocal){
			validate_prev_doc(this.frm,__("Please select date of transfer to new department"));		
		}
	},
	
	designation: function(){
		if(!this.frm.doc.__islocal){
			validate_prev_doc(this.frm,__("Please select date of effect for designation change"));		
		}
	},
	*/	
});

function validate_prev_doc(frm, title){
	return frappe.call({
				method: "erpnext.custom_utils.get_prev_doc",
				args: {doctype: frm.doctype, docname: frm.docname, col_list: "cost_center,branch"},
				callback: function(r) {
					if(frm.doc.cost_center && (frm.doc.cost_center !== r.message.cost_center)){
						var d = frappe.prompt({
							fieldtype: "Date",
							fieldname: "date_of_transfer",
							reqd: 1,
							description: __("*This information shall be recorded in employee internal work history.")},
							function(data) {
								cur_frm.set_value("date_of_transfer",data.date_of_transfer);
								refresh_many(["date_of_transfer"]);
							},
							title, 
							__("Update")
						);
					}
				}
		});
}

cur_frm.cscript = new erpnext.hr.EmployeeController({frm: cur_frm});

//Custom Scripts
// Ver 20160703.1 Added by SSK
/*cur_frm.fields_dict['department'].get_query = function(doc, dt, dn) {
       return {
               filters:{"branch1": doc.branch}
       }
}*/

cur_frm.add_fetch("cost_center", "branch", "branch")

cur_frm.fields_dict['designation'].get_query = function(doc, dt, dn) {
   return {
		   filters:{"employee_group": doc.employee_group}
   }
}

cur_frm.fields_dict['division'].get_query = function(doc, dt, dn) {
       return {
               //filters:{"dpt_name": doc.department} // Ver20160703.1 commented by SSK
               filters:{"dpt_name": doc.department} //Ver20160703.1 Added by SSK
       }
}

cur_frm.fields_dict['section'].get_query = function(doc, dt, dn) {
       return {
               //filters:{"d_name": doc.division} //Ver20160703.1 commented by SSK
               filters:{"d_name": doc.division, "dpt_name": doc.department} //Ver20160703.1 added by SSK
       }
}

cur_frm.fields_dict['cost_center'].get_query = function(doc, dt, dn) {
       return {
               filters:{
			"is_group": 0,
			"is_disabled": 0
		}
       }
}

cur_frm.fields_dict['gewog'].get_query = function(doc, dt, dn) {
       return {
               filters:{"dzongkhag": doc.dzongkhag}
       }
}

cur_frm.fields_dict['village'].get_query = function(doc, dt, dn) {
       return {
               filters:{"gewog": doc.gewog}
       }
}

