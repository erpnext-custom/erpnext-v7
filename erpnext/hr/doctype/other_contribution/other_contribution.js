// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.add_fetch('employee', 'employee_name', 'employee_name');
cur_frm.add_fetch('employee', 'employment_type', 'employment_type');
cur_frm.add_fetch('employee', 'employee_group', 'employee_group');
cur_frm.add_fetch('employee', 'employee_subgroup', 'employee_grade');
cur_frm.add_fetch('employee', 'designation', 'designation');

frappe.ui.form.on('Other Contribution', {
	refresh: function(frm) {
		cur_frm.set_query("cost_center", function() {
                return {
                    "filters": {
                        "is_disabled": 0,
                        "list_in_other_contribution": 1
                    }
                };
        });
	}
});
