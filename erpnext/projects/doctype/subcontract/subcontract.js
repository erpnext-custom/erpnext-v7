// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt


cur_frm.add_fetch("project", "branch", "branch");
cur_frm.add_fetch("project", "cost_center", "cost_center");
/*
cur_frm.add_fetch("project","party_type","party_type");
cur_frm.add_fetch("project","party","party");
*/

frappe.ui.form.on('Subcontract', {
	setup: function(frm){
        frm.get_docfield("boq_item").allow_bulk_edit = 1;		
		
		frm.get_field('boq_item').grid.editable_fields = [
			{fieldname: 'boq_code', columns: 1},
			{fieldname: 'item', columns: 3},
			{fieldname: 'is_selected', columns: 1},
			{fieldname: 'uom', columns: 1},
			{fieldname: 'quantity', columns: 1},
			{fieldname: 'rate', columns: 1},
			{fieldname: 'amount', columns: 2}
		];
				
		frm.get_field('boq_history_item').grid.editable_fields = [
			{fieldname: 'transaction_type', columns: 2},
			{fieldname: 'transaction_date', columns: 2},
			{fieldname: 'initial_amount', columns: 2},
			{fieldname: 'adjustment_amount', columns: 2},
			{fieldname: 'final_amount', columns: 2},
		];
	},
	
	refresh: function(frm) {
		boq_item_html(frm);
		if(!frm.doc.__islocal && frm.doc.docstatus==1){
			if(frappe.model.can_read("Subcontract Adjustment")) {
				frm.add_custom_button(__("Adjustments"), function() {
					frappe.route_options = {"subcontract": frm.doc.name}
					frappe.set_route("List", "Subcontract Adjustment");
				}, __("View"), true);
			}
			
			frm.add_custom_button(__("Advance"), function(){frm.trigger("make_subcontract_advance")},__("Make"), "icon-file-alt");
			
			/*
			if(frappe.model.can_read("Project")) {
				frm.add_custom_button(__("Project"), function() {
					frappe.route_options = {"name": frm.doc.project}
					frappe.set_route("Form", "Project", frm.doc.project);
				}, __("View"), true);
			}
			*/

			if(frappe.model.can_read("MB Entry")) {
				frm.add_custom_button(__("MB Entries"), function() {
					frappe.route_options = {"subcontract": frm.doc.name}
					frappe.set_route("List", "MB Entry");
				}, __("View"), true);
			}			
			
			if(frappe.model.can_read("Project Invoice")) {
				frm.add_custom_button(__("Invoices"), function() {
					frappe.route_options = {"subcontract": frm.doc.name}
					frappe.set_route("List", "Project Invoice");
				}, __("View"), true);
			}			
		}
		
		frm.trigger("get_defaults");
		
		if(frm.doc.docstatus==1){
			//frm.add_custom_button(__("Advance"), function(){frm.trigger("make_boq_advance")},__("Make"), "icon-file-alt");
			frm.add_custom_button(__("Adjustment"),function(){frm.trigger("make_subcontract_adjustment")},
				__("Make"), "icon-file-alt"
			);
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
			/*
			frm.add_custom_button(__("Direct Invoice"),function(){frm.trigger("make_direct_invoice")},
				__("Make"), "icon-file-alt"
			);
			*/
			frm.add_custom_button(__("Invoice"),function(){frm.trigger("make_mb_invoice")},
				__("Make"), "icon-file-alt"
			);			
		}
		
		/*
		$.each(cur_frm.doc['boq_item'], function(i, item){
			console.log($("div[data-fieldname=boq_item]").find(format('div.grid-row[data-idx="{0}"]', [item.idx])));
			$("div[data-fieldname=boq_item]").find(format('div.grid-row[data-idx="{0}"]', [item.idx])).css({'background-color': '#FF0000'});
			$("div[data-fieldname=boq_item]").find(format('div.grid-row[data-idx="{0}"]', [item.idx])).find('.grid-static-col').css({'background-color': '#FF0000'});
		})
		*/		
		
		// Not working
		/*
		$.each(cur_frm.doc['boq_item'], function(i, item){
			//console.log(item.balance_amount); this line works
			//console.log($("div[data-fieldname=boq_item]").find(format('div.grid-row[data-idx="{0}"]', [item.idx])));
			if(parseFloat(item.balance_amount || 0.0) > 0.0){
				//console.log($("div[data-fieldname=boq_item]").find(format('div.grid-row[data-idx="{0}"]', [item.idx])));
				console.log($("div[data-fieldname=boq_item]").find(format('div.grid-row[data-name="{0}"]', [item.name])));
				//$("div[data-fieldname=boq_item]").find(format('div.grid-row[data-idx="{0}"]', [item.idx])).css({'background-color': '#FF0000'});
				$("div[data-fieldname=boq_item]").find(format('div.grid-row[data-name="{0}"]', [item.name])).css({'background-color': 'red'});
				$("div[data-fieldname=boq_item]").find(format('div.grid-row[data-idx="{0}"]', [item.idx])).find('.grid-static-col').css({'background-color': '#FF0000 !important'});
			}
		});
		*/
	},
	make_subcontract_adjustment: function(frm){
		frappe.model.open_mapped_doc({
			method: "erpnext.projects.doctype.subcontract.subcontract.make_subcontract_adjustment",
			frm: frm
		});
	},
	
	make_direct_invoice: function(frm){
		frappe.model.open_mapped_doc({
			method: "erpnext.projects.doctype.subcontract.subcontract.make_direct_invoice",
			frm: frm
		});
	},
		
	make_mb_invoice: function(frm){
		frappe.model.open_mapped_doc({
			method: "erpnext.projects.doctype.subcontract.subcontract.make_mb_invoice",
			frm: frm
		});
	},	
	
	make_book_entry: function(frm){
		frappe.model.open_mapped_doc({
			method: "erpnext.projects.doctype.subcontract.subcontract.make_book_entry",
			frm: frm
		});
	},
	
	project: function(frm){
		frm.trigger("get_defaults");
	},
	
	get_defaults: function(frm){
		frm.add_fetch("project", "branch","branch");
		frm.add_fetch("project", "cost_center","cost_center");		
	},
	
	make_subcontract_advance: function(frm){
		frappe.model.open_mapped_doc({
			method: "erpnext.projects.doctype.subcontract.subcontract.make_subcontract_advance",
			frm: frm
		});
	},
	
	check_all: function(frm){
		check_uncheck_all(frm);
	}
});

frappe.ui.form.on("Subcontract Item",{
	quantity: function(frm, cdt, cdn){
		calculate_amount(frm, cdt, cdn);
	},
	
	rate: function(frm, cdt, cdn){
		calculate_amount(frm, cdt, cdn);
	},
	
	amount: function(frm, cdt, cdn){
		calculate_total_amount(frm);
	},
	
	is_selected: function(frm, cdt, cdn){
		calculate_total_amount(frm);
	},
	
	boq_item_remove: function(frm, cdt, cdn){
		calculate_total_amount(frm);
	}
})

var calculate_amount = function(frm, cdt, cdn){
	child = locals[cdt][cdn];
	amount = 0.0;
	
	amount = flt(child.quantity)*flt(child.rate)
	
	frappe.model.set_value(cdt, cdn, 'amount', flt(amount));
	frappe.model.set_value(cdt, cdn, 'balance_quantity', flt(child.quantity));
	frappe.model.set_value(cdt, cdn, 'balance_rate', flt(child.rate));
	frappe.model.set_value(cdt, cdn, 'balance_amount', flt(amount));
}

var calculate_total_amount = function(frm){
	var bi = frm.doc.boq_item || [];
	var total_amount = 0.0, balance_amount = 0.0;
	var amount = 0;
	for(var i=0; i<bi.length; i++){
		if (bi[i].is_selected && bi[i].amount){
			total_amount += flt(bi[i].amount);
		}
	}
	balance_amount = flt(total_amount) - flt(frm.doc.received_amount)
	cur_frm.set_value("total_amount",total_amount);
	cur_frm.set_value("balance_amount",balance_amount);
}

var check_uncheck_all = function(frm){
	var meb =frm.doc.boq_item || [];

	for(var id in meb){
		frappe.model.set_value("Subcontract Item", meb[id].name, "is_selected", frm.doc.check_all);
	}
}

/*
frappe.ui.form.on("BOQ Item", "is_group", function(frm, cdt, cdn){
    var child = locals[cdt][cdn];
    cur_frm.doc.boq_item.forEach(function(child){
		console.log(child);
        var sel = format('div[data-fieldname="boq_item"] > div.grid-row[data-idx="{0}"]', [child.idx]);
        if (child.is_group > 1000){
            $(sel).css('background-color', "#ff5858");
        } else {
            $(sel).css('background-color', 'transparent');
        }
    });
});
*/


var boq_item_html = function(frm){
	/*
	cur_frm.doc.boq_item.forEach(function(row){
		console.log("==========================");
		var sel = format('div[data-fieldname="boq_item"] > div.grid-row[data-idx="{0}"]', [row.idx]);
		console.log($(sel).length);

        if (row.is_group){
			console.log('is_group: 1');
            $(sel).css('backgroundColor', "#ff5858");
        } else {
			console.log('is_group: 0');
            $(sel).css('backgroundColor', 'transparent');
        }
    });
	*/
}

// toggle display of items based on boq_type
/*
$(document).find('[data-fieldname="boq_type"]').change(function(){
	console.log('test',$(this).find(":selected").text());
	if($(this).find(":selected").text() !== "Milestone Based"){
		console.log('Non milestone');
	}
	$(document).find('[data-fieldname="quantity"]').toggle($(this).find(":selected").text() !== "Milestone Based");
});
*/

