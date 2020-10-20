// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Rental Register"] = {
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
      fieldname: "month",
      label: __("Month"),
      fieldtype: "Select",
      options: ["", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"],
      default: "01",
    },
    {
      fieldname: "dzongkhag",
      label: "Dzongkhag",
      fieldtype: "Link",
      width: "80",
      options: "Dzongkhags",
    },
    {
      fieldname: "location",
      label: "Location",
      fieldtype: "Link",
      width: "80",
      options: "Locations",
    },
    {
      fieldname: "building_category",
      label: "Building Category",
      fieldtype: "Link",
      width: "80",
      options: "Building Category",
    },
    {
      fieldname: "ministry",
      label: "Ministry/Agency",
      fieldtype: "Link",
      width: "80",
      options: "Ministry and Agency",
    },
    {
      fieldtype: "Break",
    },
    {
      fieldname: "department",
      label: "Department",
      fieldtype: "Link",
      width: "80",
      options: "Tenant Department",
    },
    {
      fieldname: "town",
      label: "Town Category",
      fieldtype: "Link",
      width: "80",
      options: "Town Category",
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
      fieldname: "rental_official",
      label: __("Rental Official"),
      fieldtype: "Link",
      width: "80",
      options: "Employee",
    },
    {
      fieldname: "building_classification",
      label: __("Building Classification"),
      fieldtype: "Link",
      width: "90",
      options: "Building Classification"
    },
    {
      fieldname: "status",
      label: "Status",
      fieldtype: "Select",
      width: "80",
      options: ["Draft", "Submitted"],
      reqd: 1,
    },
  ],
};
