// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Leave Encashment', {
	onload: function(frm){
		//frm.set_query("employee", erpnext.queries.employee);
	},
	
	refresh: function(frm) {

	},
	
	employee: function(frm){
		frappe.call({
			method: "erpnext.hr.doctype.leave_encashment.leave_encashment.get_employee_cost_center",
			args: {
				division: frm.doc.division
			},
			callback: function(r){
				frm.set_value('cost_center',r.message);
			}
		});
	},
});
