// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Item Register Tool', {
	onload: function(frm) {
		if(!frm.doc.posting_date)
                {
                        frm.set_value("posting_date", get_today())
                }

	},
"purpose": function(frm){	
		if(frm.doc.purpose === "Remove"){
		frm.set_df_property('removal_reason', 'reqd', purpose = 'Remove' ? 1 : 0)
}
else if(frm.doc.purpose === "Transfer") {
                frm.set_df_property('to_employee', 'reqd', purpose = 'Transfer' ? 1 : 0)
}
}, 

 refresh: function(frm) {
                if(frm.doc.docstatus===1){
                        frm.add_custom_button(__('Items Register Ledger'), function(){
                                frappe.route_options = {
                                        ref_doc: frm.doc.name,
                                        from_date: frm.doc.posting_date,
                                        to_date: frm.doc.posting_date,
                                        branch: frm.doc.branch,
                                        option: "Summarized"
                                };
                                frappe.set_route("query-report", "Items Register Ledger");
                        }, __("View"));

                        frm.add_custom_button(__('Consumable Register Entry'), function(){
                                frappe.route_options = {
                                        ref_doc: frm.doc.name
                                };
                                frappe.set_route("List", "Consumable Register Entry");
                        }, __("View"));

                }}

});
cur_frm.add_fetch("item_code", "item_name", "item_name");
cur_frm.fields_dict['from_employee'].get_query = function(frm){
         return {
                filters: [
                     ['Employee', 'branch', '=', cur_frm.doc.branch]

                ]
             }
        }

