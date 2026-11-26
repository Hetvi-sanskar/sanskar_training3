# Copyright (c) 2026, Hetvi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate


class ServiceRequest(Document):
    def validate(self):
        if self.sla_date and self.request_date and getdate(self.sla_date) < getdate(self.request_date):
            frappe.throw("SLA Date cannot be before Request Date")
        for row in self.spare_parts:
            row.amount = (row.qty or 0) * (row.rate or 0)