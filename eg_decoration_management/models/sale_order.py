from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    decoration_order_id = fields.Many2one(comodel_name='decoration.order', string='Decoration Order')
