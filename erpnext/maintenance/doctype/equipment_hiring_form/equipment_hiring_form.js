// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Equipment Hiring Form', {
	refresh: function(frm) {
		if(frm.doc.private == "Private") {
			cur_frm.set_df_property("advance_amount", "reqd", 1)
		}
		if (frm.doc.advance_journal && frappe.model.can_read("Journal Entry")) {
			cur_frm.add_custom_button(__('Bank Entries'), function() {
				frappe.route_options = {
					"Journal Entry Account.reference_type": me.frm.doc.doctype,
					"Journal Entry Account.reference_name": me.frm.doc.name,
				};
				frappe.set_route("List", "Journal Entry");
			}, __("View"));
		}
		cur_frm.add_custom_button(__('Logbooks'), function() {
			frappe.route_options = {
				"Vehicle Logbook.ehf_name": me.frm.doc.name,
			};
			frappe.set_route("List", "Vehicle Logbook");
		}, __("View"));
		cur_frm.add_custom_button(__('Invoices'), function() {
			frappe.route_options = {
				"Hire Charge Invoice.ehf_name": me.frm.doc.name,
			};
			frappe.set_route("List", "Hire Charge Invoice");
		}, __("View"));

		if(!frm.doc.payment_completed && frm.doc.docstatus == 1) {
			cur_frm.add_custom_button(__('Close'), function() {
				cur_frm.cscript.update_status()
			}, __("Status"));
		}
	},
	onload: function(frm) {
		if (!frm.doc.request_date) {
			frm.set_value("request_date", get_today());
		}
	},
	"total_hiring_amount": function(frm) {
		if(frm.doc.docstatus != 1 && frm.doc.private == "Private") {
			frm.set_value("advance_amount", frm.doc.total_hiring_amount)
		}
	},
	"private": function(frm) {
		cur_frm.toggle_reqd("customer_cost_center", frm.doc.private == 'CDCL')
		cur_frm.toggle_reqd("customer_branch", frm.doc.private == 'CDCL')
		cur_frm.toggle_reqd("advance_amount", frm.doc.private == 'Private')
	},
});

cur_frm.add_fetch("tc_name", "terms", "terms")

cur_frm.add_fetch("cost_center", "branch", "branch")
cur_frm.add_fetch("customer", "location", "address")
cur_frm.add_fetch("customer", "telephone_and_fax", "contact_number")

cur_frm.add_fetch("customer", "cost_center", "customer_cost_center");
cur_frm.add_fetch("customer", "branch", "customer_branch");
//cur_frm.add_fetch("customer_cost_center", "branch", "customer_branch")

//Hiring Request Details
frappe.ui.form.on("Hiring Request Details", {
	"from_date": function(frm, cdt, cdn) {
		calculate_datetime(frm, cdt, cdn)
	},
	"to_date": function(frm, cdt, cdn) {
		calculate_datetime(frm, cdt, cdn)
	},
	"tender_hire_rate": function(frm, cdt, cdn) {
		
	}
})

function calculate_datetime(frm, cdt, cdn) {
	var item = locals[cdt][cdn]
	if(item.to_date && item.from_date && item.to_date >= item.from_date) {
		days = frappe.datetime.get_day_diff(item.to_date, item.from_date) + 1
		hours = days * 8
		frappe.model.set_value(cdt, cdn,"number_of_hours", hours)
		frappe.model.set_value(cdt, cdn,"total_hours", hours)
		frappe.model.set_value(cdt, cdn,"number_of_days", days)
	}
	cur_frm.refresh_field("total_hours")
	cur_frm.refresh_field("number_of_hours")
	cur_frm.refresh_field("number_of_days")
}

//Hiring Approval Details
cur_frm.add_fetch("equipment", "equipment_number", "equipment_number")

frappe.ui.form.on("Hiring Approval Details", {
	"from_date": function(frm, cdt, cdn) {
		calculate_datetime(frm, cdt, cdn)
	},
	"to_date": function(frm, cdt, cdn) {
		if(frm.doc.from_date && frm.doc.to_date && frm.doc.from_date > frm.doc.to_date) {
			msgprint("To Date cannot be smaller than from date")
			frappe.set_value("to_date", "")
		}
		else {
			calculate_datetime(frm, cdt, cdn)
		}
	},
	"rate": function(frm, cdt, cdn) {
		calculate_amount(frm, cdt, cdn)
	},
	"rate1": function(frm, cdt, cdn) {
		calculate_amount(frm, cdt, cdn)
	},
	"rate2": function(frm, cdt, cdn) {
		calculate_amount(frm, cdt, cdn)
	},
	"rate3": function(frm, cdt, cdn) {
		calculate_amount(frm, cdt, cdn)
	},
	"rate4": function(frm, cdt, cdn) {
		calculate_amount(frm, cdt, cdn)
	},
	"rate5": function(frm, cdt, cdn) {
		calculate_amount(frm, cdt, cdn)
	},
	"total_hours": function(frm, cdt, cdn) {
		calculate_amount(frm, cdt, cdn)
	},
	"approved_items_remove": function(frm) {
		calculate_total(frm)
	},
	"grand_total": function(frm, cdt, cdn) {
		calculate_total(frm)
	},
	"equipment": function(frm, cdt, cdn) {
		get_rates(frm, cdt, cdn)
	},
	"rate_type": function(frm, cdt, cdn) {
		get_rates(frm, cdt, cdn)
	},
	"equipment": function(frm, cdt, cdn) {
		doc = locals[cdt][cdn]
		cur_frm.fields_dict.approved_items.grid.toggle_reqd("equipment_number", doc.equipment)
		cur_frm.fields_dict.approved_items.grid.toggle_reqd("rate_type", doc.equipment)
		cur_frm.fields_dict.approved_items.grid.toggle_reqd("rate", doc.equipment)
		cur_frm.fields_dict.approved_items.grid.toggle_reqd("idle_rate", doc.equipment)
		cur_frm.fields_dict.approved_items.grid.toggle_reqd("place", doc.equipment)
	},
	"from_time": function(frm, cdt, cdn) {
		calculate_time(frm, cdt, cdn)
	},
	"to_time": function(frm, cdt, cdn) {
		calculate_time(frm, cdt, cdn)
	},
	"tender_hire_rate": function(frm, cdt, cdn) {
		get_diff_rates(frm, cdt, cdn)	
	}
})

function calculate_time(frm, cdt, cdn) {
	doc = locals[cdt][cdn]
	if (doc.from_time && doc.to_time) {
		var sd=Date.parse("2/12/2016"+' '+doc.from_time)
		var ed=Date.parse("2/12/2016"+' '+doc.to_time)
		console.log(sd)
		if(sd > ed) {
			frappe.msgprint("From Time should be smaller than To Date")
		}
		else {
			frappe.model.set_value(cdt, cdn, "total_hours", (frappe.datetime.get_hour_diff(doc.to_date + " " + doc.to_time, doc.from_date + " " + doc.from_time)))
			cur_frm.refresh_fields()
		}
	}
}

function get_rates(frm, cdt, cdn) {
	doc = locals[cdt][cdn]
	if (doc.equipment && doc.rate_type) {
		return frappe.call({
			method: "erpnext.maintenance.doctype.equipment_hiring_form.equipment_hiring_form.get_hire_rates",
			args: {"e": doc.equipment, "rtype": doc.rate_type},
			callback: function(r) {
				if(r.message) {
					if(doc.rate_type == "Without Fuel") {
						frappe.model.set_value(cdt, cdn, "rate", r.message[0].without_fuel)
					}
					else {
						frappe.model.set_value(cdt, cdn, "rate", r.message[0].with_fuel)
					}
					frappe.model.set_value(cdt, cdn, "idle_rate", r.message[0].idle)
				}				
				cur_frm.refresh_fields()
			}
		})	
	}
}

function get_diff_rates(frm, cdt, cdn) {
	doc = locals[cdt][cdn]
	if (doc.equipment && doc.rate_type && doc.tender_hire_rate) {
		return frappe.call({
			method: "erpnext.maintenance.doctype.equipment_hiring_form.equipment_hiring_form.get_diff_hire_rates",
			args: { "tr": doc.tender_hire_rate},
			callback: function(r) {
				if(r.message) {
					if(doc.rate_type == "Without Fuel") {
						frappe.model.set_value(cdt, cdn, "rate", r.message[0].without_fuel)
					}
					else {
						frappe.model.set_value(cdt, cdn, "rate", r.message[0].with_fuel)
					}
					frappe.model.set_value(cdt, cdn, "idle_rate", r.message[0].idle)
				}				
				cur_frm.refresh_fields()
			}
		})
	}
}

function calculate_total(frm) {
	var total = 0;
	frm.doc.approved_items.forEach(function(d) { 
		total += d.grand_total	
	})
	frm.set_value("total_hiring_amount", total)
	frm.refresh_field("total_hiring_amount")
}

function calculate_amount(frm, cdt, cdn) {
	var item = locals[cdt][cdn]
	if(item.rate && item.total_hours) {
		grand_amount = item.rate * item.total_hours
		if(item.rate1) {
			grand_amount += item.rate1 * item.total_hours
		}
		if(item.rate2) {
			grand_amount += item.rate2 * item.total_hours
		}
		if(item.rate3) {
			grand_amount += item.rate3 * item.total_hours
		}
		if(item.rate4) {
			grand_amount += item.rate4 * item.total_hours
		}
		if(item.rate5) {
			grand_amount += item.rate5 * item.total_hours
		}
		frappe.model.set_value(cdt, cdn,"grand_total", grand_amount)
	}
	cur_frm.refresh_field("grand_total")
	
}

//Filter equipments based on branch
frappe.ui.form.on("Equipment Hiring Form", "refresh", function(frm) {
	frm.fields_dict['approved_items'].grid.get_field('equipment').get_query = function(doc, cdt, cdn) {
		doc = locals[cdt][cdn]
		return {
			"query": "erpnext.maintenance.doctype.equipment_hiring_form.equipment_hiring_form.equipment_query",
			filters: {'branch': frm.doc.branch, 'equipment_type': doc.equipment_type, "from_date": doc.from_date, "to_date": doc.to_date}
		}
	}
	cur_frm.set_query("tc_name", function() {
		return {
		    "filters": {
			"disabled": 0,
			"reference": "Equipment Hiring Form"
		    }
		};
	});
	cur_frm.set_query("customer", function() {
		if(frm.doc.private == "CDCL") {
			return {
			    "filters": {
				"disabled": 0,
				"customer_group": "Internal"
			    }
			};
		}
		else if(frm.doc.private == "Private") {
			return {
			    "filters": {
				"disabled": 0,
				"customer_group": "Domestic"
			    }
			};
		}
		else {
			return {
			    "filters": {
				"disabled": 0,
				"customer_group": ["not in", "Internal, Domestic"]
			    }
			};
		}
	});
});

cur_frm.cscript.update_status = function(){
	var doc = cur_frm.doc;
	frappe.ui.form.is_saving = true;
	frappe.call({
		method: "erpnext.maintenance.doctype.equipment_hiring_form.equipment_hiring_form.update_status",
		args: {name: doc.name},
		callback: function(r){
			cur_frm.reload_doc();
		},
		always: function() {
			frappe.ui.form.is_saving = false;
		}
	});
}

frappe.ui.form.on("Hiring Approval Detail", "refresh", function(frm) {
    cur_frm.set_query("tender_hire_rate", function() {
        return {
            "filters": {
                "customer": frm.doc.customer,
		"equipment_type": frm.doc.equipment_type,
		"docstatus": 1,
		"branch": frm.doc.branch
            }
        };
    });
})

cur_frm.fields_dict['approved_items'].grid.get_field('tender_hire_rate').get_query = function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	return {
		filters: [
		['Tender Hire Rate', 'docstatus', '=', 1],
		['Tender Hire Rate', 'branch', '=', frm.branch],
		['Tender Hire Rate', 'customer', '=', frm.customer],
		['Tender Hire Rate', 'from_date', '<=', get_today()],
		['Tender Hire Rate', 'to_date', '>=', get_today()],
		['Tender Hire Rate', 'equipment_type', '=', d.equipment_type]
		]
	}
}
