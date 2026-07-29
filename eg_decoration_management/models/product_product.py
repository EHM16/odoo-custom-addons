from odoo import models, fields, api
from random import randint


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _get_default_color(self):
        return randint(1, 11)

    is_decoration_product = fields.Boolean("Is Decoration Product")
    is_decoration_package = fields.Boolean("Is Decoration Package")
    is_additional_item = fields.Boolean("Is Additional Item")
    is_additional_service = fields.Boolean("Is Additional Service")

    color = fields.Integer(string="Color", default=_get_default_color)
