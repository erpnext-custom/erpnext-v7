// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Asset Modifier Tool', {
	refresh: function(frm) {
			frm.disable_save();
	},

	update_asset_value: function(frm) {
		if(frm.doc.asset && frm.doc.value > 0) {
			frappe.call({
				method: "erpnext.accounts.doctype.asset_modifier_tool.asset_modifier_tool.change_value",
				args: {
					"asset": frm.doc.asset,
					"value": frm.doc.value
				},
				callback: function(r) {
					if(r.message == "DONE") {
						cur_frm.set_df_property("update_asset_value", "read_only", 1)
						msgprint("An amount of Nu. " + frm.doc.amount + " has been added to " + frm.doc.asset )
					}
					else {
						msgprint(r.message)
					}
				}
			});
		}
		else if(frm.doc.amount <= 0) {
			msgprint("Amount should be greater than 0")
		}
		else {
			msgprint("Fill all fields before submitting")
		}
	},

});
