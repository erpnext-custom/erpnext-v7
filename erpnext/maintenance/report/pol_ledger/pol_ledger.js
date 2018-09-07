// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["POL Ledger"] = {
	"filters": [
		{	
			"fieldname": "branch",
			"label": ("Branch"),
			"fieldtype": "Link",
			"options": "Branch",
			"width": "100",
			"reqd":1
		},
		{
			"fieldname":"from_date",
			"label": ("From Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd":1
		},
		{
			"fieldname":"to_date",
			"label": ("To Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd":1
		},
		{	
			"fieldname": "equipment",
			"label": ("Equipment"),
			"fieldtype": "Link",
			"options": "Equipment",
			"width": "100",
		},
	],
	"formatter":function (row, cell, value, columnDef, dataContext, default_formatter) {
                value = default_formatter(row, cell, value, columnDef, dataContext);
		/*console.log('---------------');
		console.log(columnDef);
		console.log(dataContext);
		console.log(value); */
		if(columnDef.name === "Transaction No"){
			console.log("TRans No: " + value);
		}
                if(columnDef.name === "Reference"){
		       console.log("Purpose : " + value);
		}
                /*if (value == "X") {
                        //var $value = $(value).css({"background-color": "rgb(208, 73, 73)", "font-weight": "bold"});
                        //value = $value.wrap("<p></p>").parent().html();
                        value = "<div style='color: rgb(208, 73, 73); background-color: rgb(208, 73, 73); width: 100%; height: 100%; border: -5;'>" + value + "</div>"
                                                                                        }*/
                        return value;
                 }
		
}
