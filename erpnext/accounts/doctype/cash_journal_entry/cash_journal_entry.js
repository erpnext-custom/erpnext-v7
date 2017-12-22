// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Cash Journal Entry', {
	setup: function(frm) {
		frm.get_docfield("cash_journal_detail").allow_bulk_edit = 1;		
		frm.get_field('cash_journal_detail').grid.editable_fields = [
			{fieldname: 'particulars', columns: 3},
			{fieldname: 'quantity', columns: 1},
			{fieldname: 'rate', columns: 1},
			{fieldname: 'amount', columns: 2},
			{fieldname: 'budget_account', columns: 2},
			{fieldname: 'remarks', columns: 1}
		];
	},	
	
	onload: function(frm){
		frm.fields_dict.reference_no.get_query = function(){
			return {
				filters:{
					'cost_center': frm.doc.cost_center,
					'docstatus': 1,
					'closing_balance': [">",0],
					'entry_date': ["<=",frm.doc.entry_date],
					'entry_type': 'Receipt'
				}
			}
		};
		
		frm.fields_dict['cash_journal_detail'].grid.get_field('budget_account').get_query = function(){
			return{
				filters: {
					'root_type': 'Expense'
				}
			}
		};
		
		if(frm.doc.__islocal) {
			frappe.call({
					method: "erpnext.custom_utils.get_user_info",
					args: {
						"user": frappe.session.user
					},
					callback(r) {
							cur_frm.set_value("cost_center", r.message.cost_center);
							cur_frm.set_value("branch", r.message.branch);
					}
			});
        }
	},
	
	refresh: function(frm) {
		set_mandatory(frm);
	},
	
	entry_type: function(frm){
		set_mandatory(frm);
		calculate_totals(frm);
	},
	
	amount: function(frm){
		calculate_totals(frm);
	},

	reference_no: function(frm){
		calculate_totals(frm);
	},
	
	project: function(frm){
		frm.add_fetch("project","branch","branch");
		frm.add_fetch("project","cost_center","cost_center");
	},
});


frappe.ui.form.on('Cash Journal Detail',{
	quantity: function(frm, cdt, cdn){
		calculate_amount(frm, cdt, cdn);
	},
	
	rate: function(frm, cdt, cdn){
		calculate_amount(frm, cdt, cdn);
	},
	
	amount: function(frm){
		calculate_totals(frm);
	},
	
	cash_journal_detail_remove: function(frm){
		calculate_totals(frm);
	},	
});

var set_mandatory = function(frm){
	frm.toggle_reqd(["imprest_type", "amount"], (frm.doc.entry_type == 'Receipt' ? 1 : 0));
	frm.toggle_reqd("reference_no", (frm.doc.entry_type == 'Purchase' ? 1 : 0));
	if (frm.doc.entry_type == 'Purchase'){
		frm.add_fetch("reference_no", "project","project");
		frm.add_fetch("reference_no", "project_name","project_name");
		frm.add_fetch("reference_no", "branch","branch");
		frm.add_fetch("reference_no", "cost_center","cost_center");
		frm.add_fetch("reference_no", "imprest_type","imprest_type");
		
		frm.set_df_property("project", "read_only", 1);
	}
	else {
		frm.set_df_property("project", "read_only", 0);
	}
}

var calculate_amount = function(frm, cdt, cdn){
	var child  = locals[cdt][cdn];
	var amount = 0.0;
	
	amount = parseFloat(child.quantity || 0.0)*parseFloat(child.rate || 0.0);
	frappe.model.set_value(cdt, cdn, "amount", parseFloat(amount || 0.0));
}

var get_opening_balance = function(frm){
	var opening_balance = 0.0;
	frappe.call({
		method: "erpnext.accounts.doctype.cash_journal_entry.cash_journal_entry.get_opening_balance",
		args: {
			"reference_no": frm.doc.reference_no
		},
		callback: function(r){
			if(r.message){
				opening_balance =  frappe.model.sync(parseFloat(r.message || 0.0));
			}
			else {
				opening_balance = 0.0;
			}
			//cur_frm.set_value("opening_balance",opening_balance);
		},
		async: 0
	});
	return opening_balance;
}

var calculate_totals = function(frm){
	var det = frm.doc.cash_journal_detail || [];
	var tot_opening_balance = 0.0, 
		tot_receipt_amount  = 0.0, 
		tot_purchase_amount = 0.0, 
		tot_closing_balance = 0.0;

	if(frm.doc.entry_type == 'Receipt'){
		tot_receipt_amount = parseFloat(frm.doc.amount || 0.0);
	} else {
		tot_opening_balance = get_opening_balance(frm);
				
		for(var i=0; i<det.length; i++){
			tot_purchase_amount += parseFloat(det[i].amount || 0.0);
		}		
	}
	
	tot_closing_balance = parseFloat(tot_opening_balance || 0.0) + parseFloat(tot_receipt_amount || 0.0) - parseFloat(tot_purchase_amount || 0.0);
	
	cur_frm.set_value("opening_balance", tot_opening_balance);
	cur_frm.set_value("receipt_amount", tot_receipt_amount);
	cur_frm.set_value("purchase_amount", tot_purchase_amount);
	cur_frm.set_value("closing_balance", tot_closing_balance)
}

