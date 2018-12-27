// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Equipment Hiring Extension', {
	refresh: function(frm) {
		if (frm.doc.journal && frappe.model.can_read("Journal Entry")) {
                        cur_frm.add_custom_button(__('Bank Entries'), function() {
                                frappe.route_options = {
                                        "Journal Entry.name": me.frm.doc.journal,
                                };
                                frappe.set_route("List", "Journal Entry");
                        }, __("View"));
                }
	},
	onload: function(frm) {
		if(!frm.doc.posting_date) {
			frm.set_value("posting_date", get_today())
		}
	},
	"hours": function(frm) {
		cur_frm.set_value("total_amount", frm.doc.hours * frm.doc.rate)
		cur_frm.refresh_field("total_amount")
	},
});

cur_frm.add_fetch("equipment", "equipment_number", "equipment_number")
cur_frm.add_fetch("ehf_name", "cost_center", "cost_center")
cur_frm.add_fetch("ehf_name", "customer", "customer")

frappe.ui.form.on("Equipment Hiring Extension", "refresh", function(frm) {
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
