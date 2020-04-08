// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Load Request', {
	refresh: function(frm) {
		custom.apply_default_settings(frm);
	},
	onload: function(frm) {
                frm.set_query("vehicle", function() {
                        return {
                                "filters": {
                                        "user": frm.doc.user,
					"vehicle_status": "Active",
                                }
                        }
                });
                frm.set_query("crm_branch", function() {
                        return {
                                filters: {
                                        "has_common_pool": 1
                                }
                        }
                });
        },
        "user": function(frm) {
                frm.set_value("vehicle","");
        },

});
