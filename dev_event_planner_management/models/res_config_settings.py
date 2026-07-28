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


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    planner_block_venue_conflict = fields.Boolean(
        string='Block Venue Double-Booking',
        config_parameter='dev_event_planner_management.block_venue_conflict',
        help='When enabled, saving an event that overlaps a confirmed booking '
             'at the same venue is blocked instead of only warned about.')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
