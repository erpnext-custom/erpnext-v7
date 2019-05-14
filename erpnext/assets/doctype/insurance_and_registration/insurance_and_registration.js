// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Insurance and Registration', {
	refresh: function(frm){
		disable_drag_drop(frm)		
            }, 
	onload: function(frm) {
		disable_drag_drop(frm)
		if (!frm.doc.posting_date) {
			frm.set_value("posting_date", get_today());
		}	
	},
	
	insurance_for: function(frm){
		if (frm.doc.insurance_for == "Equipment"){
			cur_frm.add_fetch("insurance_type", "equipment_type", "equipment_type")
			cur_frm.add_fetch("insurance_type", "equipment_number", "equipment_number")
			cur_frm.add_fetch("insurance_type", "equipment_model", "equipment_model")
			cur_frm.add_fetch("insurance_type", "engine_number", "engine_number")
                        cur_frm.add_fetch("insurance_type", "chassis_number", "chassis_number")
	
		}
		 if(frm.doc.insurance_for == "Project"){
			cur_frm.add_fetch("insurance_type", "branch", "branch");
		
		}
		if(frm.doc.insurance_for == "Asset"){
			cur_frm.add_fetch("insurance_type", "asset_category", "asset_category")
                        cur_frm.add_fetch("insurance_type", "asset_name", "asset_name")
                        cur_frm.add_fetch("insurance_type", "asset_sub_category", "asset_sub_category")
		}
		}
			
	});

function disable_drag_drop(frm) {
        frm.page.body.find('[data-fieldname="in_items"] [data-idx] .data-row').removeClass('sortable-handle');
}






