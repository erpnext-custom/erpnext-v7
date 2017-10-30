// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Equipment', {
	onload: function(frm) {
		cur_frm.set_df_property("asset_code", "reqd", 1) 
	},
	refresh: function(frm) {
		cur_frm.set_df_property("engine_number", "read_only", frm.doc.engine_number ? 1 : 0)
		cur_frm.set_df_property("chassis_number", "read_only", frm.doc.chassis_number ? 1 : 0)
	},
	validate: function(frm) {
		if (frm.doc.operators) {
			frm.doc.operators.forEach(function(d) { 
				frm.set_value("current_operator", d.operator)
			})
			frm.refresh_field("current_operator")
		}
	},
	not_cdcl: function(frm) {
		cur_frm.toggle_reqd("asset_code", frm.doc.not_cdcl == 0) 
	}
});

frappe.ui.form.on("Equipment", "refresh", function(frm) {
    cur_frm.set_query("equipment_model", function() {
        return {
            "filters": {
		"equipment_type": frm.doc.equipment_type
            }
        };
    });
    cur_frm.set_query("equipment_type", function() {
        return {
            "filters": {
		"equipment_category": frm.doc.equipment_category
            }
        };
    });
})

cur_frm.fields_dict['operators'].grid.get_field('operator').get_query = function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	if (d.employee_type == "Employee") {
		return {
			filters: [
			['Employee', 'designation', 'in', ['Operator', 'Driver']],
			['Employee', 'branch', '=', frm.branch],
			['Employee', 'status', '=', 'Active']
			]
		}
	}
	else {
		return {
			filters: [
				['Muster Roll Employee', 'branch', '=', frm.branch],
				['Muster Roll Employee', 'status', '=', 'Active']
			]
		}
	}
}
