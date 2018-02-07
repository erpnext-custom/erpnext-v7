// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
cur_frm.add_fetch("project", "cost_center", "cost_center")
cur_frm.add_fetch("custodian", "employee_name", "custodian_name")
cur_frm.add_fetch("asset_code", "asset_name", "asset_name")
cur_frm.add_fetch("asset_code", "gross_purchase_amount", "gross_amount")

cur_frm.add_fetch("current_custodian", "employee_name", "c_custodian_name")

frappe.ui.form.on('Bulk Asset Transfer', {
	refresh: function(frm) {
	},
	get_assets: function(frm) {
		return frappe.call({
			method: "get_assets",
			doc: frm.doc,
			callback: function(r, rt) {
				frm.refresh_field("items");
				frm.refresh_fields();
			}
		});
	}
});
