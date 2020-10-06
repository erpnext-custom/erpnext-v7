// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Muster Roll Payment"] = {
  filters: [
    {
      fieldname: "branch",
      label: "Branch",
      fieldtype: "Link",
      width: "80",
      options: "Branch",
    },
  ],
};
