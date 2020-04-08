cur_frm.add_fetch("vehicle", "drivers_name", "driver_name");
cur_frm.add_fetch("vehicle", "contact_no", "driver_mobile_no");

frappe.ui.form.on('Vehicle Update', {
        refresh: function(frm) {
		custom.apply_default_settings(frm);
        },
        "user": function(frm) {
                if(frm.doc.user){
                        cur_frm.set_query("vehicle", function() {
                                return {
                                    "filters": {
                                        "user": frm.doc.user,
					"vehicle_status": "Active",
                                    }
                                };
                         });
                }
        },
});
