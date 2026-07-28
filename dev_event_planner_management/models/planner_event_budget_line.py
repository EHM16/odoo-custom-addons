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


class PlannerEventBudgetLine(models.Model):
    _name = 'planner.event.budget.line'
    _description = 'Event Budget Line'
    _order = 'event_id, category_id, id'

    event_id = fields.Many2one(
        'planner.event', required=True, ondelete='cascade', index=True)
    company_id = fields.Many2one(related='event_id.company_id')
    currency_id = fields.Many2one(related='event_id.currency_id')
    category_id = fields.Many2one('planner.budget.category', string='Category', required=True)
    description = fields.Char()
    vendor_line_id = fields.Many2one(
        'planner.event.vendor.line', string='Vendor Booking',
        domain="[('event_id', '=', event_id)]")
    amount_estimated = fields.Monetary(string='Estimated')
    amount_contracted = fields.Monetary(
        string='Contracted', compute='_compute_amounts', store=True, readonly=False,
        help='Defaults from the linked vendor booking; can be overridden.')
    amount_actual = fields.Monetary(
        string='Actual', compute='_compute_amounts', store=True, readonly=False,
        help='Defaults from posted vendor bills; can be overridden.')
    variance = fields.Monetary(compute='_compute_variance', string='Variance')

    @api.depends('vendor_line_id.contracted_cost', 'vendor_line_id.amount_billed',
                 'vendor_line_id.state')
    def _compute_amounts(self):
        for line in self:
            vendor = line.vendor_line_id
            if vendor and vendor.state != 'cancelled':
                line.amount_contracted = vendor.contracted_cost
                line.amount_actual = vendor.amount_billed
            else:
                line.amount_contracted = line.amount_contracted or 0.0
                line.amount_actual = line.amount_actual or 0.0

    @api.depends('amount_estimated', 'amount_actual', 'amount_contracted')
    def _compute_variance(self):
        for line in self:
            actual_or_contracted = line.amount_actual or line.amount_contracted
            line.variance = line.amount_estimated - actual_or_contracted

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
