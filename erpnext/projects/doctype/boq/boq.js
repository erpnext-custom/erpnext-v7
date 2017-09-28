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
		if(!frm.doc.__islocal){
			if(frappe.model.can_read("Project")) {
				frm.add_custom_button(__("Project"), function() {
					frappe.route_options = {"name": frm.doc.project}
					frappe.set_route("Form", "Project", frm.doc.project);
				}, __("View"), true);
			}

			if(frappe.model.can_read("MB Entry")) {
				frm.add_custom_button(__("Measurement Book Entries"), function() {
					frappe.route_options = {"boq": frm.doc.name}
					frappe.set_route("List", "MB Entry");
				}, __("View"), true);
			}			
			
			if(frappe.model.can_read("Project Invoice")) {
				frm.add_custom_button(__("Invoices"), function() {
					frappe.route_options = {"boq": frm.doc.name}
					frappe.set_route("List", "Project Invoice");
				}, __("View"), true);
			}			
		}
		
		if(frm.doc.docstatus==1 && parseFloat(frm.doc.claimed_amount) < (parseFloat(frm.doc.total_amount)+parseFloat(frm.doc.price_adjustment))){
			/*
			frm.add_custom_button(__("Claim Advance"),function(){frm.trigger("claim_advance")},
				__("Make"), "icon-file-alt"
			);
			*/
			frm.add_custom_button(__("Measurement Book Entry"),function(){frm.trigger("make_book_entry")},
				__("Make"), "icon-file-alt"
			);
			frm.add_custom_button(__("Direct Invoice"),function(){frm.trigger("make_direct_invoice")},
				__("Make"), "icon-file-alt"
			);
			frm.add_custom_button(__("MB Based Invoice"),function(){frm.trigger("make_mb_invoice")},
				__("Make"), "icon-file-alt"
			);			
		}
	},
	make_direct_invoice: function(frm){
		frappe.model.open_mapped_doc({
			method: "erpnext.projects.doctype.boq.boq.make_direct_invoice",
			frm: frm
		});
	},
	
	make_mb_invoice: function(frm){
		frappe.model.open_mapped_doc({
			method: "erpnext.projects.doctype.boq.boq.make_mb_invoice",
			frm: frm
		});
	},	
	
	make_book_entry: function(frm){
		frappe.model.open_mapped_doc({
			method: "erpnext.projects.doctype.boq.boq.make_book_entry",
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
	
	//if(child.quantity && child.rate){
	amount = parseFloat(child.quantity)*parseFloat(child.rate)
	//}
	
	frappe.model.set_value(cdt, cdn, 'amount', parseFloat(amount));
	frappe.model.set_value(cdt, cdn, 'balance_quantity', parseFloat(child.quantity));
	frappe.model.set_value(cdt, cdn, 'balance_amount', parseFloat(amount));
}

var calculate_total_amount = function(frm){
	var bi = frm.doc.boq_item || [];
	var total_amount = 0.0, balance_amount = 0.0;
	
	for(var i=0; i<bi.length; i++){
		if (bi[i].amount){
			total_amount += parseFloat(bi[i].amount);
		}
	}
	balance_amount = parseFloat(total_amount) - parseFloat(frm.doc.received_amount)
	cur_frm.set_value("total_amount",total_amount);
	cur_frm.set_value("balance_amount",balance_amount);
}