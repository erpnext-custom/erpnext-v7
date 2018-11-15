// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Operators Over Time Details', {
	refresh: function(frm) {
		frm.set_value("posting_date", frappe.datetime.get_today());
	},
	operator: function(frm) {
		frappe.call({
				method: "erpnext.hr.doctype.operators_over_time_details.operators_over_time_details.getoperatordtl",
				asyasdasdnc: false,
				args: {
					"employee_type" : frm.doc.employee_type,
					"operator": frm.doc.operator,					
				},
				callback: function(r){
					if(r.message){
						console.log(r.message);
						frm.set_value("operator_name", r.message);
					}
				}
		});
	}
});

cur_frm.cscript.employee_type = function() {
	cur_frm.set_value("operator", "");
	cur_frm.set_value("operator_name", "");	
}

frappe.ui.form.on("Operators Over Time Details", "refresh", function(frm) {
	 cur_frm.set_query("operator", function() { 
		if (frm.doc.employee_type == "Employee") {
			return {
				filters: [
				['Employee', 'designation', 'in', ['Operator', 'Driver']],
				['Employee', 'status', '=', 'Active']
				]
			}
		}
		else {
			return {
				filters: [
					['Muster Roll Employee', 'status', '=', 'Active']
				]
			}
		}
	});
});
