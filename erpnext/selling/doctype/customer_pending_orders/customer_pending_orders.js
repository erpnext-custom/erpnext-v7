// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Customer Pending Orders', {
	// rate: function(frm){
	// 	Calculate_Amount(frm);
	// },
	// quantity: function(frm){
	// 	Calculate_Amount(frm);
	// }
	// rate: function(frm, cdt, cdn){
	// 	calculate_amount(frm, cdt, cdn);
	// 	console.log(frm);
	// },
	// quantity: function(frm, cdt, cdn){
	// 	calculate_amount(frm, cdt, cdn);
	// 	console.log("quantity");
	// }


	// rate: function (frm, cdt, cdn) {
	// 	child = locals[cdt][cdn];
	// 	var quant = child.no * child.coefficient * child.height * child.length * child.breath
	// 	frappe.model.set_value(cdt, cdn, 'quantity', parseFloat(quant));
	// },
	// [Customer Pending Orders]: function(frm, cdt, cdn) {
	// 	var d = locals[cdt][cdn];
	// 	var total = 0;
	// 	frappe.model.set_value(d.doctype, d.name, "[Custoner Pending Orders]", d.[rate] * d.[quantity]);
    //     frm.doc.[CHILDTABLEFIELDINPARENT].forEach(function(d) { total += d.[CHILDTABLEPRODUCT]; });
    //     frm.set_value('[PARENTDOCTYPETOTALFIELD]', total);
	// }

});
frappe.ui.form.on('Customer Pending Table Item', {
	rate: function(frm, cdt, cdn){
		calculate_amount(frm, cdt, cdn);
		//console.log(frm);
		// calculate_total(frm,cdt,cdn)

	},
	quantity: function(frm, cdt, cdn){
		calculate_amount(frm, cdt, cdn);
		//console.log("quantity");
		// calculate_total(frm,cdt,cdn)
	}

});

function calculate_amount(frm, cdt, cdn){
	child = locals[cdt][cdn];
	var amount = child.quantity * child.rate
	frappe.model.set_value(cdt, cdn,"amount", amount)
	console.log(frm.doc.total)
	var total_amount = frm.doc.total + child.amount
	console.log("total amount: " , total_amount)
	frm.set_value("total", total_amount)
	// frm.refresh("total")

}

function calculate_total(frm, cdt, cdn){
	var local = locals[cdt][cdn]
	console.log(local)
	var total_amount  = frm.doc.total + local.amount
	console.log(total_amount)
	// console.log(total)
	frm.set_value("total", total_amount)
	frm.refresh("total")
}

// frappe.ui.form.on('Customer Pending Orders', 'Customer Pending Table Item','amount',function(frm, cdt,cdn){
// 	var Items = frm.doc.amount;
// 	console.log(Items);
// 	var amount_total = 0;
// 	for (var i in Items){
// 		amount_total = amount_total + Items[i].amount;
// 	}
// 	frm.set_value("total", amount_total);
// 	fr.refresh("total")
// 	console.log(amount_total)

// });






