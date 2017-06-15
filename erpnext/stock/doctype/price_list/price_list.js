// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

$.extend(cur_frm.cscript, {
	refresh: function() {
		cur_frm.add_custom_button(__("Add / Edit Prices"), function() {
			frappe.route_options = {
				"price_list": cur_frm.doc.name
			};
			frappe.set_route("Report", "Item Price");
		}, "icon-money");
	}
});

// additional validation on dates
frappe.ui.form.on("Price List", "price_valid_to", function(frm) {
    if (frm.doc.price_valid_to < frm.doc.price_valid_from) {
        msgprint(__("To Date should be greater than From Date"));
        frm.set_value("price_valid_to", get_today());
        validated = false;
    }
});

// additional validation on dates
frappe.ui.form.on("Price List", "price_valid_from", function(frm) {
    if (frm.doc.price_valid_from > frm.doc.price_valid_to) {
        msgprint(__("To Date should be greater than From Date"));
        frm.set_value("price_valid_from", get_today());
        validated = false;
    }
});
