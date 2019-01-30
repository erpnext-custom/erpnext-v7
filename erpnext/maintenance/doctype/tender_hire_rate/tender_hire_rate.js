// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Tender Hire Rate', {
	refresh: function(frm) {

	}
});

frappe.ui.form.on("Tender Hire Rate", "refresh", function(frm) {
    cur_frm.set_query("equipment_model", function() {
        return {
            "filters": {
		"equipment_type": frm.doc.equipment_type,
            }
        };
    });
})
