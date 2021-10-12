// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Technical Sanction Bill', {
	refresh: function (frm) {
		if (frm.doc.docstatus == 1 && !frm.doc.maintenance_payment) {
			frm.add_custom_button("Make Payment", function () {
				frappe.model.open_mapped_doc({
					method: "erpnext.rental_management.doctype.technical_sanction_bill.technical_sanction_bill.make_payment",
					frm: cur_frm
				});
			});
		}
		if (frm.doc.docstatus === 1) {
			frm.add_custom_button(__('Accounting Ledger'), function () {
				frappe.route_options = {
					voucher_no: frm.doc.name,
					from_date: frm.doc.posting_date,
					to_date: frm.doc.posting_date,
					company: "National Housing Development Corporation Ltd.",
					group_by_voucher: false
				};
				frappe.set_route("query-report", "General Ledger");
			}, __("View"));
		}
	},

	"deduction": function (frm) {
		console.log("hello world")
		calculate_total_amount(frm)
	},
	"get_advances": function (frm) {
		if (frm.doc.technical_sanction && frm.doc.party_type && frm.doc.party) {
			frappe.call({
				method: "erpnext.rental_management.doctype.technical_sanction_bill.technical_sanction_bill.get_advance_list",
				args: {
					"technical_sanction": frm.doc.technical_sanction,
					"party_type": frm.doc.party_type,
					"party": frm.doc.party
				},
				callback: function (r) {
					if (r.message) {
						cur_frm.clear_table("advance");
						r.message.forEach(function (adv) {
							var row = frappe.model.add_child(frm.doc, "Technical Sanction Bill Advance", "advance");
							row.reference_doctype = "Technical Sanction Advance";
							row.reference_name = adv['name'];
							row.total_amount = flt(adv['balance_amount']);
							row.allocated_amount = 0.00;
						});
						frm.refresh_field("advance");
					}
					else {
						cur_frm.clear_table("advance");
						cur_frm.refresh();
					}
				}
			});
		}
		else {
			frappe.throw("Either party type or party are missing in the technical sanction!")
		}
	},
});

frappe.ui.form.on('Technical Sanction Deduction', {
	"deduction_amount": function (frm, cdt, cdn) {
		calculate_total_amount(frm)
	},
	deduction_remove: function (frm) {
		calculate_total_amount(frm)
	},
})
frappe.ui.form.on('Technical Sanction Bill Advance', {
	"allocated_amount": function (frm, cdt, cdn) {
		console.log("hello world")
		calculate_total_amount(frm)
	},
})

function calculate_total_amount(frm) {
	frappe.call({
		method: "calculate_total_amount",
		arg: {},
		callback: function (r, rt) { frm.refresh_fields() },
		doc: frm.doc,
	});
}