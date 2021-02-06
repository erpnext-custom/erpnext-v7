// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Lot Allotment', {
	refresh: function(frm) {

	},
	onload: function(frm){
	},
	customer_id: function(frm) {
		cur_frm.set_value("branch",null)
	}
	

});

frappe.ui.form.on('Lot Allotment', "refresh", function(frm){
	cur_frm.set_query('site', function(){
		return{
			"filters": {
				"user":cur_frm.doc.customer_id,
				"product_category":"Timber"
			}
		}
	})
	// cur_frm.set_query('customer_id', function(){
	// 	return{
	// 		"filters":{
	// 			"account_type": "CRM",
	// 			"enabled":1
	// 		}
	// 	}
	// })
	cur_frm.set_query('customer_id', function(){
		return{
			"query": "erpnext.controllers.queries.get_crm_users"
		}
	})
})


// frappe.ui.form.on("Lot Allotment", "onload", function(frm){

// })

frappe.ui.form.on("Lot Allotment Lots",{
	lot_number: function(frm, cdt, cdn){
		var row = locals[cdt][cdn]
		populate_lot_details(frm,row);
	},
	before_lot_list_lot_remove: function(frm, cdt, cdn){
		var row = locals[cdt][cdn];
		remove_lot_details(frm, row);
	}
})


frappe.ui.form.on("Lot Allotment Details",{
	price_template: function(frm, cdt, cdn) {
		d = locals[cdt][cdn];
		if(d.location){
			loc = d.location;
		}else{
			loc = "NA";
		}
		frappe.call({
				method: "erpnext.production.doctype.selling_price.selling_price.get_selling_rate",
				args: {
						"price_list": d.price_template,
						"branch": d.branch,
						"item_code": d.item,
						"transaction_date": cur_frm.doc.posting_date,
						"location": loc
				},
				callback: function(r) {
					console.log(r.message);
						frappe.model.set_value(cdt, cdn, "price_list_rate", r.message)
						frappe.model.set_value(cdt, cdn, "rate", r.message)
						frappe.model.set_value(cdt,cdn, "amount", d.total_volume*r.message)
						cur_frm.refresh_field("price_list_rate")
						cur_frm.refresh_field("rate")
						cur_frm.refresh_field("amount")
				}
		})	
	}
})


function populate_lot_details (frm, row){
	if(in_list(user_roles,"CRM Back Office") && frm.doc.docstatus == 0){
		frappe.call({
			method:"get_lot_list_detail",
			doc:  cur_frm.doc,
			args: {'lot_number': row.lot_number, 'posting_date': cur_frm.doc.posting_date},
			callback: function(r, rt){
				if(r.message){
					console.log(r.message[0])
					r.message.forEach(function(v){
						var rows = frappe.model.add_child(frm.doc, "Lot Allotment Details", "lot_list_details");
						rows.lot_number 		= v['lot_number'];
						rows.branch = v['branch'];
						rows.location = v['location'];
						rows.item	= v['item'];
						rows.item_name	= v['item_name'];
						rows.item_sub_group		= v['item_sub_group'];
						rows.total_volume 	= v['total_volume'];
						rows.total_pieces 	= v['total_pieces'];
						rows.price_template = v['parent'];
						rows.price_list_rate = v['selling_price'];
						rows.rate = v['selling_price'];
						rows.amount = parseFloat(rows.rate) * parseFloat(rows.total_volume)
					});
				}
				refresh_field("lot_list_details");
			}
	
		})
	}
}

function remove_lot_details(frm,row){
	var tbl = cur_frm.doc.lot_list_details || [];
	var i = tbl.length;
	while(i--)
	{
		if(tbl[i].lot_number == row.lot_number)
		{
			cur_frm.get_field("lot_list_details").grid.grid_rows[i].remove();
		}
	}
	cur_frm.refresh();
}

//Filtering unused lots - Kinley Dorji 09/11/2020
cur_frm.fields_dict['lot_list_lot'].grid.get_field('lot_number').get_query = function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	return {
		query: "erpnext.production.doctype.lot_list.lot_list.get_la_lot_list",
		filters: {'branch': cur_frm.doc.branch}
	}
}

//Filtering selling price list
cur_frm.fields_dict['lot_list_details'].grid.get_field('price_template').get_query = function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	return {
			query: "erpnext.controllers.queries.price_template_list",
			filters: {'item_code': d.item, 'transaction_date': cur_frm.doc.posting_date, 'branch': d.branch, 'location': d.location}
	}
}

cur_frm.fields_dict['lot_list_details'].grid.get_field('location').get_query = function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	return {
			filters: {'branch': d.branch}
	}
}