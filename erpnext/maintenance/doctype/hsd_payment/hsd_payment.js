// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
cur_frm.add_fetch("branch", "expense_bank_account", "bank_account")
cur_frm.add_fetch("fuelbook", "supplier", "supplier")
cur_frm.add_fetch("branch", "expense_bank_account", "bank_account")

frappe.ui.form.on('HSD Payment', {
	onload: function(frm) {
		if(!frm.doc.posting_date) {
			frm.set_value("posting_date", get_today())
		}
	},

	refresh: function(frm) {
		if(frm.doc.docstatus == 1) {
			cur_frm.add_custom_button(__('Accounting Ledger'), function() {
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

	"branch": function(frm) {
		return frappe.call({
			method: "erpnext.custom_utils.get_cc_warehouse",
			args: {
				"branch": frm.doc.branch
			},
			callback: function(r) {
				cur_frm.set_value("cost_center", r.message.cc)
				cur_frm.refresh_fields()
			}
		})
	},

	"get_pol_invoices": function(frm) {
		if(frm.doc.fuelbook) {
			return frappe.call({
				method: "get_invoices",
				doc: frm.doc,
				callback: function(r, rt) {
					frm.refresh_field("items");
					frm.refresh_fields();
				}
			});
		}
		else {
			msgprint("Select Fuelbook before clicking on the button")
		}
	},

	"amount": function(frm) {
		if(frm.doc.amount > frm.doc.actual_amount) {
			cur_frm.set_value("amount", frm.doc.actual_amount)
			msgprint("Amount cannot be greater than the Total Payable Amount")
		}
		else {
			var total = frm.doc.amount
			frm.doc.items.forEach(function(d) {
				var allocated = 0
				if (total > 0 && total >= d.payable_amount ) {
					allocated = d.payable_amount
				}
				else if(total > 0 && total < d.payable_amount) {
					allocated = total
				}
				else {
					allocated = 0
				}
			
				d.allocated_amount = allocated
				d.balance_amount = d.payable_amount - allocated
				total-=allocated
			})
			cur_frm.refresh_field("items")
		}
	}
});

frappe.ui.form.on("HSD Payment", "refresh", function(frm) {
    	cur_frm.set_query("fuelbook", function() {
		return {
		    "filters": {
			"is_disabled": 0,
			"branch": frm.doc.branch
		    }
		};
	    });
})
	
