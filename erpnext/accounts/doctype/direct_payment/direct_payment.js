// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Direct Payment', {
	refresh: function(frm) {
		if(!frm.doc.posting_date) {
			frm.set_value("posting_date", get_today())
		}

		if(frm.doc.docstatus == 1) {
			if(frappe.model.can_read("Journal Entry")) {
				cur_frm.add_custom_button('Bank Entries', function() {
					frappe.route_options = {
						"Journal Entry Account.reference_type": frm.doc.doctype,
						"Journal Entry Account.reference_name": frm.doc.name,
					};
					frappe.set_route("List", "Journal Entry");
				}, __("View"));
			}
		}
	},
	"amount": function(frm) {
		calculate_tds(frm);
	},
	"tds_percent": function(frm) {
		calculate_tds(frm);
	}
});

function calculate_tds(frm) {
	var tds = flt(frm.doc.tds_percent * frm.doc.amount / 100 )
	frm.set_value("tds_amount", tds)
	frm.set_value("balance_amount", frm.doc.amount - tds)

	if(frm.doc.tds_percent == 2) {
		frm.set_value("tds_account", "TDS-2% - SMCL")
	}
	if(frm.doc.tds_percent == 3) {
		frm.set_value("tds_account", "TDS-3% - SMCL")
	}
	if(frm.doc.tds_percent == 5) {
		frm.set_value("tds_account", "TDS-5% - SMCL")
	}
	if(frm.doc.tds_percent == 10) {
		frm.set_value("tds_account", "TDS on dividend - SMCL")
	}
}

