from odoo import models, fields


class DecorationChecklistTemplate(models.Model):
    _name = "decoration.checklist.template"
    _description = "Decoration Checklist Template"

    name = fields.Char(string="Name")
    decoration_checklist_item_ids = fields.One2many(comodel_name="decoration.checklist.item",
                                                    inverse_name="checklist_template_id", string="Checklist Items")
