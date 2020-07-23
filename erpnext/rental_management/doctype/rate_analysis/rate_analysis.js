// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Rate Analysis', {
	refresh: function(frm) {

	},
});

frappe.ui.form.on("Rate Analysis Item", {
        "type": function(frm, cdt, cdn) {
                c = locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn, "item_code","");
                frappe.model.set_value(cdt, cdn, "item_name","");
                frappe.model.set_value(cdt, cdn, "uom","");
	},
	"item_code": function(frm, cdt, cdn) {
		c = locals[cdt][cdn];
		cur_frm.add_fetch("item_code","item_name","item_name");
		cur_frm.add_fetch("item_code","stock_uom","uom");
		if(c.type =="Service")
			cur_frm.add_fetch("item_code","cost","rate");
		else if(c.type == "Item")
			get_map(frm, cdt, cdn);
		
        },
	"rate": function(frm, cdt, cdn) {
		c = locals[cdt][cdn];
		if(c.qty){
			frappe.model.set_value(cdt, cdn, "amount", c.rate * c.qty);
			update_amount(frm, cdt, cdn);
		}
	},

	"warehouse": function(frm, cdt, cdn) {
		c = locals[cdt][cdn];
		if(c.type == "Item"){
			get_map(frm, cdt, cdn);
		}
	},
	"qty": function(frm, cdt, cdn) {
		c = locals[cdt][cdn];
		if(c.rate){
			frappe.model.set_value(cdt, cdn, "amount", c.rate * c.qty);
			update_amount(frm, cdt, cdn);
		}
	},
	"service_category": function(frm, cdt,cdn){
		c = locals[cdt][cdn];
	/*	if(c.type = 'Service'){
			console.log(c.type + " and " + c.service_category);
			cur_frm.fields_dict['item_code'].get_query = function(doc, dt, dn) {
       				return {
               				filters:{
                        			"item_group": c.service_category,
                			}
       				}
			}
		} */
	} 
});

cur_frm.fields_dict['item'].grid.get_field('item_code').get_query = function(frm, cdt, cdn) {
	c = locals[cdt][cdn];
	if(c.type == "Service"){
	     return {
		filters:{
			"item_group": c.service_category,
		}
	   }
	}
}

function get_map(frm, cdt, cdn) 
{	
	c = locals[cdt][cdn];
	if(frm.doc.posting_date && c.item_code && c.posting_time && c.warehouse){
		frappe.call({
			method: "erpnext.stock.doctype.stock_reconciliation.stock_reconciliation.get_stock_balance_for",
			args: {
				item_code: c.item_code,
				warehouse: c.warehouse,
				posting_date: frm.doc.posting_date,
				posting_time: c.posting_time
			},
			callback: function(r) {
				frappe.model.set_value(cdt, cdn, "rate", r.message.rate);
			}
		});
	}
}

function update_amount(frm, cdt, cdn)
{
	d = locals[cdt][cdn];
	var items = frm.doc.item || [];
        var total_amount = 0;
	var total_base_amount = 0;
        for(var i = 0; i < items.length; i++ ){
                total_base_amount += items[i].amount;
		console.log("Total : " + total_base_amount);
        }
	console.log("test :" + total_base_amount);

        frm.set_value("base_amount", total_base_amount);
	
	if(frm.doc.base_amount > 0){
		var amt1 = 0.05 * frm.doc.base_amount;
		var amt2 = 0.01 * (frm.doc.base_amount + amt1);
		var amt3 = 0.1 * (frm.doc.base_amount + amt1 + amt2);
		frm.set_value("tools_plants", amt1);
		frm.set_value("water_charges", amt2);
		frm.set_value("overhead_cost", amt3);
	}
	frm.set_value("total_amount", frm.doc.base_amount + amt1 + amt2 + amt3);
}
			

















