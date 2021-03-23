// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Standard Sawn Balance', {
	refresh: function(frm) {
		cur_frm.set_query("size", function() {
			return {
				"filters": {
					"type": "size"
				}
			};
		});
		cur_frm.set_query("length", function() {
			return {
				"filters": {
					"type": "length"
				}
			};
		});
		cur_frm.set_query("item", function() {
			return {
				"filters": {
					"item_sub_group": "Sawn"
				}
			};
		});
	}

});
