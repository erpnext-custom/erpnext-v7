// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Break Down Report', {
	refresh: function(frm) {
		if (frm.doc.docstatus == 1 && !frm.doc.job_card) {
			frm.add_custom_button("Create Job Card", function() {
				frappe.model.open_mapped_doc({
					method: "erpnext.maintenance.doctype.break_down_report.break_down_report.make_job_card",
					frm: cur_frm
				})
			});
		}

	},
	onload: function(frm) {
		if (!frm.doc.date) {
			frm.set_value("date", get_today());
		}
	},
	owned_by: function(frm) {
		cur_frm.toggle_reqd("customer_cost_center", frm.doc.owned_by == 'CDCL')
		cur_frm.toggle_reqd("customer_branch", frm.doc.owned_by == 'CDCL')
	}
});

cur_frm.add_fetch("cost_center", "branch", "branch");
cur_frm.add_fetch("customer", "customer_group", "client");
cur_frm.add_fetch("equipment", "equipment_model", "equipment_model");
cur_frm.add_fetch("equipment", "equipment_type", "equipment_type");
cur_frm.add_fetch("equipment", "equipment_number", "equipment_number");

cur_frm.add_fetch("customer_cost_center", "branch", "customer_branch");

frappe.ui.form.on("Break Down Report", "refresh", function(frm) {
    cur_frm.set_query("equipment", function() {
        return {
            "filters": {
                "branch": frm.doc.branch
            }
        };
    });
    cur_frm.set_query("cost_center", function() {
        return {
            "filters": {
		"is_group": 0,
		"is_disabled": 0
            }
        };
    });
});

