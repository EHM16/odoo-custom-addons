from collections import defaultdict
from dateutil.relativedelta import relativedelta
from odoo import _, api, fields, models


class DecorationDashboard(models.AbstractModel):
    _name = "decoration.dashboard"
    _description = "Event Decoration Management Dashboard"

    @api.model
    def _event_amount(self, decoration_order_id):
        return ((decoration_order_id.total_package_item_amount or 0.0) + (decoration_order_id.total_amount or 0.0))

    @api.model
    def _compare(self, current_value, previous_value):
        if not previous_value:
            return {"value": 100 if current_value else 0,
                    "direction": "up" if current_value else "flat",
                    "label": _("vs. previous period"), }

        percentage_value = round(((current_value - previous_value) / previous_value) * 100)
        return {"value": abs(percentage_value),
                "direction": ("up" if percentage_value > 0 else "down" if percentage_value < 0 else "flat"),
                "label": _("vs. previous period"),
                }

    @api.model
    def _to_date(self, date_value, fallback_date):
        if not date_value:
            return fallback_date
        try:
            return fields.Date.to_date(date_value)
        except (TypeError, ValueError):
            return fallback_date

    @api.model
    def _event_date_domain(self, start_date, end_date):
        return [("event_start", ">=", start_date), ("event_start", "<=", end_date)]

    @api.model
    def get_dashboard_data(self, start_date=False, end_date=False):
        today_date = fields.Date.context_today(self)
        default_start_date = today_date.replace(day=1)
        default_end_date = today_date + relativedelta(day=31)
        selected_start_date = self._to_date(start_date, default_start_date)
        selected_end_date = self._to_date(end_date, default_end_date)
        if selected_start_date > selected_end_date:
            selected_start_date, selected_end_date = (selected_end_date, selected_start_date,)

        selected_period_days = (selected_end_date - selected_start_date).days + 1
        previous_end_date = selected_start_date - relativedelta(days=1)
        previous_start_date = previous_end_date - relativedelta(days=selected_period_days - 1)

        selected_decoration_order_domain = self._event_date_domain(selected_start_date, selected_end_date)
        previous_decoration_order_domain = self._event_date_domain(previous_start_date, previous_end_date, )
        active_state_values = ["new", "progress"]
        value_state_values = ["new", "progress", "done"]

        selected_value_order_domain = selected_decoration_order_domain + [("state", "in", value_state_values)]
        previous_value_order_domain = previous_decoration_order_domain + [("state", "in", value_state_values)]
        selected_active_order_domain = selected_decoration_order_domain + [("state", "in", active_state_values)]
        previous_active_order_domain = previous_decoration_order_domain + [("state", "in", active_state_values)]

        selected_decoration_order_ids = self.env["decoration.order"].search(selected_value_order_domain)
        previous_decoration_order_ids = self.env["decoration.order"].search(previous_value_order_domain)
        selected_order_value = sum(
            self._event_amount(decoration_order_id) for decoration_order_id in selected_decoration_order_ids)
        previous_order_value = sum(
            self._event_amount(decoration_order_id) for decoration_order_id in previous_decoration_order_ids)

        selected_guest_count = sum(selected_decoration_order_ids.mapped("approx_guests"))
        previous_guest_count = sum(previous_decoration_order_ids.mapped("approx_guests"))

        active_installation_count = self.env["decoration.order"].search_count(selected_active_order_domain)
        previous_active_installation_count = self.env["decoration.order"].search_count(previous_active_order_domain)
        selected_lead_start_datetime = fields.Datetime.to_datetime(selected_start_date)
        selected_lead_end_datetime = fields.Datetime.to_datetime(selected_end_date + relativedelta(days=1))
        open_decoration_lead_count = self.env["crm.lead"].search_count(
            [("active", "=", True), ("decoration_start", ">=", selected_lead_start_datetime),
             ("decoration_start", "<", selected_lead_end_datetime), ("probability", "<", 100), ])

        status_values = [("new", _("New"), "new"), ("progress", _("In Progress"), "progress"),
                         ("done", _("Completed"), "done"), ("cancel", _("Cancelled"), "cancelled"), ]
        status_rows = []
        total_status_count = self.env["decoration.order"].search_count(selected_decoration_order_domain) or 1
        for state_value, state_label, state_css_class in status_values:
            status_count = self.env["decoration.order"].search_count(
                selected_decoration_order_domain + [("state", "=", state_value)])
            status_rows.append({"key": state_value,
                                "label": state_label,
                                "count": status_count,
                                "percent": round((status_count / total_status_count) * 100),
                                "class": state_css_class, })

        event_decoration_order_ids = self.env["decoration.order"].search(selected_active_order_domain,
                                                                         order="event_start asc, id asc", limit=7, )
        event_rows = []
        decoration_order_state_labels = dict(self.env["decoration.order"]._fields["state"].selection)
        for decoration_order_id in event_decoration_order_ids:
            event_rows.append({
                "id": decoration_order_id.id,
                "name": decoration_order_id.name or _("New"),
                "title": decoration_order_id.title or _("Untitled project"),
                "customer": (decoration_order_id.partner_id.name or _("Walk-in customer")),
                "event_type": (decoration_order_id.event_type_id.name or _("Decoration project")),
                "date": (fields.Date.to_string(
                    decoration_order_id.event_start) if decoration_order_id.event_start else False),
                "is_today": decoration_order_id.event_start == today_date,
                "guests": decoration_order_id.approx_guests or 0,
                "staff_count": len(decoration_order_id.employee_ids),
                "state": decoration_order_state_labels.get(decoration_order_id.state, decoration_order_id.state),
                "state_key": decoration_order_id.state,
                "value": self._event_amount(decoration_order_id),
            })

        trend_decoration_order_ids = self.env["decoration.order"].search(
            selected_decoration_order_domain + [("state", "!=", "cancel")])
        event_type_data = defaultdict(lambda: {"count": 0, "value": 0.0})
        package_data = defaultdict(lambda: {"count": 0, "value": 0.0})

        for decoration_order_id in trend_decoration_order_ids:
            event_type_name = (decoration_order_id.event_type_id.name or _("Other Events"))
            decoration_order_value = self._event_amount(decoration_order_id)
            event_type_data[event_type_name]["count"] += 1
            event_type_data[event_type_name]["value"] += decoration_order_value
            decoration_package_ids = decoration_order_id.decoration_package_ids
            if not decoration_package_ids:
                package_data[_("Custom Project")]["count"] += 1
                package_data[_("Custom Project")]["value"] += decoration_order_value

            for decoration_package_id in decoration_package_ids:
                package_name = decoration_package_id.name or _("Untitled Package")
                package_data[package_name]["count"] += 1
                package_data[package_name]["value"] += decoration_order_value

        max_event_type_count = max([event_type_value["count"] for event_type_value in event_type_data.values()] or [1])
        event_type_rows = [{"name": event_type_name,
                            "count": event_type_value["count"],
                            "value": event_type_value["value"],
                            "percent": round((event_type_value["count"] / max_event_type_count) * 100), }
                           for event_type_name, event_type_value in event_type_data.items()]
        event_type_rows.sort(key=lambda event_type_row: (event_type_row["count"], event_type_row["value"]),
                             reverse=True, )
        max_package_count = max([package_value["count"] for package_value in package_data.values()] or [1])
        package_rows = [{"name": package_name,
                         "count": package_value["count"],
                         "percent": round((package_value["count"] / max_package_count) * 100)}
                        for package_name, package_value in package_data.items()]
        package_rows.sort(key=lambda package_row: (package_row["count"], package_row["name"]), reverse=True)
        activity_end_date = min(selected_end_date, selected_start_date + relativedelta(days=6), )
        activity_rows = []
        max_activity_count = 1

        for day_offset in range((activity_end_date - selected_start_date).days + 1):
            activity_date = selected_start_date + relativedelta(days=day_offset)
            activity_count = self.env["decoration.order"].search_count(
                [("event_start", "=", activity_date), ("state", "in", active_state_values)])
            max_activity_count = max(max_activity_count, activity_count)
            activity_rows.append({"label": activity_date.strftime("%a"),
                                  "date": fields.Date.to_string(activity_date),
                                  "count": activity_count,
                                  "is_today": activity_date == today_date, })

        for activity_row in activity_rows:
            activity_row["height"] = (max(10, round((activity_row["count"] / max_activity_count) * 100))
                                      if activity_row["count"] else 7)
        alert_start_date = max(today_date, selected_start_date)
        alert_end_date = min(today_date + relativedelta(days=2), selected_end_date)
        urgent_decoration_order_domain = []
        urgent_installation_count = 0

        if alert_start_date <= alert_end_date:
            urgent_decoration_order_domain = self._event_date_domain(alert_start_date, alert_end_date) + [
                ("state", "in", active_state_values)]
            urgent_installation_count = self.env["decoration.order"].search_count(urgent_decoration_order_domain)
        unassigned_decoration_order_domain = selected_active_order_domain + [("employee_ids", "=", False)]
        unassigned_installation_count = self.env["decoration.order"].search_count(unassigned_decoration_order_domain)
        new_decoration_order_domain = selected_decoration_order_domain + [("state", "=", "new")]
        new_project_count = self.env["decoration.order"].search_count(new_decoration_order_domain)
        alert_rows = []
        if urgent_installation_count:
            alert_rows.append({
                "kind": "urgent",
                "icon": "fa-clock-o",
                "title": _("%s installation(s) need attention soon") % urgent_installation_count,
                "description": _("New or in-progress decoration projects are scheduled within the next two days."),
                "domain": urgent_decoration_order_domain, })
        if unassigned_installation_count:
            alert_rows.append({
                "kind": "staff",
                "icon": "fa-users",
                "title": _("%s project(s) have no decoration staff") % unassigned_installation_count,
                "description": _("Assign a decoration team before material preparation and setup begin."),
                "domain": unassigned_decoration_order_domain, })
        if new_project_count:
            alert_rows.append({
                "kind": "draft",
                "icon": "fa-paint-brush",
                "title": _("%s new project(s) are waiting for planning") % new_project_count,
                "description": "Review event details, package selection, customer requirements, and staff allocation",
                "domain": new_decoration_order_domain,
            })
        if not alert_rows:
            alert_rows.append({
                "kind": "success",
                "icon": "fa-check-circle",
                "title": _("Everything is on track"),
                "description": _("There are no immediate decoration actions requiring attention in this date range."),
                "domain": selected_decoration_order_domain,
            })
        company_id = self.env.company
        company_currency_id = company_id.currency_id
        return {
            "today": fields.Date.to_string(today_date),
            "company": {"id": company_id.id,
                        "name": company_id.name,
                        "logo_url": "/web/image/res.company/%s/logo" % company_id.id, },
            "currency": {"name": company_currency_id.name,
                         "symbol": company_currency_id.symbol,
                         "position": company_currency_id.position,
                         "decimal_places": company_currency_id.decimal_places, },
            "filters": {"start_date": fields.Date.to_string(selected_start_date),
                        "end_date": fields.Date.to_string(selected_end_date), },
            "range": {"start_date": fields.Date.to_string(selected_start_date),
                      "end_date": fields.Date.to_string(selected_end_date),
                      "previous_start_date": fields.Date.to_string(previous_start_date),
                      "previous_end_date": fields.Date.to_string(previous_end_date),
                      "activity_end_date": fields.Date.to_string(activity_end_date),
                      },
            "metrics": {"active_installations": active_installation_count,
                        "selected_value": selected_order_value,
                        "selected_guests": selected_guest_count,
                        "open_leads": open_decoration_lead_count,
                        "active_change": self._compare(active_installation_count, previous_active_installation_count),
                        "value_change": self._compare(selected_order_value, previous_order_value),
                        "guests_change": self._compare(selected_guest_count, previous_guest_count, ),
                        "leads_label": _("opportunities in selected range"),
                        },
            "status_rows": status_rows,
            "upcoming_events": event_rows,
            "event_types": event_type_rows[:5],
            "packages": package_rows[:5],
            "activity": activity_rows,
            "alerts": alert_rows[:3],
            "counts": {"confirmed_packages": self.env["decoration.package"].search_count([("state", "=", "confirm")]),
                       "decoration_staff": self.env["hr.employee"].search_count([("is_decoration_staff", "=", True),
                                                                                 ("active", "=", True), ]),
                       "events_in_range": self.env["decoration.order"].search_count(selected_active_order_domain)},
        }
