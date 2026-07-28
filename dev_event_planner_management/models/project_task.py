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


class ProjectTask(models.Model):
    _inherit = 'project.task'

    planner_event_id = fields.Many2one(
        'planner.event', string='Planned Event',
        compute='_compute_planner_event_id', store=True, readonly=False,
        copy=False, index=True)
    checklist_template_line_id = fields.Many2one(
        'planner.checklist.template.line', string='Checklist Template Line',
        copy=False)

    @api.depends('project_id.planner_event_id')
    def _compute_planner_event_id(self):
        for task in self:
            if not task.planner_event_id and task.project_id.planner_event_id:
                task.planner_event_id = task.project_id.planner_event_id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
