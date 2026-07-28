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


class PlannerEventStage(models.Model):
    _name = 'planner.event.stage'
    _description = 'Event Stage'
    _order = 'sequence, id'

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    fold = fields.Boolean(string='Folded in Kanban')
    description = fields.Text(translate=True)
    active = fields.Boolean(default=True)
    is_booked_stage = fields.Boolean(
        string='Booked Stage',
        help='Events in or after this stage are confirmed bookings: they act as '
             'conflict sources for venue and staff double-booking checks.')
    is_locked_stage = fields.Boolean(
        string='Final Details Lock',
        help='Entering this stage stamps the final headcount and meal totals '
             'used on the BEO.')
    is_closeout_stage = fields.Boolean(
        string='Closeout Stage',
        help='The daily cron moves events past their end date to the first '
             'closeout stage.')
    is_done_stage = fields.Boolean(string='Done Stage')
    is_cancelled_stage = fields.Boolean(string='Cancelled Stage')
    mail_template_id = fields.Many2one(
        'mail.template', string='Email Template',
        domain=[('model', '=', 'planner.event')],
        help='Sent to the customer when the event reaches this stage.')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
