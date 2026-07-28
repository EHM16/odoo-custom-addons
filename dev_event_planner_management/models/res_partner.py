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


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_event_vendor = fields.Boolean(string='Event Vendor')
    vendor_category_ids = fields.Many2many(
        'planner.vendor.category', string='Vendor Categories')
    vendor_rating = fields.Selection([
        ('1', 'Poor'),
        ('2', 'Fair'),
        ('3', 'Good'),
        ('4', 'Very Good'),
        ('5', 'Excellent'),
    ], string='Vendor Rating')
    vendor_notes = fields.Text(string='Vendor Notes')
    is_event_venue = fields.Boolean(string='Event Venue')
    venue_capacity = fields.Integer()
    venue_amenities = fields.Text()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
