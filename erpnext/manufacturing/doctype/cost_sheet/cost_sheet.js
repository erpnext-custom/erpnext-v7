// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Cost Sheet', {
	refresh: function(frm) {
		frm.set_query("bom", function() {
			return {
				"filters": {
					"item": frm.doc.item,
					"is_active": 1
				}
			};
		});
		frm.set_query("item", function() {
			return {
				"filters": {
					"is_sales_item":1
				}
			}
		});
	},
	"bom": function(frm) {
		if(!frm.doc.item){
			console.log("select Item before BOM");
		}
	},
	"item": function(frm) {
		cur_frm.set_value("bom","");
		cur_frm.set_value("bom_cost", "");
	},
	"bom_cost": function(frm){
		if(frm.doc.items){
			l_cost = 0
			frm.doc.items.forEach(function(d) {
				l_cost += d.amount;
			});
			frm.set_value("prime_cost", parseFloat(l_cost) + parseFloat(frm.doc.bom_cost));
		}
		else
			frm.set_value("prime_cost", frm.doc.bom_cost);
	}
});

frappe.ui.form.on("Cost Sheet Item", {
	refresh: function(frm, cdt, cdn) {

	},
	"rate": function(frm, cdt, cdn) {
		i = locals[cdt][cdn];
		if(i.hours)
			frappe.model.set_value(cdt, cdn, "amount", i.hours * i.rate);	
		cal_cost(frm, cdt, cdn);
	},
	"hours": function(frm, cdt, cdn) {
		i = locals[cdt][cdn];
		if(i.rate)
			frappe.model.set_value(cdt, cdn, "amount", i.hours * i.rate);
		cal_cost(frm, cdt,cdn);
	},
	"amount": function(frm, cdt, cdn){
		i = locals[cdt][cdn];
	}	
});

function cal_cost(frm, cdt, cdn){
	labor_cost = 0
	frm.doc.items.forEach(function(d) {
		labor_cost += d.amount;
	});
	frm.set_value("prime_cost", parseFloat(labor_cost) + parseFloat(frm.doc.bom_cost));
}

