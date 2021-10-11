// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Rental Revenue"] = {
  filters: [
    {
      fieldname: "fiscal_year",
      label: __("Fiscal Year"),
      fieldtype: "Link",
      options: "Fiscal Year",
      default: frappe.defaults.get_user_default("fiscal_year"),
      reqd: 1,
    },
    {
      fieldname: "from_month",
      label: "From Month",
      fieldtype: "Select",
      options: ["01"],
      default: "01",
    },
    {
      fieldname: "to_month",
      label: "To Month",
      fieldtype: "Select",
      options: ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"],
      reqd: 1,
    },
    {
      fieldname: "dzongkhag",
      label: "Dzongkhag",
      fieldtype: "Link",
      width: "80",
      options: "Dzongkhags",
      reqd: 1,
    },
    {
      fieldname: "building_category",
      label: "Building Category",
      fieldtype: "Link",
      width: "80",
      options: "Building Category",
      reqd: 1,
    },
    {
      fieldname: "status",
      label: "Status",
      fieldtype: "Select",
      width: "80",
      options: ["Draft", "Submitted"],
      default: "Submitted",
      reqd: 1,
    },
  ]
};

