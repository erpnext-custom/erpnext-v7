// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Vehicle Logbook', {
	refresh: function(frm) {
		
	},
	"vlogs_on_form_rendered": function(frm, grid_row, cdt, cdn) {
		var row = cur_frm.open_grid_row();
		if(!row.grid_form.fields_dict.operator.value) {
			row.grid_form.fields_dict.operator.set_value(frm.doc.equipment_operator)
                	row.grid_form.fields_dict.operator.refresh()
		}
	},
	"equipment": function(frm) {
		if(frm.doc.ehf_name && frm.doc.equipment) {
			frappe.call({
				"method": "erpnext.maintenance.doctype.equipment_hiring_form.equipment_hiring_form.get_rates",
				args: {"form": frm.doc.ehf_name, "equipment": frm.doc.equipment},
				callback: function(r) {
					if(r.message) {
						cur_frm.set_value("rate_type", r.message[0].rate_type)
						cur_frm.set_value("work_rate", r.message[0].rate)
						cur_frm.set_value("idle_rate", r.message[0].idle_rate)
						cur_frm.refresh_fields()
					}
				}
			})
			frappe.call({
				"method": "erpnext.maintenance.doctype.equipment.equipment.get_yards",
				args: {"equipment": frm.doc.equipment},
				callback: function(r) {
					if(r.message) {
						cur_frm.set_value("ys_km", r.message[0].lph)
						cur_frm.set_value("ys_hours", r.message[0].kph)
						cur_frm.refresh_fields()
					}
					else {
						msgprint("No yardsticks settings for the equipment")
					}
				}
			})

			get_openings(frm.doc.equipment, frm.doc.from_date, frm.doc.to_date)
		}
	},
	"final_km": function(frm) {
		calculate_distance_km(frm)
	},
	"initial_km": function(frm) {
		calculate_distance_km(frm)
	},
	"to_date": function(frm) {
		if(frm.doc.from_date > frm.doc.to_date) {
			frappe.msgprint("From Date cannot be greater than To Date")
		}
		else {
			get_openings(frm.doc.equipment, frm.doc.from_date, frm.doc.to_date)
		}
	},
	"from_date": function(frm) {
		if(frm.doc.from_date > frm.doc.to_date) {
			frappe.msgprint("From Date cannot be greater than To Date")
		}
		else {
			get_openings(frm.doc.equipment, frm.doc.from_date, frm.doc.to_date)
		}
	},
	"total_work_time": function(frm) {
		if(frm.doc.total_work_time && frm.doc.ys_hours && frm.doc.rate_type == 'With Fuel') {
			cur_frm.set_value("consumption_hours", frm.doc.total_work_time * frm.doc.ys_hours)
			cur_frm.set_value("consumption", frm.doc.consumption_km + frm.doc.consumption_hours)
			cur_frm.refresh_fields()
		}
	},
	"distance_km": function(frm) {
		if(frm.doc.distance_km && frm.doc.ys_km && frm.doc.rate_type == 'With Fuel') {
			cur_frm.set_value("consumption_km", frm.doc.distance_km / frm.doc.ys_km)
			cur_frm.set_value("consumption", frm.doc.consumption_km + frm.doc.consumption_hours)
			cur_frm.refresh_fields()
		}
	},
	opening_balance: function(frm) {
		frm.set_value("closing_balance", frm.doc.hsd_received + frm.doc.opening_balance - frm.doc.consumption)
		cur_frm.refresh_field("closing_balance")
	},
	hsd_received: function(frm) {
		frm.set_value("closing_balance", frm.doc.hsd_received + frm.doc.opening_balance - frm.doc.consumption)
		cur_frm.refresh_field("closing_balance")
	},
	consumption: function(frm) {
		frm.set_value("closing_balance", frm.doc.hsd_received + frm.doc.opening_balance - frm.doc.consumption)
		cur_frm.refresh_field("closing_balance")
	}
});

function calculate_distance_km(frm) {
	if(frm.doc.initial_km && frm.doc.final_km) {
		if(frm.doc.final_km > frm.doc.initial_km) {
			cur_frm.set_value("distance_km", frm.doc.final_km - frm.doc.initial_km)
			frm.refresh_fields()
		}
		else {
			cur_frm.set_value("distance_km", "0")
			frm.refresh_fields()
			frappe.msgprint("Final KM should be greater than Initial KM")
		}
	}
}

cur_frm.add_fetch("equipment", "equipment_number", "equipment_number")
cur_frm.add_fetch("equipment", "current_operator", "equipment_operator")
cur_frm.add_fetch("operator", "employee_name", "driver_name")

//Vehicle Log Item  Details
frappe.ui.form.on("Vehicle Log", {
	"from_time": function(frm, cdt, cdn) {
		calculate_time(frm, cdt, cdn)
	},
	"to_time": function(frm, cdt, cdn) {
		calculate_time(frm, cdt, cdn)
	},
	"from_km_reading": function(frm, cdt, cdn) {
		calculate_time(frm, cdt, cdn)
	},
	"to_km_reading": function(frm, cdt, cdn) {
		calculate_time(frm, cdt, cdn)
	},
	"idle_time": function(frm, cdt, cdn) {
		total_time(frm, cdt, cdn)
	},
	"work_time": function(frm, cdt, cdn) {
		total_time(frm, cdt, cdn)
        }
})

function get_openings(equipment, from_date, to_date) {
	if (equipment && from_date && to_date) {
		frappe.call({
			"method": "erpnext.maintenance.doctype.vehicle_logbook.vehicle_logbook.get_opening",
			args: {"equipment": equipment, "from_date": from_date, "to_date": to_date},
			callback: function(r) {
				if(r.message) {
					cur_frm.set_value("opening_balance", r.message[0])
					cur_frm.set_value("hsd_received", r.message[1])
					cur_frm.refresh_fields()
				}
			}
		})
	}
}

function total_time(frm, cdt, cdn) {
	var total_idle = total_work = 0;
	frm.doc.vlogs.forEach(function(d) {
		if(d.idle_time) { 
			total_idle += d.idle_time
		}
		if(d.work_time) {
			total_work += d.work_time
		}	
	})
	frm.set_value("total_idle_time", total_idle)
	frm.set_value("total_work_time", total_work)
	cur_frm.refresh_field("total_work_time")
	cur_frm.refresh_field("total_idle_time")
}

function calculate_time(frm, cdt, cdn) {
	var item = locals[cdt][cdn]
	if(item.from_time && item.to_time && item.to_time >= item.from_time) {
		frappe.model.set_value(cdt, cdn,"time", frappe.datetime.get_hour_diff(Date.parse("2/12/2016"+' '+item.to_time), Date.parse("2/12/2016"+' '+item.from_time)))
	}
	cur_frm.refresh_field("time")
}

function calculate_distance(frm, cdt, cdn) {
	var item = locals[cdt][cdn]
	if(item.from_km_reading && item.to_km_reading && item.to_km_reading >= item.from_km_reading) {
		frappe.model.set_value(cdt, cdn,"distance", item.to_km_reading - item.from_km_reading)
	}
	cur_frm.refresh_field("distance")
}

frappe.ui.form.on("Vehicle Logbook", "refresh", function(frm) {
    cur_frm.set_query("ehf_name", function() {
        return {
            "filters": {
                "payment_completed": 0,
		"docstatus": 1,
		"branch": frm.doc.branch
            }
        };
    });

    cur_frm.set_query("equipment", function() {
        return {
	    query: "erpnext.maintenance.doctype.equipment.equipment.get_equipments",
            "filters": {
                "ehf_name": frm.doc.ehf_name,
            }
        };
    });
	
});
