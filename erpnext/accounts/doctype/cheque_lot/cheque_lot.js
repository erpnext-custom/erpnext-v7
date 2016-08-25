// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Cheque Lot', {
	no_of_cheques: function(frm) {
		if(frm.doc.start_no) {
			frm.set_value("end_no", frm.doc.start_no + frm.doc.no_of_cheques)
		}
	},
	start_no: function(frm) {
		if(frm.doc.no_of_cheques) {
			frm.set_value("end_no", frm.doc.start_no + frm.doc.no_of_cheques)
		}
		frm.set_value("next_no", frm.doc.start_no)
	}
});
