# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################
from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    planner_event_id = fields.Many2one(
        'planner.event', string='Planned Event', copy=False, index=True)

    def _action_confirm(self):
        # The event owns its project (locked decision 12.9): make sure it
        # exists before sale_project generates tasks, so service lines land in
        # the event project instead of spawning their own.
        for order in self.filtered('planner_event_id'):
            event = order.planner_event_id
            event._ensure_project()
            if not order.project_id:
                order.project_id = event.project_id
        res = super()._action_confirm()
        for order in self.filtered('planner_event_id'):
            order.planner_event_id._on_quote_confirmed(order)
        return res

    def _prepare_invoice(self):
        vals = super()._prepare_invoice()
        if self.planner_event_id:
            vals['planner_event_id'] = self.planner_event_id.id
        return vals

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
