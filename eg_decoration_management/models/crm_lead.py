from odoo import models, fields, api
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    decoration_street = fields.Char(string="Street")
    decoration_street2 = fields.Char(string="Street 2")
    decoration_city = fields.Char(string="City")
    decoration_state_id = fields.Many2one('res.country.state', string="State")
    decoration_zip = fields.Char(string="Zip")
    decoration_country_id = fields.Many2one('res.country', string="Country")

    decoration_event_type_id = fields.Many2one(comodel_name='decoration.event.type', string="Event Type")
    decoration_start = fields.Datetime(string="Event Start")
    decoration_end = fields.Datetime(string="Event End")
    decoration_package_ids = fields.Many2many(comodel_name='decoration.package', string='Decoration Package')
    decoration_guest = fields.Integer(string="Approx Guest")

    view_decoration_order_button = fields.Boolean(string="Decoration Order Created",
                                                  compute='_compute_view_create_decoration_order_button')
    decoration_order_count = fields.Integer(string="Decoration Orders", compute="_compute_decoration_order_count")

    def _compute_view_create_decoration_order_button(self):
        for rec in self:
            if rec.stage_id.is_won:
                rec.view_decoration_order_button = True
            else:
                rec.view_decoration_order_button = False

    def action_create_decoration_order(self):
        missing_fields = []
        if not self.decoration_start:
            missing_fields.append("Event Start Date")
        if not self.decoration_end:
            missing_fields.append("Event End Date")
        if not self.decoration_event_type_id:
            missing_fields.append("Event Type")
        if not self.decoration_street:
            missing_fields.append("Street")
        if not self.decoration_city:
            missing_fields.append("City")
        if not self.decoration_state_id:
            missing_fields.append("State")
        if not self.decoration_country_id:
            missing_fields.append("Country")
        if not self.decoration_guest:
            missing_fields.append("Approx Guests")
        if not self.decoration_package_ids:
            missing_fields.append("Decoration Package")
        if missing_fields:
            raise UserError("Please fill the following fields before creating a Decoration Order:\n\n• " + "\n• ".join(
                missing_fields))
        existing_decoration_order_id = self.env['decoration.order'].search([('lead_id', '=', self.id)], limit=1)
        if existing_decoration_order_id:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Decoration Order',
                'res_model': 'decoration.order',
                'res_id': existing_decoration_order_id.id,
                'view_mode': 'form',
                'target': 'current',
            }
        decoration_order_id = self.env['decoration.order'].create({
            'lead_id': self.id,
            'title': self.name or '',
            'partner_id': self.partner_id.id or False,
            'user_id': self.user_id.id or self.env.user.id,
            'event_type_id': self.decoration_event_type_id.id or False,
            'event_start': self.decoration_start.date() if self.decoration_start else False,
            'event_end': self.decoration_end.date() if self.decoration_end else False,
            'street': self.decoration_street or '',
            'street2': self.decoration_street2 or '',
            'city': self.decoration_city or '',
            'state_id': self.decoration_state_id.id or False,
            'zip': self.decoration_zip or '',
            'country_id': self.decoration_country_id.id or False,
            'decoration_package_ids': [(6, 0, self.decoration_package_ids.ids)],
            'approx_guests': self.decoration_guest or 1,
            'company_id': self.company_id.id or self.env.company.id,
            'currency_id': self.company_id.currency_id.id or self.env.company.currency_id.id,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Decoration Order',
            'res_model': 'decoration.order',
            'res_id': decoration_order_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_decoration_order(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Decoration Order',
            'res_model': 'decoration.order',
            'domain': [('lead_id', '=', self.id)],
            'view_mode': 'list,form',
            'target': 'current',
        }

    def _compute_decoration_order_count(self):
        for rec in self:
            rec.decoration_order_count = self.env['decoration.order'].search_count([('lead_id', '=', rec.id)])

    def action_sale_quotations_new(self):
        self.ensure_one()
        action = super().action_sale_quotations_new()
        if not self.decoration_package_ids:
            return action
        order_lines = []
        for package_id in self.decoration_package_ids:
            if not package_id.product_id:
                raise UserError(f"Decoration Package '{package_id.name}' has no linked Product.")
            order_lines.append((0, 0, {
                'product_id': package_id.product_id.id,
                'name': package_id.name,
                'product_uom_qty': 1,
                'price_unit': package_id.sales_price, }))

        ctx = dict(action.get('context', {}))
        ctx.update(
            {'default_order_line': order_lines, 'default_company_id': self.company_id.id or self.env.company.id, })
        action['context'] = ctx
        return action
