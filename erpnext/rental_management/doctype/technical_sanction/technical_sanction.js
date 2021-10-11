// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/*cur_frm.add_fetch("item","item_name","item_name");
cur_frm.add_fetch("item","stock_uom","uom");
*/
frappe.ui.form.on('Technical Sanction', {
	setup: function (frm) {
		frm.get_docfield("detail_measurement").allow_bulk_edit = 1;
	},
	onload: function (frm) {
		frm.set_query("supplier", function () {
			return {
				"filters": {
					"vendor_group": "Contractor",
					//"vendor_type" : "GEP"
				}
			}
		});
	},
	refresh: function (frm) {
		if (frm.doc.docstatus == 1 && !frm.doc.bill && frm.doc.party && frm.doc.party_type) {
			frm.add_custom_button("Make Advance", function () {
				frappe.model.open_mapped_doc({
					method: "erpnext.rental_management.doctype.technical_sanction.technical_sanction.make_advance",
					frm: cur_frm
				});
			});
		}
		if (frm.doc.docstatus == 1 && !frm.doc.revised_technical_sanction && !frm.doc.bill) {
			frm.add_custom_button("Prepare RTS", function () {
				frappe.model.open_mapped_doc({
					method: "erpnext.rental_management.doctype.technical_sanction.technical_sanction.prepare_rts",
					frm: cur_frm
				});
			});
			if (!frm.doc.bill) {
				frm.add_custom_button("Prepare Bill", function () {
					frappe.model.open_mapped_doc({
						method: "erpnext.rental_management.doctype.technical_sanction.technical_sanction.prepare_bill",
						frm: cur_frm
					});
				});
			}
		}
	},
	"get_items": function (frm) {
		return frappe.call({
			method: "get_technical_sanction_items",

			doc: frm.doc,
			callback: function (r, rt) {
				frm.refresh_field("material_items");
				frm.refresh_fields();
			}
		});
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
			frappe.model.get_value("Rate Analysis", { 'name': c.service }, ['total_amount', 'title', 'uom'],
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

frappe.ui.form.on("Technical Sanction Materials", {
	"item_code": function (frm, cdt, cdn) {
		c = locals[cdt][cdn];
	}
});

frappe.ui.form.on("Technical Sanction Detail Item", {
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
			frappe.model.get_value("Rate Analysis", { 'name': c.service }, ['total_amount', 'title', 'uom'],
				function (d) {
					frappe.model.set_value(cdt, cdn, 'amount', d.total_amount);
					frappe.model.set_value(cdt, cdn, 'total', d.total_amount * d.qty);
				});
		} else if (c.type == "Item") {
			console.log("Item");
		}
	},
	"breath": function (frm, cdt, cdn) {
		calculate_quantity(frm, cdt, cdn)
	},
	"length": function (frm, cdt, cdn) {
		calculate_quantity(frm, cdt, cdn)
	},
	"height": function (frm, cdt, cdn) {
		calculate_quantity(frm, cdt, cdn)
	},
	"coef": function (frm, cdt, cdn) {
		calculate_quantity(frm, cdt, cdn)
	},
	"number": function (frm, cdt, cdn) {
		calculate_quantity(frm, cdt, cdn)
	},

});
function calculate_quantity(frm, cdt, cdn) {
	child = locals[cdt][cdn]
	if (child.breath && child.length) {
		child.qty = child.breath * child.length
		let height = 1
		let coef = 1
		let number = 1

		if (child.height) {
			height = child.height
		}
		if (child.coef) {
			coef = child.coef
		}
		if (child.number) {
			number = child.number
		}
		child.qty = child.breath * child.length * height * coef * number
		child.qty = child.qty.toFixed(2)
	}
	frm.refresh_fields()
}


/*
cur_frm.fields_dict['service'].get_query = function(doc, cdt, cdn){
	return {
		"filters":{}
	}
} */
