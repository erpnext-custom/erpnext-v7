// copy from cdcl
// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
//  this doctype is modified by Birendra as per requirement of client

frappe.ui.form.on('Asset Issue Details', {
	refresh: function(frm) {

	},
	"qty": function(frm){
		if(frm.doc.asset_rate){
	 		frm.set_value("amount", frm.doc.qty * frm.doc.asset_rate);
		}
	},
	"asset_rate": function(frm){
		if(frm.doc.qty){
	 		frm.set_value("amount", frm.doc.qty * frm.doc.asset_rate);
		}
	}
});

cur_frm.fields_dict['item_code'].get_query = function(doc) {
        return {
               "filters": {
                       "item_group": "Fixed Asset"
                }
        }
}

cur_frm.add_fetch("item_code", "item_name", "item_name");
