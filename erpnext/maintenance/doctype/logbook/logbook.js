// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.add_fetch("equipment", "supplier", "supplier")
cur_frm.add_fetch("equipment_hiring_form", "target_hour", "target_hours")

frappe.ui.form.on('Logbook', {
	refresh: function(frm) {
	    cur_frm.set_query("equipment_hiring_form", function() {
		return {
		    "filters": {
			"equipment": frm.doc.equipment,
			"docstatus": 1,
			"branch": frm.doc.branch
		    }
		};
	    });

	}
});
