// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.add_fetch("branch", "expense_bank_account", "credit_account")
cur_frm.add_fetch("settlement_account","account_type","settlement_account_type");
frappe.ui.form.on('Transporter Payment', {
	setup: function(frm) {
		frm.get_field('items').grid.editable_fields = [
                        {fieldname: 'receiving_warehouse', columns: 2},
                        {fieldname: 'posting_date', columns: 2},
                        {fieldname: 'qty', columns: 1},
                        {fieldname: 'transportation_rate', columns: 2},
                        {fieldname: 'unloading_amount', columns: 1},
                        {fieldname: 'total_amount', columns: 2},
                ];
		frm.get_field('pols').grid.editable_fields = [
			{fieldname: 'posting_date', columns: 2},
			{fieldname: 'qty', columns: 2},
			{fieldname: 'rate', columns: 2},
			{fieldname: 'amount', columns: 2},
			{fieldname: 'allocated_amount', columns:2}
		];
	},
	onload: function(frm) {
		if(!frm.doc.posting_date) {
			cur_frm.set_value("posting_date", get_today())
		}
		frm.set_query("credit_account", function() {
			return {
				filters: {
					is_group: 0
				}
			}
		})
		frm.set_query("equipment", function() {
			return {
				filters: {
					is_disabled: 0
				}
			}
		})
		frm.fields_dict['deductions'].grid.get_field('party_type').get_query = function(){
				return {
						filters: {"name": ["in", ["Customer", "Supplier","Employee","Equipment"]]}
				}
		};
		total_html(frm);
	},

	refresh: function(frm) {
                if(frm.doc.docstatus===1){
                        frm.add_custom_button(__('Accounting Ledger'), function(){
                                frappe.route_options = {
                                        voucher_no: frm.doc.name,
                                        from_date: frm.doc.posting_date,
                                        to_date: frm.doc.posting_date,
                                        company: frm.doc.company,
                                        group_by_voucher: false
                                };
                                frappe.set_route("query-report", "General Ledger");
                        }, __("View"));
                }
		total_html(frm);
	},
	branch: function(frm){
		reset_items(frm);
	},
	from_date: function(frm){
		reset_items(frm);
	},
	to_date: function(frm){
		reset_items(frm);
	},
	equipment: function(frm){
		reset_items(frm);
	},
	get_details: function(frm) {
		get_payment_details(frm);
	},
	tds_percent: function(frm){
		calculate_totals(frm);
	},
	security_deposit_percent: function(frm){
		calculate_totals(frm);
	},
	weighbridge_charge: function(frm){
		calculate_totals(frm);
	},
	/*"deduction_amount": function(frm) {
		var payable = flt(frm.doc.net_payable) - flt(frm.doc.deduction_amount)
		frappe.msgprint(payable)
		cur_frm.set_value("amount_payable", payable) 
	}*/
});

frappe.ui.form.on('Transporter Payment Item', {
        items_remove: function(frm, cdt, cdn){
		calculate_totals(frm);
        },
});

// Ver.2020.06.23 Begins, by SHIV on 2020/06/23
// Following code is moved from gt_details button for better code maintednance
function calculate_totals(frm){
	cur_frm.call({
		method: "calculate_total",
		doc:frm.doc,
		callback: function(r, rt){
			total_html(frm);
		},
	});
}

function reset_items(frm){
	cur_frm.clear_table("items");
	cur_frm.clear_table("pols");
	calculate_totals(frm);
}

function get_payment_details(frm){
	cur_frm.clear_table("items");
	cur_frm.clear_table("pols");
	
	cur_frm.call({
		method: "get_payment_details",
		doc:frm.doc,
		callback: function(r, rt){
			total_html(frm);
			cur_frm.set_value("amount_payable", flt(r.message));
			frm.refresh_fields();
		},
		freeze: false,
		freeze_message: "Loading Payment Details..... Please Wait"
	});

	frm.refresh_field("items");
	frm.refresh_field("pols");
	cur_frm.refresh();
}
// Ver.2020.06.23 Ends

function roundToTwo(num) {    
    return +(Math.round(num + "e+2")  + "e-2");
}

function numberWithCommas(x) {
    var parts = x.toString().split(".");
    parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    return parts.join(".");
}

var get_row = function(label, value, with_border=0, suffix=""){
	var fmt_value = numberWithCommas(roundToTwo(flt(value)));
	var fmt_suffix= "";

	if(suffix){
		fmt_suffix = `(${suffix})`;
	}

	if(with_border){
		return `<tr>
				<td>${label}</td>
				<td align="right" style="border-top: 1px solid #8D99A6;border-bottom: 1px solid #8D99A6;">${fmt_value}</td>
				<td style="padding: 5px;">${fmt_suffix}</td></tr>`;
	}
	else{
		return `<tr><td>${label}</td><td align="right">${fmt_value}</td><td style="padding: 5px;">${fmt_suffix}</td></tr>`;
	}
}

var total_html = function(frm){
	$(cur_frm.fields_dict.total_html.wrapper).html('<table style="width: 100%; font-weight: bold;"></table>');	
	var row = "";
	row += get_row('Total No.of Trips', flt(frm.doc.total_trip), 0);
	row += get_row('Transfer Charges', flt(frm.doc.transfer_charges), 0, "+");
	row += get_row('Delivery Charges', flt(frm.doc.delivery_charges), 0, "+");
	row += get_row('Transportation Amount', flt(frm.doc.transportation_amount), 1);
	row += get_row('Unloading Amount', flt(frm.doc.unloading_amount), 0, "+");
	row += get_row('Transporter Trip Log Count', flt(frm.doc.within_warehouse_trip), 0);
	row += get_row('Within Warehouse Transportation Amt.', flt(frm.doc.within_warehouse_amount), 1, '+');
	row += get_row("Production Trip Count", flt(frm.doc.production_trip_count), 0);
	row += get_row('Production Transportation Amt.', flt(frm.doc.production_transport_amount), 1, '+');
	row += get_row('Gross Amount', flt(frm.doc.gross_amount), 1);
	row += get_row('POL Amount', flt(frm.doc.pol_amount), 0, "-");
	row += get_row('Net Amount', flt(frm.doc.net_payable), 1);
	row += get_row('Weighbridge Charges', flt(frm.doc.weighbridge_amount), 0, "-");
	row += get_row('Other Deductions, TDS & SD', flt(frm.doc.other_deductions), 0, "-");
	row += get_row('Payable Amount', flt(frm.doc.amount_payable), 1);
	
	$(cur_frm.fields_dict.total_html.wrapper).html('<table style="width: 100%; font-weight: bold;">'+row+'</table>');	
}


/*frappe.ui.form.on('Transporter Payment Pol', {
        refresh: function(frm, cdt, cdn) {
	var child = locals[cdt][cdn]
		if(!frm.child.allocated_amount) {
		frappe.model.set_value(cdt, cdn, "allocated_amount", frm.child.amount);
		}
        }})*/

