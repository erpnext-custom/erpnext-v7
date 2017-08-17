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
	}
});

/*cur_frm.fields_dict['customer'].get_query = function(frm) {
	if(cur_frm.doc.private == "Private") {
	console.log("INSIDE")
		return {
			filters: [["Customer", "customer_group", "like", "Internal"]]
			//filters:[['customer_group', '=', 'Private Agency'], ['customer_group', '=', 'Individual']]
		}
	}
	else {
	console.log("OUTSIDE")
		return {
			filters:[['customer_group', '!=', 'Private Agency'], ['customer_group', '!=', 'Individual']]
		}
	}
}*/

cur_frm.add_fetch("cost_center", "branch", "branch")
cur_frm.add_fetch("customer", "location", "address")
cur_frm.add_fetch("customer", "telephone_and_fax", "contact_number")

cur_frm.add_fetch("customer_cost_center", "branch", "customer_branch")
//Hiring Request Details
frappe.ui.form.on("Hiring Request Details", {
	"from_date": function(frm, cdt, cdn) {
		calculate_datetime(frm, cdt, cdn)
	},
	"to_date": function(frm, cdt, cdn) {
		calculate_datetime(frm, cdt, cdn)
	},
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
		calculate_datetime(frm, cdt, cdn)
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
	}
})

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
		return {
			filters:[['branch', "=", frm.doc.branch]]
		}
	}
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
				"customer_group": [["!=","Internal"], ["!=", "Domestic"]]
			    }
			};
		}
	});
});

