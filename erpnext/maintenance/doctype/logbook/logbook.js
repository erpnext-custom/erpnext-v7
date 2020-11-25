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

	},

	equipment: function(frm) {
                return frappe.call({
                        method: "get_ehf",
                        doc: frm.doc,
                        callback: function(r, rt) {
                                frm.refresh_fields();
                        },
                        freeze: true,
                });
        },
});

frappe.ui.form.on("Logbook Item", {
	"uom": function(frm, cdt, cdn) {
		calculate_time(frm, cdt, cdn)
	},
	"initial_time": function(frm, cdt, cdn) {
		calculate_time(frm, cdt, cdn)
	},
	"initial_reading": function(frm, cdt, cdn) {
		calculate_time(frm, cdt, cdn)
	},
	"target_trip": function(frm, cdt, cdn) {
		calculate_time(frm, cdt, cdn)
	},
	"final_reading": function(frm, cdt, cdn) {
		calculate_time(frm, cdt, cdn)
	},
	"idle_time": function(frm, cdt, cdn) {
		calculate_time(frm, cdt, cdn)
	},
})

function calculate_time(frm, cdt, cdn) {
	var hour = 0
	var item = locals[cdt][cdn]
	if(item.uom == "Hour") {
		hour = item.final_reading - item.initial_reading
	}
	else if(item.uom == "Time") {
		hour = frappe.datetime.get_hour_diff("2020-12-12 " + item.initial_time, "2020-12-12 " + item.final_time) - item.idle_time
	}
	else {
		if (item.target_trip) {
			hour = item.initial_reading/item.target_trip*frm.doc.scheduled_working_hour
		}
	}
	frappe.model.set_value(cdt, cdn,"hours", hour)
	cur_frm.refresh_fields()
}
