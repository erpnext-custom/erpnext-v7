// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Equipment Modifier Tool', {
	setup: function(frm){
		frm.get_field('items').grid.editable_fields = [
			{fieldname: 'equipment', columns: 3},
			{fieldname: 'equipment_number', columns: 2},
			{fieldname: 'equipment_model', columns: 3},
			{fieldname: 'equipment_type', columns: 2},
			{fieldname: 'equipment_category', columns: 2},
		];		
	},
	refresh: function(frm) {
	cur_frm.set_query("current_equipment_model", function() {
        return {
            "filters": {
                "equipment_type": frm.doc.current_equipment_type
            }
        };
    	});
	cur_frm.set_query("new_equipment_model", function() {
        return {
            "filters": {
                "equipment_type": frm.doc.new_equipment_type
            }
        };
        });
	},
	get_equipment: function(frm) {
                return frappe.call({
                        method: "get_equipment",
                        doc: frm.doc,
                        callback: function(r, rt) {
                                frm.refresh_field("items");
                                frm.refresh_fields();
                        }
                });
	}

});
cur_frm.fields_dict['items'].grid.get_field('equipment').get_query = function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	return {
		filters: [
		['Equipment', 'is_disabled', '=', 0],
		['Equipment', 'equipment_type', '=', frm.current_equipment_type],
		['Equipment', 'equipment_model', '=', frm.current_equipment_model]
		]
                }
        };
