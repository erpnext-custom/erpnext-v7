// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/*
------------------------------------------------------------------------------------------------------------------------------------------
Version          Author         Ticket#           CreatedOn          ModifiedOn          Remarks
------------ --------------- --------------- ------------------ -------------------  -----------------------------------------------------
1.0.190401       SHIV		                                     	2019/04/01         Refined process for making SL and GL entries
------------------------------------------------------------------------------------------------------------------------------------------                                                                          
*/
cur_frm.add_fetch("branch", "cost_center", "cost_center")
cur_frm.add_fetch("item_code", "item_name", "item_name")
cur_frm.add_fetch("item_code", "stock_uom", "uom")
cur_frm.add_fetch("item_code", "item_group", "item_group")
cur_frm.add_fetch("equipment", "equipment_model", "equipment_model")
cur_frm.add_fetch("equipment", "equipment_number", "equipment_number")

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
		];
		frm.get_field('items').grid.editable_fields = [
			{fieldname: 'item_code', columns: 3},
			{fieldname: 'qty', columns: 2},
			{fieldname: 'uom', columns: 1},
			{fieldname: 'price_template', columns: 2},
			{fieldname: 'cop', columns: 2},
		];
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
	
	/* ++++++++++ Ver 1.0.190401 Begins ++++++++++*/
	// Following code added by SHIV on 2019/04/01
	branch: function(frm){
		frm.set_value("warehouse","");
	},
	
	warehouse: function(frm){
		update_items(frm);
	},
	
	cost_center: function(frm){
		update_items(frm);
	},
	/* ++++++++++ Ver 1.0.190401 Ends ++++++++++++*/
	get_product: function(frm){
		get_finish_product(frm);
	}
});

frappe.ui.form.on("Production", "refresh", function(frm) {
    cur_frm.set_query("warehouse", function() {
        return {
            query: "erpnext.controllers.queries.filter_branch_wh",
            filters: {'branch': frm.doc.branch}
        }
    });

    cur_frm.set_query("branch", function() {
        return {
            "filters": {
		"is_disabled": 0
            }
        };
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

	item_code: function(frm, cdt, cdn) {
		/* ++++++++++ Ver 1.0.190401 Begins ++++++++++*/
		// Following code added by SHIV on 2019/04/01
		update_expense_account(frm, cdt, cdn);
		/* ++++++++++ Ver 1.0.190401 Ends ++++++++++++*/
		frappe.model.set_value(cdt, cdn, "production_type", frm.doc.production_type);
		cur_frm.refresh_fields();
	},
	
	items_add: function(frm, cdt, cdn){
		frappe.model.set_value(cdt, cdn, "warehouse", frm.doc.warehouse);
		frappe.model.set_value(cdt, cdn, "cost_center", frm.doc.cost_center);
	},
});

/* ++++++++++ Ver 1.0.190401 Begins ++++++++++*/
// Following code added by SHIV on 2019/04/01
frappe.ui.form.on("Production Material Item", {
	item_code: function(frm, cdt, cdn){
		update_expense_account(frm, cdt, cdn);
	},
	raw_materials_add: function(frm, cdt, cdn){
		frappe.model.set_value(cdt, cdn, "warehouse", frm.doc.warehouse);
		frappe.model.set_value(cdt, cdn, "cost_center", frm.doc.cost_center);
	},
});

var update_expense_account = function(frm, cdt, cdn){
	var row = locals[cdt][cdn];
	if(row.item_code){
		frappe.call({
			method: "erpnext.production.doctype.production.production.get_expense_account",
			args: {
				"company": frm.doc.company,
				"item": row.item_code,
			},
			callback: function(r){
				frappe.model.set_value(cdt, cdn, "expense_account", r.message);
				cur_frm.refresh_field("expense_account");
			}
		})
	}
}

var update_items = function(frm){
	// Production Product Item
	var items = frm.doc.items || [];
	for(var i=0; i<items.length; i++){
		frappe.model.set_value("Production Product Item", items[i].name, "cost_center", frm.doc.cost_center);
		frappe.model.set_value("Production Product Item", items[i].name, "warehouse", frm.doc.warehouse);
	}
	
	// Production Material Item
	var raw_materials = frm.doc.raw_materials || [];
	for(var i=0; i<raw_materials.length; i++){
		frappe.model.set_value("Production Material Item", raw_materials[i].name, "cost_center", frm.doc.cost_center);
		frappe.model.set_value("Production Material Item", raw_materials[i].name, "warehouse", frm.doc.warehouse);
	}
}

cur_frm.fields_dict['items'].grid.get_field('expense_account').get_query = function(frm, cdt, cdn){
	return {
		filters: {
			"company": frm.company,
			"is_group": 0
		}
	};
}

cur_frm.fields_dict['raw_materials'].grid.get_field('expense_account').get_query = function(frm, cdt, cdn){
	return {
		filters: {
			"company": frm.company,
			"is_group": 0
		}
	};
}
/* ++++++++++ Ver 1.0.190401 Ends ++++++++++++*/
		
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

cur_frm.fields_dict['items'].grid.get_field('vehicle_no').get_query = function(frm, cdt, cdn) {
	        var d = locals[cdt][cdn];
		        return {
				                query: "erpnext.controllers.queries.get_equipment_no"
							        };
}

function get_finish_product(frm){
	if (frm.doc.branch && frm.doc.raw_materials){
		return frappe.call({
				method: "get_finish_product",
				doc: cur_frm.doc,
				callback: function(r, rt){					
					if(r.message){
						console.log(r.message);
						cur_frm.clear_table("items");
						r.message.forEach(function(rec) {
							var row = frappe.model.add_child(cur_frm.doc, "Production Product Item", "items");
							row.item_code = rec['item_code'];
							row.item_name = rec['item_name'];		
							row.qty = rec['qty'];
							row.uom = rec['uom'];
							row.item_group = rec['item_group'];
							row.price_template = rec['price_template'];
							row.cop = rec['cop'];
							row.cost_center = rec['cost_center'];
							row.warehouse = rec['warehouse'];
							row.expense_account = rec['expense_account'];
						});
					}
					else
					{
						cur_frm.clear_table("items");
					}					
				cur_frm.refresh();
				},
            });     
	}else{
		frappe.msgprint("To get the finish product, please enter the branch and raw material");
	}
}