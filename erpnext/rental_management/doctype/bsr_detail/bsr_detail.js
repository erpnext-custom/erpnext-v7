// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt


frappe.ui.form.on('BSR Detail', {
	refresh: function(frm) {

	},
	"type": function(frm){
		frm.set_value("item","");
		frm.set_value("item_name","");
		frm.set_value("bsr_code","");
		frm.set_value("category","");
		frm.set_value("sub_category","");
		frm.set_value("uom","");

	},
	"item": function(frm){
		frm.add_fetch("item", "bsr_item_code","bsr_code");
		frm.add_fetch("item", "item_group","category");
		frm.add_fetch("item", "item_sub_group","sub_category");
		frm.add_fetch("item", "stock_uom","uom");
		frm.add_fetch("item", "item_name","item_name");
	}
});
