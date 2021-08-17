// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
cur_frm.add_fetch("branch", "revenue_bank_account", "income_account");
cur_frm.add_fetch("technical_sanction", "total_amount", "service_charges");
cur_frm.add_fetch("technical_sanction", "material_charges", "material_charges");
frappe.ui.form.on('Mechanical Payment', {
	onload: function (frm) {
		cur_frm.set_query("income_account", function () {
			return {
				"filters": [
					["is_group", "=", "0"],

				]
			}
		});
		cur_frm.set_query("tds_account", function () {
			return {
				"filters": [
					["is_group", "=", "0"],

				]
			}
		});
		if (frm.doc.payment_for == "Hire Charge Invoice" && frm.doc.docstatus != 1) {
			cur_frm.set_value("tds_amount", "");
			cur_frm.set_value("tds_account", "");
			cur_frm.toggle_display('tds_rate', 0);
		}
	},
	refresh: function (frm) {
		if (frm.doc.docstatus === 1) {
			frm.add_custom_button(__('Accounting Ledger'), function () {
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

	"receivable_amount": function (frm) {
		console.log("receivable_amount")
		calculate_totals(frm)
	},

	"tds_amount": function (frm) {
		console.log("tds_amount")
		calculate_totals(frm)
		frm.toggle_reqd("tds_account", frm.doc.tds_amount)
	},

	get_series: function (frm) {
		return frappe.call({
			method: "get_series",
			doc: frm.doc,
			callback: function (r, rt) {
				frm.reload_doc();
			}
		});
	},

	get_transactions: function (frm) {
		//load_accounts(frm.doc.company)
		return frappe.call({
			method: "get_transactions",
			doc: frm.doc,
			callback: function (r, rt) {
				frm.refresh_field("items");
				frm.refresh_fields();
			},
			freeze: true,
			freeze_message: "Fetching Transactions......Please Wait"
		});
	},

	"receivable_amount": function (frm) {
		if (frm.doc.receivable_amount > frm.doc.actual_amount) {
			cur_frm.set_value("receivable_amount", frm.doc.actual_amount)
			msgprint("Receivable Amount cannot be greater than the Total Payable Amount")
		}
		else {
			var total = frm.doc.receivable_amount
			frm.doc.items.forEach(function (d) {
				var allocated = 0
				if (total > 0 && total >= d.outstanding_amount) {
					allocated = d.outstanding_amount
				}
				else if (total > 0 && total < d.outstanding_amount) {
					allocated = total
				}
				else {
					allocated = 0
				}

				d.allocated_amount = allocated
				total -= allocated
			})
			cur_frm.refresh_field("items")
		}
	},
	"items_on_form_rendered": function (frm, grid_row, cdt, cdn) {
		var row = cur_frm.open_grid_row();
		row.grid_form.fields_dict.reference_type.set_value(frm.doc.payment_for)
		row.grid_form.fields_dict.reference_type.refresh()
	},
	"payment_for": function (frm) {
		if (frm.doc.payment_for == "Transporter Payment") {
			frappe.model.get_value('Production Account Settings', { 'company': frm.doc.company }, 'transportation_account', function (d) {
				frm.set_value("transportation_account", d.transportation_account);
			});
			frappe.model.get_value('Branch', { 'branch': frm.doc.branch }, 'expense_bank_account', function (d) {
				frm.set_value("expense_account", d.expense_bank_account);
			});

		}
		calculate_totals(frm);
	},
	"other_deduction": function (frm) {
		console.log("other_deduction")
		calculate_totals(frm);
	}
});
// added by phuntsho to auto calculate tds amount
cur_frm.cscript.tds_rate = function (frm) {
	console.log("here")
	var percent = 0;
	switch (cur_frm.doc.tds_rate) {
		case "2%":
			percent = 2
			break;
		case "3%":
			percent = 3
			break;
		case "5%":
			percent = 5
			break;
		case "10%":
			percent = 10
			break;
		default:
			percent = 0
	}

	if (percent > 0) {
		frappe.call({
			method: "erpnext.accounts.doctype.purchase_invoice.purchase_invoice.get_tds_accounts",
			args: {
				"percent": percent
			},
			callback: function (r) {
				cur_frm.set_value("tds_account", r.message);
			}
		})
	}
	if (percent == 0) {
		cur_frm.set_value("tds_account", "")
	}
	cur_frm.refresh_field("tds_account")
	cur_frm.set_value("tds_amount", (percent / 100) * cur_frm.doc.payable_amount);
	calculate_totals(cur_frm)
}
function calculate_totals(frm) {
	if (in_list(["Transporter Payment", "Maintenance Payment", "Job Card"], frm.doc.payment_for)) {
		var net_amount = frm.doc.total_amount - (frm.doc.tds_amount + frm.doc.other_deduction);
		frm.set_value("net_amount", net_amount);
	}
	else {
		if (frm.doc.receivable_amount) {
			frm.set_value("net_amount", frm.doc.receivable_amount - frm.doc.tds_amount)
			cur_frm.refresh_field("net_amount")
		}
	}
	console.log("net_amount:" + net_amount);
}

cur_frm.fields_dict['items'].grid.get_field('reference_name').get_query = function (frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	return {
		filters: {
			"docstatus": 1,
			"branch": frm.branch,
			"customer": frm.customer,
			"outstanding_amount": [">", 0]
		}
	}
}

frappe.ui.form.on("Transporter Payment Item", {
	"delivery_note": function (frm, cdt, cdn) {
		console.log("delivery_note")
		var items = frm.doc.transporter_payment_item;
		var total = 0;
		for (var i = 0; i < items.length; i++) {
			total += parseFloat(items[i].amount);
		}
		frm.set_value('total_amount', total);
		calculate_totals(frm);
	}
})

frappe.ui.form.on("Mechanical Payment Item", {
	"reference_name": function (frm, cdt, cdn) {
		var item = locals[cdt][cdn]
		rec_amount = flt(frm.doc.receivable_amount)
		act_amount = flt(frm.doc.actual_amount)
		if (item.reference_name) {
			frappe.call({
				method: "frappe.client.get_value",
				args: {
					doctype: item.reference_type,
					fieldname: ["outstanding_amount"],
					filters: {
						name: item.reference_name
					}
				},
				callback: function (r) {
					frappe.model.set_value(cdt, cdn, "outstanding_amount", r.message.outstanding_amount)
					frappe.model.set_value(cdt, cdn, "allocated_amount", r.message.outstanding_amount)
					cur_frm.refresh_field("outstanding_amount")
					cur_frm.refresh_field("allocated_amount")

					cur_frm.set_value("actual_amount", act_amount + flt(r.message.outstanding_amount))
					cur_frm.refresh_field("actual_amount")
					cur_frm.set_value("receivable_amount", rec_amount + flt(r.message.outstanding_amount))
					cur_frm.refresh_field("receivable_amount")
				}
			})
		}
	},

	"before_items_remove": function (frm, cdt, cdn) {
		doc = locals[cdt][cdn]
		amount = flt(frm.doc.receivable_amount)
		ac_amount = flt(frm.doc.actual_amount) - flt(doc.outstanding_amount)
		cur_frm.set_value("actual_amount", ac_amount)
		cur_frm.refresh_field("actual_amount")
		cur_frm.trigger("receivable_amount")
	}
})
