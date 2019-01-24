// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.add_fetch("employee", "employment_type", "employment_type");
cur_frm.add_fetch("employee", "employee_group", "employee_group");
cur_frm.add_fetch("employee", "employee_subgroup", "employee_subgroup");
cur_frm.add_fetch("employee", "branch", "branch");
cur_frm.add_fetch("employee", "cost_center", "cost_center");
cur_frm.add_fetch("employee", "business_activity", "business_activity");

frappe.ui.form.on('Salary Advance', {
	total_claim: function(frm){
		cur_frm.set_value("monthly_deduction", Math.ceil(parseFloat(frm.doc.total_claim)/ frm.doc.deduction_month));
	},
	
	deduction_month: function(frm){
		cur_frm.set_value("monthly_deduction", Math.ceil(parseFloat(frm.doc.total_claim)/ frm.doc.deduction_month));
	},
		
	employee: function(frm) {
		get_basic_salary(frm.doc);
	},
});

var get_basic_salary=function(doc){
	cur_frm.call({
		method: "get_basic_salary",
		doc:doc
	});

}
