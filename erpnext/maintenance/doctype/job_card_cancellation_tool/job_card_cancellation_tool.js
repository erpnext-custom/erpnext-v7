// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Job Card Cancellation Tool', {
	get_stock: function(frm) {
			frm.refresh_field("items");
			frm.refresh_field();
			return frappe.call({
                        	method: "get_stock_items",
                        	doc: frm.doc,
                        	callback: function(r, rt) {
                                	frm.refresh_field("items");
                                	frm.refresh_fields();
                        }
                });

		

	}
});

                                      

                                         



