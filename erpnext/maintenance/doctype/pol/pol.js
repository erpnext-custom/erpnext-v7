// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
cur_frm.add_fetch("equipment", "equipment_number", "equipment_number")
cur_frm.add_fetch("cost_center", "branch", "branch")
cur_frm.add_fetch("cost_center", "warehouse", "warehouse")
cur_frm.add_fetch("fuelbook", "branch", "fuelbook_branch")
cur_frm.add_fetch("equipment", "fuelbook", "own_fb")
cur_frm.add_fetch("pol_type", "item_name", "item_name")
cur_frm.add_fetch("pol_type", "stock_uom", "stock_uom")

frappe.ui.form.on('POL', {
	onload: function(frm) {
		if(!frm.doc.posting_date) {
			frm.set_value("posting_date", get_today());
		}
	},
	refresh: function(frm) {
		if(frm.doc.jv) {
			cur_frm.add_custom_button(__('Bank Entries'), function() {
				frappe.route_options = {
					"Journal Entry Account.reference_type": me.frm.doc.doctype,
					"Journal Entry Account.reference_name": me.frm.doc.name,
				};
				frappe.set_route("List", "Journal Entry");
			}, __("View"));
		}
		if(frm.doc.docstatus == 1) {
			cur_frm.add_custom_button(__("Stock Ledger"), function() {
				frappe.route_options = {
					voucher_no: frm.doc.name,
					from_date: frm.doc.posting_date,
					to_date: frm.doc.posting_date,
					company: frm.doc.company
				};
				frappe.set_route("query-report", "Stock Ledger Report");
			}, __("View"));

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

	"qty": function(frm) {
		calculate_total(frm)
	},

	"rate": function(frm) {
		calculate_total(frm)
	},

	"discount_amount": function(frm) {
		calculate_total(frm)
	},

	"is_disabled": function(frm) {
		cur_frm.toggle_reqd("disabled_date", frm.doc.is_disabled)
	}
});

function calculate_total(frm) {
	if(frm.doc.qty && frm.doc.rate) {
		frm.set_value("total_amount", frm.doc.qty * frm.doc.rate)
		frm.set_value("outstanding_amount", frm.doc.qty * frm.doc.rate)
	}

	if(frm.doc.qty && frm.doc.rate && frm.doc.discount_amount) {
		frm.set_value("total_amount", (frm.doc.qty * frm.doc.rate) - frm.doc.discount_amount)
		frm.set_value("outstanding_amount", (frm.doc.qty * frm.doc.rate) - frm.doc.discount_amount)
	}
}	

frappe.ui.form.on("POL", "refresh", function(frm) {
    cur_frm.set_query("cost_center", function() {
        return {
            "filters": {
		"is_disabled": 0,
		"is_group": 0
            }
        };
    });

    cur_frm.set_query("equipment", function() {
        return {
            "filters": {
		"is_disabled": 0
            }
        };
    });

   cur_frm.set_query("fuelbook", function() {
	if(frm.doc.book_type && frm.doc.supplier) {
		if(frm.doc.book_type == "Own") {
			return {
				"filters": {
					"name": frm.doc.own_fb
					}
				}
		}
		
		if(frm.doc.book_type == "Common") {
			return {
				"filters": {
					"supplier": frm.doc.supplier,
					"type": "Common",
					"branch": frm.doc.branch
					}
				}
		}
	}
    })

    cur_frm.set_query("pol_type", function() {
        return {
            "filters": {
		"disabled": 0,
		"is_pol_item": 1
            }
        };
    });
  
  cur_frm.set_query("warehouse", function() {
        return {
                query: "erpnext.controllers.queries.filter_branch_wh",
                filters: {'branch': frm.doc.branch}
        }
    });

  cur_frm.set_query("equipment_warehouse", function() {
        return {
                query: "erpnext.controllers.queries.filter_branch_wh",
                filters: {'branch': frm.doc.equipment_branch}
        }
    });

  cur_frm.set_query("hiring_warehouse", function() {
        return {
                query: "erpnext.controllers.queries.filter_branch_wh",
                filters: {'branch': frm.doc.hiring_branch}
        }
    });
})
