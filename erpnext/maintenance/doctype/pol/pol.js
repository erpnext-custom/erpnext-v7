// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
cur_frm.add_fetch("equipment", "equipment_number", "equipment_number")

frappe.ui.form.on('POL', {
	onload: function(frm) {
		if(!frm.doc.date) {
			frm.set_value("date", get_today());
		}
	},
	"qty": function(frm) {
		calculate_total(frm)
	},

	"rate": function(frm) {
		calculate_total(frm)
	},

	"discount_amount": function(frm) {
		calculate_total(frm)
	},
});

function calculate_total(frm) {
	if(frm.doc.qty && frm.doc.rate) {
		frm.set_value("total_amount", frm.doc.qty * frm.doc.rate)
	}

	if(frm.doc.qty && frm.doc.rate && frm.doc.discount_amount) {
		frm.set_value("total_amount", (frm.doc.qty * frm.doc.rate) - frm.doc.discount_amount)
	}
}	
