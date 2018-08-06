// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Budget Reappropriation Tool', {
	refresh: function(frm) {
		frm.disable_save();
	},

	reappropriate_button: function(frm) {
		if(frm.doc.from_cost_center && frm.doc.to_cost_center && frm.doc.from_account && frm.doc.to_account && frm.doc.amount && frm.doc.amount > 0 && frm.doc.fiscal_year) { 
			frappe.call({
				method: "erpnext.budget.doctype.budget_reappropriation_tool.budget_reappropriation_tool.reappropriate",
				args: {
					"from_cc": frm.doc.from_cost_center,
					"to_cc": frm.doc.to_cost_center,
					"from_acc": frm.doc.from_account,
					"to_acc": frm.doc.to_account,
					"amount": frm.doc.amount,
					"fiscal_year": frm.doc.fiscal_year
				},
				callback: function(r) {
					if(r.message == "DONE") {
						cur_frm.set_df_property("reappropriate_button", "read_only", 1)	
						msgprint("An amount of Nu. " + frm.doc.amount + " has been reappropriated")
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
	},

	/*test: function(frm) {
			frappe.call({
				method: "erpnext.budget.doctype.budget_reappropriation_tool.budget_reappropriation_tool.change",
				args: {
				},
				callback: function(r) {
					if(r.message == "DONE") {
						msgprint("An amount of Nu. " + frm.doc.amount + " has been reappropriated")
					}
					else {
						msgprint(r.message)
					}
				}
	})
	}*/
});

//cost center
//-----------------------
cur_frm.fields_dict.to_cost_center.get_query = function(doc) {
	return{
		filters:{
			'is_group': 0,
			'is_disabled': 0,
		}
	}
}

//cost center
//-----------------------
cur_frm.fields_dict.from_cost_center.get_query = function(doc) {
	return{
		filters:{
			'is_group': 0,
			'is_disabled': 0,
		}
	}
}
