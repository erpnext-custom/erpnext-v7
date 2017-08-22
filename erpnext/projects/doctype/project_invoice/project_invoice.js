// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Project Invoice', {
	setup: function(frm){
		frm.get_field('project_invoice_boq').grid.editable_fields = [
			{fieldname: 'item', columns: 3},
			{fieldname: 'uom', columns: 1},
			{fieldname: 'quantity', columns: 2},
			{fieldname: 'rate', columns: 2},
			{fieldname: 'amount', columns: 2}
		];
	},
	
	refresh: function(frm) {

	}
});
