// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Deviation Item Statement', {
	refresh: function(frm) {
		frm.get_field('items').grid.editable_fields = [
                        { fieldname: 'boq_code', columns: 2 },
                        { fieldname: 'item', columns: 3 },
                        { fieldname: 'uom', columns: 1 },
                        { fieldname: 'quantity', columns: 1 },
                        { fieldname: 'amount', columns: 2 },
                        { fieldname: 'rate', columns: 3 }
                ];
	}
});
