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
					'project': frm.doc.project
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

	}
});


frappe.ui.form.on('Cash Journal Detail',{
	
});