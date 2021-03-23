// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('CRM Product Requisition', {
	refresh: function(frm) {

	},
	product_category: function(frm) {
		if(cur_frm.doc.product_category == "" || cur_frm.doc.product_category == null){
			cur_frm.set_value("item",null);
			cur_frm.set_value("item_name",null);
			cur_frm.set_value("qty",null);
			cur_frm.set_value("uom",null);
		}
	},
	item: function(frm) {
		if(cur_frm.doc.item == "" || cur_frm.doc.item == null){
			cur_frm.set_value("item_name",null);
			cur_frm.set_value("qty",null);
			cur_frm.set_value("uom",null);
		}
	}
});

frappe.ui.form.on('CRM Product Requisition','refresh',function(frm) {
	cur_frm.set_query('customer_id', function(){
		return{
			"query": "erpnext.controllers.queries.get_crm_users"
		}
	})
	cur_frm.set_query('item', function(){
		return{
			"query": "erpnext.controllers.queries.get_pc_items",
			"filters": { "product_category":cur_frm.doc.product_category}
		}
	})

});
