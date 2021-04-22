// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.add_fetch("site","site_type","site_type");
cur_frm.add_fetch("site","longitude","longitude");
cur_frm.add_fetch("site","latitude","latitude");
cur_frm.add_fetch("site","dzongkhag","dzongkhag");
cur_frm.add_fetch("site","plot_no","plot_no");
cur_frm.add_fetch("site","location","site_location");
cur_frm.add_fetch("site_type","payment_required","payment_required");
cur_frm.add_fetch("item", "item_name", "item_name");
cur_frm.add_fetch("item", "item_sub_group", "item_sub_group");
cur_frm.add_fetch("item", "stock_uom", "uom");

frappe.ui.form.on('Customer Order', {
	setup: function(frm){
		frm.get_field('pool_vehicles').grid.editable_fields = [
			{fieldname: 'vehicle_capacity', columns: 3},
			{fieldname: 'noof_truck_load', columns: 3},
			{fieldname: 'quantity', columns: 3},
		];
		frm.get_field('sawns').grid.editable_fields = [
			{fieldname: 'item', columns: 2},
			{fieldname: 'size', columns: 2},
			{fieldname: 'length', columns: 2},
			{fieldname: 'qty', columns: 2},
		];
	},
	onload: function(frm){
		cur_frm.set_query("user", function(){
			return{
					"query": "erpnext.controllers.queries.get_crm_users"
			}
		});
	
		cur_frm.set_query("site", function(){
			return {
				"filters": [
					["user", "=", frm.doc.user],
					["enabled", "=", "1"],
					["product_category", "=", frm.doc.product_category]
				]
			}
		});
		
		cur_frm.set_query("lot_allotment_no",function(){
			return{
				"filters": [
					["customer_id", "=", frm.doc.user],
					["docstatus", "=", "1"],
					["site", "=", frm.doc.site ]
				]
			}
		})
		
		cur_frm.fields_dict.item_type.get_query = function() {
			return {
				"query": "erpnext.crm_utils.get_item_types_query",
				filters: {
					'product_category': frm.doc.product_category,
				}
			}
		}

		cur_frm.fields_dict.item.get_query = function() {
			return {
				"query": "erpnext.crm_utils.get_site_items",
				filters: {
					'product_category': frm.doc.product_category,
					'item_type': frm.doc.item_type,
					'site': frm.doc.site}
			}
		}

		cur_frm.fields_dict.branch.get_query = function() {
			return {
				"query": "erpnext.crm_utils.get_branch_rate_query",
				filters: {
					'site': frm.doc.site,
					'item': frm.doc.item,
					'product_group': frm.doc.product_group,
					'destination_dzongkhag': frm.doc.destination_dzongkhag,
					'product_category': frm.doc.product_category 
				}
			}
		}

		cur_frm.fields_dict.location.get_query = function() {
			return {
				"query": "erpnext.crm_utils.get_branch_location_query",
				filters: {
					'branch': frm.doc.branch,
					'item': frm.doc.item
				}
			}
		}
	
		frm.fields_dict['pool_vehicles'].grid.get_field('vehicle_capacity').get_query = function(){
			return{
				filters: {
					'is_crm_item': 1,
				}
			}
		};
		
		frm.fields_dict['vehicles'].grid.get_field('vehicle').get_query = function(){
			return{
				"query": "erpnext.crm_utils.get_vehicles_query",
				filters: {
					'user': frm.doc.user,
					'site': frm.doc.site,
					'transport_mode': frm.doc.transport_mode
				}
			}
		};
		
		cur_frm.fields_dict.product_group.get_query = function() {
			return {
				"query": "erpnext.crm_utils.get_product_groups_query",
				filters: {
					'product_category': frm.doc.product_category
				}
			}
		};
	},

	refresh: function(frm) {
		// apply_local_settings(frm);
		custom.apply_default_settings(frm);
		add_custom_buttons(frm);
		get_user_details(frm,'refresh');

		if(cur_frm.doc.selection_based_on!="Lot" && cur_frm.doc.selection_based_on!="Measurement"){
			set_transport_mode(frm);
			get_branch_location(frm);
		}

		if(cur_frm.doc.selection_based_on)
		{
			check_selection_based_on(frm,cur_frm.doc.selection_based_on,1)
		}
		apply_product_category_settings(frm);
		check_product_group(frm, 'refresh');
		apply_qty_based_validations(frm);
	},

	user: function(frm){
		cur_frm.set_value("site", null);
		get_user_details(frm,'update');
	},


	product_category: function(frm){
		cur_frm.set_value("site", null);
		cur_frm.set_value("site_type", null);
		cur_frm.set_value("item", null);
		cur_frm.set_value("selection_based_on",null)
		check_product_group(frm, 'update')
		apply_product_category_settings(frm);
		update_total_quantity(frm);
	},

	product_group: function(frm){
		if(cur_frm.doc.product_group == ""){
			cur_frm.set_value("selection_based_on",null)
		}
		check_selection_based_on(frm, cur_frm.doc.selection_based_on,0);
		apply_qty_based_validations(frm);
	},

	lot_allotment_no: function(frm){
		if(cur_frm.doc.lot_allotment_no == ""){
			cur_frm.set_value("lot_allotment_no",null)
			cur_frm.set_value("branch",null)
		}
		if(cur_frm.doc.site != null && cur_frm.doc.lot_allotment_no != null){
			if(cur_frm.doc.selection_based_on == "Lot"){
			cur_frm.clear_table("lots")
			populate_lots(frm, cur_frm.doc.lot_allotment_no);
			}
		}
	},

	site: function(frm){
		if(cur_frm.doc.site == ""){
			cur_frm.set_value("site",null)
		}
		cur_frm.set_value("item", null);
		if(!frm.doc.site){
			cur_frm.clear_table("lots")
			cur_frm.set_value("dzongkhag", null);
			cur_frm.set_value("plot_no", null);
			cur_frm.set_value("site_location", null);
			cur_frm.set_value("longitude", null);
			cur_frm.set_value("latitude", null);
		}
			cur_frm.refresh_fields();
		get_limit_details(frm);
	},

	item_type: function(frm){
		cur_frm.set_value("item", null);
	},

	item: function(frm){
		//get_branch_items(frm);	//NEED TO LOOK INTO THIS
		cur_frm.set_value("branch", null);
		if(!frm.doc.item){
			cur_frm.set_value("item_name", null);
			cur_frm.set_value("item_sub_group", null);
			cur_frm.set_value("uom", null);
		}
		get_limit_details(frm);
	},

	branch: function(frm){
		if(cur_frm.doc.selection_based_on != "Measurement" && cur_frm.doc.selection_based_on != "Lot"){
			cur_frm.set_value("location", "");
			frm.refresh_field('location');
			get_branch_location(frm);
			cur_frm.set_value("transport_mode", "");
			if (cur_frm.doc.product_category != "Timber")
			{
				get_branch_item(frm);
			}
			get_limit_details(frm);
			set_transport_mode(frm,'update');
		}
		else{
			cur_frm.clear_table("sawns");
		}
	},

	location: function(frm){
		get_branch_location_item(frm);
	},

	has_common_pool: function(frm){
		/*
		if(frm.doc.branch && !frm.doc.has_common_pool){
			cur_frm.set_value("transport_mode", "Self Owned Transport");
			cur_frm.set_df_property("transport_mode", "read_only", 1);
		} else {
			cur_frm.set_df_property("transport_mode", "read_only", 0);
		}
		*/
	},

	transport_mode: function(frm){
		//get_distance(frm);
		cur_frm.set_value("vehicles","");
		apply_product_category_settings(frm);
		update_total_quantity(frm);
	},

	vehicle_capacity: function(frm){
		update_total_quantity(frm);
	},

	noof_truck_load: function(frm){
		update_total_quantity(frm);
	},

	quantity: function(frm){
		update_total_quantity(frm);
	},

	distance: function(frm, cdt, cdn){
		update_total_quantity(frm);
	},

	place_order: function(frm){
		create_order_and_payment(frm);
	},

	total_quantity: function(frm){
		apply_qty_based_validations(frm);
	}
});

frappe.ui.form.on('Customer Order Vehicle', {
	noof_truck_load: function(frm, cdt, cdn){
		var row = locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn, "quantity", flt(row.vehicle_capacity)*flt(row.noof_truck_load));
	},
	quantity: function(frm, cdt, cdn){
		update_total_quantity(frm);
	},
	vehicles_remove: function(frm, cdt, cdn){
		update_total_quantity(frm);
	},
});

frappe.ui.form.on("Customer Order","branch", function(frm){
	cur_frm.set_query("item", "sawns", function (frm) {
		if(cur_frm.doc.branch == "" || cur_frm.doc.branch == null){
			frappe.throw("Please Select Branch First")
		}
		else{
        return {
			"query":"erpnext.controllers.queries.get_sawn_items",
            "filters": {
				"branch":cur_frm.doc.branch
            }
		}
		}
	});
	cur_frm.set_query("size", "sawns", function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
        return {
			"query":"erpnext.controllers.queries.get_sawn_items",
            "filters": {
				"branch":cur_frm.doc.branch,
				"item":row.item
            }
        }
	});
	cur_frm.set_query("length", "sawns", function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
        return {
			"query":"erpnext.controllers.queries.get_sawn_items",
            "filters": {
				"branch":cur_frm.doc.branch,
				"item":row.item,
				"size":row.size
            }
        }
	});
});

frappe.ui.form.on("Customer Order Sawn", {
	length: function(frm, cdt, cdn){
		var row = locals[cdt][cdn];
		frappe.call({
			method:"erpnext.crm_utils.get_sawn_timber",
			args: {'branch':cur_frm.doc.branch, 'item':row.item, 'size':row.size, 'length':row.length},
			callback: function(r, rt){
				if(r.message){
					r.message.forEach(function(v){
						frappe.model.set_value(cdt, cdn, "price_template", v['price_template']);
						frappe.model.set_value(cdt, cdn, "rate", v['selling_price']);
						frappe.model.set_value(cdt, cdn, "unit_cft", v['unit_cft']);
					});
				}
				refresh_field("sawns");
			}
		})
	},
	qty: function(frm, cdt, cdn){
		var row = locals[cdt][cdn];
		if(row.price_template != null && row.rate != null){
			frappe.model.set_value(cdt, cdn, "amount", row.rate*row.qty*row.unit_cft.toFixed(2));
			frappe.model.set_value(cdt, cdn, "total_cft", row.qty*row.unit_cft.toFixed(2))

		}
	}
});

frappe.ui.form.on('Customer Order Pool', {
	noof_truck_load: function(frm, cdt, cdn){
		var row = locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn, "quantity", flt(row.vehicle_capacity)*flt(row.noof_truck_load));
	},
	quantity: function(frm, cdt, cdn){
		update_total_quantity(frm);
	},
	pool_vehicles_remove: function(frm, cdt, cdn){
		update_total_quantity(frm);
	},
});

//following method created by Kinley Dorji on 2020/11/27
var populate_lots = function(frm, lot_allotment_no){
	if(frm.doc.docstatus == 0){
		frappe.call({
			method:"get_lots",
			doc: cur_frm.doc,
			args: {'lot_allotment_no': lot_allotment_no},
			callback: function(r, rt){
				if(r.message){
					r.message.forEach(function(v){
					var rows = frappe.model.add_child(frm.doc, "Customer Order Lots","lots");
					rows.lot_number = v['lot_number'];
					rows.total_volume = v['total_volume'];
					rows.discount = v['discount'];
					rows.additional = v['additional'];
					rows.payable_amount = v['payable_amount'];
					rows.pieces = v['pieces'];
					});
				}
				refresh_field("lots");
			}
		})
	}
}
//#######################################################

// following method created by SHIV on 2021/03/19
// site selection is not mandatory for Sawn Timber Orders with quantity <= 25
var apply_qty_based_validations = function(frm){
	if(frm.doc.product_category == "Timber" && frm.doc.product_group == "Sawn Timber"){
		if(flt(frm.doc.total_quantity) <= 25){
			cur_frm.toggle_display("sb_site_details", 0);
			cur_frm.toggle_reqd("site", 0);
		} else {
			cur_frm.toggle_display("sb_site_details", 1);
			cur_frm.toggle_reqd("site", 1);
		}
	}
}

var apply_product_category_settings = function(frm){
	if(frm.doc.product_category){
		frappe.call({
			method: 'frappe.client.get_value',
			args: {
				doctype: 'Product Category',
				filters: {
					'name': frm.doc.product_category
				},
				fieldname: '*'
			},
			callback: function(r){
				if(r.message){
					// Toggle for Timber By Products
					if(frm.doc.product_category == "Timber By Products"){
						cur_frm.toggle_display(["item_type", "destination_dzongkhag"], 1);
						cur_frm.toggle_reqd(["item_type", "destination_dzongkhag"], 1);
					} else {
						cur_frm.toggle_display(["item_type", "destination_dzongkhag"], 0);
						cur_frm.toggle_reqd(["item_type", "destination_dzongkhag"], 0);
					}

					// Toggle Site
					cur_frm.toggle_display("sb_site_details", r.message.site_required);
					cur_frm.toggle_reqd("site", r.message.site_required);

					// following code added by SHIV on 2021/03/19
					// site is not required for timber orders with qty <= 25
					if(frm.doc.product_category == "Timber" && frm.doc.product_group == "Sawn Timber" && flt(frm.doc.total_quantity) <= 25){
						cur_frm.toggle_reqd("site", 0);
						cur_frm.toggle_display("sb_site_details", 0);
					}

					// Toggle Transport Mode
					cur_frm.toggle_display("transport_mode", r.message.transport_mode_required);
					cur_frm.toggle_display("quantity", !r.message.transport_mode_required);
					cur_frm.toggle_display("has_common_pool", r.message.transport_mode_required);
					cur_frm.toggle_display("lead_time", r.message.transport_mode_required);
					// cur_frm.set_value("transport_mode", "");
					if(r.message.transport_mode_required){
						if(frm.doc.transport_mode){
							if(frm.doc.transport_mode == "Common Pool" || frm.doc.transport_mode == "Others"){
								cur_frm.toggle_display("pool_vehicles", 1);
								cur_frm.toggle_display("vehicles", 0);
							} else {
								cur_frm.toggle_display("pool_vehicles", 0);
								cur_frm.toggle_display("vehicles", 1);
							}
						} else {
							cur_frm.toggle_display("pool_vehicles", 0);
							cur_frm.toggle_display("vehicles", 0);
						}
					} else {
						cur_frm.toggle_display("pool_vehicles", r.message.transport_mode_required);
						cur_frm.toggle_display("vehicles", r.message.transport_mode_required);
					}
					
					cur_frm.toggle_reqd("transport_mode", r.message.transport_mode_required);
					cur_frm.toggle_reqd("quantity", !r.message.transport_mode_required);
				}
			}
		});
	} else {
		// Toggle for Timber By Products
		cur_frm.toggle_display(["item_type", "destination_dzongkhag"], 0);
		cur_frm.toggle_reqd(["item_type", "destination_dzongkhag"], 0);

		// Toggle Site
		cur_frm.toggle_display("sb_site_details", 0);
		cur_frm.toggle_reqd("site", 0);

		// Toggle Transport Mode
		cur_frm.toggle_display("transport_mode", 1);
		cur_frm.toggle_reqd("transport_mode", 1);
		cur_frm.toggle_display("quantity", 0);
		cur_frm.toggle_reqd("quantity", 0);
	} 
}

var get_user_details = function(frm, mode){
	if(frm.doc.user){
		frappe.call({
			method: 'frappe.client.get_value',
			args: {
				doctype: 'User Account',
				filters: {
					'name': frm.doc.user
				},
				fieldname: '*'
			},
			callback: function(r){
				custom.update_user_details(frm, r, mode);
			}
		});
	} else {
		custom.update_user_details(frm, {}, mode);
	}
}

var clear_locals = function(frm){
	frappe.model.remove_from_locals("Customer Order", frm.docname);
}

var create_order_and_payment = function(frm, payment_type){
	if(cur_frm.is_dirty()){
		msgprint("There are unsaved changes on this page. Please save first and try again");
		throw("Please save the order first");
	}

	if(!frm.doc.__islocal){
		frappe.call({
			method: 'frappe.client.get_value',
			args: {
				doctype: 'Site Type',
				filters: {
					'name': frm.doc.site_type,
				},
				fieldname: ['payment_required', 'credit_allowed', 'mode_of_payment'],
			},
			callback: function(r){
				if(r.message){
					if(payment_type == 'paynow'){
						if(cint(r.message.payment_required)){
							var doc 	= frappe.model.get_new_doc('Customer Payment');
							doc.user 	= frm.doc.user;
							doc.site 	= frm.doc.site;
							doc.customer_order = frm.docname;
							doc.branch	= frm.doc.branch;
							doc.customer	= frm.doc.customer;
							doc.sales_order = frm.doc.sales_order;
							doc.approval_status = 'Pending'
							//doc.total_payable_amount = frm.doc.total_payable_amount;
							//doc.total_paid_amount 	 = frm.doc.total_paid_amount;
							//doc.total_balance_amount = frm.doc.total_balance_amount
							frappe.set_route('Form', 'Customer Payment', doc.name);
						} else {
							frm.savesubmit();
						}
					} else {
						if(cint(r.message.credit_allowed)){
							var doc 	= frappe.model.get_new_doc('Customer Payment');
							doc.user 	= frm.doc.user;
							doc.site 	= frm.doc.site;
							doc.customer_order = frm.docname;
							doc.branch	= frm.doc.branch;
							doc.customer	= frm.doc.customer;
							doc.sales_order = frm.doc.sales_order;
							doc.mode_of_payment = r.message.mode_of_payment;
							doc.approval_status = 'Pending'
							frappe.set_route('Form', 'Customer Payment', doc.name);
						}
					}
				}
			}
		});
	}
}

// var apply_local_settings = function(frm){
// 	let pay_now = '[data-fieldname="place_order"][data-doctype="Customer Order"]';
// 	$(pay_now).removeClass();
// 	$(pay_now).addClass("btn btn-success btn-block");
// 	$(pay_now).width("50%");
// }

var get_distance = function(frm){
	if(frm.doc.site && frm.doc.item && frm.doc.branch){
		frappe.call({
			method: 'frappe.client.get_value',
			args: {
				doctype: 'Site Distance',
				filters: {
					'parent': frm.doc.site,
					'branch': frm.doc.branch,
					'item': frm.doc.item
				},
				fieldname: ['distance'],
			},
			callback: function(r){
				if(r.message){
					cur_frm.set_value("distance", flt(r.message.distance));
				}else{
					cur_frm.set_value("distance", 0);
				}
			}
		});
	}else{
		cur_frm.set_value("distance", 0);
	}
}

var reset_quota_details = function(frm){
	cur_frm.set_value("site_item_name", null);
	cur_frm.set_value("total_available_quantity", 0);
	cur_frm.set_value("daily_quantity_limit", 0);
	cur_frm.set_value("daily_available_quantity", 0);
	cur_frm.set_value("daily_quantity_limit_count", 0);
	cur_frm.set_value("daily_available_quantity_count", 0);
	cur_frm.set_value("weekly_quantity_limit", 0);
	cur_frm.set_value("weekly_available_quantity", 0);
	cur_frm.set_value("weekly_quantity_limit_count", 0);
	cur_frm.set_value("weekly_available_quantity_count", 0);
	cur_frm.set_value("monthly_quantity_limit", 0);
	cur_frm.set_value("monthly_available_quantity", 0);
	cur_frm.set_value("monthly_quantity_limit_count", 0);
	cur_frm.set_value("monthly_available_quantity_count", 0);
	cur_frm.set_value("yearly_quantity_limit", 0);
	cur_frm.set_value("yearly_available_quantity", 0);
	cur_frm.set_value("yearly_quantity_limit_count", 0);
	cur_frm.set_value("yearly_available_quantity_count", 0);
}

var get_limit_details = function(frm){
	if(frm.doc.user && frm.doc.site && frm.doc.item && frm.doc.branch){
		reset_quota_details(frm);
		frappe.call({
			method: "erpnext.crm_utils.get_limit_details",
			args: {"product_category": frm.doc.product_category, "customer": frm.doc.user, "site": frm.doc.site, "branch": frm.doc.branch, "item": frm.doc.item, "selection_based_on":""},
			callback: function(r, rt) {
				if(r.message){
					cur_frm.set_value("site_item_name", r.message.site_item_name);
					cur_frm.set_value("total_available_quantity", flt(r.message.total_available_quantity));
					if("has_limit" in r.message){
						var balance=0;
						cur_frm.set_value("order_limit_type", r.message.has_limit.limit_type);
						cur_frm.set_value("daily_quantity_limit", flt(r.message.has_limit.daily_quantity_limit));
						cur_frm.set_value("daily_quantity_limit_count", flt(r.message.has_limit.daily_quantity_limit_count));
						cur_frm.set_value("weekly_quantity_limit", flt(r.message.has_limit.weekly_quantity_limit));
						cur_frm.set_value("weekly_quantity_limit_count", flt(r.message.has_limit.weekly_quantity_limit_count));
						cur_frm.set_value("monthly_quantity_limit", flt(r.message.has_limit.monthly_quantity_limit));
						cur_frm.set_value("monthly_quantity_limit_count", flt(r.message.has_limit.monthly_quantity_limit_count));
						cur_frm.set_value("yearly_quantity_limit", flt(r.message.has_limit.yearly_quantity_limit));
						cur_frm.set_value("yearly_quantity_limit_count", flt(r.message.has_limit.yearly_quantity_limit_count));
						
						if(r.message.has_limit.limit_type == "Quantity"){
							if(flt(r.message.has_limit.daily_quantity_limit)){
								balance = flt(r.message.has_limit.daily_quantity_limit)-flt(r.message.has_limit.daily_ordered_quantity);
								cur_frm.set_value("daily_available_quantity", flt(balance));
							}
							if(flt(r.message.has_limit.weekly_quantity_limit)){
								balance = flt(r.message.has_limit.weekly_quantity_limit)-flt(r.message.has_limit.weekly_ordered_quantity);
								cur_frm.set_value("weekly_available_quantity", flt(balance));
							}
							if(flt(r.message.has_limit.monthly_quantity_limit)){
								balance = flt(r.message.has_limit.monthly_quantity_limit)-flt(r.message.has_limit.monthly_ordered_quantity);
								cur_frm.set_value("monthly_available_quantity", flt(balance));
							}
							if(flt(r.message.has_limit.daily_quantity_limit)){
								balance = flt(r.message.has_limit.yearly_quantity_limit)-flt(r.message.has_limit.yearly_ordered_quantity);
								cur_frm.set_value("yearly_available_quantity", flt(balance));
							}
						}else if(r.message.has_limit.limit_type == "Truck Loads"){
							if(flt(r.message.has_limit.daily_quantity_limit_count)){
								balance = flt(r.message.has_limit.daily_quantity_limit_count)-flt(r.message.has_limit.daily_ordered_quantity_count);
								cur_frm.set_value("daily_available_quantity_count", flt(balance));
							}
							if(flt(r.message.has_limit.weekly_quantity_limit_count)){
								balance = flt(r.message.has_limit.weekly_quantity_limit_count)-flt(r.message.has_limit.weekly_ordered_quantity_count);
								cur_frm.set_value("weekly_available_quantity_count", flt(balance));
							}
							if(flt(r.message.has_limit.monthly_quantity_limit_count)){
								balance = flt(r.message.has_limit.monthly_quantity_limit_count)-flt(r.message.has_limit.monthly_ordered_quantity_count);
								cur_frm.set_value("monthly_available_quantity_count", flt(balance));
							}
							if(flt(r.message.has_limit.daily_quantity_limit_count)){
								balance = flt(r.message.has_limit.yearly_quantity_limit_count)-flt(r.message.has_limit.yearly_ordered_quantity_count);
								cur_frm.set_value("yearly_available_quantity_count", flt(balance));
							}
						}
					}
				}
				//frm.refresh_field("vehicles");
			}
		});
	} else {
		reset_quota_details(frm);
	}
}

/*
var get_vehicles = function(frm){
	cur_frm.clear_table("vehicles");
	if(frm.doc.user && frm.doc.transport_mode=="Self Owned Transport"){
		frappe.call({
			method: "erpnext.crm_utils.get_vehicles",
			args: {"user": frm.doc.user},
			callback: function(r, rt) {
				if(r.message){
					r.message.forEach(function(v){
						var row = frappe.model.add_child(frm.doc, "Customer Order Vehicle", "vehicles");
						row.vehicle 		= v['name'];
						row.drivers_name	= v['drivers_name'];
						row.contact_no 		= v['contact_no'];
						row.vehicle_capacity 	= v['vehicle_capacity'];
					});
				}
				frm.refresh_field("vehicles");
				//cur_frm.refresh();
			}
		});
	}
}
*/

/*########## Ver.2020.11.23 Begins ##########*/
// following method is created as a replacement for the following one by SHIV on 2020/11/23 to accommodate Phase-II
var update_total_quantity = function(frm){
	var tbl = ((["Common Pool", "Others"].includes(frm.doc.transport_mode))?frm.doc.pool_vehicles:frm.doc.vehicles) || [];	
	var total_quantity = 0;
	var total_transportation_rate = 0;

	if(frm.doc.product_category){
		frappe.call({
			method: 'frappe.client.get_value',
			args: {
				doctype: 'Product Category',
				filters: {
					'name': frm.doc.product_category
				},
				fieldname: '*'
			},
			callback: function(r){
				if(r.message){
					if(r.message.transport_mode_required){
						for(var i=0; i<tbl.length; i++){
							total_quantity += flt(tbl[i].quantity);
						}
					
						if(["Common Pool", "Others"].includes(frm.doc.transport_mode)){
							if(frm.doc.transport_mode=="Common Pool"){
								total_transportation_rate = flt(frm.doc.distance)*flt(total_quantity)*flt(frm.doc.transport_rate);
							}
							//cur_frm.set_value("quantity", total_quantity);
						}
					} else {
						total_quantity = flt(frm.doc.quantity);
						total_transportation_rate = 0;
					}
				}
				cur_frm.set_value("total_quantity", total_quantity);
				if(cur_frm.doc.selection_based_on != "Lot")
				{
					cur_frm.set_value("total_item_rate", flt(total_quantity)*flt(frm.doc.item_rate));
					cur_frm.set_value("total_transportation_rate", total_transportation_rate);
					cur_frm.set_value("total_payable_amount", (flt(total_quantity)*flt(frm.doc.item_rate))+flt(total_transportation_rate));
				}
			}
		});
	} else {
		cur_frm.set_value("total_quantity", total_quantity);
		if(cur_frm.doc.selection_based_on != "Lot"){
		cur_frm.set_value("total_item_rate", flt(total_quantity)*flt(frm.doc.item_rate));
		cur_frm.set_value("total_transportation_rate", total_transportation_rate);
		cur_frm.set_value("total_payable_amount", (flt(total_quantity)*flt(frm.doc.item_rate))+flt(total_transportation_rate));
		}
	}
}

// following method is replaced with the above one by SHIV on 2020/11/23 to accommodate Phase-II
// var update_total_quantity = function(frm){
// 	var tbl = ((["Common Pool", "Others"].includes(frm.doc.transport_mode))?frm.doc.pool_vehicles:frm.doc.vehicles) || [];	
// 	var total_quantity = 0;
// 	var total_transportation_rate = 0;

// 	for(var i=0; i<tbl.length; i++){
// 		total_quantity += flt(tbl[i].quantity);
// 	}

// 	if(["Common Pool", "Others"].includes(frm.doc.transport_mode)){
// 		if(frm.doc.transport_mode=="Common Pool"){
// 			total_transportation_rate = flt(frm.doc.distance)*flt(total_quantity)*flt(frm.doc.transport_rate);
// 		}
// 		cur_frm.set_value("quantity", total_quantity);
// 	}
	
// 	cur_frm.set_value("total_quantity", total_quantity);
// 	cur_frm.set_value("total_item_rate", flt(total_quantity)*flt(frm.doc.item_rate));
// 	cur_frm.set_value("total_transportation_rate", total_transportation_rate);
// 	cur_frm.set_value("total_payable_amount", (flt(total_quantity)*flt(frm.doc.item_rate))+flt(total_transportation_rate));
// }
/*########## Ver.2020.11.23 Ends ##########*/

var cleanup_branch = function(frm){
	cur_frm.set_value("has_common_pool", null);
	cur_frm.set_value("lead_time", null);
	cur_frm.set_value("selling_price", null);
	cur_frm.set_value("item_rate", null);
	cur_frm.set_value("transportation_rate", null);
	cur_frm.set_value("transport_rate", null);
	cur_frm.set_value("distance", 0);
}

var cleanup_location = function(frm){
	cur_frm.set_value("selling_price", null);
	cur_frm.set_value("item_rate", null);
}

var set_transport_mode = function(frm,action='refresh'){
	var options = [];

	if(frm.doc.docstatus==0 && frm.doc.branch && (frm.doc.site || frm.doc.product_category)){
		cur_frm.set_df_property("transport_mode", "read_only", 0);
		frappe.call({
			method: "erpnext.crm_utils.get_transport_mode",
			args: {"site": frm.doc.site, "branch": frm.doc.branch, "product_category": frm.doc.product_category},
			callback: function(r){
				if(r.message){
					r.message.forEach(function(m){
						options = options.concat([{value: m, label: m}]);
					});
					if(r.message.length == 1){
						if(action == "update"){
							cur_frm.set_value("transport_mode", r.message[0]);
						}
						cur_frm.set_df_property("transport_mode", "read_only", 1);
					}
					frm.set_df_property("transport_mode", "options", options);
				}else{
					frm.set_df_property("transport_mode", "options", options);
				}
			}
		});
	}
}

var set_branch_location = function(frm, r){
	var options = [],departmental=0;
	if(r.message){
		r.message.forEach(function(v){
			options = options.concat([{value: v['location'], label: v['location']}]);
			if(v['location']=='Departmental'){
				departmental += 1;
			}
		});
	}
	//frm.set_df_property("location", "options", [''].concat(options));
	frm.set_df_property("location", "options", options);
	if(departmental && !frm.doc.location){
		cur_frm.set_value('location', 'Departmental');
	}
	frm.refresh_field('location');
}

var get_branch_location = function(frm){
	if(frm.doc.branch && frm.doc.item){
		frm.set_df_property("location", "options", []);
		frappe.call({
			method: "erpnext.crm_utils.get_branch_location",
			args: {"site": frm.doc.site || null, "branch": frm.doc.branch, "item": frm.doc.item},
			callback: function(r, rt) {
				set_branch_location(frm, r);
			},
		});
	}else{
		cleanup_location(frm);
	}
	frm.refresh_field('location');
}

var get_branch_location_item = function(frm){
	if(frm.doc.branch && frm.doc.item && frm.doc.location){
		frappe.call({
			method: "erpnext.crm_utils.get_branch_location",
			args: {"site": frm.doc.site, "branch": frm.doc.branch, "item": frm.doc.item, "location": frm.doc.location},
			callback: function(r, rt) {
				if(r.message){
					if(r.message.length==1){
						cur_frm.set_value("location", r.message[0].location);
						cur_frm.set_value("selling_price", r.message[0].selling_price);
						cur_frm.set_value("item_rate", r.message[0].item_rate);
					} else {
						cleanup_location(frm);
					}
				} else {
					cleanup_location(frm);
				}
				update_total_quantity(frm);
			},
		});
	}else{
		cleanup_location(frm);
		update_total_quantity(frm);
	}
}

/*########## Ver.2020.11.19 Begins ##########*/
// following code is no longer required, commented by SHIV on 2020/11/19 
/*
var get_branch_location_old = function(frm){
	cur_frm.set_df_property("location", "read_only", 0);
	cur_frm.toggle_reqd("location", 1);
	if(frm.doc.branch && frm.doc.item){
		frappe.call({
			method: "erpnext.crm_utils.get_branch_location",
			args: {"site": frm.doc.site, "branch": frm.doc.branch, "item": frm.doc.item, "location": frm.doc.location},
			callback: function(r, rt) {
				console.log(r);
				if(r.message){
					if(r.message.length==1){
						cur_frm.set_value("location", r.message[0].location);
						cur_frm.set_value("selling_price", r.message[0].selling_price);
						cur_frm.set_value("item_rate", r.message[0].item_rate);
						cur_frm.set_df_property("location", "read_only", !r.message[0].location);
						cur_frm.toggle_reqd("location", 0);
					} else {
						cleanup_location(frm);
						cur_frm.set_df_property("location", "read_only", 0);
					}
				} else {
					cur_frm.set_df_property("location", "read_only", 0);
					cleanup_location(frm);
				}
				update_total_quantity(frm);
			},
		});
	}else{
		cleanup_location(frm);
		update_total_quantity(frm);
	}
}
*/
/*########## Ver.2020.11.19 Ends ##########*/

var get_branch_item = function(frm){
	if(frm.doc.branch && frm.doc.item){
		frappe.call({
			method: "erpnext.crm_utils.get_branch_rate",
			args: {"branch": frm.doc.branch, "item": frm.doc.item, "site": frm.doc.site},
			callback: function(r, rt) {
				if(r.message){
					if(r.message.length==1){
						cur_frm.set_value("has_common_pool", r.message[0].has_common_pool);
						cur_frm.set_value("lead_time", r.message[0].lead_time);
						//cur_frm.set_value("selling_price", r.message[0].selling_price);
						//cur_frm.set_value("item_rate", r.message[0].item_rate);
						cur_frm.set_value("transportation_rate", r.message[0].tr_name);
						cur_frm.set_value("transport_rate", r.message[0].tr_rate);
						cur_frm.set_value("distance", r.message[0].distance);
						//get_distance(frm);
					} else {
						cleanup_branch(frm);
					}
				} else {
					cleanup_branch(frm);
				}
				update_total_quantity(frm);
				//get_branch_location(frm);
			},
		});
	}else{
		cleanup_branch(frm);
		update_total_quantity(frm);
	}
}

var get_branch_items = function(frm){
	if(frm.doc.item){
		return frappe.call({
			method: "erpnext.crm_utils.get_branch_rate",
			args: {"site": frm.doc.site, "item": frm.doc.item},
			callback: function(r, rt) {
				cur_frm.clear_table("sources");
				if(r.message){
					if(r.message.length==1){
						cur_frm.set_value("branch", r.message[0].branch);
						cur_frm.set_value("has_common_pool", r.message[0].has_common_pool);
						cur_frm.set_value("lead_time", r.message[0].lead_time);
						//cur_frm.set_value("selling_price", r.message[0].selling_price);
						//cur_frm.set_value("item_rate", r.message[0].item_rate);
						cur_frm.set_value("transportation_rate", r.message[0].tr_name);
						cur_frm.set_value("transport_rate", r.message[0].tr_rate);
						cur_frm.set_value("distance", r.message[0].distance);
						$('[data-fieldname="sources"]').closest('.visible-section').addClass("hidden");
					} else {
						cur_frm.set_value("branch", null);
						cleanup_branch(frm);
						('[data-fieldname="sources"]').closest('.visible-section').removeClass("hidden");
					}
					r.message.forEach(function(v){
						var row = frappe.model.add_child(frm.doc, "Customer Order Branch", "sources");
						if(v['has_common_pool']){
							row.transportation_rate = v['tr_name'];
							row.transport_rate 	= v['tr_rate'];
						}
						row.lead_time 		= v['lead_time'];
						row.branch 		= v['branch'];
						row.has_common_pool	= v['has_common_pool'];
						//row.selling_price	= v['selling_price'];
						//row.item_rate 		= v['item_rate'];
					});
				} else {
					cur_frm.set_value("branch", null);
					cleanup_branch(frm);
				}
				frm.refresh_field("sources");
				update_total_quantity(frm);
				//cur_frm.refresh();
			},
		});
	}else{
		cur_frm.set_value("item_name", null);
		cur_frm.set_value("item_sub_group", null);
		cur_frm.set_value("uom", null);
		cur_frm.set_value("branch", null);
		cleanup_branch(frm);
		cur_frm.clear_table("sources");
		frm.refresh_field("sources");
		update_total_quantity(frm);
	}
}

var testPay = function(frm) {
  //var xhttp = new XMLHttpRequest();
  var url = "http://uatbfssecure.rma.org.bt:8080/BFSSecure/makePayment";
  var data = "bfs_benfTxnTime=20200122151200&bfs_txnCurrency=BTN&bfs_paymentDesc=TestPayment&bfs_benfId=BE10000103&bfs_remitterEmail=sivasankar.k2003%40gmail.com&bfs_version=1.0&bfs_checkSum=0CD43EEE2128729FD399149FF8D265348B95867CF601054CDB0A4D16E0804E8A2418F9FD6E14E05363AFB814456579F35D9E68042B747EC3C8ABA5049BDE9F871E7B89A13F117AC6EB17B948970356C3B8AF98FCE8A092BC6CE309258EA97E7ECDD629DF31BFBB5A426EF2F4FCC76F892E2943163A366FA071A73CE1EA8C34620B4E84EBDD8B61A9A8637FDF59B8EB29A824D7F0A352CADE35421B70FBA0B26A6A842943EF65D427B4A3BD1831D4A3690E9316F4BA063C6A9DF07E4B76686F76D750D904B3DA2A680E76B0DACC46B5B37E0BBBEBDA06F3748A9B32817F9BE88769FFC55E52F1265EA96F02CEF7DC265A3CE1F764029D24E30BCB9AFEC945&bfs_benfBankCode=01&bfs_txnAmount=1.00&bfs_orderNo=20200123191752&bfs_msgType=AR";
  /*
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      document.getElementById("demo").innerHTML = this.responseText;
    }
  };
  xhttp.open("POST", url+"?"+data, true);
  xhttp.send();
  */
	$.ajax({
		url: url,
		type: 'POST',
		data: data,
		dataType: 'html',
		success: function (data, textStatus, xhr) {
			console.log(data)
			msgprint(("Success!! "));
			//msgprint(('<div class="row">'+data+'</div>'));
			//console.log(xhr);
			//window.location.href = data;
		},
		error: function (data, textStatus, xhr) {
			//console.log('data');
			//console.log(data);
			//console.log('textStatus');
			//console.log(textStatus);
			//console.log('xhr');
			//console.log(xhr);
			msgprint(("Failure!! "));
		}
	});
}

var add_custom_buttons = function(frm){
	/*
	frm.add_custom_button(__("Web"), function(){
		testPay(frm);
	}).addClass("btn-warning");
	*/

	// following if condition is replaced by SHIV on 2020/11/23 to accommodate Phase-II
	//if(!frm.doc.__islocal && flt(frm.doc.total_balance_amount) > 0 && frm.doc.docstatus != 2){
	if(!frm.doc.__islocal && frm.doc.site && flt(frm.doc.total_balance_amount) > 0 && frm.doc.docstatus != 2){
		frappe.call({
			method: 'frappe.client.get_value',
			args: {
				doctype: 'Site Type',
				filters: {
					'name': frm.doc.site_type
				},
				fieldname: '*',
			},
			callback: function(r){
				if(r.message){
					frm.add_custom_button(__("Pay Now"), function(){
						create_order_and_payment(frm, 'paynow');
					}).addClass("btn-warning");
					if(frm.doc.docstatus != 1 && cint(r.message.credit_allowed)){
						frm.add_custom_button(__("Pay Later"), function(){
							create_order_and_payment(frm, 'paylater');
						}).addClass("btn-warning");
					}
				}
			}
		});
	}
}

var check_product_group = function(frm, mode){
	if(frm.doc.product_category){
		frappe.call({
			method:"erpnext.crm_utils.get_product_groups",
			args:{
				"product_category":frm.doc.product_category
			},
			callback: function(r){
				if(r.message){
					cur_frm.toggle_display("product_group",1);
					cur_frm.toggle_reqd("product_group",1);
					cur_frm.toggle_display("selection_based_on",1);
				}
				else{
					clear_fields(mode);
				}
			}
		});
	}
	else{
		clear_fields(mode);
	}
	cur_frm.refresh_fields()
}

var clear_fields = function(mode="refresh"){
	cur_frm.toggle_reqd("product_group",0);
	cur_frm.toggle_display("product_group",0);
	cur_frm.toggle_display("selection_based_on",0);
	cur_frm.toggle_display("challan_cost",0);
	cur_frm.toggle_display("lot_allotment_no",0);

	if(mode == "update"){
		cur_frm.set_value("product_group",null);
		cur_frm.set_value("selection_based_on",null);
		cur_frm.set_value("challan_cost",null);
		cur_frm.set_value("lot_allotment_no",null);
		cur_frm.clear_table("lots");
	}
 }

 var check_selection_based_on = function(frm, selection_based_on, refresh){
	if(selection_based_on == "Item"){
		cur_frm.clear_table("lots");
		cur_frm.clear_table("sawns");
		cur_frm.toggle_display("section_break_lots",0);
		cur_frm.toggle_reqd("item",1);
		cur_frm.toggle_reqd("branch",1);
		cur_frm.toggle_reqd("location",1);
		cur_frm.toggle_reqd("lot_allotment_no",0);
		cur_frm.toggle_reqd("transport_mode",1);
		cur_frm.toggle_display("transport_mode",1);
		cur_frm.toggle_display("total_quantity",1);
		cur_frm.toggle_display("total_item_rate",1);
		cur_frm.set_value("challan_cost",null);
		cur_frm.toggle_display("lot_allotment_no",null);
		cur_frm.toggle_display("challan_cost",0);
		cur_frm.toggle_display("lot_allotment_no",0);
		cur_frm.toggle_display("sb_sawn",0);
		apply_product_category_settings(frm);
		cur_frm.refresh_fields();
	}
	else if(selection_based_on == "Lot"){
		cur_frm.toggle_reqd("item",0);
		cur_frm.toggle_reqd("branch",0);
		cur_frm.toggle_reqd("location",0);
		cur_frm.toggle_reqd("transport_mode",0);
		cur_frm.toggle_reqd("lot_allotment_no",1);
		if(refresh==0){
		cur_frm.set_value("transport_mode",null);
		cur_frm.set_value("vehicle_capacity",null);
		cur_frm.set_value("noof_truck_load",null);
		cur_frm.set_value("total_item_rate",null);
		cur_frm.set_value("total_transportation_rate",null);
		cur_frm.set_value("item",null);
		cur_frm.set_value("item_name",null);
		cur_frm.set_value("item_sub_group",null);
		cur_frm.set_value("uom",null);
		cur_frm.set_value("site_item_name",null);
		cur_frm.set_value("location",null);
		cur_frm.set_value("has_common_pool",null);
		cur_frm.set_value("item_rate",null);
		cur_frm.set_value("has_common_pool",null);
		cur_frm.set_value("lead_time",null);
		cur_frm.set_value("transport_rate",null);
		cur_frm.set_value("distance",null);
		cur_frm.set_value("challan_cost",null);
		}
		cur_frm.clear_table("vehicles");
		cur_frm.clear_table("pool_vehicles");
		cur_frm.clear_table("sources");
		cur_frm.clear_table("sawns");
		cur_frm.toggle_display("item",0);
		cur_frm.toggle_display("item_name",0);
		cur_frm.toggle_display("item_sub_group",0);
		cur_frm.toggle_display("uom",0);
		cur_frm.toggle_display("site_item_name",0);
		cur_frm.toggle_display("has_common_pool",0);
		cur_frm.toggle_display("location",0);
		cur_frm.toggle_display("item_rate",0);
		cur_frm.toggle_display("lead_time",0);
		cur_frm.toggle_display("transport_rate",0);
		cur_frm.toggle_display("distance",0);
		cur_frm.toggle_display("sources",0);
		cur_frm.toggle_display("transport_mode",0);
		cur_frm.toggle_display("vehicle_capacity",0);
		cur_frm.toggle_display("noof_truck_load",0);
		cur_frm.toggle_display("total_item_rate",0);
		cur_frm.toggle_display("sb_sawn",0);
		cur_frm.toggle_display("total_transportation_rate",0);
		cur_frm.toggle_display("section_break_lots",1);
		cur_frm.toggle_display("challan_cost",1);
		cur_frm.toggle_display("lot_allotment_no",1);
		cur_frm.toggle_display("challan_cost",1);
		if(cur_frm.doc.lot_allotment_no && refresh == 0){
			populate_lots(frm, cur_frm.doc.lot_allotment_no)
		}
		else{
			cur_frm.refresh_fields();
		}
	}
	else if(selection_based_on == "Measurement"){
		cur_frm.toggle_reqd("item",0);
		cur_frm.toggle_reqd("location",0);
		cur_frm.toggle_reqd("transport_mode",0);
		cur_frm.toggle_reqd("lot_allotment_no",0);
		cur_frm.toggle_reqd("quantity",0);
		if(refresh==0){
		cur_frm.set_value("transport_mode",null);
		cur_frm.set_value("vehicle_capacity",null);
		cur_frm.set_value("noof_truck_load",null);
		cur_frm.set_value("total_item_rate",null);
		cur_frm.set_value("total_transportation_rate",null);
		cur_frm.set_value("item",null);
		cur_frm.set_value("item_name",null);
		cur_frm.set_value("item_sub_group",null);
		cur_frm.set_value("uom",null);
		cur_frm.set_value("site_item_name",null);
		cur_frm.set_value("location",null);
		cur_frm.set_value("has_common_pool",null);
		cur_frm.set_value("item_rate",null);
		cur_frm.set_value("has_common_pool",null);
		cur_frm.set_value("lead_time",null);
		cur_frm.set_value("transport_rate",null);
		cur_frm.set_value("distance",null);
		}
		cur_frm.clear_table("vehicles");
		cur_frm.clear_table("pool_vehicles");
		cur_frm.clear_table("sources");
		cur_frm.toggle_display("item",0);
		cur_frm.toggle_display("item_name",0);
		cur_frm.toggle_display("item_sub_group",0);
		cur_frm.toggle_display("item_rate",0);
		cur_frm.toggle_display("uom",0);
		cur_frm.toggle_display("location",0);
		cur_frm.toggle_display("transport_mode",0);
		cur_frm.toggle_display("vehicle_capacity",0);
		cur_frm.toggle_display("noof_truck_load",0);
		cur_frm.toggle_display("total_item_rate",0);		
		cur_frm.toggle_display("total_transportation_rate",0);
		cur_frm.toggle_display("sb_sawn",1);
		cur_frm.toggle_display("section_break_lots",1);
		cur_frm.toggle_display("challan_cost",0);
		cur_frm.toggle_display("lot_allotment_no",);
		cur_frm.refresh_fields();
	}
	else{
		cur_frm.clear_table("lots");
		cur_frm.clear_table("sawns");
		cur_frm.toggle_display("section_break_lots",0);
		cur_frm.toggle_display("sb_sawn",0);
		cur_frm.toggle_reqd("item",1);
		cur_frm.toggle_reqd("branch",1);
		cur_frm.toggle_reqd("location",1);
		cur_frm.toggle_reqd("lot_allotment_no",0);
		cur_frm.toggle_reqd("transport_mode",1);
		cur_frm.toggle_display("transport_mode",1);
		cur_frm.toggle_display("total_quantity",1);
		cur_frm.toggle_display("total_item_rate",1);
		cur_frm.set_value("lot_allotment_no",null);
		cur_frm.set_value("challan_cost",null);
		cur_frm.toggle_display("lot_allotment_no",0);
		cur_frm.toggle_display("challan_cost",0);
		apply_product_category_settings(frm);
		cur_frm.refresh_fields();
	}
 }
