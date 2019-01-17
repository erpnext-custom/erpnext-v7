// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Salary Advance', {
	
	onload: function(frm){
		if(!frm.doc.posting_date){
			frm.set_value("posting_date", get_today());
	
		}
	},

	deduction_month(frm){
			cur_frm.set_value("monthly_deduction", parseFloat(frm.doc.claim_amount)/ frm.doc.deduction_month);
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
