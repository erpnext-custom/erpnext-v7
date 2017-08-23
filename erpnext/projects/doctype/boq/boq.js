// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('BOQ', {
	setup: function(frm){
		frm.get_field('boq_item').grid.editable_fields = [
			{fieldname: 'boq_code', columns: 1},
			{fieldname: 'item', columns: 3},
			{fieldname: 'is_group', columns: 1},
			{fieldname: 'uom', columns: 1},
			{fieldname: 'quantity', columns: 1},
			{fieldname: 'rate', columns: 1},
			{fieldname: 'amount', columns: 1}
		];
	},
	
	refresh: function(frm) {
		if(frm.doc.balance_amount > 0){
			frm.add_custom_button(__("Claim Advance"),function(){frm.trigger("claim_advance")},
				__("Make"), "icon-file-alt"
			);
			
			frm.add_custom_button(__("Make Invoice"),function(){frm.trigger("make_project_invoice")},
				__("Make"), "icon-file-alt"
			);
		}
	},
	
	make_project_invoice: function(frm){
		frappe.model.open_mapped_doc({
			method: "erpnext.projects.doctype.boq.boq.make_project_invoice",
			frm: frm
		});
	},
});

frappe.ui.form.on("BOQ Item",{
	quantity: function(frm, cdt, cdn){
		calculate_amount(frm, cdt, cdn);
	},
	
	rate: function(frm, cdt, cdn){
		calculate_amount(frm, cdt, cdn);
	},
	
	amount: function(frm){
		calculate_total_amount(frm);
	},
})

var calculate_amount = function(frm, cdt, cdn){
	child = locals[cdt][cdn];
	amount = 0.0;
	
	if(child.quantity && child.rate){
		amount = parseFloat(child.quantity)*parseFloat(child.rate)
	}
	
	frappe.model.set_value(cdt, cdn, 'amount', parseFloat(amount));
	frappe.model.set_value(cdt, cdn, 'balance_quantity', parseFloat(child.quantity));
	frappe.model.set_value(cdt, cdn, 'balance_amount', parseFloat(amount));
}

var calculate_total_amount = function(frm){
	var bi = frm.doc.boq_item || [];
	total_amount = 0.0;
	
	for(var i=0; i<bi.length; i++){
		if (bi[i].amount){
			total_amount += parseFloat(bi[i].amount);
		}
	}
	
	cur_frm.set_value("total_amount",total_amount);
}