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
	},
	item_code: function(frm) {
		frappe.call({
            "method": "frappe.client.get_value",
            args: {
                doctype: "Item",
                fieldname: 'asset_category',
                filters: { name: frm.doc.item_code },
            },
            callback: function (r) {
				if(r.message.asset_category == 'Motor Vehicle' || r.message.asset_category == 'Plant & Machinary'){
					frm.toggle_reqd(['equipment_model'], 1);
					frm.toggle_reqd(['equipment_type'], 1);
				}
				else{
					frm.toggle_reqd(['equipment_model'], 0);
					frm.toggle_reqd(['equipment_type'], 0);
				}
            }
		});
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

frappe.form.link_formatters['Item'] = function(value, doc) {
	return value
}