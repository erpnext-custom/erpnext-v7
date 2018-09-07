// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('HSD Adjustment', {
	setup: function(frm) {
                frm.get_docfield("items").allow_bulk_edit = 1;
        },	
	get_equipments: function(frm) {
		return frappe.call({
			method: "get_equipments",
			doc: frm.doc,
			callback: function(r, rt) {
				frm.refresh_field("items");
				frm.refresh_fields();
			},
                        freeze: true,
                        freeze_message: "Loading Equipment Data.... Please Wait!"
		});
	}
});

cur_frm.fields_dict['items'].grid.get_field('equipment').get_query = function(frm, cdt, cdn) {
	return {
		"filters": {
			"branch": frm.branch
		    } 
	}
}

