# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe

from frappe.model.document import Document

class Branch(Document):
        def validate(self):
                self.update_gis_policy_no()
                
        def update_gis_policy_no(self):
                # Following code commented due to performance issue
                '''
                prev_doc = frappe.get_doc(self.doctype, self.name)
                if prev_doc.gis_policy_number != self.gis_policy_number:
                        for e in frappe.get_all("Employee",["name"],{"branch": self.name}):
                             emp = frappe.get_doc("Employee",e.name)
                             emp.update({"gis_policy_number": self.gis_policy_number})
                             emp.save(ignore_permissions = True)
                '''

                prev_doc = frappe.get_doc(self.doctype, self.name)
                if prev_doc.gis_policy_number != self.gis_policy_number:
                        frappe.db.sql("""
                                update `tabEmployee`
                                set gis_policy_number = '{1}'
                                where branch = '{0}'
                        """.format(self.name, self.gis_policy_number))
