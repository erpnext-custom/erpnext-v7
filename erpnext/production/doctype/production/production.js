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
cur_frm.add_fetch("item_code", "species", "timber_species")
cur_frm.add_fetch("item_code", "item_sub_group", "item_sub_group")
cur_frm.add_fetch("item_code", "material_measurement", "reading_select")
cur_frm.add_fetch("machine_name", "equipment_number", "equipment_number")
cur_frm.add_fetch("machine_name", "equipment_type", "equipment_type")

frappe.ui.form.on('Production', {
	onload: function(frm) {
                if (!frm.doc.posting_date) {
                        frm.set_value("posting_date", get_today());
                }
	},

	setup: function(frm) {
		//frm.get_docfield("raw_materials").allow_bulk_edit = 1;
		//frm.get_docfield("items").allow_bulk_edit = 1;
		frm.get_field('raw_materials').grid.editable_fields = [
			{fieldname: 'item_code', columns: 3},
			{fieldname: 'qty', columns: 2},
			{fieldname: 'uom', columns: 1},
		];
		frm.get_field('items').grid.editable_fields = [
			{fieldname: 'item_code', columns: 3},
			{fieldname: 'qty', columns: 2},
			{fieldname: 'uom', columns: 1},
			{fieldname: 'item_sub_group', columns: 2},
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
	
	business_activity: function(frm){
		update_items(frm);
	},
	/* ++++++++++ Ver 1.0.190401 Ends ++++++++++++*/
});

frappe.ui.form.on("Production", "validate", function(frm) {
	if(!frappe.user.has_role('Production Master')){
	var date = frappe.datetime.add_days(get_today(), -3);
	if (frm.doc.posting_date < date ) {
		frappe.throw(__("You Can Not Create Submit For Posting Date Beyond Past 3 Days"));
		frappe.validated = false;
	}
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
			"query":"erpnext.controllers.queries.filter_range_location",
            "filters": {
                "range": frm.doc.range,
            }
        };
	});
    cur_frm.set_query("range", function () {
        return {
		    "query": "erpnext.controllers.queries.filter_branch_rng",
            "filters": {
                "branch": frm.doc.branch,
            }
        };
    });
    cur_frm.set_query("adhoc_production", function() {
        return {
            "filters": {
                "branch": frm.doc.branch,
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
				frappe.model.set_value(cdt, cdn, "cop", r.message);
				cur_frm.refresh_field("cop")
			}
		})
	},

	"item_code": function(frm, cdt, cdn) {
		/* ++++++++++ Ver 1.0.190401 Begins ++++++++++*/
		// Following code added by SHIV on 2019/04/01
		update_expense_account(frm, cdt, cdn);
		/* ++++++++++ Ver 1.0.190401 Ends ++++++++++++*/
		frappe.model.set_value(cdt, cdn, "production_type", frm.doc.production_type);

		/// ########## Var.2020.11.03 Begins ##########
		// Following code added by SHIV on 2020/11/03
		frappe.model.set_value(cdt, cdn, "reading_select", null);
		// ########## Var.2020.11.03 Ends ##########
		cur_frm.refresh_fields()
	},
	
	/* ++++++++++ Ver 1.0.190401 Begins ++++++++++*/
	// Following code added by SHIV on 2019/04/01
	items_add: function(frm, cdt, cdn){
		frappe.model.set_value(cdt, cdn, "business_activity", frm.doc.business_activity);
		frappe.model.set_value(cdt, cdn, "warehouse", frm.doc.warehouse);
		frappe.model.set_value(cdt, cdn, "cost_center", frm.doc.cost_center);
	},
	/* ++++++++++ Ver 1.0.190401 Ends ++++++++++++*/
	
	// Followng code is commented by SHIV on 2020/11/03 as the code is hard coded
	// //Following code added by Kinley on 2020/10/29
	// reading_select: function(frm, cdt, cdn){
	// 	row = locals[cdt][cdn]
	// 	if(row.reading_select == "6.1 - 12 ft (Length)(Post)")
	// 	{
	// 		if(row.item_code != '600271')
	// 		{
	// 			frappe.model.set_value(cdt, cdn, "reading_select","")
	// 			frappe.throw("This reading is only applicable for item 600271: Dangchung (6\'1\" to 12\' -Others) Post")
	// 		}
	// 	}
	// 	else if(row.reading_select == "12.1 - 17.11 ft (Length)(Post)")
	// 	{
	// 		if(row.item_code != '600272')
	// 		{
	// 			frappe.model.set_value(cdt, cdn, "reading_select","")
	// 			frappe.throw("This reading is only applicable for item 600272: Flag Post (12\'1\" to 17\'11\")- Others Post")
	// 		}
	// 	}
	// 	else if(row.reading_select == "18 ft and above (Length)(Post)")
	// 	{
	// 		if(row.item_code != '600273')
	// 		{
	// 			frappe.model.set_value(cdt, cdn, "reading_select","")
	// 			frappe.throw("This reading is only applicable for item 600273: Tsim (18\' Above -others) Post")	
	// 		}
	// 	}
	// 	else
	// 	{
	// 		if(row.item_code == "600271" || row.item_code == "600272" || row.item_code == "600273")
	// 		{
	// 			frappe.model.set_value(cdt, cdn, "reading_select","")
	// 			frappe.throw("This reading is not applicable for this item")
	// 		}
	// 	}
	// }
	// /* +++++++++++++++++++++++++++++++++++++++++++*/
})

/* ++++++++++ Ver 1.0.190401 Begins ++++++++++*/
// Following code added by SHIV on 2019/04/01
frappe.ui.form.on("Production Material Item", {
	item_code: function(frm, cdt, cdn){
		update_expense_account(frm, cdt, cdn);
	},
	raw_materials_add: function(frm, cdt, cdn){
		frappe.model.set_value(cdt, cdn, "business_activity", frm.doc.business_activity);
		frappe.model.set_value(cdt, cdn, "warehouse", frm.doc.warehouse);
		frappe.model.set_value(cdt, cdn, "cost_center", frm.doc.cost_center);
	},
	"lot_list": function(frm, cdt, cdn){
                var d = locals[cdt][cdn];
                if(d.item_code && d.lot_list){ get_balance(frm, cdt, cdn); }
        }
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
		frappe.model.set_value("Production Product Item", items[i].name, "business_activity", frm.doc.business_activity);
		frappe.model.set_value("Production Product Item", items[i].name, "cost_center", frm.doc.cost_center);
		frappe.model.set_value("Production Product Item", items[i].name, "warehouse", frm.doc.warehouse);
	}
	
	// Production Material Item
	var raw_materials = frm.doc.raw_materials || [];
	for(var i=0; i<raw_materials.length; i++){
		frappe.model.set_value("Production Material Item", raw_materials[i].name, "business_activity", frm.doc.business_activity);
		frappe.model.set_value("Production Material Item", raw_materials[i].name, "cost_center", frm.doc.cost_center);
		frappe.model.set_value("Production Material Item", raw_materials[i].name, "warehouse", frm.doc.warehouse);
	}
}

// ########## Ver.2020.11.03 BEGINS ##########
// following code added by SHIV on 2020/11/03 inorder to remove existing hardcoding
cur_frm.fields_dict['items'].grid.get_field('reading_select').get_query = function(frm, cdt, cdn){
	var row = locals[cdt][cdn];
	return {
		query: "erpnext.controllers.queries.get_measurements",
		filters: {
			item_code: row.item_code,
			item_sub_group: row.item_sub_group
		}
	};
}
// ########## Ver.2020.11.03 ENDS ##########

// Added by Sonam Chophel on 02/01/2022 to filter machine name
cur_frm.fields_dict['machine_details'].grid.get_field('machine_name').get_query = function(frm, cdt, cdn){
	var d = locals[cdt][cdn];
	return{
		filters: [
			['Equipment', 'equipment_type', 'in', 'Briquette, Chain Saw, Sand Dredging Machine, Backhoe, Pay Loader, Swing Yarder, Excavator, Bandsaw, Sawmill, Wheel Loader, Cable Crane'],
		]
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

cur_frm.fields_dict['raw_materials'].grid.get_field('lot_list').get_query = function(frm, cdt, cdn) {
        var item = locals[cdt][cdn];
        return {
                query: "erpnext.controllers.queries.filter_lots",
                filters: {'branch': cur_frm.doc.branch, 'item':item.item_code},
                searchfield : "lot_no"
        }
}

cur_frm.fields_dict['items'].grid.get_field('price_template').get_query = function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        return {
                query: "erpnext.controllers.queries.get_cop_list",
                filters: {'item_code': d.item_code, 'posting_date': frm.posting_date, 'branch': frm.branch}
        }
}

function get_balance(frm, cdt, cdn){
         var d = locals[cdt][cdn];
                 frappe.call({
                        method: "erpnext.selling.doctype.sales_order.sales_order.get_lot_detail",
                        args: {
                                "branch": cur_frm.doc.branch,
                                "item_code": d.item_code,
                                "lot_number": d.lot_list,
                        },
                        callback: function(r) {
                                console.log(r.message);
                                if(r.message){
                                        var balance = r.message[0]['total_volume'];
                                        var lot_check = r.message[0]['lot_check'];
                                        if(lot_check)
                                        {
                                                console.log(balance);
                                                if(balance < 0){
                                                        frappe.msgprint("Not available volume under the selected Lot");
                                                }
                                                else{
                                                        frappe.model.set_value(cdt, cdn, "qty", balance);
                                                }
                                        }
                                }
                                else{
                                        frappe.msgprint("Invalid Lot Number. Please verify the lot number with Material and Branch");
                                }
                        }
                });
}

