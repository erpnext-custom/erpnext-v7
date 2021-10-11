// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
//

frappe.ui.form.on('Officiating Employee', {
	refresh: function (frm) {
		if (frm.doc.to_date < get_today) {
			/*cur_frm.add_custom_button(__('Revoke Permissions'), this.revoke_permission)
			frm.add_custom_button("Create Job Card", function() {
				return frappe.call({
					method: "erpnext.hr.doctype.officiating_employee.officiating_employee.revoke_perm",
					args: {frm: cur_frm},
					callback: function(r) {}
				})
			});*/
		}
	},
	onload: function (frm) {
		if (!frm.doc.posting_date) {
			frm.set_value("posting_date", get_today())
		}
		//cur_frm.fields_dict.officiate.$input.autocomplete("disable");
	},
	// Following added by phuntsho on jan 25 2021
	employee: function (frm) {
		frm.clear_table("transfer_roles")
		refresh_field("transfer_roles");
		frappe.call({
			method: "erpnext.hr.doctype.officiating_employee.officiating_employee.get_roles",
			args: { employee: frm.doc.employee },
			callback: function (r) {
				if (!r.message) {
					console.log("no roles")
				}
				else {
					r.message.map(function (data) {
						if (data !== "All" && data !== "Guest") {
							var rows = frm.add_child("transfer_roles");
							rows.roles = data
						}
					})
				}
				refresh_field("transfer_roles");

			}
		})
	},
	officiate: function (frm) {
		frm.clear_table("officiating_role_history")
		refresh_field("officiating_role_history");
		frappe.call({
			method: "erpnext.hr.doctype.officiating_employee.officiating_employee.get_roles",
			args: { employee: frm.doc.officiate },
			callback: function (r) {
				if (!r.message) {
					console.log("no roles")
				}
				else {
					r.message.map(function (data) {
						if (data !== "All" && data !== "Guest") {
							var row = frm.add_child("officiating_role_history");
							row.roles = data
						}
					})
				}
				refresh_field("officiating_role_history");

			}
		})
	},
	from_date: function (frm) {
		if (frm.doc.from_date && frm.doc.to_date && frm.doc.to_date < frm.doc.from_date) {
			cur_frm.set_vaue("from_date", "")
			cur_frm.refresh_field("from_date")
			frappe.msgprint("To Date cannot be smaller than from date")
		}
	},
	to_date: function (frm) {
		if (frm.doc.from_date && frm.doc.to_date && frm.doc.to_date < frm.doc.from_date) {
			cur_frm.set_vaue("to_date", "")
			cur_frm.refresh_field("to_date")
			frappe.msgprint("To Date cannot be smaller than from date")
		}
	},
	select_all: function (frm) {
		var items = frm.doc.transfer_roles
		if (frm.doc.select_all) {
			items.map(function (rows) {
				rows.check = 1
			})
		}
		else {
			items.map(function (rows) {
				rows.check = 0
			})
		}
		refresh_field("transfer_roles");
	},
	// ----- end of code by phuntsho --------

	/*validate: function(frm) {
		if(frm.doc.employee) {
			return frappe.call({
				method: "validate",
				doc: frm.doc,
				callback: function(r, rt) {
					frm.refresh_field("items");
					frm.refresh_fields();
				}
			});
		}
	},*/
	"revoke_permission": function (frm) {
		return frappe.call({
			method: "revoke_perm",
			doc: frm.doc,
			callback: function (r, rt) {
			}
		})
	}
});

// cur_frm.add_fetch("employee", "employee_name", "employee_name")
// cur_frm.add_fetch("officiate", "employee_name", "officiate_name")



