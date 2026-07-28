# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################
from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    planner_event_id = fields.Many2one(
        'planner.event', string='Planned Event', copy=False, index=True)

    def _prepare_invoice(self):
        vals = super()._prepare_invoice()
        if self.planner_event_id:
            vals['planner_event_id'] = self.planner_event_id.id
        return vals

    def button_confirm(self):
        res = super().button_confirm()
        # Confirming the vendor's order books the vendor on the event
        vendor_lines = self.env['planner.event.vendor.line'].search([
            ('purchase_order_id', 'in', self.ids),
            ('state', 'in', ('to_source', 'requested', 'quoted')),
        ])
        vendor_lines.with_context(skip_lock_log=True).write({'state': 'booked'})
        return res


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        # Vendor costs post to the event's analytic account for the per-event P&L
        for line in lines:
            event = line.order_id.planner_event_id
            if event and not line.analytic_distribution:
                account = event._ensure_analytic_account()
                line.analytic_distribution = {str(account.id): 100}
        return lines

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
