// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Salary Remittance', {


onload: function(frm){
},
	


get_details: function(frm) {
	get_records(frm.doc.month, frm.doc.fiscal_year)
	//get_message(original_message)
		}

});

function get_records(month, fiscal_year) {
	frappe.call({
		method: "erpnext.accounts.doctype.salary_remittance.salary_remittance.get_dtls",
		args: {
			
			"month" : month,
			"fiscal_year" : fiscal_year
			
		     },
		callback: function(r) {
				console.log(r);
				cur_frm.clear_table("items");
				r.message.forEach(function(mr) {

				var row = frappe.model.add_child(cur_frm.doc, "Salary Remittance Item", "items");

						row.salary_component 	= mr['salary_component'];
						row.bank 		= mr['institution_name'];
						row.amount 	= mr['amount'];
						row.original_message = mr['message']

						refresh_field("items");
						});
						
			}
		})
	}

