// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Supplementary Budget Tool', {
	refresh: function(frm) {
		frm.disable_save();
	},

	post_budget: function(frm) {
		if(frm.doc.to_cc && frm.doc.to_acc && frm.doc.amount && frm.doc.amount > 0 && frm.doc.fiscal_year) { 
			frappe.call({
				method: "erpnext.accounts.doctype.supplementary_budget_tool.supplementary_budget_tool.supplement",
				args: {
					"to_cc": frm.doc.to_cc,
					"to_acc": frm.doc.to_acc,
					"amount": frm.doc.amount,
					"fiscal_year": frm.doc.fiscal_year
				},
				callback: function(r) {
					if(r.message == "DONE") {
						cur_frm.set_df_property("post_budget", "read_only", 1)	
						msgprint("An amount of Nu. " + frm.doc.amount + " has been supplemented")
					}
					else {
						msgprint(r.message)
					}
				}
			});
		}
		else if(frm.doc.amount <= 0) {
			msgprint("Amount should be greater than 0")
		}
		else {
			msgprint("Fill all fields before submitting")
		}
	}
});

//cost center
//-----------------------
cur_frm.fields_dict.to_cc.get_query = function(doc) {
	return{
		filters:{
			'is_group': 0,
			'is_disabled': 0,
		}
	}
}
