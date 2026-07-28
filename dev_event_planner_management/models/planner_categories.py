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


class PlannerEventTag(models.Model):
    _name = 'planner.event.tag'
    _description = 'Event Tag'
    _order = 'name'

    name = fields.Char(required=True, translate=True)
    color = fields.Integer(string='Color Index')

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Tag name already exists.'),
    ]


class PlannerVendorCategory(models.Model):
    _name = 'planner.vendor.category'
    _description = 'Vendor Category'
    _order = 'sequence, name'

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Vendor category already exists.'),
    ]


class PlannerBudgetCategory(models.Model):
    _name = 'planner.budget.category'
    _description = 'Budget Category'
    _order = 'sequence, name'

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    is_cancellation_fee = fields.Boolean(
        string='Cancellation Fees Category',
        help='Vendor drop-out costs are reclassified to this category.')

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Budget category already exists.'),
    ]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
