// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/*
--------------------------------------------------------------------------------------------------------------------------
Version          Author          CreatedOn          ModifiedOn          Remarks
------------ --------------- ------------------ -------------------  -----------------------------------------------------
2.0		          SHIV		                        28/11/2017         * Code added to fetch cost_center, branch, customer
																			automatically based on logged in user.
--------------------------------------------------------------------------------------------------------------------------                                                                          
*/

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
		
		// Ver 2.0 Begins, following code added by SHIV on 28/11/2017
		if(frm.doc.__islocal) {
			frappe.call({
				method: "erpnext.custom_utils.get_user_info",
				args: {"user": frappe.session.user},
				callback(r) {
					cur_frm.set_value("cost_center", r.message.cost_center);
					cur_frm.set_value("branch", r.message.branch);
					cur_frm.set_value("customer", r.message.customer);
				}
			});
		}
		// Ver 2.0 Ends
	},
	owned_by: function(frm) {
		cur_frm.set_value("customer", "")
		cur_frm.set_value("equipment", "")
		cur_frm.toggle_reqd("customer_cost_center", frm.doc.owned_by == 'CDCL')
		cur_frm.toggle_reqd("customer_branch", frm.doc.owned_by == 'CDCL')

		//cur_frm.toggle_reqd("equipment_model", frm.doc.owned_by != 'Others')
		//cur_frm.toggle_reqd("equipment_number", frm.doc.owned_by != 'Others')
	}
});

cur_frm.add_fetch("cost_center", "branch", "branch");
cur_frm.add_fetch("customer", "customer_group", "client");
cur_frm.add_fetch("customer", "cost_center", "customer_cost_center");
cur_frm.add_fetch("customer", "branch", "customer_branch");
cur_frm.add_fetch("equipment", "equipment_model", "equipment_model");
cur_frm.add_fetch("equipment", "equipment_type", "equipment_type");
cur_frm.add_fetch("equipment", "equipment_number", "equipment_number");

//cur_frm.add_fetch("customer_cost_center", "branch", "customer_branch");

frappe.ui.form.on("Break Down Report", "refresh", function(frm) {
    cur_frm.set_query("equipment", function() {
	if (frm.doc.owned_by == "Own") {
		return {
		    "filters": {
			"is_disabled": 0,
			"branch": frm.doc.branch
		    }
		};
	}
	else if (frm.doc.owned_by == "CDCL"){
		return {
		    "filters": {
			"is_disabled": 0,
			"branch": frm.doc.customer_branch
		    }
		};
	}
	else {}
    });

    cur_frm.set_query("cost_center", function() {
        return {
            "filters": {
		"is_group": 0,
		"is_disabled": 0
            }
        };
    });

    cur_frm.set_query("customer", function() {
	if(frm.doc.owned_by == "Own") {
		return {
		    "filters": {
			"disabled": 0,
			"cost_center": frm.doc.cost_center,
			"branch": frm.doc.branch
		    }
		};
	}
	if(frm.doc.owned_by == "CDCL") {
		return {
		    "filters": {
			"disabled": 0,
			"customer_group": "Internal",
			"branch": ["!=", frm.doc.branch]
		    }
		};
	}
	else {
		return {
		    "filters": {
			"disabled": 0,
			"customer_group": ["!=","Internal"]
		    }
		};
	}
    });
});

