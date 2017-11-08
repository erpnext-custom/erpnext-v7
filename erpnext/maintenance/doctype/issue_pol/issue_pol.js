// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Issue POL', {
	onload: function(frm) {
		if(!frm.doc.date) {
			frm.set_value("date", get_today())
		}
	},
	"items_on_form_rendered": function(frm, grid_row, cdt, cdn) {
		var row = cur_frm.open_grid_row();
		/*if(!row.grid_form.fields_dict.pol_type.value) {
			//row.grid_form.fields_dict.pol_type.set_value(frm.doc.pol_type)
                	row.grid_form.fields_dict.pol_type.refresh()
		}*/
	},
});

cur_frm.add_fetch("equipment", "equipment_number", "equipment_number")

frappe.ui.form.on("Issue POL", "refresh", function(frm) {
	cur_frm.set_query("tanker", function() {
		return {
			filters:[['branch', "=", frm.doc.branch], ['equipment_type', '=', 'Fuel Tanker']]
		}
	})
	frm.fields_dict['items'].grid.get_field('equipment').get_query = function(doc, cdt, cdn) {
		doc = locals[cdt][cdn]
		return {
			filters: {
				'hsd_type': frm.doc.pol_type, 
				"is_disabled": 0, 
			}
		}
	}
})
