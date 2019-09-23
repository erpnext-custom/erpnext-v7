// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
cur_frm.add_fetch("item", "item_name", "item_name");
frappe.ui.form.on('Lot List', {
	setup: function(frm){
                frm.get_docfield("items").allow_bulk_edit = 1;
        },
	refresh: function(frm) {
			
	},
});

frappe.ui.form.on("Lot List", "refresh", function(frm) {
    cur_frm.set_query("item", function() {
        return {
            "filters": {
                "item_sub_group": frm.doc.item_sub_group,
                "disabled" : 0
            }
        };

    });
});


frappe.ui.form.on("Lot List Item", {
        "length": function(frm, cdt, cdn) {
                        d = locals[cdt][cdn];
                        if(frm.doc.item_sub_group == "Sawn" || frm.doc.item_sub_group == "Block" || frm.doc.item_sub_group == "Field Sawn"){
                                if(d.girth > 0 && d.height > 0){
                                        update_volume(frm, cdt, cdn);
                                }
                        }else{
                                if(d.girth > 0){
                                        update_volume(frm, cdt, cdn);
                                }
                        }
                },
        "girth": function(frm, cdt, cdn) {
                        d = locals[cdt][cdn];
                        if(frm.doc.item_sub_group == "Sawn" || frm.doc.item_sub_group == "Block" || frm.doc.item_sub_group == "Field Sawn"){
                                if(d.length > 0 && d.height > 0){
                                        update_volume(frm, cdt, cdn);
                                }
                        }else{
                                if(d.length > 0){
                                        update_volume(frm, cdt, cdn);
                                }
                        }
                },
        "height": function(frm, cdt, cdn) {
                        d = locals[cdt][cdn];
                        if(frm.doc.item_sub_group == "Sawn" || frm.doc.item_sub_group == "Block" || frm.doc.item_sub_group == "Field Sawn"){
                                if(d.length > 0 && d.girth > 0){
                                        update_volume(frm, cdt, cdn);
                                }
                        }
                },
	"number_pieces": function(frm, cdt, cdn) {
			update_volume(frm, cdt, cdn);
		}
});


function update_volume(frm, cdt, cdn)
{
	d = locals[cdt][cdn];
	if(frm.doc.item_sub_group == "Sawn" || frm.doc.item_sub_group == "Block" || frm.doc.item_sub_group == "Field Sawn"){
                var volume = ((d.length * d.girth * d.height) / 144) * d.number_pieces;
        }
        else{
		var f = d.girth.toString().split(".");
		var in_inches = 0;
		if(f.length == 1){
			f[0] = d.girth;
			f[1] = 0;
		}
		var girth = (parseFloat(f[0]) * 12) + parseFloat(f[1]);
		//console.log("Girth" + girth +" f1 " + f[0] + " f2 " + f[1]);
		var volume = (((girth * girth) * d.length ) / 1809.56) * d.number_pieces;
	}

	frappe.model.set_value(cdt, cdn, "volume", volume);
	
	var items = frm.doc.items || [];
	var total_vol = 0;
	for(var i = 0; i < items.length; i++ ){
		total_vol += items[i].volume;
	}

	frm.set_value("total_volume", total_vol);
	frm.set_value("total_pieces", items.length);
}

