// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.add_fetch("equipment", "equipment_type", "equipment_type")
cur_frm.add_fetch("equipment", "equipment_number", "equipment_number")
cur_frm.add_fetch("equipment", "equipment_model", "equipment_model")

frappe.ui.form.on('Insurance and Registration', {
	refresh: function(frm) {

	}
});
