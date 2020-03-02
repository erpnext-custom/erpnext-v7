// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Bank Guarantee', {
	refresh: function(frm) {
		cur_frm.set_query("project", function() {
			return {
				"filters": {
					"party": cur_frm.doc.party,
					"status": "Open"
				}
			};
		});
	},
	start_date: function(frm) {
		var end_date = frappe.datetime.add_days(cur_frm.doc.start_date, cur_frm.doc.validity - 1);
		cur_frm.set_value("end_date", end_date);
	},
	validity: function(frm) {
		var end_date = frappe.datetime.add_days(cur_frm.doc.start_date, cur_frm.doc.validity - 1);
		cur_frm.set_value("end_date", end_date);
	},
	
	entry_type: function(frm) {
		frm.set_value("party_type", frm.doc.entry_type=="Pay" ? "Customer" : "Supplier");
	},
	
	party_type: function(frm) {
		frm.set_value("party", null);
	}
});
