// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
cur_frm.add_fetch("service","item_name","item_name");
cur_frm.add_fetch("item_code","item_name","item_name");
cur_frm.add_fetch("item_code","purchase_uom","uom");

frappe.ui.form.on('Technical Sanction', {
	refresh: function(frm) {
	}
});


frappe.ui.form.on("Technical Sanction Item", {
	"service": function(frm, cdt, cdn) {
		c = locals[cdt][cdn];
		frappe.model.get_value("Service", {'name':c.service}, 'same_rate', 
			function(d){
				if(d.same_rate){
					frappe.model.get_value("Service",{'name':c.service},'cost',
					function(e){
						frappe.model.set_value(cdt,cdn,'amount', e.cost);
					});
				}else if(frm.doc.region){
					frappe.model.get_value("BSR Item", {'parent':c.service, 'region':frm.doc.region}, 'rate', 
						function(f){
							frappe.model.set_value(cdt, cdn, 'amount', f.rate);	
					});
				}else{
					frappe.msgprint("Select a region as the rate is different across region");
				}
			});	
	}
});

frappe.ui.form.on("Technical Sanction Material", {
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
