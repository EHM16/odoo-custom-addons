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

from odoo import api, fields, models


class PlannerEventDashboard(models.Model):
    _inherit = 'planner.event'

    @api.model
    def get_dashboard_data(self, date_from=None, date_to=None, type_ids=None,
                           planner_ids=None):
        """Single aggregated RPC feeding the OWL dashboard (PLAN §15,
        locked decision 12.14). All KPIs and chart series in one round-trip."""
        now = fields.Datetime.now()
        today = fields.Date.context_today(self)
        base_domain = [('stage_id.is_cancelled_stage', '=', False)]
        if date_from:
            base_domain.append(('date_start', '>=', date_from))
        if date_to:
            base_domain.append(('date_start', '<=', date_to))
        if type_ids:
            base_domain.append(('event_type_id', 'in', type_ids))
        if planner_ids:
            base_domain.append(('user_id', 'in', planner_ids))

        events = self.search(base_domain)
        booked = events.filtered(lambda e: e.stage_id.is_booked_stage)
        tentative = events - booked

        # ---- KPI row -------------------------------------------------------
        upcoming = events.filtered_domain([
            ('date_start', '>=', fields.Date.to_string(today)),
            ('date_start', '<=', fields.Date.to_string(today + timedelta(days=30)))
        ])
        pipeline_value = sum(
            tentative.sale_order_ids.filtered(
                lambda so: so.state in ('draft', 'sent')).mapped('amount_total'))
        quarter_start = today.replace(
            month=(today.month - 1) // 3 * 3 + 1, day=1)
        booked_this_quarter = booked.filtered(
            lambda e: e.date_start and e.date_start.date() >= quarter_start)
        booked_revenue = sum(booked_this_quarter.mapped('total_revenue'))
        # Same-length window before the quarter, for the trend badge
        prev_start = quarter_start - timedelta(days=92)
        prev_booked = self.search(base_domain).filtered(
            lambda e: e.stage_id.is_booked_stage and e.date_start
            and prev_start <= e.date_start.date() < quarter_start)
        prev_revenue = sum(prev_booked.mapped('total_revenue'))
        revenue_trend = (
            round((booked_revenue - prev_revenue) / prev_revenue * 100.0)
            if prev_revenue else 0)
        margins = booked.filtered('total_revenue').mapped('margin_pct')
        avg_margin = sum(margins) / len(margins) if margins else 0.0
        unpaid_lines = booked.payment_line_ids.filtered(
            lambda l: l.state not in ('paid',) and l.amount)
        overdue_lines = unpaid_lines.filtered(lambda l: l.state == 'overdue')
        unconfirmed_shifts = self.env['planner.event.staff.line'].search_count([
            ('state', 'in', ('draft', 'requested')),
            ('date_from', '>=', now),
            ('event_id.stage_id.is_cancelled_stage', '=', False),
        ])
        overdue_tasks = self.env['project.task'].search_count([
            ('planner_event_id', 'in', events.ids),
            ('date_deadline', '<', now),
            ('state', 'not in', ('1_done', '1_canceled')),
        ])

        # ---- Chart series ----------------------------------------------------
        month_keys = []
        cursor = today.replace(day=1) - timedelta(days=330)
        cursor = cursor.replace(day=1)
        for _i in range(12):
            month_keys.append(cursor.strftime('%Y-%m'))
            cursor = (cursor + timedelta(days=32)).replace(day=1)
        revenue_by_month = dict.fromkeys(month_keys, 0.0)
        cost_by_month = dict.fromkeys(month_keys, 0.0)
        for event in booked.filtered('date_start'):
            key = event.date_start.strftime('%Y-%m')
            if key in revenue_by_month:
                revenue_by_month[key] += event.total_revenue
                cost_by_month[key] += event.budget_total_contracted

        by_type, margin_by_type = {}, {}
        for event in events:
            type_name = event.event_type_id.name or self.env._('Undefined')
            by_type[type_name] = by_type.get(type_name, 0) + 1
            if event.stage_id.is_booked_stage and event.total_revenue:
                margin_by_type.setdefault(type_name, []).append(event.margin_pct)
        margin_by_type = {
            name: sum(values) / len(values) for name, values in margin_by_type.items()}

        by_source = {}
        for event in booked:
            source = event.lead_id.source_id.name or self.env._('Direct')
            by_source[source] = by_source.get(source, 0) + 1

        funnel = [
            {'stage': stage.name,
             'count': len(events.filtered(lambda e, s=stage: e.stage_id == s))}
            for stage in self.env['planner.event.stage'].search(
                [('is_cancelled_stage', '=', False)])
        ]

        week_load = []
        week_start = today - timedelta(days=today.weekday())
        for i in range(12):
            start = week_start + timedelta(weeks=i)
            end = start + timedelta(days=7)
            count = len(booked.filtered(
                lambda e: e.date_start and start <= e.date_start.date() < end))
            week_load.append({'label': start.strftime('%d %b'), 'count': count})

        # ---- Operational lists -----------------------------------------------
        attention = []
        for line in overdue_lines:
            attention.append({
                'event_id': line.event_id.id, 'event': line.event_id.name,
                'reason': self.env._('Overdue: %(name)s (%(amount).2f)',
                                     name=line.name, amount=line.amount)})
        for event in booked:
            pending_staff = event.staff_line_ids.filtered(
                lambda l: l.state in ('draft', 'requested'))
            if pending_staff and event.date_start and event.date_start <= now + timedelta(days=14):
                attention.append({
                    'event_id': event.id, 'event': event.name,
                    'reason': self.env._('%(count)s unconfirmed staff shift(s)',
                                         count=len(pending_staff))})
            reconfirm = event.vendor_line_ids.filtered('needs_reconfirmation')
            if reconfirm:
                attention.append({
                    'event_id': event.id, 'event': event.name,
                    'reason': self.env._('%(count)s vendor(s) need reconfirmation',
                                         count=len(reconfirm))})
            if event.headcount_locked and event.beo_version > 1:
                attention.append({
                    'event_id': event.id, 'event': event.name,
                    'reason': self.env._('Changed after lock (BEO v%(version)s)',
                                         version=event.beo_version)})

        upcoming_list = []
        for event in booked.filtered(
                lambda e: e.date_start and e.date_start >= now).sorted('date_start')[:8]:
            paid = sum(event.payment_line_ids.filtered(
                lambda l: l.state == 'paid').mapped('amount'))
            total = sum(event.payment_line_ids.mapped('amount'))
            staff_total = event.staff_line_ids.filtered(
                lambda l: l.state not in ('declined', 'cancelled'))
            staff_confirmed = staff_total.filtered(lambda l: l.state == 'confirmed')
            upcoming_list.append({
                'id': event.id,
                'name': event.name,
                'reference': event.reference,
                'date': fields.Datetime.to_string(event.date_start),
                'partner': event.partner_id.name,
                'venue': event.venue_id.name or '',
                'checklist_pct': round(event.task_progress),
                'payment_pct': round(paid / total * 100) if total else 0,
                'staff_pct': round(len(staff_confirmed) / len(staff_total) * 100)
                             if staff_total else 100,
            })

        return {
            'currency': {
                'symbol': self.env.company.currency_id.symbol,
                'position': self.env.company.currency_id.position,
            },
            'generated_at': fields.Datetime.context_timestamp(self, now).strftime('%Y-%m-%d %H:%M:%S'),
            'kpis': {
                'upcoming_events': len(upcoming),
                'pipeline_value': pipeline_value,
                'booked_revenue': booked_revenue,
                'revenue_trend': revenue_trend,
                'avg_margin_pct': round(avg_margin, 1),
                'outstanding_balance': sum(unpaid_lines.mapped('amount')),
                'overdue_count': len(overdue_lines),
                'unconfirmed_shifts': unconfirmed_shifts,
                'overdue_tasks': overdue_tasks,
            },
            'charts': {
                'months': month_keys,
                'revenue_by_month': [revenue_by_month[k] for k in month_keys],
                'cost_by_month': [cost_by_month[k] for k in month_keys],
                'by_type': by_type,
                'by_source': by_source,
                'funnel': funnel,
                'margin_by_type': margin_by_type,
                'week_load': week_load,
            },
            'attention': attention[:12],
            'upcoming': upcoming_list,
            'filters': {
                'types': [{'id': t.id, 'name': t.name}
                          for t in self.env['planner.event.type'].search([])],
                'planners': [{'id': u.id, 'name': u.name}
                             for u in events.user_id],
            },
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
