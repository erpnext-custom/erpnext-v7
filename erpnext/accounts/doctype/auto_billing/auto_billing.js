// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Auto Billing', {
	setup: function(frm){
                frm.get_field('items').grid.editable_fields = [
                        {fieldname: 'schedule_date', columns: 3},
                        {fieldname: 'ref_doc', columns: 3},
                        {fieldname: 'ref_name', columns: 3},
                        {fieldname: 'posted', columns: 1},
                ];
        }
});
