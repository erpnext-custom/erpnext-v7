
// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
frappe.ui.form.on('Consolidated Invoice', {
	refresh: function(frm) {
		if(!frm.doc.posting_date) {
			frm.set_value("posting_date", get_today())
		}

		if(frm.doc.items && frm.doc.docstatus==1) {
			if(frm.doc.payment_entry){
				frm.add_custom_button(__('Payment Entry'), function(){
					frappe.route_options = {
						"consolidated_invoice_id": frm.docname,
					};
					frappe.set_route("List", "Payment Entry");
				}, __("View"));
			} else {
				frm.add_custom_button("Receive Payment", function() {
					frappe.model.open_mapped_doc({
						method: "erpnext.selling.doctype.consolidated_invoice.consolidated_invoice.make_payment_entry",
						frm: cur_frm
					})
				}, __("Payment"));
			}
		}

	},
	to_date: function(frm) {
		get_invoices(frm);
	},
	from_date: function(frm) {
		get_invoices(frm);
	},
	customer: function(frm){
		get_invoices(frm);
	},
	branch: function(frm){
		if(frm.doc.branch != null && frm.doc.branch != undefined && frm.doc.branch != ""){
			frappe.call({
				method: "frappe.client.get_value",
				args: {
					doctype: "Branch", 
					fieldname:"cost_center",
					filters: {
						name: frm.doc.branch
					}
				},
				callback: function(r) {
					if(r.message.cost_center) {
						cur_frm.set_value("cost_center", r.message.cost_center)
					}
				}
			})
		}	
	},
	cost_center: function(frm){
		get_invoices(frm);
	},
	sales_order: function(frm) {
		if(frm.doc.cost_center){
		frm.fields_dict['sales_order'].get_query = function(doc) {
					return {
						query:"erpnext.controllers.queries.filter_cost_center_branch",
						filters: {
							"cost_center": frm.doc.cost_center
						}
					};
			}
		}
		if(frm.doc.sales_order){
			frappe.call({
				method:"frappe.client.get_value",
				args: {
				doctype:"Sales Order",
				filters: {
				name: cur_frm.doc.sales_order
				},
				fieldname:["customer"]
				},
				callback: function(r) {
					if(r.message.customer != null)
					{
						frm.set_value("customer",r.message.customer)
					}
					frm.refresh_fields();
				}
			})
		}
	}
});

// cur_frm.add_fetch("item_price", "price_list_rate", "rate")
// cur_frm.add_fetch("item_code", "stock_uom", "uom")
// cur_frm.add_fetch("item_code", "item_name", "item_name")

function get_invoices(frm) {
	cur_frm.clear_table("items");
	cur_frm.set_value("total_amount", null)
	cur_frm.set_value("quantity", null)
	cur_frm.refresh_fields("items");
	if(frm.doc.from_date && frm.doc.to_date && frm.doc.customer && frm.doc.cost_center){
		frappe.call({
			method: "erpnext.selling.doctype.consolidated_invoice.consolidated_invoice.get_invoices",
			args: {
				"name": frm.doc.name,
				"from_date": frm.doc.from_date,
				"to_date": frm.doc.to_date,
				"customer": frm.doc.customer,
				"cost_center": frm.doc.cost_center
			},
			callback: function(r) {
				if(r.message) {
					var total_amount = 0;
					var total_qty = 0;
					cur_frm.clear_table("items");
					r.message.forEach(function(invoice) {
						var row = frappe.model.add_child(cur_frm.doc, "Consolidated Invoice Item", "items");
						row.invoice_no = invoice['name']
						row.sales_order = invoice['sales_order']
						row.amount = invoice['amount']
						row.cost_of_goods = invoice['cost_of_goods']
						row.qty = invoice['qty']
						row.transportation_cost = invoice['transportation_charges']
						row.loading_cost = invoice['loading_cost']
						row.challan_cost = invoice['challan_cost']
						row.date = invoice['posting_date']
						row.due_date = invoice['due_date']
						row.delivery_note = invoice['delivery_note']
						refresh_field("items");

						total_amount += invoice['outstanding_amount']
						total_qty += invoice['accepted_qty']
					});

					cur_frm.set_value("total_amount", total_amount)
					cur_frm.set_value("quantity", total_qty)
				}
				cur_frm.refresh_fields("items");
			},
			freeze: true,
            freeze_message: '<span style="color:white; background-color: red; padding: 10px 50px; border-radius: 5px;">Fetching Invoices...</span>',
		});
	}
}
