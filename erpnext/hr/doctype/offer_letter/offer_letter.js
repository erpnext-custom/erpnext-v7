// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.provide("erpnext.offer_letter");

frappe.ui.form.on("Offer Letter", {
	select_terms: function(frm) {
		frappe.model.get_value("Terms and Conditions", frm.doc.select_terms, "terms", function(value) {
			frm.set_value("terms", value.terms);
		});
	},

	refresh:function(frm){
		if((!frm.doc.__islocal) && (frm.doc.status=='Accepted') && (frm.doc.docstatus===1)){
			frm.add_custom_button(__('Make Employee'),
				function() {
					erpnext.offer_letter.make_employee(frm)
				}
			);
		}
	}

});

erpnext.offer_letter.make_employee = function(frm) {
	frappe.model.open_mapped_doc({
		method: "erpnext.hr.doctype.offer_letter.offer_letter.make_employee",
		frm: frm
	});
};

// Ver 20160701.1 by SSK, Original Version

// Terms and Conditions population
frappe.ui.form.on("Offer Letter", {
	hr_terms: function(frm) {
		frappe.model.get_value("Terms of Reference", frm.doc.hr_terms, "hr_terms", function(value) {
			frm.set_value("hr_terms_desc", value.hr_terms);
		});
	}
});
