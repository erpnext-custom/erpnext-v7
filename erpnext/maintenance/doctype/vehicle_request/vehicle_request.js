// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.add_fetch('employee','branch','branch');
frappe.ui.form.on('Vehicle Request', {
	refresh: function(frm) {

	},
	setup: function(frm) {
                frm.get_field('items').grid.editable_fields = [
                        {fieldname: 'employee', columns: 2},
                        {fieldname: 'employee_name', columns: 2},
                        {fieldname: 'designation', columns: 2},
			{fieldname: 'division', columns: 3},
                ];
        },
	"r_status": function(frm) {
		cur_frm.toggle_enable("equipment", frm.r_status !='Approved');
		cur_frm.toggle_enable("operator", frm.r_sttus!='Approved');
		cur_frm.toggle_reqd("equipment", frm.doc.r_status == "Approved");
		cur_frm.toggle_reqd("operator", frm.doc.r_status == "Approved");
		cur_frm.toggle_reqd("rejection_message", frm.doc.r_status == "Rejected");
}
})

//Returns own equipments
cur_frm.fields_dict.equipment.get_query = function(doc) {
	return{
		filters:{
			'not_cdcl': 0,
			'is_disabled': 0,
			'equipment_type': doc.equipment_type,
			'branch':doc.branch,
		}
	}
}

//Returns list of Active Employee
cur_frm.fields_dict['items'].grid.get_field('employee').get_query = function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        return {
                query: "erpnext.controllers.queries.employee_query",
		filters: {'branch': frm.branch}
        }
}
