// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('RRCO Receipt Modifier', {
	setup: function(frm){
		frm.get_field('items').grid.editable_fields = [
			{fieldname: 'receipt_no', columns: 2},
			{fieldname: 'purchase_invoice', columns: 2},
			{fieldname: 'receipt_number', columns: 2},
			{fieldname: 'receipt_date', columns: 2},
			{fieldname: 'cheque_no', columns: 2},
			{fieldname: 'cheque_date', columns: 2},

		];		
	},
	refresh: function(frm) {
		//frm.disable_save()
		cur_frm.toggle_display("supplier", true)
	},
	get_entries: function(frm) {
		cur_frm.call({
			method: "get_entries",
			doc: frm.doc,
		})
	},

});

cur_frm.fields_dict.items.grid.get_field("receipt_no").get_query = function(doc) {
	return {
		filters: {
			"docstatus": 1
		}
	}
}
