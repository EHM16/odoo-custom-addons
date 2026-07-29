from odoo import models, fields


class DecorationChecklistItem(models.Model):
    _name = "decoration.checklist.item"
    _description = "Decoration Checklist Item"

    sequence = fields.Integer(default=10)
    name = fields.Char(string="Name")
    checklist_template_id = fields.Many2one(comodel_name="decoration.checklist.template", string="Checklist Template")
    display_type = fields.Selection([('line_section', "Section"), ('line_note', "Note")], default=False)
