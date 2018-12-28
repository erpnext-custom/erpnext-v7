// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('POL Issue Report', {
	onload: function(frm) {
		if(!frm.doc.date) {
			frm.set_value("date", get_today())
		}
	}
});

cur_frm.add_fetch("equipment", "equipment_number", "equipment_number")
