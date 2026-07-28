# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################
from datetime import timedelta

import pytz

from odoo import api, fields, models
from odoo.addons.base.models.res_partner import _tz_get
from odoo.exceptions import UserError


class PlannerEvent(models.Model):
    _name = 'planner.event'
    _description = 'Planned Event'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'date_start, id'

    _mail_post_access = 'read'

    # Identity
    name = fields.Char(string='Event Title', required=True, tracking=True)
    reference = fields.Char(
        string='Reference', copy=False, readonly=True, default=lambda self: self.env._('New'))
    event_type_id = fields.Many2one('planner.event.type', string='Event Type', tracking=True)
    tag_ids = fields.Many2many('planner.event.tag', string='Tags')
    color = fields.Integer(string='Color Index')
    company_id = fields.Many2one(
        'res.company', required=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one(related='company_id.currency_id')
    active = fields.Boolean(default=True)

    # Client
    partner_id = fields.Many2one(
        'res.partner', string='Client', required=True, tracking=True)
    contact_person = fields.Char(string='Contact Person')
    client_phone = fields.Char(related='partner_id.phone', string='Client Phone')
    client_email = fields.Char(related='partner_id.email', string='Client Email')
    lead_id = fields.Many2one('crm.lead', string='Source Opportunity', copy=False)

    # When / where
    date_start = fields.Datetime(string='Event Start', required=True, tracking=True)
    date_end = fields.Datetime(string='Event End', tracking=True)
    date_tz = fields.Selection(
        _tz_get, string='Timezone', default=lambda self: self.env.user.tz or 'UTC')
    venue_id = fields.Many2one(
        'res.partner', string='Venue', tracking=True,
        domain=[('is_event_venue', '=', True)])
    venue_capacity = fields.Integer(related='venue_id.venue_capacity')
    on_site_contact = fields.Char(string='On-site Contact')

    # Scale / lock
    guest_count_expected = fields.Integer(string='Expected Guests', tracking=True)
    guest_count_final = fields.Integer(string='Final Guests', readonly=True, copy=False)
    headcount_locked = fields.Boolean(readonly=True, copy=False)
    locked_meal_totals = fields.Text(readonly=True, copy=False)
    beo_version = fields.Integer(default=1, copy=False, readonly=True)

    # Pipeline
    stage_id = fields.Many2one(
        'planner.event.stage', string='Stage', tracking=True, copy=False,
        group_expand='_read_group_expand_full',
        default=lambda self: self.env['planner.event.stage'].search([], limit=1))
    kanban_state = fields.Selection([
        ('normal', 'In Progress'),
        ('done', 'Ready for Next Stage'),
        ('blocked', 'Blocked'),
    ], default='normal', copy=False, required=True)
    is_booked = fields.Boolean(related='stage_id.is_booked_stage')
    is_locked = fields.Boolean(related='stage_id.is_locked_stage')
    is_cancelled = fields.Boolean(related='stage_id.is_cancelled_stage')
    user_id = fields.Many2one(
        'res.users', string='Lead Planner', tracking=True,
        default=lambda self: self.env.user)
    coordinator_id = fields.Many2one('res.users', string='Coordinator', tracking=True)
    date_booked = fields.Datetime(string='Booked on', readonly=True, copy=False)

    # Money
    analytic_account_id = fields.Many2one(
        'account.analytic.account', string='Analytic Account', copy=False)
    budget_line_ids = fields.One2many('planner.event.budget.line', 'event_id')
    budget_total_estimated = fields.Monetary(
        compute='_compute_budget_totals', string='Estimated Cost')
    budget_total_contracted = fields.Monetary(
        compute='_compute_budget_totals', string='Contracted Cost')
    budget_total_actual = fields.Monetary(
        compute='_compute_budget_totals', string='Actual Cost')
    total_revenue = fields.Monetary(
        compute='_compute_revenue', store=True, string='Revenue',
        help='Untaxed total of confirmed sale orders.')
    margin = fields.Monetary(
        compute='_compute_revenue', store=True, string='Projected Margin')
    margin_pct = fields.Float(compute='_compute_margin_pct', string='Margin %')

    # Links
    sale_order_ids = fields.One2many('sale.order', 'planner_event_id', copy=False)
    sale_order_count = fields.Integer(compute='_compute_counts')
    project_id = fields.Many2one('project.project', string='Project', copy=False)
    task_ids = fields.One2many('project.task', 'planner_event_id', string='Checklist Tasks')
    task_count = fields.Integer(compute='_compute_task_stats')
    task_progress = fields.Float(compute='_compute_task_stats', string='Checklist Progress')
    purchase_order_ids = fields.One2many('purchase.order', 'planner_event_id', copy=False)
    purchase_order_count = fields.Integer(compute='_compute_counts')
    invoice_ids = fields.Many2many(
        'account.move', compute='_compute_invoice_ids', string='Invoices')
    invoice_count = fields.Integer(compute='_compute_invoice_ids')
    meeting_count = fields.Integer(compute='_compute_meeting_count')

    # Lines
    vendor_line_ids = fields.One2many('planner.event.vendor.line', 'event_id', copy=True)
    staff_line_ids = fields.One2many('planner.event.staff.line', 'event_id', copy=False)
    schedule_line_ids = fields.One2many('planner.event.schedule.line', 'event_id', copy=True)
    guest_ids = fields.One2many('planner.event.guest', 'event_id', copy=False)
    guest_count = fields.Integer(compute='_compute_guest_stats', string='Guest List Size')
    guest_seats = fields.Integer(compute='_compute_guest_stats', string='Guest Seats')
    meal_choice_ids = fields.One2many('planner.meal.choice', 'event_id', copy=False)
    payment_line_ids = fields.One2many('planner.event.payment.line', 'event_id', copy=False)
    payment_schedule_warning = fields.Char(compute='_compute_payment_schedule_warning')

    # Conflicts
    conflict_message = fields.Char(compute='_compute_conflicts')

    survey_sent = fields.Boolean(copy=False, readonly=True)

    # Notes
    note = fields.Html(string='Notes')
    internal_brief = fields.Html(string='Internal Brief')
    properties = fields.Properties(
        'Properties', definition='event_type_id.properties_definition', copy=True)

    # ------------------------------------------------------------------
    # Computes
    # ------------------------------------------------------------------
    @api.depends('budget_line_ids.amount_estimated', 'budget_line_ids.amount_contracted',
                 'budget_line_ids.amount_actual')
    def _compute_budget_totals(self):
        for event in self:
            event.budget_total_estimated = sum(event.budget_line_ids.mapped('amount_estimated'))
            event.budget_total_contracted = sum(event.budget_line_ids.mapped('amount_contracted'))
            event.budget_total_actual = sum(event.budget_line_ids.mapped('amount_actual'))

    @api.depends('sale_order_ids.state', 'sale_order_ids.amount_untaxed',
                 'budget_line_ids.amount_contracted')
    def _compute_revenue(self):
        for event in self:
            confirmed = event.sale_order_ids.filtered(lambda so: so.state == 'sale')
            event.total_revenue = sum(confirmed.mapped('amount_untaxed'))
            event.margin = event.total_revenue - event.budget_total_contracted

    @api.depends('total_revenue', 'margin')
    def _compute_margin_pct(self):
        for event in self:
            event.margin_pct = (
                event.margin / event.total_revenue * 100.0 if event.total_revenue else 0.0)

    @api.depends('sale_order_ids', 'purchase_order_ids')
    def _compute_counts(self):
        for event in self:
            event.sale_order_count = len(event.sale_order_ids)
            event.purchase_order_count = len(event.purchase_order_ids)

    @api.depends('task_ids', 'task_ids.state', 'task_ids.stage_id', 'task_ids.stage_id.fold', 'task_ids.is_closed')
    def _compute_task_stats(self):
        for event in self:
            tasks = event.task_ids
            total = len(tasks)
            closed = len(tasks.filtered(lambda t: t.is_closed or t.state in ('1_done', '1_canceled') or t.stage_id.fold))
            event.task_count = total
            event.task_progress = (closed / total * 100.0) if total else 0.0

    @api.depends('sale_order_ids.invoice_ids', 'payment_line_ids.invoice_ids')
    def _compute_invoice_ids(self):
        for event in self:
            invoices = (event.sale_order_ids.invoice_ids
                        | event.payment_line_ids.invoice_ids)
            event.invoice_ids = invoices
            event.invoice_count = len(invoices)

    def _compute_meeting_count(self):
        counts = dict(self.env['calendar.event']._read_group(
            [('res_model', '=', self._name), ('res_id', 'in', self.ids)],
            ['res_id'], ['__count']))
        for event in self:
            event.meeting_count = counts.get(event.id, 0)

    @api.depends('guest_ids.seats')
    def _compute_guest_stats(self):
        for event in self:
            event.guest_count = len(event.guest_ids)
            event.guest_seats = sum(event.guest_ids.mapped('seats'))

    @api.depends('payment_line_ids.amount', 'sale_order_ids.state',
                 'sale_order_ids.amount_total')
    def _compute_payment_schedule_warning(self):
        for event in self:
            event.payment_schedule_warning = False
            confirmed_total = sum(event.sale_order_ids.filtered(
                lambda so: so.state == 'sale').mapped('amount_total'))
            schedule_total = sum(event.payment_line_ids.mapped('amount'))
            if (event.payment_line_ids and confirmed_total
                    and event.currency_id.compare_amounts(schedule_total, confirmed_total)):
                event.payment_schedule_warning = self.env._(
                    'Payment schedule total (%(schedule)s) differs from confirmed '
                    'order total (%(orders)s).',
                    schedule=f'{schedule_total:,.2f}', orders=f'{confirmed_total:,.2f}')

    @api.depends('venue_id', 'date_start', 'date_end', 'stage_id')
    def _compute_conflicts(self):
        for event in self:
            event.conflict_message = False
            if not event.venue_id or not event.date_start or event.is_cancelled:
                continue
            confirmed, tentative = event._get_overlapping_events()
            if confirmed or tentative:
                event.conflict_message = self.env._(
                    'This date at %(venue)s already has %(confirmed)s confirmed and '
                    '%(tentative)s tentative event(s).',
                    venue=event.venue_id.name,
                    confirmed=len(confirmed), tentative=len(tentative))

    def _get_overlapping_events(self):
        """Return (confirmed, tentative) planner.event recordsets overlapping
        self at the same venue. Cancelled events never count."""
        self.ensure_one()
        date_end = self.date_end or self.date_start
        others = self.search([
            ('id', '!=', self.id),
            ('venue_id', '=', self.venue_id.id),
            ('stage_id.is_cancelled_stage', '=', False),
            ('date_start', '<=', date_end),
            '|', ('date_end', '>=', self.date_start),
            '&', ('date_end', '=', False), ('date_start', '>=', self.date_start),
        ])
        confirmed = others.filtered(lambda e: e.stage_id.is_booked_stage)
        return confirmed, others - confirmed

    @api.constrains('venue_id', 'date_start', 'date_end', 'stage_id')
    def _check_venue_double_booking(self):
        """Blocking only when the settings toggle is on, and only against
        confirmed bookings (locked decisions 12.3 and 12.11)."""
        block = self.env['ir.config_parameter'].sudo().get_param(
            'dev_event_planner_management.block_venue_conflict')
        if not block:
            return
        for event in self:
            if not event.venue_id or not event.date_start or event.is_cancelled:
                continue
            confirmed, _tentative = event._get_overlapping_events()
            if confirmed:
                raise UserError(self.env._(
                    '%(venue)s is already booked on this date by the confirmed '
                    'event "%(event)s". Venue double-booking is blocked in the '
                    'Event Planner settings.',
                    venue=event.venue_id.name, event=confirmed[0].name))

    # ------------------------------------------------------------------
    # CRUD / stage workflow
    # ------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('reference') or vals['reference'] == self.env._('New'):
                vals['reference'] = self.env['ir.sequence'].next_by_code(
                    'planner.event') or self.env._('New')
        events = super().create(vals_list)
        for event in events:
            event._apply_event_type_templates()
            if event.stage_id.is_booked_stage:
                event._action_book()
        return events

    def write(self, vals):
        stage_before = {event: event.stage_id for event in self}
        if 'stage_id' in vals and 'kanban_state' not in vals:
            vals['kanban_state'] = 'normal'
        res = super().write(vals)
        if 'stage_id' in vals:
            for event in self:
                if event.stage_id != stage_before[event]:
                    event._on_stage_changed(stage_before[event])
        return res

    def _on_stage_changed(self, previous_stage):
        self.ensure_one()
        stage = self.stage_id
        if stage.is_booked_stage and not self.date_booked:
            self._action_book()
        if stage.is_locked_stage and not self.headcount_locked:
            self._action_lock()
        elif not stage.is_locked_stage and self.headcount_locked:
            self.headcount_locked = False
            
        if stage.is_done_stage:
            self._check_done_gate()
        if stage.mail_template_id:
            self.message_post_with_source(
                stage.mail_template_id,
                subtype_xmlid='mail.mt_comment',
            )

    def _check_done_gate(self):
        self.ensure_one()
        if self.env.user.has_group('dev_event_planner_management.group_event_planner_manager'):
            return
        unpaid = self.payment_line_ids.filtered(lambda l: l.state not in ('paid',))
        open_tasks = self.project_id.task_ids.filtered(
            lambda t: t.state not in ('1_done', '1_canceled'))
        if unpaid or open_tasks:
            raise UserError(self.env._(
                'This event still has %(unpaid)s unpaid installment(s) and %(tasks)s '
                'open task(s). Only an Event Planner Manager can move it to Done.',
                unpaid=len(unpaid), tasks=len(open_tasks)))

    def _action_book(self):
        for event in self:
            event.date_booked = event.date_booked or fields.Datetime.now()
            event._ensure_analytic_account()
            event._ensure_project()
            event._generate_checklist()
            event._generate_payment_lines()
        booked_stage = self.env['planner.event.stage'].search(
            [('is_booked_stage', '=', True)], limit=1)
        for event in self.filtered(lambda e: not e.stage_id.is_booked_stage):
            if booked_stage:
                event.stage_id = booked_stage

    def _action_lock(self):
        for event in self:
            meal_totals = event._get_meal_totals()
            event.write({
                'headcount_locked': True,
                'guest_count_final': event.guest_seats or event.guest_count_expected,
                'locked_meal_totals': '\n'.join(
                    f'{name}: {qty}' for name, qty in meal_totals) or False,
            })
            event.message_post(body=self.env._(
                'Final details locked: %(count)s guests.',
                count=event.guest_count_final))

    def _get_meal_totals(self):
        self.ensure_one()
        totals = self.env['planner.event.guest']._read_group(
            [('event_id', '=', self.id), ('meal_choice_id', '!=', False)],
            ['meal_choice_id'], ['seats:sum'])
        return [(choice.name, seats) for choice, seats in totals]

    def _on_quote_confirmed(self, order):
        """Called by sale.order._action_confirm: booking happens the moment the
        client signs and pays the quote on the portal."""
        self.ensure_one()
        if not self.stage_id.is_booked_stage:
            self._action_book()
        else:
            self._generate_checklist()
        self.message_post(body=self.env._(
            'Quotation %(order)s confirmed.', order=order.name))

    def _log_post_lock_change(self, description):
        """Called by line models when a locked event is modified."""
        for event in self.filtered('headcount_locked'):
            if event.stage_id.is_done_stage or event.is_cancelled:
                continue
            event.beo_version += 1
            event.message_post(body=self.env._(
                'Changed after lock (BEO now v%(version)s): %(description)s',
                version=event.beo_version, description=description))

    # ------------------------------------------------------------------
    # Generation helpers (event owns its project — locked decision 12.9)
    # ------------------------------------------------------------------
    def _ensure_analytic_account(self):
        for event in self.filtered(lambda e: not e.analytic_account_id):
            plan, _other = self.env['account.analytic.plan']._get_all_plans()
            event.analytic_account_id = self.env['account.analytic.account'].create({
                'name': f'{event.reference} - {event.name}',
                'plan_id': plan.id,
                'partner_id': event.partner_id.id,
                'company_id': event.company_id.id,
            })
        return self.analytic_account_id

    def _ensure_project(self):
        for event in self.filtered(lambda e: not e.project_id):
            event._ensure_analytic_account()
            template = event.event_type_id.project_template_id
            name = f'{event.reference} - {event.name}'
            if template:
                project = template.copy({
                    'name': name,
                    'partner_id': event.partner_id.id,
                    'active': True,
                })
                # Template tasks keep their names but must not keep old deadlines
                project.task_ids.date_deadline = False
            else:
                type_ids = []
                for s_name in ['To Do', 'In Progress', 'Done']:
                    stage = self.env['project.task.type'].search([('name', '=', s_name)], limit=1)
                    if not stage:
                        stage = self.env['project.task.type'].sudo().create({'name': s_name})
                    type_ids.append(stage.id)
                    
                project = self.env['project.project'].create({
                    'name': name,
                    'partner_id': event.partner_id.id,
                    'privacy_visibility': 'portal',
                    'type_ids': [(6, 0, type_ids)],
                })
            project.write({
                'planner_event_id': event.id,
                'account_id': event.analytic_account_id.id,
                'date_start': fields.Date.context_today(event),
                'date': event.date_start.date() if event.date_start else False,
            })
            event.project_id = project
        return self.project_id

    def _generate_checklist(self):
        for event in self:
            template_lines = event.event_type_id.checklist_template_ids
            if not template_lines:
                continue
            event._ensure_project()
            
            # Retroactively fix project stages if missing
            if not event.project_id.type_ids:
                type_ids = []
                for s_name in ['To Do', 'In Progress', 'Done']:
                    stage = self.env['project.task.type'].search([('name', '=', s_name)], limit=1)
                    if not stage:
                        stage = self.env['project.task.type'].sudo().create({'name': s_name})
                    type_ids.append(stage.id)
                event.project_id.type_ids = [(6, 0, type_ids)]
                # Fix existing tasks in 'None'
                tasks_without_stage = event.project_id.task_ids.filtered(lambda t: not t.stage_id)
                if tasks_without_stage and type_ids:
                    tasks_without_stage.write({'stage_id': type_ids[0]})
                    
            existing = self.env['project.task'].with_context(active_test=False).search(
                [('planner_event_id', '=', event.id),
                 ('checklist_template_line_id', 'in', template_lines.ids)])
            done_templates = existing.mapped('checklist_template_line_id')
            vals_list = []
            
            first_stage_id = event.project_id.type_ids[0].id if event.project_id.type_ids else False
            
            for line in template_lines - done_templates:
                vals_list.append({
                    'name': line.name,
                    'description': line.description or False,
                    'project_id': event.project_id.id,
                    'planner_event_id': event.id,
                    'checklist_template_line_id': line.id,
                    'date_deadline': event.date_start + timedelta(days=line.days_offset),
                    'user_ids': [(6, 0, event._resolve_checklist_user(line).ids)],
                    'sequence': line.sequence,
                    'stage_id': first_stage_id,
                })
            if vals_list:
                self.env['project.task'].create(vals_list)

    def _resolve_checklist_user(self, template_line):
        self.ensure_one()
        if template_line.responsible_role == 'user' and template_line.user_id:
            return template_line.user_id
        if template_line.responsible_role == 'coordinator':
            return self.coordinator_id or self.user_id
        return self.user_id

    def _generate_payment_lines(self):
        for event in self.filtered(lambda e: not e.payment_line_ids):
            scheme = event.event_type_id.payment_scheme_id
            if not scheme:
                continue
            self.env['planner.event.payment.line'].create([{
                'event_id': event.id,
                'name': line.name,
                'sequence': line.sequence,
                'percentage': line.percentage,
                'trigger': line.trigger,
                'days_offset': line.days_offset,
            } for line in scheme.line_ids])
        self.payment_line_ids._compute_due_date()

    def _apply_event_type_templates(self):
        """On creation: copy the run-of-show skeleton from the event type.
        Template hours are local to the event's timezone — midnight is
        computed in date_tz and converted back to UTC for storage."""
        for event in self:
            if event.schedule_line_ids or not event.event_type_id.schedule_template_ids:
                continue
            tz = pytz.timezone(event.date_tz or self.env.user.tz or 'UTC')
            local_start = pytz.UTC.localize(event.date_start).astimezone(tz)
            base_local = local_start.replace(hour=0, minute=0, second=0, microsecond=0)

            def to_utc(day_offset, hour):
                local = tz.normalize(
                    base_local + timedelta(days=day_offset, hours=hour))
                return local.astimezone(pytz.UTC).replace(tzinfo=None)

            self.env['planner.event.schedule.line'].create([{
                'event_id': event.id,
                'name': line.name,
                'sequence': line.sequence,
                'location': line.location,
                'notes': line.notes,
                'time_start': to_utc(line.day_offset, line.hour_start),
                'time_end': to_utc(line.day_offset, line.hour_end),
            } for line in event.event_type_id.schedule_template_ids])

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def action_book(self):
        self._action_book()

    def action_generate_checklist(self):
        self._ensure_project()
        self._generate_checklist()
        return self.action_view_tasks()

    def action_create_quotation(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': self.env._('New Quotation'),
            'res_model': 'planner.event.quote.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_event_id': self.id},
        }

    def action_reschedule(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': self.env._('Reschedule Event'),
            'res_model': 'planner.event.reschedule.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_event_id': self.id},
        }

    def action_cancel_event(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': self.env._('Cancel Event'),
            'res_model': 'planner.event.cancel.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_event_id': self.id},
        }

    def action_duplicate_event(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': self.env._('Duplicate Event'),
            'res_model': 'planner.event.duplicate.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_event_id': self.id},
        }

    def action_view_quotations(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': self.env._('Quotations'),
            'res_model': 'sale.order',
            'view_mode': 'list,form',
            'domain': [('planner_event_id', '=', self.id)],
            'context': {
                'default_planner_event_id': self.id,
                'default_partner_id': self.partner_id.id,
            },
        }

    def action_view_project(self):
        self.ensure_one()
        self._ensure_project()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.project',
            'view_mode': 'form',
            'res_id': self.project_id.id,
        }

    def action_view_tasks(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': self.env._('Checklist'),
            'res_model': 'project.task',
            'view_mode': 'kanban,list,form,calendar',
            'domain': [('planner_event_id', '=', self.id)],
            'context': {
                'default_project_id': self.project_id.id,
                'default_planner_event_id': self.id,
            },
        }

    def action_view_purchase_orders(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': self.env._('Vendor Orders'),
            'res_model': 'purchase.order',
            'view_mode': 'list,form',
            'domain': [('planner_event_id', '=', self.id)],
            'context': {'default_planner_event_id': self.id},
        }

    def action_view_invoices(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': self.env._('Invoices'),
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.invoice_ids.ids)],
        }

    def action_view_meetings(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': self.env._('Meetings'),
            'res_model': 'calendar.event',
            'view_mode': 'calendar,list,form',
            'domain': [('res_model', '=', self._name), ('res_id', '=', self.id)],
            'context': {
                'default_res_model': self._name,
                'default_res_id': self.id,
                'default_partner_ids': [(4, self.partner_id.id)],
                'default_name': self.name,
            },
        }

    def action_view_guests(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': self.env._('Guest List'),
            'res_model': 'planner.event.guest',
            'view_mode': 'list,form',
            'domain': [('event_id', '=', self.id)],
            'context': {'default_event_id': self.id},
        }

    def action_send_beo(self):
        """Render the BEO PDF and post it to all operational parties: vendors
        on active lines, confirmed staff and the coordinator (PLAN §5)."""
        self.ensure_one()
        report = self.env.ref('dev_event_planner_management.action_report_beo')
        pdf, _type = self.env['ir.actions.report']._render_qweb_pdf(report, self.ids)
        attachment = self.env['ir.attachment'].create({
            'name': f'BEO-v{self.beo_version}-{self.reference.replace("/", "-")}.pdf',
            'type': 'binary',
            'raw': pdf,
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/pdf',
        })
        vendors = self.vendor_line_ids.filtered(
            lambda l: l.state not in ('cancelled',)).vendor_id
        staff_partners = self.staff_line_ids.filtered(
            lambda l: l.state == 'confirmed').employee_id.work_contact_id
        coordinator = self.coordinator_id.partner_id
        recipients = vendors | staff_partners | coordinator
        self.message_post(
            body=self.env._(
                'BEO version %(version)s distributed to %(count)s recipient(s).',
                version=self.beo_version, count=len(recipients)),
            partner_ids=recipients.ids,
            attachment_ids=attachment.ids,
            subtype_xmlid='mail.mt_comment',
        )
        return True

    # ------------------------------------------------------------------
    # Crons (PLAN §6 — all exclude cancelled events)
    # ------------------------------------------------------------------
    @api.model
    def _cron_move_to_closeout(self):
        """Past events move In Progress -> Closeout, never straight to Done:
        final balance and vendor bills are still open there (PLAN §12 / review
        finding 6)."""
        closeout = self.env['planner.event.stage'].search(
            [('is_closeout_stage', '=', True)], limit=1)
        if not closeout:
            return
        past = self.search([
            ('date_end', '!=', False),
            ('date_end', '<', fields.Datetime.now()),
            ('stage_id.is_booked_stage', '=', True),
            ('stage_id.is_closeout_stage', '=', False),
            ('stage_id.is_done_stage', '=', False),
            ('stage_id.is_cancelled_stage', '=', False),
        ])
        past.write({'stage_id': closeout.id})

    @api.model
    def _cron_send_surveys(self):
        """Feedback survey N days after the event ends — triggered by the date,
        not by the Done stage."""
        template = self.env.ref(
            'dev_event_planner_management.mail_template_survey_invite',
            raise_if_not_found=False)
        if not template:
            return
        threshold = fields.Datetime.now() - timedelta(days=2)
        events = self.search([
            ('survey_sent', '=', False),
            ('date_end', '!=', False),
            ('date_end', '<=', threshold),
            ('stage_id.is_cancelled_stage', '=', False),
            ('stage_id.is_booked_stage', '=', True),
            ('event_type_id.default_survey_id', '!=', False),
        ])
        for event in events.filtered(lambda e: e.partner_id.email):
            template.send_mail(event.id, force_send=False)
            event.survey_sent = True

    def _compute_access_url(self):
        super()._compute_access_url()
        for event in self:
            event.access_url = f'/my/events/{event.id}'

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
