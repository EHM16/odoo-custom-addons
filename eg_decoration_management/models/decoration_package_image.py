from odoo import models, fields, api
import base64
import os


class DecorationPackageImage(models.Model):
    _name = "decoration.package.image"
    _description = "Decoration Package Images"

    name = fields.Char(string="Title")
    image = fields.Image(string="Image")
    file_size = fields.Char(string="File Size")
    decoration_package_id = fields.Many2one(comodel_name='decoration.package', string='Decoration Package')

    @api.onchange("image")
    def _compute_file_size(self):
        for record in self:
            if record.image:
                image_data = base64.b64decode(record.image)

                file_size_kb = len(image_data) / 1024
                record.file_size = f"{round(file_size_kb, 2)} KB"
            else:
                record.file_size = ""
