// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Hire Charge Parameter', {
	refresh: function(frm) {
		disable_drag_drop(frm)
	},

	onload: function(frm) {
		disable_drag_drop(frm)
	},

	"items_on_form_rendered": function(frm, grid_row, cdt, cdn) {
		var row = cur_frm.open_grid_row();
		var d = get_today().toString()
		row.grid_form.fields_dict.from_date.set_value(d.substring(8) + "-" + d.substring(5, 7) + "-" + d.substring(0, 4))
		row.grid_form.fields_dict.rate_fuel.set_value(frm.doc.with_fuel)
		row.grid_form.fields_dict.rate_wofuel.set_value(frm.doc.without_fuel)
		row.grid_form.fields_dict.idle_rate.set_value(frm.doc.idle)
		row.grid_form.fields_dict.yard_hours.set_value(frm.doc.lph)
		row.grid_form.fields_dict.yard_distance.set_value(frm.doc.kph)
		row.grid_form.fields_dict.perf_bench.set_value(frm.doc.benchmark)
		row.grid_form.fields_dict.main_int.set_value(frm.doc.interval)
		row.grid_form.fields_dict.from_date.refresh()
	},
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
