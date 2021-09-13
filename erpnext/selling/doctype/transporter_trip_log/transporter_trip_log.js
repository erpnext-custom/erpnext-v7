// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Transporter Trip Log', {
	setup: function(frm) {
		frm.get_docfield("item").allow_bulk_edit = 1;
	}
});

frappe.ui.form.on('Trip Log Item', {
	equipment: function(frm,cdt,cdn){
		var items = locals[cdt][cdn];
		if(items.equipment == ""){
			items.equipment_number = "";
			items.equipment_type = "";
			items.equipment_model = "";
			items.rate = "";
			items.amount = "";
			frm.refresh_fields(['equipment_number', 'equipment_type', 'equipment_model', 'rate', 'amount']);	
		}
	},
	transporter_payment_eligible: function(frm,cdt,cdn){
		var items = locals[cdt][cdn];
		if(items.transporter_payment_eligible == 0){
			items.expense_account = "";
			items.transporter_rate = "";
			frm.refresh_fields(['expense_account', 'transporter_rate']);	
		}
	}
});