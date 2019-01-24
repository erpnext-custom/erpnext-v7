// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
cur_frm.add_fetch("branch", "cost_center", "cost_center")
cur_frm.add_fetch("item_code", "item_name", "item_name")
cur_frm.add_fetch("item_code", "stock_uom", "uom")
cur_frm.add_fetch("item_code", "item_group", "item_group")
cur_frm.add_fetch("item_code", "species", "timber_species")
cur_frm.add_fetch("item_code", "item_sub_group", "item_sub_group")

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
			{fieldname: 'item_sub_group', columns: 2},
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

	},
});

frappe.ui.form.on("Production", "refresh", function(frm) {
    cur_frm.set_query("warehouse", function() {
        return {
                query: "erpnext.controllers.queries.filter_branch_wh",
                filters: {'branch': frm.doc.branch}
        }
    });

    cur_frm.set_query("location", function() {
        return {
            "filters": {
                "branch": frm.doc.branch,
		"is_disabled": 0
            }
        };
    });
    cur_frm.set_query("adhoc_production", function() {
        return {
            "filters": {
                "branch": frm.doc.branch,
                "location": frm.doc.location,
		"is_disabled": 0
            }
        };
    });
})

frappe.ui.form.on("Production Product Item", { 
	"price_template": function(frm, cdt, cdn) {
		d = locals[cdt][cdn]
		frappe.call({
			method: "erpnext.production.doctype.cost_of_production.cost_of_production.get_cop_amount",
			args: {
				"cop": d.price_template,
				"branch": cur_frm.doc.branch,
				"item_code": d.item_code,
				"posting_date": cur_frm.doc.posting_date 
			},
			callback: function(r) {
				frappe.model.set_value(cdt, cdn, "cop", r.message)
				cur_frm.refresh_field("cop")
			}
		})
	},

	"item_code": function(frm, cdt, cdn) {
		frappe.model.set_value(cdt, cdn, "production_type", frm.doc.production_type)
		cur_frm.refresh_fields()
	}
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

cur_frm.fields_dict['items'].grid.get_field('price_template').get_query = function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        return {
                query: "erpnext.controllers.queries.get_cop_list",
                filters: {'item_code': d.item_code, 'posting_date': frm.posting_date, 'branch': frm.branch}
        }
}


