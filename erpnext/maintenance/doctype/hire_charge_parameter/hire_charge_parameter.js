// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Hire Charge Parameter', {
	refresh: function(frm) {
		disable_drag_drop(frm)
	},

	onload: function(frm) {
		disable_drag_drop(frm)
	}
});

function disable_drag_drop(frm) {
	frm.page.body.find('[data-fieldname="items"] [data-idx] .data-row').removeClass('sortable-handle');
}

frappe.ui.form.on("Hire Charge Parameter", "refresh", function(frm) {
    cur_frm.set_query("equipment_model", function() {
        return {
            "filters": {
		"equipment_type": frm.doc.equipment_type
            }
        };
    });
})
