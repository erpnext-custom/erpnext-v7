// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/*
--------------------------------------------------------------------------------------------------------------------------
Version          Author          CreatedOn          ModifiedOn          Remarks
------------ --------------- ------------------ -------------------  -----------------------------------------------------
  2.0		      SHIV           05/09/2017                          Original Version
--------------------------------------------------------------------------------------------------------------------------                                                                          
*/

frappe.ui.form.on('Project Payment', {
	// Follwoing code is added by SHIV on 2017/08/11
	setup: function(frm) {
		frm.get_field('references').grid.editable_fields = [
			{fieldname: 'reference_doctype', columns: 2},
			{fieldname: 'reference_name', columns: 2},
			{fieldname: 'total_amount', columns: 2},
			{fieldname: 'allocated_amount', columns: 2}
		];
		frm.get_field('advances').grid.editable_fields = [
			{fieldname: 'reference_doctype', columns: 2},
			{fieldname: 'reference_name', columns: 2},
			{fieldname: 'total_amount', columns: 2},
			{fieldname: 'allocated_amount', columns: 2}
		];
		frm.get_field('deductions').grid.editable_fields = [
			{fieldname: 'account', columns: 3},
			{fieldname: 'cost_center', columns: 2},
			{fieldname: 'amount', columns: 2}
		];		
	},
	
	refresh: function(frm) {

	}
});
