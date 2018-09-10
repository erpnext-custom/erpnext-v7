// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
cur_frm.add_fetch("asset_code", "branch", "branch")

frappe.ui.form.on('Equipment', {
	onload: function(frm) {
		cur_frm.set_df_property("asset_code", "reqd", 1) 
	},
	refresh: function(frm) {
		cur_frm.set_df_property("engine_number", "read_only", frm.doc.engine_number ? 1 : 0)
		cur_frm.set_df_property("asset_code", "read_only", frm.doc.asset_code ? 1 : 0)
		cur_frm.set_df_property("chassis_number", "read_only", frm.doc.chassis_number ? 1 : 0)
		cur_frm.set_df_property("hsd_type", "read_only", frm.doc.hsd_type ? 1 : 0)
		cur_frm.set_df_property("equipment_category", "read_only", frm.doc.equipment_category ? 1 : 0)
		cur_frm.set_df_property("branch", "read_only", frm.doc.asset_code ? 1 : 0)
		if(!frm.doc.__islocal && in_list(user_roles, "Asset User")) {
			frm.set_df_property("operator", "read_only", 1)
			cur_frm.set_df_property("branch", "read_only", frm.doc.asset_code ? 1 : 0)
			frm.set_df_property("is_disabled", "read_only", 0)
		}
		if(!frm.doc.__islocal && in_list(user_roles, "Mechanical Master")) {
			frm.set_df_property("operator", "read_only", 0)
			frm.set_df_property("branch", "read_only", 1)
			frm.set_df_property("is_disabled", "read_only", 1)
		}
		if(!frm.doc.__islocal && in_list(user_roles, "Fleet User")) {
			frm.set_df_property("operator", "read_only", 0)
			frm.set_df_property("branch", "read_only", 1)
			frm.set_df_property("is_disabled", "read_only", 1)
		}
		if(!frm.doc.__islocal && in_list(user_roles, "Asset Manager")) {
			frm.set_df_property("asset_code", "read_only", 0)
		}
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
    cur_frm.set_query("branch", function() {
	return {
		"filters": {
			"is_disabled": 0
		}
	}
    });
    cur_frm.set_query("fuelbook", function() {
	return {
		"filters": {
			"is_disabled": 0,
			"branch": frm.doc.branch
		}
	}
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

frappe.ui.form.on('Equipment History', {
        before_equipment_history_remove: function(frm, cdt, cdn) {
                doc = locals[cdt][cdn]
                if(!doc.__islocal) {
                        frappe.throw("Cannot delete saved Items")
                }
        }
})

