// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
cur_frm.add_fetch("pol_type", "item_name", "item_name")

frappe.ui.form.on('Equipment POL Transfer', {
	onload: function(frm) {
		if(!frm.doc.posting_date) {
			frm.set_value("posting_date", get_today())
		}
	},

	refresh: function(frm) {
		if(frm.doc.docstatus == 1) {
			cur_frm.add_custom_button(__('Accounting Ledger'), function() {
				frappe.route_options = {
					voucher_no: frm.doc.name,
					from_date: frm.doc.posting_date,
					to_date: frm.doc.posting_date,
					company: frm.doc.company,
					group_by_voucher: false
				};
				frappe.set_route("query-report", "General Ledger");
			}, __("View"));
		}
	}
});

frappe.ui.form.on("Equipment POL Transfer", "refresh", function(frm) {
    	cur_frm.set_query("pol_type", function() {
		return {
		    "filters": {
			"disabled": 0,
			"is_hsd_item": 1
		    }
		};
	    });

    	cur_frm.set_query("from_equipment", function() {
		return {
		    "filters": {
			"is_disabled": 0,
			"branch": frm.doc.branch
		    }
		};
	    });
})

