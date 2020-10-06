// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Tenant Flat Transfer Tool', {
	refresh: function (frm) {
		if (frm.doc.floor_area_change == 1) {
			frm.toggle_display("new_tenant_information", 0)
			frm.toggle_display("personal_detail", 0)
		}
	},
	owner_ship_transfer: function (frm) {
		console.log('ownership', frm.doc.owner_ship_transfer);
		cur_frm.toggle_reqd("new_citizen_id", frm.doc.owner_ship_transfer);
		frm.toggle_reqd("new_ministry_agency", frm.doc.owner_ship_transfer);
		frm.toggle_reqd("new_department", frm.doc.owner_ship_transfer);
		frm.toggle_reqd("transfer_date", frm.doc.owner_ship_transfer);
		frm.toggle_reqd("new_tenant_name", frm.doc.owner_ship_transfer);

		if (frm.doc.owner_ship_transfer) {
			if (frm.doc.floor_area_change) {
				frm.set_value("floor_area_change", 0);
				frm.toggle_display("new_tenant_information", 1)
				frm.toggle_display("personal_detail", 1)
				frm.toggle_display("new_floor_area", 0)

			}
		} else {
			frm.set_value("floor_area_change", 1);
			frm.toggle_display("new_tenant_information", 0)
			frm.toggle_display("personal_detail", 0)
			frm.toggle_display("new_floor_area", 1)
		}

	},

	floor_area_change: function (frm) {
		if (frm.doc.floor_area_change) {
			if (frm.doc.owner_ship_transfer) {
				frm.set_value("owner_ship_transfer", 0);
				frm.toggle_display("new_tenant_information", 0)
				frm.toggle_display("personal_detail", 0)
				frm.toggle_display("new_floor_area", 1)
			}
		} else {
			frm.set_value("owner_ship_transfer", 1);
			frm.toggle_display("new_tenant_information", 1)
			frm.toggle_display("personal_detail", 1)
			frm.toggle_display("new_floor_area", 0)
		}
	},
});
