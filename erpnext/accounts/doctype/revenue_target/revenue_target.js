// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/*
--------------------------------------------------------------------------------------------------------------------------
Version          Author          CreatedOn          ModifiedOn          Remarks
------------ --------------- ------------------ -------------------  -----------------------------------------------------
1.0		          SHIV		                        15/11/2017         Original Version
--------------------------------------------------------------------------------------------------------------------------                                                                          
*/

frappe.ui.form.on('Revenue Target', {
	setup: function(frm){
		frm.get_docfield("revenue_target_account").allow_bulk_edit = 1;
		
		frm.get_field("revenue_target_account").grid.editable_fields = [
			{fieldname: 'cost_center', columns: 2},
			{fieldname: 'account', columns: 2},
			{fieldname: 'account_code', columns: 2},
			{fieldname: 'target_amount', columns: 2}
		];
	},
	onload: function(frm){
		frm.fields_dict['revenue_target_account'].grid.get_field('account').get_query = function(){
			return{
				filters: {
					'root_type': 'Income'
				}
			}
		}
	},
	refresh: function(frm) {

	}
});

frappe.ui.form.on('Revenue Target Account',{
	target_amount: function(frm){
		calculate_total(frm);
	},
	
	revenue_target_account_remove: function(frm){
		calculate_total(frm);
	},
});

var calculate_total = function(frm){
	var list = frm.doc.revenue_target_account || [];
	var tot_target_amount = 0.0;
	
	for(var i=0; i<list.length; i++){
		tot_target_amount = parseFloat(tot_target_amount || 0) + parseFloat(list[i].target_amount || 0.0);
	}
	
	cur_frm.set_value("tot_target_amount", parseFloat(tot_target_amount));
}