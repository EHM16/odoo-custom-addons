from odoo import models, fields


class HREmployee(models.Model):
    _inherit = 'hr.employee'

    is_decoration_staff = fields.Boolean(string="Decoration Staff")
