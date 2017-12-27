// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt
/*
--------------------------------------------------------------------------------------------------------------------------
Version          Author          CreatedOn          ModifiedOn          Remarks
------------ --------------- ------------------ -------------------  -----------------------------------------------------
1.0		          SHIV		                        27/12/2017         "Not Saved" indicator added.
--------------------------------------------------------------------------------------------------------------------------                                                                          
*/

// render
frappe.listview_settings['Travel Claim'] = {
	add_fields: ["employee_name", "employee", "grade", "balance_amount", "supervisor_approval", "docstatus", "claim_status"],
	has_indicator_for_draft: 1,
	get_indicator: function(doc) {

		// Ver 1.0 Begins, Following if condition added by SHIV on 27/12/2017
		if(doc.__islocal) {
				return ["Not Saved", "orange", ""]
		}
		// Ver 1.0 Ends
		
		if(doc.docstatus==0) {
			//if(doc.claim_status == "Rejected by Supervisor" || doc.claim_status == "Rejected by HR") {
			if(doc.claim_status != "") {
				return ["Claim Rejected", "red", "claim_status,like,Rejected"];
			}
			else if(doc.supervisor_approval==1) {
				return ["Supervisor Approved", "blue", "supervisor_approval,=,Yes|docstatus,=,0|claim_status,not like,Rejected"];
			}
			else {
				return ["Claim Draft", "orange", "docstatus,=,0|claim_status,not like,Rejected|supervisor_approval,!=,Yes"];
			}
		}

		if(doc.docstatus == 1) {
				return ["Claim Approved", "green", "docstatus,=,1"];
		}
	}
};
