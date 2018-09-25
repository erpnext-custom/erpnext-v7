// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
cur_frm.add_fetch("branch", "cost_center", "cost_center")
cur_frm.add_fetch("item_code", "item_name", "item_name")
cur_frm.add_fetch("item_code", "stock_uom", "uom")
cur_frm.add_fetch("price_template", "rate_amount", "cop")

frappe.ui.form.on('Production', {
	onload: function(frm) {
                if (!frm.doc.posting_date) {
                        frm.set_value("posting_date", get_today());
                }
	},

	setup: function(frm) {
		frm.get_field('raw_materials').grid.editable_fields = [
			{fieldname: 'item_code', columns: 3},
			{fieldname: 'qty', columns: 2},
			{fieldname: 'uom', columns: 1},
		]
		frm.get_field('items').grid.editable_fields = [
			{fieldname: 'item_code', columns: 3},
			{fieldname: 'qty', columns: 2},
			{fieldname: 'uom', columns: 1},
			{fieldname: 'cop', columns: 2},
		]
	},

	refresh: function(frm) {
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

	}
});

frappe.ui.form.on("Production", "refresh", function(frm) {
    cur_frm.set_query("warehouse", function() {
        return {
            "filters": {
                "branch": frm.doc.branch,
		"disabled": 0
            }
        };
    });
})

cur_frm.fields_dict['raw_materials'].grid.get_field('item_code').get_query = function(frm, cdt, cdn) {
	return {
            filters: {
                "disabled": 0,
                "is_production_item": 1,
            }
        };
}

cur_frm.fields_dict['items'].grid.get_field('item_code').get_query = function(frm, cdt, cdn) {
	return {
            filters: {
                "disabled": 0,
                "is_production_item": 1,
            }
        };
}



