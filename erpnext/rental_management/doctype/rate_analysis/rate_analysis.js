// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Rate Analysis', {
	refresh: function(frm) {

	}
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
        },
	"rate": function(frm, cdt, cdn) {
		c = locals[cdt][cdn];
		if(c.qty){
			frappe.model.set_value(cdt, cdn, "amount", c.rate * c.qty);
			update_amount(frm, cdt, cdn);
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
			

















