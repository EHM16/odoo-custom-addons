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
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class PlannerPaymentScheme(models.Model):
    _name = 'planner.payment.scheme'
    _description = 'Payment Scheme'
    _order = 'name'

    name = fields.Char(required=True, translate=True)
    active = fields.Boolean(default=True)
    line_ids = fields.One2many('planner.payment.scheme.line', 'scheme_id', string='Installments')
    deposit_percentage = fields.Float(
        string='Deposit %', compute='_compute_deposit_percentage',
        help='Percentage of the first on-booking installment; used as the '
             'prepayment percentage on portal quotes.')

    @api.depends('line_ids.trigger', 'line_ids.percentage')
    def _compute_deposit_percentage(self):
        for scheme in self:
            booking_lines = scheme.line_ids.filtered(lambda l: l.trigger == 'booking')
            scheme.deposit_percentage = booking_lines[:1].percentage

    @api.constrains('line_ids')
    def _check_total_percentage(self):
        for scheme in self:
            total = sum(scheme.line_ids.mapped('percentage'))
            if scheme.line_ids and float_compare(total, 100.0, precision_digits=2):
                raise ValidationError(self.env._(
                    'Payment scheme "%(name)s" installments must total 100%% '
                    '(currently %(total).1f%%).', name=scheme.name, total=total))


class PlannerPaymentSchemeLine(models.Model):
    _name = 'planner.payment.scheme.line'
    _description = 'Payment Scheme Installment'
    _order = 'sequence, id'

    scheme_id = fields.Many2one('planner.payment.scheme', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    name = fields.Char(required=True, translate=True, default='Installment')
    percentage = fields.Float(string='%', required=True)
    trigger = fields.Selection([
        ('booking', 'On Booking'),
        ('before_event', 'Days Before Event'),
        ('after_event', 'Days After Event'),
    ], required=True, default='before_event')
    days_offset = fields.Integer(
        string='Days', default=0,
        help='Number of days before/after the event date the installment is due.')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
