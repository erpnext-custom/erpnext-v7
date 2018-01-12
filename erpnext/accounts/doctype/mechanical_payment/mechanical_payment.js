// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
frappe.ui.form.on('Mechanical Payment', {
	refresh: function(frm) {
		if(frm.doc.docstatus===1){
			frm.add_custom_button(__('Accounting Ledger'), function(){
				frappe.route_options = {
					voucher_no: frm.doc.name,
					from_date: frm.doc.posting_date,
					to_date: frm.doc.posting_date,
					company: frm.doc.company,
					group_by_voucher: false
				};
				frappe.set_route("query-report", "General Ledger");
			}, __("View"));
		} 

	},
	"receivable_amount": function(frm) {
		calculate_totals(frm)
	},
	"tds_amount": function(frm) {
		calculate_totals(frm)
		frm.toggle_reqd("tds_account", frm.doc.tds_amount)
	}
});

function calculate_totals(frm) {
	if (frm.doc.receivable_amount) {
		frm.set_value("net_amount", frm.doc.receivable_amount - frm.doc.tds_amount)
		cur_frm.refresh_field("net_amount")
	}
}

