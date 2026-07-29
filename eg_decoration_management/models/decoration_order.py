from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
import base64


class DecorationOrder(models.Model):
    _name = 'decoration.order'
    _description = 'Decoration Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Name', default=lambda self: 'New')
    title = fields.Char(string='Title')
    state = fields.Selection([('new', 'New'), ('progress', 'In Progress'), ('done', 'Completed'), ('cancel', 'Cancel')],
                             default='new', tracking=True)
    lead_id = fields.Many2one(comodel_name='crm.lead', string='Lead')
    partner_id = fields.Many2one(comodel_name='res.partner', string='Customer')
    phone = fields.Char(related='partner_id.phone', readonly=False)
    email = fields.Char(related='partner_id.email', readonly=False)

    event_type_id = fields.Many2one(comodel_name='decoration.event.type', string='Event Type')
    event_start = fields.Date(string='Event Start')
    event_end = fields.Date(string='Event End')

    street = fields.Char(string="Street")
    street2 = fields.Char(string="Street2")
    city = fields.Char(string="City")
    state_id = fields.Many2one(comodel_name="res.country.state", string="State")
    zip = fields.Char(string="ZIP")
    country_id = fields.Many2one(comodel_name="res.country", string="Country")

    user_id = fields.Many2one(comodel_name='res.users', string='Event Leader')
    company_id = fields.Many2one(comodel_name='res.company', default=lambda self: self.env.company)
    approx_guests = fields.Integer(string='Approx Guests')
    currency_id = fields.Many2one(comodel_name='res.currency', default=lambda self: self.env.company.currency_id)
    decoration_package_ids = fields.Many2many(comodel_name='decoration.package', string='Decoration Package')

    decoration_package_item_ids = fields.One2many(comodel_name='decoration.package.item',
                                                  inverse_name='decoration_order_id', string='Decoration Package Item')

    additional_item_ids = fields.One2many(comodel_name='decoration.additional.item', inverse_name='decoration_order_id',
                                          string='Additional Items')

    additional_service_ids = fields.One2many(comodel_name='decoration.additional.service',
                                             inverse_name='decoration_order_id', string='Additional Service')

    employee_ids = fields.Many2many(comodel_name='hr.employee', string='Decoration Staffs')

    total_additional_item_amount = fields.Monetary(string='Additional Item Total', compute='_compute_totals',
                                                   store=True)
    total_additional_service_amount = fields.Monetary(string='Additional Service Total', compute='_compute_totals',
                                                      store=True)
    total_amount = fields.Monetary(string='Grand Total', compute='_compute_totals', store=True)
    total_package_item_amount = fields.Monetary(string='Package Item Total', compute='_compute_package_item_total',
                                                store=True)
    sale_order_count = fields.Integer(string='Sale Orders', compute='_compute_sale_order_count')
    delivery_count = fields.Integer(string="Deliveries", compute="_compute_delivery_count")

    @api.model_create_multi
    def create(self, vals_list):
        for val in vals_list:
            val['name'] = self.env['ir.sequence'].next_by_code('decoration.order') or 'New'
        return super(DecorationOrder, self).create(vals_list)

    def action_state_progress(self):
        for rec in self:
            rec.state = 'progress'

    def action_state_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    def action_create_sale_order(self):
        for rec in self:
            if not rec.decoration_package_item_ids:
                raise ValidationError("No package items to create a Sale Order.")
            if not rec.partner_id:
                raise ValidationError("Please select a customer.")

            sale_order_id = self.env['sale.order'].create({
                'partner_id': rec.partner_id.id,
                'origin': rec.name,
                'decoration_order_id': rec.id,
                'company_id': rec.company_id.id,
            })

            sale_order_line_vals_list = []
            for package_item_id in rec.decoration_package_item_ids:
                if package_item_id.display_type:
                    sale_order_line_vals_list.append({
                        'order_id': sale_order_id.id,
                        'display_type': package_item_id.display_type,
                        'name': package_item_id.name,
                    })
                else:
                    if not package_item_id.product_id:
                        raise ValidationError("Please select a product on every package item line.")
                    if not package_item_id.uom_id:
                        raise ValidationError(
                            f"Please select a unit of measure for {package_item_id.product_id.display_name}."
                        )

                    sale_order_line_vals_list.append({
                        'order_id': sale_order_id.id,
                        'product_id': package_item_id.product_id.id,
                        'name': package_item_id.name or package_item_id.product_id.display_name,
                        'product_uom_qty': package_item_id.quantity,
                        'product_uom_id': package_item_id.uom_id.id,
                        'price_unit': package_item_id.price_unit,
                    })

            self.env['sale.order.line'].create(sale_order_line_vals_list)
            rec.state = 'done'

            return {
                'type': 'ir.actions.act_window',
                'name': 'Sale Order',
                'res_model': 'sale.order',
                'res_id': sale_order_id.id,
                'view_mode': 'form',
            }

    def action_create_additional_item_sale_order(self):
        for rec in self:
            if not rec.partner_id:
                raise ValidationError("Please select a customer.")

            additional_item_ids = rec.additional_item_ids.filtered(
                lambda additional_item_id: not additional_item_id.item_sale_order_id
            )

            if not additional_item_ids:
                raise ValidationError(
                    "There are no pending additional items. Sale Orders have already been created for all items."
                )

            for additional_item_id in additional_item_ids:
                if not additional_item_id.product_id:
                    raise ValidationError("Please select a product on every additional item line.")
                if not additional_item_id.uom_id:
                    raise ValidationError(
                        f"Please select a unit of measure for {additional_item_id.product_id.display_name}."
                    )

            sale_order_id = self.env['sale.order'].create({
                'partner_id': rec.partner_id.id,
                'origin': rec.name,
                'decoration_order_id': rec.id,
                'company_id': rec.company_id.id,
            })

            sale_order_line_vals_list = []
            for additional_item_id in additional_item_ids:
                sale_order_line_vals_list.append({
                    'order_id': sale_order_id.id,
                    'product_id': additional_item_id.product_id.id,
                    'name': additional_item_id.name or additional_item_id.product_id.display_name,
                    'product_uom_qty': additional_item_id.quantity,
                    'product_uom_id': additional_item_id.uom_id.id,
                    'price_unit': additional_item_id.price_unit,
                })

            self.env['sale.order.line'].create(sale_order_line_vals_list)
            additional_item_ids.write({
                'item_sale_order_id': sale_order_id.id,
            })

            return {
                'type': 'ir.actions.act_window',
                'name': 'Sale Order',
                'res_model': 'sale.order',
                'res_id': sale_order_id.id,
                'view_mode': 'form',
            }

    def action_create_additional_service_sale_order(self):
        for rec in self:
            if not rec.partner_id:
                raise ValidationError("Please select a customer.")

            additional_service_ids = rec.additional_service_ids.filtered(
                lambda additional_service_id: not additional_service_id.service_sale_order_id
            )

            if not additional_service_ids:
                raise ValidationError(
                    "There are no pending additional services. Sale Orders have already been created for all services."
                )

            for additional_service_id in additional_service_ids:
                if not additional_service_id.product_id:
                    raise ValidationError("Please select a product on every additional service line.")

            sale_order_id = self.env['sale.order'].create({
                'partner_id': rec.partner_id.id,
                'origin': rec.name,
                'decoration_order_id': rec.id,
                'company_id': rec.company_id.id,
            })

            sale_order_line_vals_list = []
            for additional_service_id in additional_service_ids:
                sale_order_line_vals_list.append({
                    'order_id': sale_order_id.id,
                    'product_id': additional_service_id.product_id.id,
                    'name': additional_service_id.name or additional_service_id.product_id.display_name,
                    'product_uom_qty': 1.0,
                    'product_uom_id': additional_service_id.product_id.uom_id.id,
                    'price_unit': additional_service_id.price_unit,
                })

            self.env['sale.order.line'].create(sale_order_line_vals_list)
            additional_service_ids.write({
                'service_sale_order_id': sale_order_id.id,
            })

            return {
                'type': 'ir.actions.act_window',
                'name': 'Sale Order',
                'res_model': 'sale.order',
                'res_id': sale_order_id.id,
                'view_mode': 'form',
            }

    @api.onchange('decoration_package_ids')
    def _onchange_decoration_package_ids(self):
        if self.decoration_package_ids:
            lines = [(5, 0, 0)]
            for decoration_package_id in self.decoration_package_ids:
                for package_item_id in decoration_package_id.package_item_ids:
                    lines.append((0, 0, {
                        'decoration_package_id': decoration_package_id.id,
                        'display_type': package_item_id.display_type,
                        'product_id': package_item_id.product_id.id,
                        'name': package_item_id.name or package_item_id.product_id.display_name,
                        'quantity': package_item_id.quantity,
                        'price_unit': package_item_id.price_unit,
                        'uom_id': package_item_id.uom_id.id,
                    }))
            self.decoration_package_item_ids = lines
        else:
            self.decoration_package_item_ids = [(5, 0, 0)]
            return

    @api.depends('additional_item_ids.subtotal', 'additional_service_ids.price_unit')
    def _compute_totals(self):
        for rec in self:
            rec.total_additional_item_amount = sum(line.subtotal for line in rec.additional_item_ids)
            rec.total_additional_service_amount = sum(line.price_unit for line in rec.additional_service_ids)
            rec.total_amount = (rec.total_additional_item_amount + rec.total_additional_service_amount)

    @api.depends('decoration_package_item_ids.total_price')
    def _compute_package_item_total(self):
        for rec in self:
            rec.total_package_item_amount = sum(line.total_price for line in rec.decoration_package_item_ids)

    def _compute_sale_order_count(self):
        for rec in self:
            rec.sale_order_count = self.env['sale.order'].search_count([('decoration_order_id', '=', rec.id)])

    def action_view_sale_order(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sale Order',
            'res_model': 'sale.order',
            'domain': [('decoration_order_id', '=', self.id)],
            'view_mode': 'list,form',
        }

    def _compute_delivery_count(self):
        for rec in self:
            sale_order_ids = self.env['sale.order'].search([('decoration_order_id', '=', rec.id)])
            picking_ids = sale_order_ids.mapped('picking_ids')
            rec.delivery_count = len(picking_ids)

    def action_view_delivery_orders(self):
        sale_order_ids = self.env['sale.order'].search([('decoration_order_id', '=', self.id)])
        picking_ids = sale_order_ids.mapped('picking_ids')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Delivery Orders',
            'res_model': 'stock.picking',
            'view_mode': 'list,form',
            'domain': [('id', 'in', picking_ids.ids)],
        }

    def action_send_decoration_order_mail(self):
        self.ensure_one()
        if not self.partner_id:
            raise UserError("Please select a Customer before sending email.")
        report_id = self.env.ref('eg_decoration_management.report_decoration_order_custom')
        pdf_content, _ = report_id._render_qweb_pdf(report_id.report_name, [self.id])
        attachment_id = self.env['ir.attachment'].create({
            'name': f"Decoration_Order_{self.name}.pdf",
            'type': 'binary',
            'datas': base64.b64encode(pdf_content),
            'res_model': 'decoration.order',
            'res_id': self.id,
            'mimetype': 'application/pdf',
        })
        subject = f"Decoration Order - {self.name}"
        body_html = f"""
            <p>Dear {self.partner_id.name},</p>
            <p>Please find attached the details of your decoration order.</p>
            <ul>
                <li><strong>Order Reference:</strong> {self.name}</li>
                <li><strong>Event:</strong> {self.title or '-'}</li>
                <li><strong>Event Type:</strong> {self.event_type_id.name or '-'}</li>
                <li><strong>Event Start:</strong> {self.event_start or '-'}</li>
                <li><strong>Event End:</strong> {self.event_end or '-'}</li>
                <li><strong>Total Amount:</strong> {self.total_package_item_amount + self.total_amount} {self.currency_id.symbol}</li>
            </ul>
            <p>If you need any changes or clarification, please contact us.</p>
            <p>Thanks & Regards,<br/>
            {self.env.user.name}</p>
        """
        action = self.env['ir.actions.actions']._for_xml_id('mail.action_email_compose_message_wizard')
        action['context'] = {
            'default_model': 'decoration.order',
            'default_res_ids': [self.id],
            'default_composition_mode': 'comment',
            'default_partner_ids': [(6, 0, [self.partner_id.id])],
            'default_subject': subject,
            'default_attachment_ids': [(6, 0, [attachment_id.id])],
            'default_body': body_html,
        }

        return action
