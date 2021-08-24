# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from erpnext.accounts.utils import make_asset_transfer_gl
from frappe.utils import getdate, nowdate
from erpnext.assets.asset_utils import check_valid_asset_transfer
from erpnext.custom_utils import get_branch_from_cost_center

class AssetMovement(Document):
    def validate(self):
        self.assign_data()
        self.validate_asset()
        self.basic_validations()

    def basic_validations(self):
        if self.posting_date > nowdate():
            frappe.throw(_("Asset cannot be moved for Date after today"))

        if self.target_warehouse:
            self.validate_warehouses()

        if not self.target_custodian_type and not self.target_cost_center:
            frappe.throw("Target Custodian Type or Cost Center is Mandatory")

        if self.target_custodian_type:
            self.validate_custodian()
        
        if self.target_cost_center:
            if self.target_cost_center == self.current_cost_center:
                frappe.throw("Target and Source Cost Center cannot be same.")

    def assign_data(self):
        self.source_custodian_type = frappe.db.get_value("Asset", self.asset, "issued_to")
        if self.source_custodian_type == 'Employee':
            self.employee_source_custodian = frappe.db.get_value("Asset", self.asset, "issue_to_employee")
        if self.source_custodian_type == 'Desuup':
            self.desuup_source_custodian = frappe.db.get_value("Asset", self.asset, "issue_to_desuup")
        if self.source_custodian_type == 'Other':
            self.other_source_custodian = frappe.db.get_value("Asset", self.asset, "issue_to_other")

        self.current_cost_center = frappe.db.get_value("Asset", self.asset, "cost_center")
        self.current_business_activity = frappe.db.get_value("Asset", self.asset, "business_activity")	

    def validate_asset(self):
        status, company = frappe.db.get_value("Asset", self.asset, ["status", "company"])
        if status in ("Draft", "Scrapped", "Sold"):
            frappe.throw(_("{0} asset cannot be transferred").format(status))
            
        if company != self.company:
            frappe.throw(_("asset {0} does not belong to company {1}").format(self.asset, self.company))
            
    def validate_warehouses(self):
        if not self.source_warehouse:
            self.source_warehouse = frappe.db.get_value("Asset", self.asset, "warehouse")
        
        if self.source_warehouse == self.target_warehouse:
            frappe.throw(_("Source and Target Warehouse cannot be same"))

    def validate_custodian(self):
        if self.target_custodian_type == 'Employee':
            if not self.employee_target_custodian:
                frappe.throw("Employee Target Custodian cannot be blank")
        elif self.target_custodian_type == 'Desuup':
            if not self.desuup_target_custodian:
                frappe.throw("Desuup Target Custodian cannot be blank")
        else:
            if not self.other_target_custodian:
                frappe.throw("Other Target Custodian cannot be blank")

        if not self.source_custodian_type:
            self.source_custodian_type = frappe.db.get_value("Asset", self.asset, "issued_to")
            if self.source_custodian_type == 'Employee':
                self.employee_source_custodian = frappe.db.get_value("Asset", self.asset, "issue_to_employee")
            if self.source_custodian_type == 'Desuup':
                self.desuup_source_custodian = frappe.db.get_value("Asset", self.asset, "issue_to_desuup")
            if self.source_custodian_type == 'Other':
                self.other_source_custodian = frappe.db.get_value("Asset", self.asset, "issue_to_other")

        if self.source_custodian_type == self.target_custodian_type:
            if self.employee_target_custodian and self.employee_source_custodian == self.employee_target_custodian:
                frappe.throw(_("Source and Target Custodian cannot be same"))
            if self.desuup_target_custodian and self.desuup_source_custodian == self.desuup_target_custodian:
                frappe.throw(_("Source and Target Custodian cannot be same"))
            if self.other_target_custodian and self.other_source_custodian == self.other_target_custodian:
                frappe.throw(_("Source and Target Custodian cannot be same"))

    def before_submit(self):
        self.assign_data()
        if not self.target_business_activity:
            check_valid_asset_transfer(self.asset, self.posting_date)
    
    def on_submit(self):
        if self.target_business_activity:
            set_business_activity(self.asset, self.current_business_activity, self.target_business_activity, True)
            # return
        if self.target_warehouse:
            self.set_latest_warehouse_in_asset()

        if self.target_custodian_type:
            self.set_latest_custodian_in_asset()
            # if self.target_custodian_cost_center != self.current_cost_center:		
            # 	make_asset_transfer_gl(self, self.asset, self.posting_date, self.current_cost_center, self.target_custodian_cost_center)
        if self.target_cost_center:	
            self.set_latest_cc_in_asset()
            make_asset_transfer_gl(self, self.asset, self.posting_date, self.current_cost_center, self.target_cost_center)
    
    def on_cancel(self):
        if self.target_business_activity:
            set_business_activity(self.asset, self.current_business_activity, self.target_business_activity, False)
            # return

        check_valid_asset_transfer(self.asset, self.posting_date)
        self.check_depreciation_done()
        if self.target_warehouse:
            self.set_latest_warehouse_in_asset()
        if self.target_custodian_type:
            self.set_latest_custodian_in_asset(True)
        if self.target_cost_center:	
            self.set_latest_cc_in_asset(True)
        self.cancel_gl_entries()

    def check_depreciation_done(self):
        if self.target_custodian_type:
            if self.target_custodian_cost_center != self.current_cost_center:		
                self.check_gls()
        if self.target_cost_center:	
            self.check_gls()

    def check_gls(self):
        jes = frappe.db.sql("select je.name from `tabJournal Entry` je, `tabJournal Entry Account` jea where je.name = jea.parent and jea.reference_name = %s and je.posting_date between %s and %s", (self.asset, self.posting_date, getdate(nowdate())), as_dict=True)
        for a in jes:
            frappe.throw("Cannot cancel since asset depreciations had already taken place")

    def cancel_gl_entries(self):
        frappe.db.sql("delete from `tabGL Entry` where voucher_no = %s", self.name)
    
    def set_latest_warehouse_in_asset(self):
        latest_movement_entry = frappe.db.sql("""select target_warehouse from `tabAsset Movement`
            where asset=%s and docstatus=1 and company=%s
            order by posting_date desc limit 1""", (self.asset, self.company))
        
        if latest_movement_entry:
            warehouse = latest_movement_entry[0][0]
        else:
            warehouse = frappe.db.sql("""select source_warehouse from `tabAsset Movement`
                where asset=%s and docstatus=2 and company=%s
                order by posting_date asc limit 1""", (self.asset, self.company))[0][0]
        
        frappe.db.set_value("Asset", self.asset, "warehouse", warehouse)
    
    def set_latest_custodian_in_asset(self, cancel=None):
        #latest_movement_entry = frappe.db.sql("""select target_custodian from `tabAsset Movement`
        #	where asset=%s and docstatus=1 and company=%s
        #	order by posting_date desc limit 1""", (self.asset, self.company))
        #
        #if latest_movement_entry:
        #	custodian = latest_movement_entry[0][0]
        #else:
        #	custodian = frappe.db.sql("""select source_custodian from `tabAsset Movement`
        #		where asset=%s and docstatus=2 and company=%s
        #		order by posting_date asc limit 1""", (self.asset, self.company))[0][0]
        if cancel:
            if self.source_custodian_type == 'Employee':
                custodian_type = self.source_custodian_type
                custodian = self.employee_source_custodian
            elif self.source_custodian_type == 'Desuup':
                custodian_type = self.source_custodian_type
                custodian = self.desuup_source_custodian
            else:
                custodian_type = self.source_custodian_type
                custodian = self.other_source_custodian
            purpose = "Cancel"

        else:
            if self.target_custodian_type == 'Employee':
                custodian_type = self.target_custodian_type
                custodian = self.employee_target_custodian
            elif self.target_custodian_type == 'Desuup':
                custodian_type = self.target_custodian_type
                custodian = self.desuup_target_custodian
            else:
                custodian_type = self.target_custodian_type
                custodian = self.other_target_custodian
            purpose = "Submit"
        
        if self.target_cost_center and self.current_cost_center != self.target_cost_center:
            cost_center = self.target_cost_center
        else:
            cost_center = self.current_cost_center

        if custodian_type == 'Employee':
            frappe.db.set_value("Asset", self.asset, "issued_to", custodian_type)
            frappe.db.set_value("Asset", self.asset, "issue_to_employee", custodian)
            frappe.db.set_value("Asset", self.asset, "employee_name", (frappe.db.get_value("Employee",custodian,"employee_name")))
        elif custodian_type == 'Desuup':
            frappe.db.set_value("Asset", self.asset, "issued_to", custodian_type)
            frappe.db.set_value("Asset", self.asset, "issue_to_desuup", custodian)
            frappe.db.set_value("Asset", self.asset, "desuup_name", (frappe.db.get_value("Desuup",custodian,"desuup_name")))
        else:
            frappe.db.set_value("Asset", self.asset, "issued_to", custodian_type)
            frappe.db.set_value("Asset", self.asset, "issue_to_other", custodian)

        branch = get_branch_from_cost_center(cost_center)
        frappe.db.set_value("Asset", self.asset, "cost_center", cost_center)
        frappe.db.set_value("Asset", self.asset, "branch", branch)
        
        equipment = frappe.db.get_value("Equipment", {"asset_code": self.asset}, "name")
        if equipment:
            save_equipment(equipment, branch, self.posting_date, self.name, purpose)

    def set_latest_cc_in_asset(self, cancel=None):
        #latest_movement_entry = frappe.db.sql("""select target_cost_center from `tabAsset Movement`
        #	where asset=%s and docstatus=1 and company=%s
        #	order by posting_date desc limit 1""", (self.asset, self.company))
        #
        #if latest_movement_entry:
        #	cc = latest_movement_entry[0][0]
        #else:
        #	cc = frappe.db.sql("""select current_cost_center from `tabAsset Movement`
        #		where asset=%s and docstatus=2 and company=%s
        #		order by posting_date asc limit 1""", (self.asset, self.company))[0][0]
        if cancel:
            cc = self.current_cost_center
            purpose = "Cancel"
        else:
            cc = self.target_cost_center
            purpose = "Submit"

        branch = get_branch_from_cost_center(cc)
        frappe.db.set_value("Asset", self.asset, "cost_center", cc)
        frappe.db.set_value("Asset", self.asset, "branch", branch)

        equipment = frappe.db.get_value("Equipment", {"asset_code": self.asset}, "name")
        if equipment:
            save_equipment(equipment, branch, self.posting_date, self.name, purpose)

def set_business_activity(asset, source_ba, target_ba, submit):
    ba = source_ba
    if submit:
        ba = target_ba	
    asset = frappe.get_doc("Asset", asset)
    if not submit and target_ba != asset.business_activity:
        frappe.throw("Business Area Already Changed after this Transaction")
    asset.db_set("business_activity" , ba)
    equipment = frappe.db.get_value("Equipment", {"asset_code": asset.name}, "name")
    if equipment:
        equip = frappe.get_doc("Equipment", equipment)
        equip.db_set("business_activity", ba)

def save_equipment(equipment, branch, posting_date, ref_doc, purpose):
    if not frappe.db.get_single_value("Accounts Settings", "update_equipment_from_asset"):
        return
    equip = frappe.get_doc("Equipment", equipment)
    equip.branch = branch
    equip.create_equipment_history(branch, posting_date, ref_doc, purpose)
    equip.save()

