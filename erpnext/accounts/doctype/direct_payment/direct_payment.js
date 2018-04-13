// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.add_fetch("cost_center", "branch", "branch")

frappe.ui.form.on('Direct Payment', {
	refresh: function(frm) {
		if(!frm.doc.posting_date) {
			frm.set_value("posting_date", get_today())
		}

		if(frm.doc.docstatus == 1) {
			if(frappe.model.can_read("Journal Entry")) {
				cur_frm.add_custom_button('Bank Entries', function() {
					frappe.route_options = {
						"Journal Entry Account.reference_type": frm.doc.doctype,
						"Journal Entry Account.reference_name": frm.doc.name,
					};
					frappe.set_route("List", "Journal Entry");
				}, __("View"));
			}
		}
	},
	"amount": function(frm) {
		frm.set_value("taxable_amount", parseFloat(frm.doc.amount))
		calculate_tds(frm);
	},
	"tds_percent": function(frm) {
		calculate_tds(frm);
	},
	"taxable_amount": function(frm) {
		calculate_tds(frm);
	},
	"tds_amount": function(frm){
		frm.set_value("balance_amount", parseFloat(frm.doc.amount) - parseFloat(frm.doc.tds_amount))
	},
	"branch": function(frm) {
		frappe.call({
			method: "frappe.client.get_value",
			args: {
				doctype: "Branch", 
				fieldname:"expense_bank_account",
				filters: {
					name: frm.doc.branch
				}
			},
			callback: function(r) {
				if(r.message.expense_bank_account) {
					cur_frm.set_value("credit_account", r.message.expense_bank_account)
				}
				else {
					frappe.throw("Setup an Expense Bank Account in the Branch")
				}
			}
		})
	}
});

function roundOff(num) {    
    return +(Math.round(num + "e+2")  + "e-2");
}

function calculate_tds(frm) {
	var tds = roundOff(parseFloat(frm.doc.tds_percent) * parseFloat(frm.doc.taxable_amount) / 100 );
	frm.set_value("tds_amount", tds);
	frm.set_value("balance_amount", frm.doc.amount - tds);

	frappe.call({
		method: "erpnext.accounts.doctype.direct_payment.direct_payment.get_tds_account",
		args: {
			percent: frm.doc.tds_percent
		},
		callback: function(r) {
			if(r.message) {
				frm.set_value("tds_account", r.message)
				cur_frm.refresh_field("tds_account")
			}
		}
	})
}

// PL cost center
//-----------------------
cur_frm.fields_dict.cost_center.get_query = function(doc) {
	return{
		filters:{
			'is_group': 0,
			'is_disabled': 0,
		}
	}
}


cur_frm.fields_dict['budget_account'].get_query = function(doc, dt, dn) {
       return {
               filters:{
			"is_group": 0,
			"freeze_account": 0
		}
       }
}
cur_frm.fields_dict['credit_account'].get_query = function(doc, dt, dn) {
       return {
               filters:{
			"is_group": 0,
			"freeze_account": 0
		}
       }
}
