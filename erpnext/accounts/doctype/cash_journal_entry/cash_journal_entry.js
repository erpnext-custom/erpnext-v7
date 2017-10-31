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
		set_mandatory(frm);
	},	
	
	onload: function(frm){
		frm.fields_dict.reference_no.get_query = function(){
			return {
				filters:{
					'project': frm.doc.project,
					'docstatus': 1,
					'closing_balance': [">",0]
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
	},
	
	refresh: function(frm) {
		set_mandatory(frm);
	},
	
	entry_type: function(frm){
		set_mandatory(frm);
		calculate_balances(frm);
		console.log(frm);
	},
	
	amount: function(frm){
		calculate_balances(frm);
	},
	
	opening_balance: function(frm){
		calculate_balances(frm);
	},
});


frappe.ui.form.on('Cash Journal Detail',{
	
});

var set_mandatory = function(frm){
	frm.toggle_reqd(["imprest_type", "amount"], (frm.doc.entry_type == 'Receipt' ? 1 : 0));
	frm.toggle_reqd("reference_no", (frm.doc.entry_type == 'Purchase' ? 1 : 0));	
}

var calculate_balances = function(frm){
	var closing_balance = 0.0;
	
	if(frm.doc.entry_type == 'Receipt'){
		frm.set_value("receipt_amount", parseFloat(frm.doc.amount || 0.0))
	} else {
		frm.set_value("receipt_amount", 0.0)
	}
	
	closing_balance = parseFloat(frm.doc.opening_balance || 0.0) + parseFloat(frm.doc.receipt_amount || 0.0) - parseFloat(frm.doc.purchase_amount || 0.0)
	frm.set_value("closing_balance", closing_balance)
}