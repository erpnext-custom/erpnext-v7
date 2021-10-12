// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Revised Technical Sanction', {
	refresh: function (frm) {
		if (frm.doc.docstatus == 1) {
			frm.add_custom_button("Prepare Bill", function () {
				frappe.model.open_mapped_doc({
					method: "erpnext.rental_management.doctype.revised_technical_sanction.revised_technical_sanction.prepare_bill",
					frm: cur_frm
				});
			});
		}
	},
});

frappe.ui.form.on("Technical Sanction Item", {
	"type": function (frm, cdt, cdn) {
		c = locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn, "service", "");
		frappe.model.set_value(cdt, cdn, "item_name", "");
		frappe.model.set_value(cdt, cdn, "uom", "");
		frappe.model.set_value(cdt, cdn, "rate", "");
		frappe.model.set_value(cdt, cdn, "bsr_item_code", "");
	},
	"service": function (frm, cdt, cdn) {
		c = locals[cdt][cdn];

		cur_frm.add_fetch("service", "item_name", "item_name");
		cur_frm.add_fetch("service", "stock_uom", "uom");

		if (c.type == "Service") {
			frappe.model.get_value("Service", { 'name': c.service }, ['same_rate', 'item_name', "bsr_item_code"],
				function (d) {
					frappe.model.set_value(cdt, cdn, 'bsr_item_code', d.bsr_item_code);
					if (d.same_rate) {
						frappe.model.get_value("Service", { 'name': c.service }, 'cost',
							function (e) {
								frappe.model.set_value(cdt, cdn, 'amount', e.cost);
								frappe.model.set_value(cdt, cdn, 'total', (e.cost * d.qty))
							});
					} else if (frm.doc.region) {
						frappe.model.get_value("BSR Item", { 'parent': c.service, 'region': frm.doc.region }, 'rate',
							function (f) {
								frappe.model.set_value(cdt, cdn, 'amount', f.rate);
								frappe.model.set_value(cdt, cdn, 'total', f.rate * d.qty)
							});
					} else {
						frappe.msgprint("Select a region as the rate is different across region");
					}
				});
		} else if (c.type == "Rate Analysis") {
			frappe.model.get_value("Rate Analysis", { 'name': c.service }, ['total_amount', 'title', 'stock_uom'],
				function (d) {
					frappe.model.set_value(cdt, cdn, 'amount', d.total_amount);
					frappe.model.set_value(cdt, cdn, 'total', d.total_amount * d.qty);
				});
		} else if (c.type == "Item") {
			console.log("Item");
		}
	},
	"qty": function (frm, cdt, cdn) {
		c = locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn, "total", c.amount * c.qty);
		var total = 0;
		for (var i in cur_frm.doc.items) {
			var item = cur_frm.doc.items[i];
			total += item.total;
		}
		cur_frm.set_value("total_amount", total);
	}

});