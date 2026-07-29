from odoo import models, fields


class DecorationEventType(models.Model):
    _name = "decoration.event.type"
    _description = "Event Decoration Type"

    name = fields.Char(string="Event Type")
    image = fields.Image(string="Image")
    description = fields.Text(string="Description")
