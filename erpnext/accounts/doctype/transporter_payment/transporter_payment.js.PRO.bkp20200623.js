// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.add_fetch("branch", "expense_bank_account", "credit_account")
cur_frm.add_fetch("settlement_account","account_type","settlement_account_type");
frappe.ui.form.on('Transporter Payment', {
	setup: function(frm) {
		frm.get_field('items').grid.editable_fields = [
			{fieldname: 'posting_date', columns: 2},
			{fieldname: 'qty', columns: 2},
			{fieldname: 'transportation_rate', columns: 3},
			{fieldname: 'total_amount', columns: 3},
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

	get_details: function(frm) {
		/*
		return frappe.call({
			method: "get_payment_details",
			doc: frm.doc,
			callback: function(r, rt) {
				frm.refresh_fields();
			},
			freeze: true,
			freeze_message: "Loading Payment Details..... Please Wait"
		})
		*/
		
		cur_frm.call({
			method: "get_payment_details",
			doc:frm.doc,
			callback: function(r, rt){
				total_html(frm);
			},
			freeze: false,
			freeze_message: "Loading Payment Details..... Please Wait"
		});

		//total_html(frm);
	},
	/*"deduction_amount": function(frm) {
		var payable = flt(frm.doc.net_payable) - flt(frm.doc.deduction_amount)
		frappe.msgprint(payable)
		cur_frm.set_value("amount_payable", payable) 
	}*/
});

function roundToTwo(num) {    
    return +(Math.round(num + "e+2")  + "e-2");
}

function numberWithCommas(x) {
    var parts = x.toString().split(".");
    parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    return parts.join(".");
}

var total_html = function(frm){
	console.log(frm.doc.total_trip);
	$(cur_frm.fields_dict.total_html.wrapper).html('<table style="width: 100%; font-weight: bold;"></table>');	
	var row = "";
		/*
        if(frm.doc.total_contribution_amount > 0){
                $(cur_frm.fields_dict.total_html.wrapper).html('<label class="control-label" style="padding-right: 0px;">Total No.of Contributors</label><br><b>'+frm.doc.total_noof_contributors+"/"+frm.doc.total_noof_employees+'</b>');
        } else {
                $(cur_frm.fields_dict.total_html.wrapper).html('<label class="control-label" style="padding-right: 0px;">Total No.of Contributors</label><br><b>'+'</b>');
        }*/
	row += '<tr><td>Total No.of Trips</td><td align="right">'+(frm.doc.total_trip?frm.doc.total_trip:0)+"</td></tr>";
	row += '<tr><td>Transportation Amount</td><td align="right">'+numberWithCommas(roundToTwo(parseFloat(frm.doc.transportation_amount?frm.doc.transportation_amount:0)))+'</td><td style="padding: 5px;">(+)</td></tr>';
	row += '<tr><td>Unloading Amount</td><td align="right">'+numberWithCommas(roundToTwo(parseFloat(frm.doc.unloading_amount?frm.doc.unloading_amount:0)))+'</td><td style="padding: 5px;">(+)</td></tr>';
	row += '<tr><td>Gross Amount</td><td align="right" style="border-top: 1px solid #8D99A6;border-bottom: 1px solid #8D99A6;">'+numberWithCommas(roundToTwo(parseFloat(frm.doc.gross_amount?frm.doc.gross_amount:0)))+'</td><td></td></tr>';
	row += '<tr><td>POL Amount</td><td align="right">'+numberWithCommas(roundToTwo(parseFloat(frm.doc.pol_amount?frm.doc.pol_amount:0)))+'</td><td style="padding: 5px;">(-)</td></tr>';
	row += '<tr><td>Net Amount</td><td align="right" style="border-top: 1px solid #8D99A6;border-bottom: 1px solid #8D99A6;">'+numberWithCommas(roundToTwo(parseFloat(frm.doc.net_payable?frm.doc.net_payable:0)))+'</td></tr>';
	row += '<tr><td>Other Deductions & TDS</td><td align="right">'+numberWithCommas(roundToTwo(parseFloat(frm.doc.other_deductions?frm.doc.other_deductions:0)))+'</td><td style="padding: 5px;">(-)</td></tr>';
	row += '<tr><td>Payable Amount</td><td align="right" style="border-top: 1px solid #8D99A6;border-bottom: 1px solid #8D99A6;">'+numberWithCommas(roundToTwo(parseFloat(frm.doc.amount_payable?frm.doc.amount_payable:0)))+'</td></tr>';
	
	$(cur_frm.fields_dict.total_html.wrapper).html('<table style="width: 100%; font-weight: bold;">'+row+'</table>');	
}


/*frappe.ui.form.on('Transporter Payment Pol', {
        refresh: function(frm, cdt, cdn) {
	var child = locals[cdt][cdn]
		if(!frm.child.allocated_amount) {
		frappe.model.set_value(cdt, cdn, "allocated_amount", frm.child.amount);
		}
        }})*/

