// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Stock Price Template', {
	refresh: function(frm) {

	}
});

//set material name based on material code
cur_frm.add_fetch("item_code", "item_name", "item_name");

// additional validation on dates
frappe.ui.form.on("Stock Price Template", "to_date", function(frm) {
    if (frm.doc.to_date < frm.doc.from_date) {
        msgprint(__("To Date should be greater than From Date"));
        frm.set_value("to_date", get_today());
        validated = false;
    }
});

// additional validation on dates
frappe.ui.form.on("Stock Price Template", "from_date", function(frm) {
    if (frm.doc.to_date < frm.doc.from_date) {
        msgprint(__("To Date should be greater than From Date"));
        frm.set_value("from_date", get_today());
        validated = false;
    }
});

frappe.ui.form.on("Stock Price Template", "refresh", function(frm) {
    cur_frm.set_query("item_code", function() {
        return {
            "filters": {
		"disabled": 0,
		"item_group": frm.doc.naming_series
            }
        };
    });
})
