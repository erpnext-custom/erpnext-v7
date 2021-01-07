// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Rental Bill', {
	refresh: function (frm) {
		// CODE ADDED BY PHUNTSHO ON DECEMBER 22 TUES 2020
		// Allow users to view the accounting ledger
		if (frm.doc.docstatus === 1 & (typeof frm.doc.rental_payment != "undefined" || typeof frm.doc.gl_reference != "undefined")) {
			if (typeof frm.doc.rental_payment != "undefined") {
				var voucher_no = frm.doc.rental_payment
			}
			else if (typeof frm.doc.gl_reference != "undefined") {
				var voucher_no = frm.doc.gl_reference
			}
			else {
				return
			}
			frm.add_custom_button(__('Accounting Ledger'), function () {
				frappe.route_options = {
					voucher_no: voucher_no,
					from_date: frm.doc.fiscal_year + '-' + frm.doc.month + "-" + "01",
					to_date: frm.doc.posting_date,
					company: frm.doc.company,
					group_by_voucher: false
				};
				frappe.set_route("query-report", "General Ledger");
			}, __("View"));
		}
	}
});
