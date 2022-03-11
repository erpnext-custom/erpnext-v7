// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

{% include 'erpnext/selling/sales_common.js' %}

cur_frm.add_fetch("rate_template", "rate", "transportation_rate")
cur_frm.add_fetch("item_code", "business_activity", "business_activity");

frappe.ui.form.on("Sales Order", {
	onload: function(frm) {
		/*erpnext.queries.setup_queries(frm, "Warehouse", function() {
			return erpnext.queries.warehouse(frm.doc);
		});
		
		if(!frm.doc.selling_price_list) {
			//set default price list
			frm.set_value("selling_price_list", "Standard Selling")
		}*/

		// formatter for material request item
		frm.set_indicator_formatter('item_code',
			function(doc) { return (doc.qty<=doc.delivered_qty) ? "green" : "orange" })
	},
	"naming_series": function(frm) {
		cur_frm.toggle_reqd("selling_price_template", frm.doc.naming_series == 'Sales Product' );

		/*
		// Following code added by SHIV on 08/12/2017
		cur_frm.fields_dict['items'].grid.get_field('item_code').get_query = function(frm, cdt, cdn) {
			var d = locals[cdt][cdn];
			return {
				filters: [
				['Item', 'item_group', '=', frm.naming_series]
				]
			}
		}*/
	},
	"discount_or_cost_amount": function(frm) {
		cur_frm.set_value("discount_amount", flt(frm.doc.discount_or_cost_amount) - flt(frm.doc.transportation_charges) - flt(frm.doc.additional_cost) - flt(frm.doc.loading_cost)-flt(frm.doc.challan_cost))
		cur_frm.refresh_field("discount_amount")
	},

	"transportation_charges": function(frm) {
		cur_frm.set_value("discount_amount", flt(frm.doc.discount_or_cost_amount) - flt(frm.doc.transportation_charges) - flt(frm.doc.additional_cost) - flt(frm.doc.loading_cost)-flt(frm.doc.challan_cost))
		cur_frm.refresh_field("discount_amount")
	},

	"additional_cost": function(frm) {
		cur_frm.set_value("discount_amount", flt(frm.doc.discount_or_cost_amount) - flt(frm.doc.transportation_charges) - flt(frm.doc.additional_cost) - flt(frm.doc.loading_cost)-flt(frm.doc.challan_cost))
		cur_frm.refresh_field("discount_amount")
        },

	"challan_cost": function(frm) {
		cur_frm.set_value("discount_amount", flt(frm.doc.discount_or_cost_amount) - flt(frm.doc.transportation_charges) - flt(frm.doc.additional_cost) - flt(frm.doc.loading_cost)-flt(frm.doc.challan_cost))
		cur_frm.refresh_field("discount_amount")
	},

	"loading_rate": function(frm) {
		var total_qty = 0;
		for (var i in cur_frm.doc.items) {
			var item = cur_frm.doc.items[i];
		        total_qty += item.qty;		
			}
		cur_frm.set_value("loading_cost", flt(total_qty) * flt(frm.doc.loading_rate));
	},
	
	"imo_quantity": function(frm) {
		cur_frm.set_value("total_imo_cost", flt(frm.doc.imo_rate) * flt(frm.doc.imo_quantity));
	},

	"loading_cost": function(frm) {
		cur_frm.set_value("discount_amount", flt(frm.doc.discount_or_cost_amount) - flt(frm.doc.transportation_charges) - flt(frm.doc.additional_cost) - flt(frm.doc.loading_cost)-flt(frm.doc.challan_cost))
		cur_frm.refresh_field("discount_amount")
	},

	"transportation_rate": function(frm) {
		cur_frm.set_value("transportation_charges", flt(frm.doc.transportation_rate) * flt(frm.doc.total_distance) * flt(frm.doc.total_quantity))
		cur_frm.trigger("transportation_charges")
		cur_frm.refresh_field("transportation_charges")
	},

	"total_distance": function(frm) {
		cur_frm.set_value("transportation_charges", flt(frm.doc.transportation_rate) * flt(frm.doc.total_distance) * flt(frm.doc.total_quantity))
		cur_frm.trigger("transportation_charges")
		cur_frm.refresh_field("transportation_charges")
	},

	"total_quantity": function(frm) {
		cur_frm.set_value("transportation_charges", flt(frm.doc.transportation_rate) * flt(frm.doc.total_distance) * flt(frm.doc.total_quantity))
		cur_frm.trigger("transportation_charges")
		cur_frm.refresh_field("transportation_charges")
	},
});

/*
// Following function added by SHIV on 08/12/2017
frappe.ui.form.on("Sales Order Item", {
	"item_code": function(frm, cdt, cdn){
		var child = locals[cdt][cdn];
		cur_frm.call({
				method: "erpnext.stock.doctype.stock_price_template.stock_price_template.get_item_rate",
				args: {
					 tran_type: 'Sales',
					 item_code: child.item_code,
					 tran_date: frm.doc.transaction_date
				},
				callback: function(r) {
				   if(r.message)  { 
						frappe.model.set_value(cdt, cdn, 'item_code', r.message[0]['item_code']);
						frappe.model.set_value(cdt, cdn, 'item_name', r.message[0]['item_name']);
						frappe.model.set_value(cdt, cdn, 'qty', 0);
						frappe.model.set_value(cdt, cdn, 'rate', r.message[0]['rate']);
						//refresh_field("items"); 
					}
				}
		});
	},
});
*/

erpnext.selling.SalesOrderController = erpnext.selling.SellingController.extend({
	refresh: function(doc, dt, dn) {
		this._super();
		var allow_purchase = false;
		var allow_delivery = false;

		if(doc.docstatus==1) {
			if(doc.status != 'Closed') {

				for (var i in cur_frm.doc.items) {
					var item = cur_frm.doc.items[i];
					if(item.delivered_by_supplier === 1 || item.supplier){
						if(item.qty > flt(item.ordered_qty)
							&& item.qty > flt(item.delivered_qty)) {
							allow_purchase = true;
						}
					}

					if (item.delivered_by_supplier===0) {
						if(item.qty > flt(item.delivered_qty)) {
							allow_delivery = true;
						}
					}

					if (allow_delivery && allow_purchase) {
						break;
					}
				}

				if (this.frm.has_perm("submit")) {
					// close
					if(flt(doc.per_delivered, 2) < 100 || flt(doc.per_billed) < 100) {
							cur_frm.add_custom_button(__('Close'), this.close_sales_order, __("Status"))
						}
				}

				// delivery note and payment
				if(flt(doc.per_delivered, 2) < 100 && ["Sales", "Shopping Cart"].indexOf(doc.order_type)!==-1 && allow_delivery) {
					if(doc.is_credit == 1 || doc.is_kidu_sale){
						cur_frm.add_custom_button(__('Delivery'), this.make_delivery_note, __("Make"));
				 	}
					if(!doc.is_kidu_sale){
						cur_frm.add_custom_button(__('Payment'), cur_frm.cscript.make_payment_entry, __("Make"));
					}
					cur_frm.page.set_inner_btn_group_as_primary(__("Make"));
				}
				//getting payment detail
				var payment_done = 0;
				if(doc.is_credit == 0){
				frappe.call({
					method: "get_payment_detail",
					doc : doc,
					async: false,
					callback: function(r) {
						if(r.message) {

							if(r.message == "1"){
								payment_done = 1					
							
						}}
					}
				});
				if(payment_done == 1){
					cur_frm.add_custom_button(__('Delivery'), this.make_delivery_note, __("Make"));
				}
				}

				/*// sales invoice
				if(flt(doc.per_billed, 2) < 100) {
					cur_frm.add_custom_button(__('Invoice'), this.make_sales_invoice, __("Make"));
				}

				// material request
				if(!doc.order_type || ["Sales", "Shopping Cart"].indexOf(doc.order_type)!==-1
					&& flt(doc.per_delivered, 2) < 100) {
						cur_frm.add_custom_button(__('Material Request'), this.make_material_request, __("Make"));
				}*/

				// make purchase order
				if(flt(doc.per_delivered, 2) < 100 && allow_purchase) {
					cur_frm.add_custom_button(__('Purchase Order'), cur_frm.cscript.make_purchase_order, __("Make"));
				}

				/*if(flt(doc.per_billed)==0) {
					cur_frm.add_custom_button(__('Payment Request'), this.make_payment_request, __("Make"));
					cur_frm.add_custom_button(__('Payment'), cur_frm.cscript.make_bank_entry, __("Make"));
				}*/

				// maintenance
				if(flt(doc.per_delivered, 2) < 100 &&
						["Sales", "Shopping Cart"].indexOf(doc.order_type)===-1) {
					cur_frm.add_custom_button(__('Maintenance Visit'), this.make_maintenance_visit, __("Make"));
					cur_frm.add_custom_button(__('Maintenance Schedule'), this.make_maintenance_schedule, __("Make"));
				}


			} else {
				if (this.frm.has_perm("submit")) {
					// un-close
					cur_frm.add_custom_button(__('Re-open'), cur_frm.cscript['Unclose Sales Order'], __("Status"));
				}
			}
		}

		if (this.frm.doc.docstatus===0) {
			cur_frm.add_custom_button(__('Quotation'),
				function() {
					// cur_frm.clear_table("items");
					erpnext.utils.map_current_doc({
						method: "erpnext.selling.doctype.quotation.quotation.make_sales_order",
						source_doctype: "Quotation",
						get_query_filters: {
							docstatus: 1,
							status: ["!=", "Lost"],
							order_type: cur_frm.doc.order_type,
							customer: cur_frm.doc.customer || undefined,
							company: cur_frm.doc.company
						}
					})
				}, __("Get items from"));
			
			cur_frm.add_custom_button(__('Product Requisition'),
                                function() {
										// cur_frm.clear_table("items");
                                        erpnext.utils.map_current_doc({
                                                method: "erpnext.selling.doctype.product_requisition.product_requisition.make_sales_order",
                                                source_doctype: "Product Requisition",
                                                get_query_filters: {
                                                        docstatus: 1,
                                                        company: cur_frm.doc.company
                                                }
                                        })
								}, __("Get items from"));
			
			cur_frm.add_custom_button(__('Lot List'),
				function() {
						//Should create a method to check for duplicate entries here
						// cur_frm.clear_table("items");
						custom_map_current_doc({
								method: "erpnext.production.doctype.lot_list.lot_list.make_sales_order",
								source_doctype: "Lot List",
								// get_query_filters: {
								// 		docstatus: 1,
								// 		company: cur_frm.doc.company
								// }
								get_query_filters: {
									query: "erpnext.production.doctype.lot_list.lot_list.get_lot_list",
									filters: {branch:cur_frm.doc.branch}
								}
						})
				}, __("Get items from"));
		}

		this.order_type(doc);
	},

	order_type: function() {
		this.frm.toggle_reqd("delivery_date", this.frm.doc.order_type == "Sales");
	},

	tc_name: function() {
		this.get_terms();
	},

	make_material_request: function() {
		frappe.model.open_mapped_doc({
			method: "erpnext.selling.doctype.sales_order.sales_order.make_material_request",
			frm: cur_frm
		})
	},

	make_delivery_note: function() {
		frappe.model.open_mapped_doc({
			method: "erpnext.selling.doctype.sales_order.sales_order.make_delivery_note",
			frm: cur_frm
		})
	},

	make_sales_invoice: function() {
		frappe.model.open_mapped_doc({
			method: "erpnext.selling.doctype.sales_order.sales_order.make_sales_invoice",
			frm: cur_frm
		})
	},

	make_maintenance_schedule: function() {
		frappe.model.open_mapped_doc({
			method: "erpnext.selling.doctype.sales_order.sales_order.make_maintenance_schedule",
			frm: cur_frm
		})
	},

	make_maintenance_visit: function() {
		frappe.model.open_mapped_doc({
			method: "erpnext.selling.doctype.sales_order.sales_order.make_maintenance_visit",
			frm: cur_frm
		})
	},

	make_purchase_order: function(){
		var dialog = new frappe.ui.Dialog({
			title: __("For Supplier"),
			fields: [
				{"fieldtype": "Link", "label": __("Supplier"), "fieldname": "supplier", "options":"Supplier",
					"get_query": function () {
						return {
							query:"erpnext.selling.doctype.sales_order.sales_order.get_supplier",
							filters: {'parent': cur_frm.doc.name}
						}
					}, "reqd": 1 },
				{"fieldtype": "Button", "label": __("Make Purchase Order"), "fieldname": "make_purchase_order", "cssClass": "btn-primary"},
			]
		});

		dialog.fields_dict.make_purchase_order.$input.click(function() {
			args = dialog.get_values();
			if(!args) return;
			dialog.hide();
			return frappe.call({
				type: "GET",
				method: "erpnext.selling.doctype.sales_order.sales_order.make_purchase_order_for_drop_shipment",
				args: {
					"source_name": cur_frm.doc.name,
					"for_supplier": args.supplier
				},
				freeze: true,
				callback: function(r) {
					if(!r.exc) {
						var doc = frappe.model.sync(r.message);
						frappe.set_route("Form", r.message.doctype, r.message.name);
					}
				}
			})
		});
		dialog.show();
	},
	close_sales_order: function(){
		cur_frm.cscript.update_status("Close", "Closed")
	}

});

// frappe.ui.form.on("Sales Order", "validate", function(frm) {
// 	if(!frappe.user.has_role('Sales Master')){
// 	var date = frappe.datetime.add_days(get_today(), -3);
// 	if (frm.doc.posting_date < date ) {
// 		frappe.throw(__("You Can Not Submit For Posting Date Beyond Past 3 Days"));
// 		frappe.validated = false;
// 	}
// 	}
// });
// for backward compatibility: combine new and previous states
$.extend(cur_frm.cscript, new erpnext.selling.SalesOrderController({frm: cur_frm}));

cur_frm.cscript.new_contact = function(){
	tn = frappe.model.make_new_doc_and_get_name('Contact');
	locals['Contact'][tn].is_customer = 1;
	if(doc.customer) locals['Contact'][tn].customer = doc.customer;
	frappe.set_route('Form', 'Contact', tn);
}

cur_frm.fields_dict['project'].get_query = function(doc, cdt, cdn) {
	return {
		query: "erpnext.controllers.queries.get_project_name",
		filters: {
			'customer': doc.customer
		}
	}
}

cur_frm.cscript.update_status = function(label, status){
	var doc = cur_frm.doc;
	frappe.ui.form.is_saving = true;
	frappe.call({
		method: "erpnext.selling.doctype.sales_order.sales_order.update_status",
		args: {status: status, name: doc.name},
		callback: function(r){
			cur_frm.reload_doc();
		},
		always: function() {
			frappe.ui.form.is_saving = false;
		}
	});
}

cur_frm.cscript['Unclose Sales Order'] = function() {
	cur_frm.cscript.update_status('Re-open', 'Draft')
}

cur_frm.cscript.on_submit = function(doc, cdt, cdn) {
	if(cint(frappe.boot.notification_settings.sales_order)) {
		cur_frm.email_doc(frappe.boot.notification_settings.sales_order_message);
	}
};

frappe.ui.form.on("Sales Order", "refresh", function(frm) {
    cur_frm.set_query("customer", function() {
        return {
            "filters": {
                "disabled": 0
            }
        };
    });
    cur_frm.set_query("rate_template", function() {
        return {
            "filters": {
                "branch": frm.doc.branch
            }
        };
    });
   cur_frm.set_query("location", function() {
	return{
		"filters":{
			"branch": frm.doc.branch,
			"is_disabled": 0
		}
	};
   });
})

/*
//Set select option for "Initial Stock Templates"
cur_frm.fields_dict['selling_price_template'].get_query = function(doc, dt, dn) {
  return {
     query: "erpnext.stock.doctype.stock_price_template.stock_price_template.get_template_list",
     filters: { naming_series: doc.naming_series, posting_date: doc.transaction_date, purpose: 'Sales' }
  };
}
//Auto add items based on the values created in the "Initial Stock Template" Setting
cur_frm.cscript.selling_price_template = function(doc) {
    cur_frm.call({
        method: "erpnext.stock.doctype.stock_price_template.stock_price_template.get_initial_values",
        args: {
             name: doc.selling_price_template
        },
        callback: function(r) {
           if(r.message)  { 
                cur_frm.clear_table("items");
                var new_row = frappe.model.add_child(cur_frm.doc, "Sales Order Item", "items");
                new_row.item_code = r.message[0]['item_code'];
                new_row.item_name = r.message[0]['item_name'];
                new_row.uom = r.message[0]['uom'];
                new_row.stock_uom = r.message[0]['stock_uom'];
                new_row.qty = 0;
                new_row.rate = r.message[0]['rate_amount'];
                refresh_field("items"); 
            }
        }
   });
	if(doc.selling_price_template) {
	       //Set item table read only
	       cur_frm.set_df_property("items", "read_only",1);
	       frappe.meta.get_docfield("Sales Order Item", "rate", cur_frm.doc.name).read_only = 1;
	       frappe.meta.get_docfield("Sales Order Item", "item_code", cur_frm.doc.name).read_only = 1;
	       refresh_field("items");
	}
	else {
	       cur_frm.set_df_property("items", "read_only", 0);
	       frappe.meta.get_docfield("Sales Order Item", "rate", cur_frm.doc.name).read_only = 1;
	       frappe.meta.get_docfield("Sales Order Item", "item_code", cur_frm.doc.name).read_only = 1;
	       refresh_field("items");
	}
}
*/

//auto list the price_templates based on branch, transaction_date, item_code
cur_frm.fields_dict['items'].grid.get_field('price_template').get_query = function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
		if(d.sales_uom){
			uom = d.sales_uom
		}else{
			uom = ''
		}
        return {
                query: "erpnext.controllers.queries.price_template_list",
                filters: {'item_code': d.item_code, 'transaction_date': frm.transaction_date, 'branch': frm.branch, 'location': frm.location, 'selling_uom': uom, 'naming_series': frm.naming_series}
        }
}

//auto list the price_templates based on branch, transaction_date, item_code, customer written by Thukten on 12 Dec, 2021
cur_frm.fields_dict['items'].grid.get_field('customer_price_list').get_query = function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	return {
			query: "erpnext.controllers.queries.customer_price_template_list",
			filters: {'item_code': d.item_code, 'transaction_date': frm.transaction_date, 'branch': frm.branch, 'location': frm.location, 'customer': frm.customer}
	}
}

cur_frm.fields_dict['items'].grid.get_field('warehouse').get_query = function(frm, cdt, cdn) {
	item = locals[cdt][cdn]
	return {
		"query": "erpnext.controllers.queries.filter_branch_wh",
		filters: {'branch': frm.branch}
	}
}

cur_frm.fields_dict['items'].grid.get_field('lot_number').get_query = function(frm, cdt, cdn) {
	var item = locals[cdt][cdn];
	return {
		query: "erpnext.controllers.queries.filter_lots",
		filters: {'branch': cur_frm.doc.branch, 'item':item.item_code},
		searchfield : "lot_no"
	}
} 

cur_frm.fields_dict['items'].grid.get_field('sales_uom').get_query = function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	return {
		query: "erpnext.controllers.queries.get_item_uom",
		filters: {'item_code': d.item_code}
	}
}

// on_selection of price_template, auto load the seling rate for items
frappe.ui.form.on("Sales Order Item", {
	"qty": function(frm, cdt, cdn) {
		var item = locals[cdt][cdn]
		if(frm.doc.naming_series == "Timber Products" && !frm.doc.is_kidu_sale) { 
			if(item.lot_number){
				get_balance(frm, cdt, cdn);
			} 
			if(item.conversion_req){
				frappe.model.set_value(cdt, cdn, "stock_qty", '')
				cur_frm.refresh_field("stock_qty")
			}
		}

		if(item.item_code && item.stock_uom){
			if(item.stock_uom != item.sales_uom && (typeof item.sales_uom != "undefined" && item.sales_uom != '')){
				frappe.model.set_value(cdt, cdn, "stock_qty", item.conversion_factor * item.qty)
				cur_frm.refresh_field("stock_qty")
			}
			else{
				frappe.model.set_value(cdt, cdn, "stock_qty", item.qty)
				cur_frm.refresh_field("stock_qty")
			}
		}
	},	

	"sales_uom": function(frm, cdt, cdn) {
		frappe.model.set_value(cdt, cdn, "price_template", "") 

		var item = locals[cdt][cdn];
		
		if(item.item_code && item.sales_uom) {
			frappe.call({
				method: "erpnext.stock.get_item_details.get_conversion_factor",
				args: {
					item_code: item.item_code,
					uom: item.sales_uom
				},
				callback: function(r) {
					if(r.message.conversion_factor){
						frappe.model.set_value(cdt, cdn, "conversion_factor", r.message.conversion_factor)
						frappe.model.set_value(cdt, cdn, "stock_qty", r.message.conversion_factor * item.qty)
						cur_frm.refresh_field("conversion_factor")
						cur_frm.refresh_field("stock_qty")
					}
				}
			});
		}
	},

	"conversion_req": function(frm, cdt, cdn) {
		frappe.model.set_value(cdt, cdn, "sales_uom", "") 
		frappe.model.set_value(cdt, cdn, "price_template", "")
		
		var row = locals[cdt][cdn]
		frm.fields_dict.items.grid.toggle_reqd("sales_uom", row.conversion_req?1:0)
		frm.refresh_field('sales_uom')

		if(frm.doc.naming_series == "Timber Products"){
			frm.fields_dict.items.grid.toggle_reqd("stock_qty", 1)
			frm.fields_dict.items.grid.toggle_enable("stock_qty", 1)
			frm.refresh_field('stock_qty')
		}

	},
	
	form_render: (frm,cdt,cdn)=>{
		var row = locals[cdt][cdn]
		frm.fields_dict.items.grid.toggle_reqd("sales_uom", row.conversion_req?1:0)
		frm.refresh_field('sales_uom')
		if(frm.doc.naming_series == "Timber Products"){
			frm.fields_dict.items.grid.toggle_reqd("stock_qty", 1)
			frm.refresh_field('stock_qty')
		}
	},
	
	"stock_qty": function(frm, cdt, cdn) {
		if(frm.doc.naming_series == "Timber Products"){
			var row = locals[cdt][cdn]
			if(row.qty != 0){
				frappe.model.set_value(cdt, cdn, "conversion_factor", row.stock_qty / row.qty)
				cur_frm.refresh_field("conversion_factor")
			}
		}
	},

	"price_template": function(frm, cdt, cdn) {
		d = locals[cdt][cdn]
		if(cur_frm.doc.location){
			loc = cur_frm.doc.location;
		}else{
			loc = ''
		}

		if(d.sales_uom){
			uom = d.sales_uom
		}else{
			uom = ''
		}

		frappe.call({
				method: "erpnext.production.doctype.selling_price.selling_price.get_selling_rate",
				args: {
						"price_list": d.price_template,
						"branch": cur_frm.doc.branch,
						"item_code": d.item_code,
						"transaction_date": cur_frm.doc.transaction_date,
						"selling_uom": uom,
						"location": loc,
						"naming_series": cur_frm.doc.naming_series			
					},
				callback: function(r) {
						frappe.model.set_value(cdt, cdn, "price_list_rate", r.message)
						frappe.model.set_value(cdt, cdn, "rate", r.message)
						cur_frm.refresh_field("price_list_rate")
						cur_frm.refresh_field("rate")
				}
            })
    },

	"customer_price_list": function(frm, cdt, cdn) {
		d = locals[cdt][cdn]
		if(cur_frm.doc.location){
			loc = cur_frm.doc.location;
		}else{
			loc = "NA";
		}
		frappe.call({
			method: "erpnext.production.doctype.customer_selling_price.customer_selling_price.get_customer_selling_rate",
			args: {
				"price_list": d.customer_price_list,
				"branch": cur_frm.doc.branch,
				"item_code": d.item_code,
				"transaction_date": cur_frm.doc.transaction_date,
				"location": loc,
				"customer": cur_frm.doc.customer
			},
			callback: function(r) {
				frappe.model.set_value(cdt, cdn, "price_list_rate", r.message);
				frappe.model.set_value(cdt, cdn, "rate", r.message);
				cur_frm.refresh_field("price_list_rate");
				cur_frm.refresh_field("rate");
			}
		})
	},

	"item_code": function(frm, cdt, cdn) {
		frappe.model.set_value(cdt, cdn, "price_template", "") 
	},

	"lot_number": function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		if(d.item_code && d.lot_number) { get_balance(frm, cdt, cdn); }
	},

	"sp_type": function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		if(d.sp_type == "General Rate"){

		}else{

		}
	}
	
});

frappe.ui.form.on("Sales Order","naming_series", function(frm){
	cur_frm.set_query("item_code", "items", function (frm) {
        return {
            "filters": {
				"item_group": cur_frm.doc.naming_series,
				"disabled":0
            }
        }
    });
});

function get_balance(frm, cdt, cdn){
		var d = locals[cdt][cdn];
		frappe.call({
			method: "erpnext.selling.doctype.sales_order.sales_order.get_lot_detail",
			args: {
				"branch": cur_frm.doc.branch,
				"item_code": d.item_code,
				"lot_number": d.lot_number,
				"total_pieces": d.total_pieces
			},
			callback: function(r) {
				if(r.message){
				var balance = r.message[0]['total_volume'];
				var lot_check = r.message[0]['lot_check'];
					if(lot_check)
					{
						if(balance < 0){
							frappe.msgprint("No available volume under the selected Lot");
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


var custom_map_current_doc = function(opts) {
	if(opts.get_query_filters) {
		opts.get_query = function() {
			//return {filters: opts.get_query_filters};
			return opts.get_query_filters;
		}
	}
	var _map = function() {
		// remove first item row if empty
		if($.isArray(cur_frm.doc.items) && cur_frm.doc.items.length > 0) {
			if(!cur_frm.doc.items[0].item_code) {
				cur_frm.doc.items = cur_frm.doc.items.splice(1);
			}
		}

		return frappe.call({
			// Sometimes we hit the limit for URL length of a GET request
			// as we send the full target_doc. Hence this is a POST request.
			type: "POST",
			method: opts.method,
			args: {
				"source_name": opts.source_name,
				"target_doc": cur_frm.doc
			},
			callback: function(r) {
				if(!r.exc) {
					var doc = frappe.model.sync(r.message);
					cur_frm.refresh();
				}
			}
		});
	}
	if(opts.source_doctype) {
		var d = new frappe.ui.Dialog({
			title: __("Get From ") + __(opts.source_doctype),
			fields: [
				{
					fieldtype: "Link",
					label: __(opts.source_doctype),
					fieldname: opts.source_doctype,
					options: opts.source_doctype,
					get_query: opts.get_query,
					reqd:1
				},
			]
		});
		d.set_primary_action(__('Get Items'), function() {
			var values = d.get_values();
			if(!values)
				return;
			opts.source_name = values[opts.source_doctype];
			d.hide();
			_map();
		})
		d.show();
	} else if(opts.source_name) {
		_map();
	}
}
