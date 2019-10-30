// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
cur_frm.add_fetch("item","item_name","item_name");
cur_frm.add_fetch("item","stock_uom","uom");

frappe.ui.form.on('Technical Sanction', {
	onload: function(frm) {
		frm.set_query("supplier", function() {
			return {
				"filters": {
					"vendor_group": "Contractor",
					//"vendor_type" : "GEP"
				}
			}
		});
	},
	refresh: function(frm) {
	},
	"get_items": function(frm) {
                return frappe.call({
                        method: "get_technical_sanction_items",
                        doc: frm.doc,
                        callback: function(r, rt) {
                                frm.refresh_field("material_items");
                                frm.refresh_fields();
                        }
                });
        },
});


frappe.ui.form.on("Technical Sanction Item", {
	"service": function(frm, cdt, cdn) {
		c = locals[cdt][cdn];

		if(c.type == "Service"){
			cur_frm.add_fetch("service","item_name","item_name");
			cur_frm.add_fetch("item_code","item_name","item_name");
			cur_frm.add_fetch("item_code","stock_uom","uom");
			
			frappe.model.get_value("Service", {'name':c.service}, ['same_rate','item_name'], 
				function(d){
					frappe.model.set_value(cdt,cdn,'item_name', d.item_name);
					if(d.same_rate){
						frappe.model.get_value("Service",{'name':c.service},'cost',
						function(e){
							frappe.model.set_value(cdt,cdn,'amount', e.cost );
							frappe.model.set_value(cdt,cdn, 'total', (e.cost * d.qty))
						});
					}else if(frm.doc.region){
						frappe.model.get_value("BSR Item", {'parent':c.service, 'region':frm.doc.region}, 'rate', 
							function(f){
								frappe.model.set_value(cdt, cdn, 'amount', f.rate);	
								frappe.model.set_value(cdt, cdn, 'total', f.rate * d.qty)
						});
					}else{
						frappe.msgprint("Select a region as the rate is different across region");
					}
				});
		}else if(c.type="Rate Analysis"){
			frappe.model.get_value("Rate Analysis", {'name':c.service}, ['total_amount','title'],
                                function(d){
                                    frappe.model.set_value(cdt, cdn, 'amount', d.total_amount );
				    frappe.model.set_value(cdt, cdn, 'total' , d.total_amount * d.qty);
				    frappe.model.set_value(cdt, cdn, 'item_name', d.title);
                                });	
		}	
	}
});

frappe.ui.form.on("Technical Sanction Materials", {
	"item_code": function(frm, cdt, cdn) {
		c = locals[cdt][cdn];	
	}
	
});

/*
cur_frm.fields_dict['service'].get_query = function(doc, cdt, cdn){
	return {
		"filters":{}
	}
} */
