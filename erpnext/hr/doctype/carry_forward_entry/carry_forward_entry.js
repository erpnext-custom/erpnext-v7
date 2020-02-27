// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Carry Forward Entry', {
	setup: function(frm) {
	frm.get_field('items').grid.editable_fields = [
			{fieldname: 'employee', columns: 2},
			{fieldname: 'employee_name', cloumns: 2},
			{fieldname: 'leaves_allocated', columns: 2},
			{fieldname: 'leaves_taken', columns: 2},
			{fieldname: 'leave_balance', columns: 2}
		];
	
	},
	"get_details": function(frm) {
		return frappe.call({
			method: "get_data",
			doc: frm.doc,
			callback: function(r, rt) {
			frm.refresh_field("items");
                        frm.refresh_fields();
                        }
		});
                }
});

/*function get_details(frm) {
        frappe.call({
                method: "erpnext.hr.doctype.carry_forward_entry.carry_forward_entry.get_data",
                callback: function(r) {
                        if(r.message) {
                                cur_frm.clear_table("items");

                                r.message.forEach(function(leaves) {
                                        var row = frappe.model.add_child(cur_frm.doc, "Leave Forward Item", "items");
                                        row.employee = leaves['employee']
                                        row.leaves_taken = leaves['leaves_taken']
					row.leave_balance = leaves['leave_balance']
                                        }
                                        refresh_field("items");

                                });

                        }
                }
        })*/
