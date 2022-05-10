// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Equipment Hiring Form', {
	refresh: function(frm) {
		/*if(frm.doc.private == "Private") {
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
		}*/
		cur_frm.add_custom_button(__('Logbooks'), function() {
			frappe.route_options = {
				"Logbook.equipment_hiring_form": me.frm.doc.name,
			};
			frappe.set_route("List", "Logbook");
		}, __("View"));

		/*if(!frm.doc.payment_completed && frm.doc.docstatus == 1) {
			cur_frm.add_custom_button(__('Close'), function() {
				cur_frm.cscript.update_status()
			}, __("Status"));
		}*/
	},

	onload: function(frm) {
		if (!frm.doc.request_date) {
			frm.set_value("request_date", get_today());
		}
	}		
});

cur_frm.add_fetch("tc_name", "terms", "terms")
cur_frm.add_fetch("equipment", "supplier", "supplier")

cur_frm.add_fetch("branch", "cost_center", "cost_center")

frappe.ui.form.on("Equipment Hiring Form", "refresh", function(frm) {
	cur_frm.set_query("branch", function() {
		return {
		    "filters": {
			"is_disabled": 0,
		    }
		};
	});
	cur_frm.set_query("equipment", function() {
		return {
		    "filters": {
			"is_disabled": 0,
			"branch": frm.doc.branch
		    }
		};
	});
});

