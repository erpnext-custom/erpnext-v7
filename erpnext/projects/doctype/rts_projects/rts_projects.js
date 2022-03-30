// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('RTS Projects', {
	refresh: function(frm) {
		frm.get_field('rts_boq_item').grid.editable_fields = [
                        { fieldname: 'boq_code', columns: 2 },
                        { fieldname: 'item', columns: 3 },
                        { fieldname: 'uom', columns: 1 },
                        { fieldname: 'quantity', columns: 1 },
                        { fieldname: 'amount', columns: 2 },
                        { fieldname: 'rate', columns: 3 }
                ];

		frm.get_field('rts_addition_item').grid.editable_fields = [
                        { fieldname: 'boq_code', columns: 2 },
                        { fieldname: 'item', columns: 3 },
                        { fieldname: 'uom', columns: 1 },
                        { fieldname: 'quantity', columns: 1 },
                        { fieldname: 'amount', columns: 2 },
                        { fieldname: 'rate', columns: 3 }
                ];


		frm.get_field('rts_substitution_item').grid.editable_fields = [
                        { fieldname: 'boq_code', columns: 2 },
                        { fieldname: 'item', columns: 3 },
                        { fieldname: 'uom', columns: 1 },
                        { fieldname: 'quantity', columns: 1 },
                        { fieldname: 'amount', columns: 2 },
                        { fieldname: 'rate', columns: 3 }
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


var calc_initial_amount = function (frm) {
        var bi = frm.doc.rts_boq_item || [];
        var initial_amount = 0.0;

        for (var i = 0; i < bi.length; i++) {
                if (bi[i].amount && !bi[i].is_group) {
                        initial_amount += parseFloat(bi[i].amount);
                }
        }
        cur_frm.set_value("initial_amount", initial_amount);
}

var cal_rebate = function(frm) {
	var rebate_amount = frm.doc.rebate
	if(frm.doc.rebate_in_percent) {
		if(frm.doc.rebate > 100) {
			frappe.msgprint("Rebate % Cannot Exceed 100");
			cur_frm.set_value("rebate", '');
			cur_frm.set_value("rebate_amount", '')
		}
		else {
			rebate_amount = parseFloat(frm.doc.rebate) * 0.01 * parseFloat(frm.doc.initial_amount)
		}
	}
	cur_frm.set_value("rebate_amount", parseFloat(rebate_amount));
	cur_frm.set_value("total_amount",  parseFloat(frm.doc.initial_amount) - parseFloat(frm.doc.rebate_amount) + parseFloat(frm.doc.addition_amount) +  parseFloat(frm.doc.substitute_amount));
       	cur_frm.set_value("after_rebate",  parseFloat(frm.doc.initial_amount) - parseFloat(frm.doc.rebate_amount));
}
