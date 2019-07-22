// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Assign Supervisor', {
	refresh: function(frm) {

	},
	setup: function(frm) {
		frm.get_field('items').grid.editable_fields = [
			{fieldname: 'employee', columns: 3},
			{fieldname: 'employee_name', columns: 3},
			{fieldname: 'designation', columns: 3},
		];
	},
	"get_employees": function(frm) {
                return frappe.call({
                        method: "get_branch_employees",
                        doc: frm.doc,
                        callback: function(r, rt) {
                                frm.refresh_field("items");
                                frm.refresh_fields();
                        },
			 freeze: true,
                         freeze_message: "Getting Active Employees Under the Selected Branch.... Please Wait!!!",
						
                });
        },
});
