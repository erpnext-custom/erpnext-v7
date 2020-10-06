// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.add_fetch("location", "location_id", "location_id");
frappe.ui.form.on('Tenant Information', {
	refresh: function(frm) {
	},
	"location": function(frm){
		calculate(frm);
		if(frm.doc.location_id && frm.doc.block_no){
			var structure_no = frm.doc.location_id + "/" + frm.doc.block_no;
			cur_frm.set_value("structure_no", structure_no);
		}
	},
	"building_category": function(frm){
		calculate(frm);
	},
	"block_no": function(frm){
		calculate(frm);
	},
	"flat_no": function(frm){
		calculate(frm);
	},
	"rate_per_sq_ft": function(frm){
		cur_frm.set_value("rent_amount", Math.round(frm.doc.floor_area * frm.doc.rate_per_sq_ft));
	},
	"floor_area": function(frm){
		cur_frm.set_value("rent_amount", Math.round(frm.doc.floor_area * frm.doc.rate_per_sq_ft));
	},
	"rent_amount": function(frm){
                cur_frm.set_value("security_deposit", Math.round(frm.doc.rent_amount + frm.doc.rent_amount));
        },
	"calculate_rent_charges": function(frm){
		calculate_rent_charges(frm);
	},
	"building_category": function(frm, cdt, cdn) {
		doc = locals[cdt][cdn]
		cur_frm.toggle_reqd("floor_area", doc.building_category !== "Pilot Housing");
		cur_frm.toggle_reqd("rate_per_sq_ft", doc.building_category !== "Pilot Housing");
		cur_frm.fields_dict.rental_charges.grid.toggle_reqd("from_date", doc.building_category !== "Pilot Housing");
		cur_frm.fields_dict.rental_charges.grid.toggle_reqd("to_date", doc.building_category !== "Pilot Housing");
		cur_frm.fields_dict.rental_charges.grid.toggle_reqd("rental_amount", doc.building_category !== "Pilot Housing");
	},
	"block_no": function(frm) {
		if (frm.doc.location){
			var structure_no = frm.doc.location_id + "/" + frm.doc.block_no;
			cur_frm.set_value("structure_no", structure_no);
		}
	}
	
});

function calculate_rent_charges(frm){
	if(frm.doc.building_category == "Pilot Housing"){
		cur_frm.clear_table("rental_charges");
		cur_frm.refresh_fields();
		
		var row = frappe.model.add_child(cur_frm.doc, "Tenant Rental Charges", "rental_charges");
		row.from_date = frm.doc.from_date;
		row.to_date = frm.doc.to_date;
		row.increment = 0.00;
		row.rental_amount = Math.round(frm.doc.original_monthly_instalment);
		cur_frm.refresh();
		
	}
	else{
		frappe.model.get_value('Rental Setting',{'name': 'Rental Setting'}, 'percent_of_increment', function(d){
			cur_frm.set_value("percent_of_increment", d.percent_of_increment);
			cur_frm.set_value("no_of_year_for_increment", d.no_of_year_for_increment);
		});
		
		if(frm.doc.rent_amount){
			var d = new Date(frm.doc.allocated_date);
			cur_frm.clear_table("rental_charges");
			cur_frm.refresh_fields();
			
			var percentage = frm.doc.percent_of_increment/100;
			var increment_year = frm.doc.no_of_year_for_increment;
			var increment = 0;
			var actual_rent = 0;
			for(var i=0;i<10;i+=increment_year){
				var yyyy = (d.getFullYear() + i).toString();
				var mm = (d.getMonth()+1).toString();
				if(mm == "1"){
					var to_mm = "12";
					to_yyyy = (d.getFullYear() + increment_year - 1 + i).toString();
				}else{
					var to_mm = d.getMonth().toString();
					to_yyyy = (d.getFullYear() + increment_year + i).toString();
				}
				var fdd = '01'.toString();
				//var to_yyyy = (d.getFullYear() + increment_year + i).toString();
				var last_day = new Date(to_yyyy, (d.getMonth()-1) +1, 0).getDate();
				console.log("Month:"+ d.getMonth() + " Date: " + last_day);
				var from_date = yyyy + '-' + (mm[1]?mm:"0"+mm[0]) + "-" + fdd;
				var to_date = to_yyyy + "-" + (to_mm[1]?to_mm:"0"+to_mm[0]) + "-" + last_day;
				console.log("from_date :" + from_date + "to Date:" + to_date);
				var row = frappe.model.add_child(cur_frm.doc, "Tenant Rental Charges", "rental_charges");
				if(i>0){	
					increment = (actual_rent > 0)?actual_rent * percentage:frm.doc.rent_amount * percentage;
					actual_rent = (actual_rent > 0)? actual_rent + increment : frm.doc.rent_amount + increment; 
					console.log("increment: " + increment + "actual rent: " + actual_rent);
				}
				row.from_date = from_date;
				row.to_date = to_date;
				row.increment = increment;
				var rental_amount = (actual_rent > 0)?actual_rent:frm.doc.rent_amount;
				row.rental_amount = Math.round(rental_amount);
			}
			cur_frm.refresh();
		}else{
			frappe.throw("Please provide Initial Rent Amount");
		}
	}
}

function calculate(frm){
	if(frm.doc.location && frm.doc.building_category && frm.doc.block_no && frm.doc.flat_no){
		frappe.model.get_value('Floor Area', {'building_category': frm.doc.building_category, 'location': frm.doc.location, 'block_no': frm.doc.block_no, 'flat_no': frm.doc.flat_no }, 'floor_area',
			  function(d) {
			    cur_frm.set_value("floor_area", d.floor_area);
			    if(frm.doc.rate_per_sq_ft){
                                 cur_frm.set_value("rent_amount", Math.round(frm.doc.rate_per_sq_ft * d.floor_area));
			    }
        	});
		frappe.model.get_value('Rate Item', {'parent': frm.doc.dzongkhag, 'building_category':frm.doc.building_category, 'location': frm.doc.location}, 'rate',
			  function(e) {
			    cur_frm.set_value("rate_per_sq_ft", e.rate);
			    if(frm.doc.floor_area){
				cur_frm.set_value("rent_amount", Math.round(frm.doc.floor_area * e.rate));
			    }
        	});
	}
}

