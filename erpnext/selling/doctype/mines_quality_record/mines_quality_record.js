// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Mines Quality Record', {
	refresh: function(frm) {

	}
});

cur_frm.add_fetch("item_code", "item_name", "item_name");

frappe.ui.form.on("Mines Quality Record", "onload", function(frm) {
	cur_frm.set_query("transporter_name", function() {
		return {
			"filters": {
				"vendor_group": "Transporter"
			}
		};
	});
});

frappe.ui.form.on("Mines Quality Record Details","sales_invoice", function(frm, cdt, cdn) {
	var record = frappe.get_doc(cdt, cdn);
        frappe.call({
            method: "erpnext.accounts.doctype.sales_invoice.sales_invoice.get_invoice_details",
            args: {
                "item_code": frm.doc.item_code,
                "invoice": record.sales_invoice
            },
            callback: function(r)  {
                if(r.message) {
                      frappe.model.set_value(cdt, cdn, "deliver_note", r.message[0])
                      frappe.model.set_value(cdt, cdn, "vehicle_no", r.message[1])
                      frappe.model.set_value(cdt, cdn, "sample_collected_on", r.message[2])
                }
            }
        })
})
