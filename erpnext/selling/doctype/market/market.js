// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Market', {
	refresh: function(frm) {

	}
});

cur_frm.cscript.refresh = function(doc, cdt, cdn) {
        cur_frm.cscript.set_root_readonly(doc);
}

cur_frm.cscript.set_root_readonly = function(doc) {
        // read-only for root territory
        if(!doc.parent_market) {
                cur_frm.set_read_only();
                cur_frm.set_intro(__("This is a root Market and cannot be edited."));
        } else {
                cur_frm.set_intro(null);
        }
}

//get query select territory
cur_frm.fields_dict['parent_market'].get_query = function(doc,cdt,cdn) {
        return{
                filters:[
                        ['Market', 'is_group', '=', 1],
                        ['Market', 'name', '!=', doc.market_name]
                ]
        }
}
