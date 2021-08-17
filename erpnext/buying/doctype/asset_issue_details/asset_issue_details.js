// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Asset Issue Details', {
	item_code: function(frm) {
		me.frm.set_query("purchase_receipt",function(doc) {
			return {
				query: "erpnext.buying.doctype.asset_issue_details.asset_issue_details.check_item_code",
				filters: {
					'item_code': doc.item_code,
				}
			}
		});
	},
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
	"purchase_receipt": function(frm){
		frappe.call({
			method: "frappe.client.get_value",
			args: {
				parent: "Purchase Receipt",
				doctype: "Purchase Receipt Item",
				fieldname: "rate",
				filters: {
					"parent": frm.doc.purchase_receipt,
					"item_code": frm.doc.item_code
				}
			},
			callback: function(r){
				if(r.message.rate){
					cur_frm.set_value("asset_rate", r.message.rate)
				}
				else{
					frappe.throw("Not working")
				}
			}
		});
	},
	issued_to: function(frm){
		frappe.call({
			method: 'frappe.client.get',
			args: {
				doctype: "Desuup",
				filters: {
					"name": frm.doc.issued_to
				},
				'fields': ['desuup_name']
			},
			callback: function(r){
				cur_frm.set_value("employee_name", r.message.desuup_name);
				cur_frm.refresh_field("employee_name")
			}
		})
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
