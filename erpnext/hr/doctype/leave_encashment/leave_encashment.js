// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

//cur_frm.add_fetch('employee','employee_name','employee_name');

cur_frm.add_fetch("employee", "employee_name", "employee_name")
cur_frm.add_fetch("employee", "employee_subgroup", "grade")
cur_frm.add_fetch("employee", "designation", "designation")
cur_frm.add_fetch("employee", "department", "department")
cur_frm.add_fetch("employee", "division", "division")
cur_frm.add_fetch("employee", "branch", "branch")
cur_frm.add_fetch("employee", "cost_center", "cost_center")


frappe.ui.form.on('Leave Encashment', {
	onload: function(frm){
		//frm.set_query("employee", erpnext.queries.employee);
		if (!frm.doc.application_date) {
			frm.set_value("application_date", get_today());
		}		
	},
	
	refresh: function(frm) {
			if(frm.doc.docstatus == 1 && frappe.model.can_read("Journal Entry")) {
				cur_frm.add_custom_button('Bank Entries', function() {
					frappe.route_options = {
						"Journal Entry Account.reference_type": frm.doc.doctype,
						"Journal Entry Account.reference_name": frm.doc.name,
					};
					frappe.set_route("List", "Journal Entry");
				}, __("View"));
			}
	},
	
	/*employee: function(frm){
                if (frm.doc.division) {
                        frappe.call({
                                method: "erpnext.hr.doctype.leave_encashment.leave_encashment.get_employee_cost_center",
                                args: {
                                        division: frm.doc.division
                                },
                                callback: function(r){
                                        frm.trigger("get_le_settings");
                                        frm.trigger("get_leave_balance");
                                        frm.set_value('cost_center',r.message);
                                }
                        });
                }
        },
	*/
	employee: function(frm){
		if (frm.doc.employee) {
			frappe.call({
				method: "erpnext.hr.doctype.leave_encashment.leave_encashment.get_employee_cost_center",
				args: {
					emp: frm.doc.employee
				},
				callback: function(r){
					frm.trigger("get_le_settings");
					frm.trigger("get_leave_balance");
					frm.set_value('cost_center',r.message);
				}
			});
		}
	},

	balance_before: function(frm){
		if (frm.doc.balance_before){
			frm.set_value('balance_after',(frm.doc.balance_before?frm.doc.balance_before:0)-frm.doc.encashed_days);
		}
	},
	
	get_leave_balance: function(frm) {
		if(frm.doc.docstatus==0 && frm.doc.employee && frm.doc.leave_type && frm.doc.application_date) {
			return frappe.call({
				method: "erpnext.hr.doctype.leave_application.leave_application.get_leave_balance_on",
				args: {
					employee: frm.doc.employee,
					ason_date: frm.doc.application_date,
					leave_type: frm.doc.leave_type,
					consider_all_leaves_in_the_allocation_period: true
				},
				callback: function(r) {
					if (r.message) {
						frm.set_value('balance_before', r.message);
					}
				}
			});
		}
	},

	get_le_settings: function(frm){
		if(frm.doc.docstatus==0 && frm.doc.employee && frm.doc.leave_type && frm.doc.application_date) {
			
			return frappe.call({
				method: "erpnext.hr.doctype.leave_encashment.leave_encashment.get_le_settings",
				callback: function(r) {
					if (r.message) {
						frm.set_value('encashed_days', r.message.encashment_days);
					}
				}
			});
		}		
	}
	
});
