// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Imprest Receipt', {
	refresh: function(frm) {
		enable_disable(frm);
	},
	onload: function(frm) {
		// Updating default information based on loggedin user
		if(frm.doc.__islocal) {
			if(!frm.doc.branch){
				frappe.call({
						method: "erpnext.custom_utils.get_user_info",
						args: {
							"user": frappe.session.user
						},
						callback(r) {
							if(r.message){
								cur_frm.set_value("cost_center", r.message.cost_center);
								cur_frm.set_value("branch", r.message.branch);
							}
						}
				});
			}
        }
		
		/*
		if(!frm.doc.entry_date){
			cur_frm.set_value("entry_date", frappe.datetime.now_datetime());
		}
		*/
	},
	branch: function(frm){
		update_totals(frm);
		
		// Update Cost Center
		if(frm.doc.branch){
			frappe.call({
				method: 'frappe.client.get',
				args: {
					doctype: 'Cost Center',
					filters: {
						'branch': frm.doc.branch
					},
					fields: ['name']
				},
				callback: function(r){
					if(r.message){
						cur_frm.set_value("cost_center", r.message.name);
						refresh_field('cost_center');
					}
				}
			});
		}
	},
	amount: function(frm){
		update_totals(frm);
	},
});

function enable_disable(frm){
	if(frm.doc.workflow_state == 'Waiting Approval'){
		if(!in_list(user_roles, "Imprest Manager") && !in_list(user_roles, "Accounts User")){
			frm.set_df_property("amount", "read_only", 1);
			frm.disable_save();
		}
	}
	else {
		frm.enable_save();
	}
}

var update_totals = function(frm){
	cur_frm.set_value("opening_balance",0.0);
	cur_frm.set_value("receipt_amount", parseFloat(frm.doc.amount || 0.0));
	cur_frm.set_value("closing_balance", parseFloat(frm.doc.amount || 0.0));
		
	if(frm.doc.branch){
		frappe.call({
			method: "erpnext.accounts.doctype.imprest_receipt.imprest_receipt.get_opening_balance",
			args: {
				"branch": frm.doc.branch,
				"docname": frm.doc.name
			},
			callback: function(r){
				if(r.message){
					cur_frm.set_value("opening_balance",parseFloat(r.message || 0.0));
					cur_frm.set_value("receipt_amount", parseFloat(frm.doc.amount || 0.0));
					cur_frm.set_value("closing_balance", parseFloat(r.message || 0.0)+parseFloat(frm.doc.receipt_amount || 0.0));
				}
			}
		});
	}
}