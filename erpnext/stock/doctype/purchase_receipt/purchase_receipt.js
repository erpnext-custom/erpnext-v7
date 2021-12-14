// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

{% include 'erpnext/buying/doctype/purchase_common/purchase_common.js' %};

frappe.provide("erpnext.stock");

frappe.ui.form.on("Purchase Receipt", {
	onload: function(frm) {
		// default values for quotation no
		var qa_no = frappe.meta.get_docfield("Purchase Receipt Item", "qa_no");
		qa_no.get_route_options_for_new_doc = function(field) {
			if(frm.is_new()) return;
			var doc = field.doc;
			return {
				"inspection_type": "Incoming",
				"purchase_receipt_no": frm.doc.name,
				"item_code": doc.item_code,
				"description": doc.description,
				"item_serial_no": doc.serial_no ? doc.serial_no.split("\n")[0] : null,
				"batch_no": doc.batch_no
			}
		}

		$.each(["warehouse", "rejected_warehouse"], function(i, field) {
			frm.set_query(field, "items", function() {
				return {
					filters: [
                                                ["Warehouse", "company", "in", ["", cstr(frm.doc.company)]],
                                                ["Warehouse", "is_group", "=", 0]
                                        ]
				}
			})
		})

		frm.set_query("supplier_warehouse", function() {
			return {
				filters: [
                                                ["Warehouse", "company", "in", ["", cstr(frm.doc.company)]],
                                                ["Warehouse", "is_group", "=", 0]
                                        ]
			}
		})
	},

	freight_and_insurance_charges: function(frm) {
		calculate_discount(frm)
	},

	discount: function(frm) {
		calculate_discount(frm)
	},

	other_charges: function(frm) {
		calculate_discount(frm)
	},

	tax: function(frm) {
		calculate_discount(frm)
	},
});

function calculate_discount(frm) {
	cur_frm.set_value("total_add_ded", frm.doc.freight_and_insurance_charges + frm.doc.other_charges + frm.doc.tax - frm.doc.discount)
	cur_frm.set_value("discount_amount", -frm.doc.freight_and_insurance_charges - frm.doc.other_charges - frm.doc.tax + frm.doc.discount)
	cur_frm.refresh_field("discount_amount")
	cur_frm.refresh_field("total_add_ded")
}

erpnext.stock.PurchaseReceiptController = erpnext.buying.BuyingController.extend({
	refresh: function() {
		this._super();
		if(this.frm.doc.docstatus===1) {
			this.show_stock_ledger();
			if (cint(frappe.defaults.get_default("auto_accounting_for_stock"))) {
				this.show_general_ledger();
			}
		}

		if(!this.frm.doc.is_return && this.frm.doc.status!="Closed") {
			/*if(this.frm.doc.docstatus==0) {
				cur_frm.add_custom_button(__('Purchase Order'),
					function() {
						erpnext.utils.map_current_doc({
							method: "erpnext.buying.doctype.purchase_order.purchase_order.make_purchase_receipt",
							source_doctype: "Purchase Order",
							get_query_filters: {
								supplier: cur_frm.doc.supplier || undefined,
								docstatus: 1,
								status: ["!=", "Closed"],
								per_received: ["<", 99.99],
								company: cur_frm.doc.company
							}
						})
				}, __("Get items from"));
			} */

			if(this.frm.doc.docstatus == 1 && this.frm.doc.status!="Closed") {
				/*if (this.frm.has_perm("submit")) {
					cur_frm.add_custom_button(__("Close"), this.close_purchase_receipt, __("Status"))
				}*/

				if (this.frm.doc.status != "Completed") {
					cur_frm.add_custom_button(__('Return'), this.make_purchase_return, __("Make"));
				}

				if(flt(this.frm.doc.per_billed) < 100) {
					cur_frm.add_custom_button(__('Invoice'), this.make_purchase_invoice, __("Make"));
				}
				cur_frm.add_custom_button(__('Asset Issue Entry'), this.make_asset_issue_entry, __('Make'));

				cur_frm.page.set_inner_btn_group_as_primary(__("Make"));
			}
		}


		/*if(this.frm.doc.docstatus==1 && this.frm.doc.status === "Closed" && this.frm.has_perm("submit")) {
			cur_frm.add_custom_button(__('Reopen'), this.reopen_purchase_receipt, __("Status"))
		} */

		this.frm.toggle_reqd("supplier_warehouse", this.frm.doc.is_subcontracted==="Yes");
	},

	make_purchase_invoice: function() {
		frappe.model.open_mapped_doc({
			method: "erpnext.stock.doctype.purchase_receipt.purchase_receipt.make_purchase_invoice",
			frm: cur_frm
		})
	},

	make_purchase_return: function() {
		frappe.model.open_mapped_doc({
			method: "erpnext.stock.doctype.purchase_receipt.purchase_receipt.make_purchase_return",
			frm: cur_frm
		})
	},

	make_asset_issue_entry: function() {
		var doc = cur_frm.doc;
		var dialog = new frappe.ui.Dialog({
			title: __("For Issuing Asset"),
			fields: [
				{	"fieldtype": "Select",
					"label": __("Material Name"),
					"fieldname": "item_name",
					"options": doc.items.map(d => d.item_name),
					"reqd": 1 
				},
				{	"fieldtype": "Button", "label": __('Issue Asset'),
					"fieldname": "make_asset_issue_entry", "cssClass": "btn-primary"
				},
			]
		});

		dialog.fields_dict.make_asset_issue_entry.$input.click(function() {
			
			var args = dialog.get_values();
			frappe.call({
				method:'frappe.client.get_value',
				args:{
					'doctype':'Item',
					fieldname:"is_fixed_asset",
					filters: {
						"item_name": args.item_name,
						"disabled": 0
					}
				},
				callback:(r)=>{
					if ( !r.message.is_fixed_asset){
						frappe.msgprint('Item selected is not a fixed asset')
						dialog.hide();
						return;
					}

					if(!args) return;
					dialog.hide();

					let business_activity = ''
					let item_code = ''
					let asset_rate = ''
					cur_frm.doc.items.map(d => {
						if (d.item_name == args.item_name){
							business_activity = d.business_activity;
							item_code = d.item_code;
							asset_rate = d.rate;
						}
					})

				var new_doc = frappe.model.get_new_doc('Asset Issue Details');
					new_doc.branch = cur_frm.doc.branch;
					new_doc.business_activity = business_activity;
					new_doc.entry_date = new Date().toJSON().slice(0,10).replace(/-/g,'-');
					new_doc.item_code = item_code;
					new_doc.purchase_receipt = cur_frm.docname;
					new_doc.asset_rate = asset_rate
					new_doc.qty = 1;
					new_doc.amount = asset_rate * new_doc.qty
					frappe.set_route('Form', 'Asset Issue Details', new_doc.name);
					
				}
			})
		});
		dialog.show()
	},

	close_purchase_receipt: function() {
		cur_frm.cscript.update_status("Closed");
	},

	reopen_purchase_receipt: function() {
		cur_frm.cscript.update_status("Submitted");
	}

});

// for backward compatibility: combine new and previous states
$.extend(cur_frm.cscript, new erpnext.stock.PurchaseReceiptController({frm: cur_frm}));

cur_frm.cscript.update_status = function(status) {
	frappe.ui.form.is_saving = true;
	frappe.call({
		method:"erpnext.stock.doctype.purchase_receipt.purchase_receipt.update_purchase_receipt_status",
		args: {docname: cur_frm.doc.name, status: status},
		callback: function(r){
			if(!r.exc)
				cur_frm.reload_doc();
		},
		always: function(){
			frappe.ui.form.is_saving = false;
		}
	})
}

cur_frm.fields_dict['supplier_address'].get_query = function(doc, cdt, cdn) {
	return {
		filters: { 'supplier': doc.supplier}
	}
}

cur_frm.fields_dict['contact_person'].get_query = function(doc, cdt, cdn) {
	return {
		filters: { 'supplier': doc.supplier }
	}
}

cur_frm.cscript.new_contact = function() {
	tn = frappe.model.make_new_doc_and_get_name('Contact');
	locals['Contact'][tn].is_supplier = 1;
	if(doc.supplier)
		locals['Contact'][tn].supplier = doc.supplier;
	frappe.set_route('Form', 'Contact', tn);
}

cur_frm.fields_dict['items'].grid.get_field('project').get_query = function(doc, cdt, cdn) {
	return {
		filters: [
			['Project', 'status', 'not in', 'Completed, Cancelled']
		]
	}
}

cur_frm.fields_dict['items'].grid.get_field('batch_no').get_query= function(doc, cdt, cdn) {
	var d = locals[cdt][cdn];
	if(d.item_code) {
		return {
			filters: {'item': d.item_code}
		}
	}
	else
		msgprint(__("Please enter Item Code."));
}

cur_frm.cscript.select_print_heading = function(doc, cdt, cdn) {
	if(doc.select_print_heading)
		cur_frm.pformat.print_heading = doc.select_print_heading;
	else
		cur_frm.pformat.print_heading = "Purchase Receipt";
}

cur_frm.fields_dict['select_print_heading'].get_query = function(doc, cdt, cdn) {
	return {
		filters: [
			['Print Heading', 'docstatus', '!=', '2']
		]
	}
}

cur_frm.fields_dict.items.grid.get_field("qa_no").get_query = function(doc) {
	return {
		filters: {
			'docstatus': 1
		}
	}
}

cur_frm.fields_dict['items'].grid.get_field('bom').get_query = function(doc, cdt, cdn) {
	var d = locals[cdt][cdn]
	return {
		filters: [
			['BOM', 'item', '=', d.item_code],
			['BOM', 'is_active', '=', '1'],
			['BOM', 'docstatus', '=', '1']
		]
	}
}

cur_frm.cscript.on_submit = function(doc, cdt, cdn) {
	if(cint(frappe.boot.notification_settings.purchase_receipt))
		cur_frm.email_doc(frappe.boot.notification_settings.purchase_receipt_message);
}

frappe.provide("erpnext.buying");

frappe.ui.form.on("Purchase Receipt", "is_subcontracted", function(frm) {
	if (frm.doc.is_subcontracted === "Yes") {
		erpnext.buying.get_default_bom(frm);
	}
	frm.toggle_reqd("supplier_warehouse", frm.doc.is_subcontracted==="Yes");
});

frappe.ui.form.on("Purchase Receipt","items_on_form_rendered", function(frm, grid_row, cdt, cdn) {
	var grid_row = cur_frm.open_grid_row();
        frappe.call({
            method: "erpnext.stock.doctype.purchase_receipt.purchase_receipt.get_item_group",
            args: {
                "item_code": grid_row.grid_form.fields_dict.item_code.value
            },
            callback: function(r)  {
                if(r.message && r.message == 'Services Works') {
                      grid_row.grid_form.fields_dict.rate.df.read_only = false
                      grid_row.grid_form.fields_dict.rate.refresh()
                }
                else {
                      grid_row.grid_form.fields_dict.rate.df.read_only = true
                      grid_row.grid_form.fields_dict.rate.refresh()
                }
            }
        })
})

//cost Center
cur_frm.fields_dict['items'].grid.get_field('cost_center').get_query = function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        return {
                query: "erpnext.controllers.queries.filter_branch_cost_center",
                filters: {'branch': frm.branch}
        }
}

