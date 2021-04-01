// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Monthly Rental Collection and Dues"] = {
	"filters": [
		{
			fieldname:"amount_receivable",
			label:(""),
			fieldtype:"Select",
			width:"100",
			options:["Amount Received","Amount Receivable"],
			default: "Amount Received",
			reqd:1,
			"on_change": function(query_report){
				var Amount_receivable = query_report.get_values().amount_receivable;
				var Fiscal_year1 = query_report.filters_by_name["fiscal_year"];
				var Month = query_report.filters_by_name["month"];
				var Dzongkhags = query_report.filters_by_name["dzongkhag"];
				var Location = query_report.filters_by_name["location"];
				var building_catago = query_report.filters_by_name["building_category"];
				var ministry_agenc = query_report.filters_by_name["ministry_agency"];
				var Department = query_report.filters_by_name["department"];
				var Payment_mode = query_report.filters_by_name["payment_mode"];
				var Building_classification = query_report.filters_by_name["building_classification"];

				if (Amount_receivable == 'Amount Receivable') {
					//Fiscal_year1.toggle(true);   //added
					//Month.toggle(true);          //added
					//Dzongkhags.toggle(true);     //added
					//Location.toggle(true);       //added
					building_catago.toggle(false);
					ministry_agenc.toggle(false);
					//Department.toggle(true);     //added
					Payment_mode.toggle(false);
					Building_classification.toggle(false);
					building_catago.df.reqd = 0;
					ministry_agenc.df.reqd = 0;
					Payment_mode.df.reqd = 0;

				}
				else{
					Fiscal_year1.toggle(true); //added
					Month.toggle(true);        //added
					Dzongkhags.toggle(true);    //added
					Location.toggle(true);       //added
					building_catago.toggle(true);
					ministry_agenc.toggle(true);
					Department.toggle(true);     //added
					Payment_mode.toggle(true);
					Building_classification.toggle(true);
					Dzongkhag.toggle(true);
					building_catago.df.reqd = 0;
					ministry_agenc.df.reqd = 0;
					Payment_mode.df.reqd = 0;
				}
				query_report.refresh();
				building_catago.refresh();
				ministry_agenc.refresh();
				Payment_mode.refresh();
				Building_classification.refresh();
				Fiscal_year1.refresh();
				Month.refresh();
				Dzongkhags.refresh();
				Location.refresh();
				Department.refresh();

			}
		},
	
		{
			fieldname: "fiscal_year",
			label: __("Fiscal Year"),
			fieldtype: "Link",
			options: "Fiscal Year",
			default: frappe.defaults.get_user_default("fiscal_year"),
			reqd:1
		
			// "on_change": function(query_report){
			// 	var AAmount_receivable = query_report.get_values().amount_receivable;
			// 	var Fiscal_year = query_report.filters_by_name["fiscal_year"];

			// 	if (AAmount_receivable == 'Amount Receivable') {
			// 		Fiscal_year.toggle(false);
			// 	}
			// 	else{
			// 			Fiscal_year.toggle(true);
			// 	}
			// 	query_report.refresh();
			// 	Fiscal_year.refresh();
				
			// },
			// 	fieldname: "from_date",
			// 	label: __("From_Date"),
			// 	fieldtype: "Date",
			// 	width:"80"
		},
		{
			fieldname: "month",
			label: __("Month"),
			fieldtype: "Select",
			options: ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"],
			default: "01",
			reqd:1
		},
		// { //amended
		// 	fieldname: "status",
		// 	label: "Status",
		// 	fieldtype: "Select",
		// 	width: "80",
		// 	options: ["Draft", "Submitted"],
		// 	reqd: 1
		// },
		{
			fieldname:"dzongkhag",
			label: ("Dzongkhag"),
			fieldtype: "Link",
			width: "80",
			options:"Dzongkhags",
			reqd: 1
		},
		{
			fieldname:"location",
			label:("Location"),
			fieldtype:"Link",
			width:"80",
			options:"Locations"
		},
		{
			fieldname:"building_category",
			label:("Building Category"),
			fieldtype:"Link",
			width:"80",
			options:"Building Category"
		},
		{
			fieldtype:"Break"
		},
		{
			fieldname:"ministry_agency",
			label:("Ministry/Agency"),
			fieldtype:"Link",
			width:"80",
			options:"Ministry and Agency"
		},
		
		{
			fieldname:"department",
			label:("Department"),
			fieldtype:"Link",
			width:"80",
			options:"Tenant Department"
		},
		{
			fieldname: "payment_mode",
			label: __("Payment Mode"),
			fieldtype: "Select",
			width: "80",
			options: ["", "Cash", "Cheque", "ePMS", "mBOB", "mPay", "TPay", "NHDCL Office"],
			default: "",
		},
		{
			fieldname:"building_classification",
			label:("Building Classification"),
			fieldtype:"Link",
			width:"100",
			options:"Building Classification"
		}

	]
}
