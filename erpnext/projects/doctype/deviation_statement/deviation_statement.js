// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Deviation Statement', {
	refresh: function(frm) {
		frm.get_docfield("items").allow_bulk_edit = 1;

                frm.get_field('items').grid.editable_fields = [
                        { fieldname: 'boq_code', columns: 1 },
                        { fieldname: 'item', columns: 3 },
                        { fieldname: 'is_group', columns: 1 },
                        { fieldname: 'uom', columns: 1 },
                        { fieldname: 'quantity', columns: 1 },
                        { fieldname: 'rate', columns: 1 },
                        { fieldname: 'amount', columns: 2 }
                ];


	},
	get_boq_list: function(frm) {
                return frm.call({
                        method: "get_boq_lists",
                        doc: frm.doc,
                        callback: function(r) {
                                frm.refresh_field("rts_boq_item");
                                frm.refresh_field("rts_substitution_item");
                                frm.refresh_field("rts_addition_item");
                        },
                        freeze: true,
                        freeze_message: "Loading BOQ Details..... Please Wait"
                });
        },

	rebate_in_percent: function(frm) {
		cal_rebate(frm);
	},
	rebate: function(frm) {
		cal_rebate(frm);
	}
});

var cal_rebate = function(frm) {
        var rebate_amount = frm.doc.rebate
        if(frm.doc.rebate_in_percent) {
                if(frm.doc.rebate > 100) {
                        frappe.msgprint("Rebate % Cannot Exceed 100");
                        cur_frm.set_value("rebate", '');
                        cur_frm.set_value("rebate_amount", '')
                }
                else {
                        rebate_amount = parseFloat(frm.doc.rebate) * 0.01 * parseFloat(frm.doc.amount)
                }
        }
        cur_frm.set_value("rebate_amount", parseFloat(rebate_amount));
	cur_frm.set_value("after_rebate", parseFloat(frm.doc.amount) - parseFloat(rebate_amount));
}
