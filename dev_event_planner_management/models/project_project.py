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


class ProjectProject(models.Model):
    _inherit = 'project.project'

    planner_event_id = fields.Many2one(
        'planner.event', string='Planned Event', copy=False, index=True)

    def action_view_planner_event(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'planner.event',
            'view_mode': 'form',
            'res_id': self.planner_event_id.id,
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
