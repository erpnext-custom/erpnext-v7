// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Project Invoice', {
	setup: function(frm){
		/*
		frm.get_field('project_invoice_boq').grid.editable_fields = [
			{fieldname: 'item', columns: 3},
			{fieldname: 'uom', columns: 1},
			{fieldname: 'invoice_quantity', columns: 2},
			{fieldname: 'invoice_rate', columns: 2},
			{fieldname: 'invoice_amount', columns: 2}
		];
		*/
		
		if(frm.doc.boq_type=="Item Based"){
			frm.get_field('project_invoice_boq').grid.editable_fields = [
				{fieldname: 'item', columns: 3},
				{fieldname: 'uom', columns: 1},
				{fieldname: 'invoice_quantity', columns: 2},
				{fieldname: 'invoice_rate', columns: 2},
				{fieldname: 'invoice_amount', columns: 2}
			];
			frm.fields_dict.project_invoice_boq.grid.toggle_enable("invoice_quantity", true);
			frm.fields_dict.project_invoice_boq.grid.toggle_enable("invoice_amount", false);
			//frm.fields_dict.project_invoice_boq.grid.set_column_disp("invoice_quantity", true);			
		} 
		else if(frm.doc.boq_type=="Milestone Based"){
			frm.get_field('project_invoice_boq').grid.editable_fields = [
				{fieldname: 'item', columns: 3},
				{fieldname: 'uom', columns: 1},
				{fieldname: 'invoice_quantity', columns: 2},
				{fieldname: 'invoice_rate', columns: 2},
				{fieldname: 'invoice_amount', columns: 2}
			];
			frm.fields_dict.project_invoice_boq.grid.toggle_enable("invoice_quantity", false);
			frm.fields_dict.project_invoice_boq.grid.toggle_enable("invoice_amount", true);
		}
		else if(frm.doc.boq_type=="Piece Rate Work Based(PRW)"){
			frm.get_field('project_invoice_boq').grid.editable_fields = [
				{fieldname: 'item', columns: 3},
				{fieldname: 'uom', columns: 1},
				{fieldname: 'invoice_quantity', columns: 2},
				{fieldname: 'invoice_rate', columns: 2},
				{fieldname: 'invoice_amount', columns: 2}
			];
			frm.fields_dict.project_invoice_boq.grid.toggle_enable("invoice_quantity", true);
			frm.fields_dict.project_invoice_boq.grid.toggle_enable("invoice_amount", false);
		}
	},
	
	refresh: function(frm) {
		
	}
});

frappe.ui.form.on("Project Invoice BOQ",{
	invoice_quantity: function(frm, cdt, cdn){
		child = locals[cdt][cdn];
		
		if(child.invoice_quantity > child.act_quantity){
			msgprint(__("Invoice Quantity cannot be greater than balance quantity.").format(child.invoice_quantity))
		}
		
		if(child.invoice_quantity && child.invoice_rate){
			frappe.model.set_value(cdt, cdn, 'invoice_amount', (parseFloat(child.invoice_quantity)*parseFloat(child.invoice_rate)));
		}
	},
	invoice_amount: function(frm, cdt, cdn){
		child = locals[cdt][cdn];
		
		if(child.invoice_amount > child.act_amount){
			msgprint(__("Invoice Amount cannot be greater than balance amount."));
		}
	},
});