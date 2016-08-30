from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Employee and Attendance"),
			"items": [
				{
					"type": "doctype",
					"name": "Employee",
					"description": _("Employee records."),
				},
				{
					"type": "doctype",
					"name": "Attendance",
					"description": _("Attendance record."),
				},                                
				{
					"type": "doctype",
					"name": "Upload Attendance",
					"description":_("Upload attendance from a .csv file"),
					"hide_count": True
				},
			]
		},
		{
			"label": _("Recruitment"),
			"items": [
				{
					"type": "doctype",
					"name": "Job Opening",
					"description": _("Opening for a Job."),
				},                                
				{
					"type": "doctype",
					"name": "Job Applicant",
					"description": _("Applicant for a Job."),
				},
				{
					"type": "doctype",
					"name": "Offer Letter",
					"description": _("Offer candidate a Job."),
				},
			]
		},
		{
			"label": _("Leaves and Holiday"),
			"items": [
				{
					"type": "doctype",
					"name": "Leave Application",
					"description": _("Applications for leave."),
				},
				{
					"type": "doctype",
					"name": "Leave Block List",
					"description": _("Block leave applications by department.")
				},                                
				{
					"type": "doctype",
					"name": "Leave Allocation",
					"description": _("Allocate leaves for a period.")
				},
				{
					"type": "doctype",
					"name":"Leave Type",
					"description": _("Type of leaves like casual, sick etc."),
				},                                
				{
					"type": "doctype",
					"name": "Holiday List",
					"description": _("Holiday master.")
				},                                
			]
		},
		{
			"label": _("Payroll"),
			"items": [
				{
					"type": "doctype",
					"name": "Salary Structure",
					"description": _("Salary template master.")
				},                                
				{
					"type": "doctype",
					"name": "Salary Slip",
					"description": _("Monthly salary statement."),
				},
                                {
					"type": "doctype",
					"name": "Salary Increment",
					"description": _("Annual Salary Increments"),
				},
				{
					"type": "doctype",
					"name": "Process Payroll",
					"label": _("Process Payroll"),
					"description":_("Generate Salary Slips"),
					"hide_count": True
				},
                                {
					"type": "doctype",
					"name": "Process Increment",
					"label": _("Process Increments"),
					"description":_("Generate Salary Increments"),
					"hide_count": True
				},
				{
					"type": "doctype",
					"name": "Salary Component",
					"label": _("Salary Components"),
					"description": _("Earnings, Deductions and other Salary components")
				}
			]
		},
		{
			"label": _("Travel Claim & Leave Encashment"),
			"items": [
				{
					"type": "doctype",
					"name": "Expense Claim",
                                        "label": _("Travel Expense Claim"),
					"description": _("Claims for company expense."),
				},
				{
					"type": "doctype",
					"name": "Leave Encashment",
					"description": _("Leave Encashment"),
				},
				{
					"type": "doctype",
					"name": "Expense Claim Type",
                                        "label": _("Travel Expense Claim Types"),
					"description": _("Types of Expense Claim.")
				},
				{
					"type": "doctype",
					"name": "Leave Encashment Settings",
					"description": _("Leave Encashment Settings"),
				},                                
			]
		},
                {
			"label": _("Training & Development"),
			"items": [
				{
					"type": "doctype",
					"name": "Training And Development",
					"description": _("Traning & Development Master."),
				},                  
			]
		},
		{
			"label": _("Appraisals"),
			"items": [
				{
					"type": "doctype",
					"name": "Appraisal",
					"description": _("Performance appraisal."),
				},
				{
					"type": "doctype",
					"name": "Appraisal Template",
					"description": _("Template for performance appraisals.")
				},                                                                
			]
		},
		{
			"label": _("Tools"),
			"icon": "icon-wrench",
			"items": [
                                {
					"type": "doctype",
					"name": "Employee Attendance Tool",
					"label": _("Employee Attendance Tool"),
					"description":_("Mark Attendance for multiple employees"),
					"hide_count": True
				},
                                {
					"type": "doctype",
					"name": "Leave Control Panel",
					"label": _("Leave Allocation Tool"),
					"description":_("Allocate leaves for the year."),
					"hide_count": True
				},
			]
		},
		{
			"label": _("Setup"),
			"icon": "icon-cog",
			"items": [
				{
					"type": "doctype",
					"name": "HR Settings",
					"description": _("Settings for HR Module")
				},
                                {
					"type": "doctype",
					"name": "Salary Tax",
					"description": _("Salary Tax Master")
				},
				{
					"type": "doctype",
					"name": "Branch",
					"description": _("Organization Branch Master.")
				},
				{
					"type": "doctype",
					"name": "Department",
					"description": _("Organization Department master.")
				},
				{
					"type": "doctype",
					"name": "Division",
					"description": _("Organization Division master.")
				},
				{
					"type": "doctype",
					"name": "Section",
					"description": _("Organization Section master.")
				},                                                                
				{
					"type": "doctype",
					"name": "Employment Type",
					"description": _("Types of employment (permanent, contract, intern etc.).")
				},
				{
					"type": "doctype",
					"name": "Designation",
					"description": _("Employee designation (e.g. CEO, Director etc.).")
				},
                                {
					"type": "doctype",
					"name": "Employee Group",
					"description": _("Employee Group Master.")
				},
                                {
					"type": "doctype",
					"name": "Employee Sub-Group",
					"description": _("Employee Sub-Group/Grade Master.")
				},
                                {
					"type": "doctype",
					"name": "Terms of Reference",
					"description": _("Employee Sub-Group/Grade Master.")
				},
                                {
					"type": "doctype",
					"name": "Dzongkhags",
					"description": _("Dzongkhag Master.")
				},
                                {
					"type": "doctype",
					"name": "Gewogs",
					"description": _("Gewog Master.")
				},
                                {
					"type": "doctype",
					"name": "Villages",
					"description": _("Village Master.")
				},
			]
		},
		{
			"label": _("Reports"),
			"icon": "icon-list",
			"items": [
                                {
					"type": "report",
					"is_query_report": True,
					"name": "Monthly Salary Register",
					"doctype": "Salary Slip"
				},
                                {
					"type": "report",
					"is_query_report": True,
					"name": "Loan Report",
                                        "label": _("Loan Report"),
					"doctype": "Salary Slip"
				},
                                {
					"type": "report",
					"is_query_report": True,
					"name": "SSS Report",
                                        "label": _("Salary Saving Scheme Report"),
					"doctype": "Salary Slip"
				},
                                {
					"type": "report",
					"is_query_report": True,
					"name": "PF Report",
                                        "label": _("PF Report"),
					"doctype": "Salary Slip"
				},
                                {
					"type": "report",
					"is_query_report": True,
					"name": "GIS Report",
                                        "label": _("GIS Report"),
					"doctype": "Salary Slip"
				},
                                {
					"type": "report",
					"is_query_report": True,
					"name": "Tax and Health Report",
                                        "label": _("Salary Tax & Health Contribution Report"),
					"doctype": "Salary Slip"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Employee Leave Balance",
					"doctype": "Leave Application"
				},
                                {
					"type": "report",
					"is_query_report": True,
					"name": "Leave Encashment Report",
                                        "label": _("Leave Encashment Report"),
					"doctype": "Leave Encashment"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Employee Birthday",
					"doctype": "Employee"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Employees working on a holiday",
					"doctype": "Employee"
				},
				{
					"type": "report",
					"name": "Employee Information",
					"doctype": "Employee"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Monthly Attendance Sheet",
					"doctype": "Attendance"
				},

			]
		},
	]
