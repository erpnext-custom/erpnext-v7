// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
// cur_frm.add_fetch("asset_code", "branch", "branch")
// cur_frm.add_fetch("hsd_type", "item_name", "item_name")
// cur_frm.add_fetch("supplier", "supplier_name", "owner_name")
// cur_frm.add_fetch("supplier", "bank_name_new", "bank_name")
// cur_frm.add_fetch("supplier", "bank_branch", "bank_branch")
// cur_frm.add_fetch("supplier", "bank_account_type", "bank_account_type")
// cur_frm.add_fetch("supplier", "account_number", "account_number")
// cur_frm.add_fetch("supplier", "ifs_code", "ifs_code")
// cur_frm.add_fetch("supplier", "vendor_tpn_no", "vendor_tpn_number")

frappe.ui.form.on('Equipment', {
	onload: function(frm) {
		//cur_frm.set_df_property("asset_code", "reqd", 1) 
		frm.set_query("asset_code", function() {
			return {
				"filters": {
					"asset_category":[ 'in', ['Motor Vehicle']]
				}
			};
		});
		frm.set_query("supplier", function(){
			return {
				"filters": {
					"vendor_group": [ 'in', ['Transporter']]
				}
			}
		});

		frm.set_query("asset_code", function(){
			return {
				"filters": {
					"docstatus": [ '=', 1]
				}
			}
		});
	},
	setup: function(frm){
		frm.get_field('model_items').grid.editable_fields = [
		{fieldname: 'equipment_type', columns: 3},
		{fieldname: 'equipment_model', columns: 3},
		{fieldname: 'modified_date', columns: 3},
		{fieldname: 'ref_doc', columns:3},
        ];
        },
	refresh: function(frm) {
		cur_frm.set_df_property("engine_number", "read_only", frm.doc.engine_number ? 1 : 0)
		cur_frm.set_df_property("asset_code", "read_only", frm.doc.asset_code ? 1 : 0)
		cur_frm.set_df_property("chassis_number", "read_only", frm.doc.chassis_number ? 1 : 0)
		cur_frm.set_df_property("hsd_type", "read_only", frm.doc.hsd_type ? 1 : 0)
		//cur_frm.set_df_property("branch", "read_only", frm.doc.branch ? 1 : 0)
		cur_frm.set_df_property("fuelbook", "read_only", frm.doc.fuelbook ? 1 : 0)
		cur_frm.set_df_property("business_activity", "read_only", frm.doc.business_activity ? 1 : 0)
		cur_frm.set_df_property("equipment_category", "read_only", frm.doc.equipment_category ? 1 : 0)
		if(frm.doc.not_cdcl == 1) {
                        cur_frm.set_df_property("branch", "read_only", 0)
                }  
	},
	// supplier:function(frm){
	// 	cur_frm.set_df_property("owner_name", "read_only", frm.doc.supplier ? 1 : 0)
	// 	cur_frm.set_df_property("bank_name", "read_only", frm.doc.supplier ? 1 : 0)
	// 	cur_frm.set_df_property("bank_branch", "read_only", frm.doc.supplier ? 1 : 0)
	// 	cur_frm.set_df_property("bank_account_type", "read_only", frm.doc.supplier ? 1 : 0)
	// 	cur_frm.set_df_property("account_number", "read_only", frm.doc.supplier ? 1 : 0)
	// 	cur_frm.set_df_property("ifs_code", "read_only", frm.doc.supplier ? 1 : 0)
	// 	cur_frm.set_df_property("vendor_tpn_number", "read_only", frm.doc.supplier ? 1 : 0)
	// },
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
		if(frm.doc.not_cdcl == 1) {
                    cur_frm.set_df_property("branch", "read_only", 0)
                }
                else {
                    cur_frm.set_df_property("branch", "read_only", 1)
                }

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
    cur_frm.set_query("hsd_type", function() {
        return {
            "filters": {
		"is_pol_item": 1,
		"is_hsd_item": 1,
		"disabled": 0
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

/*frappe.ui.form.on('Equipment History', {
        before_equipment_history_remove: function(frm, cdt, cdn) {
                doc = locals[cdt][cdn]
                if(!doc.__islocal) {
                        frappe.throw("Cannot delete saved Items")
                }
        }
})
*/
