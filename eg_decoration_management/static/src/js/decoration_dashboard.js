/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

const DASHBOARD_LAYOUT_STORAGE_KEY = "eg_decoration_management.dashboard.layout";
const WIDGET_KEYS = ["schedule", "workload", "pipeline", "eventTypes", "alerts", "packages"];
const DEFAULT_WIDGETS = {
    schedule: true,
    workload: true,
    pipeline: true,
    eventTypes: true,
    alerts: true,
    packages: true,
};
const DEFAULT_ORDER = [...WIDGET_KEYS];

export class DecorationDashboard extends Component {
    static template = "eg_decoration_management.DecorationDashboard";

    setup() {
        this.action = useService("action");
        this.orm = useService("orm");
        this.notification = useService("notification");
        [
            "loadDashboard",
            "applyDateRange",
            "resetDateRange",
            "toggleCalendar",
            "closeCalendar",
            "previousCalendarMonth",
            "nextCalendarMonth",
            "selectCalendarDate",
            "applyCalendarRange",
            "chooseDatePreset",
            "toggleLayoutEditor",
            "closeLayoutEditor",
            "toggleWidget",
            "startDrag",
            "dragOver",
            "dropWidget",
            "endDrag",
            "moveWidget",
            "resetLayout",
            "openOrders",
            "openRangeOrders",
            "openRangeOrdersByState",
            "openOrder",
            "createOrder",
            "openPackages",
            "openLeads",
        ].forEach((methodName) => {this[methodName] = this[methodName].bind(this);});

        const savedLayout = this.getSavedLayout();
        this.state = useState({loading: true,
                                error: false,
                                data: null,
                                filters: { startDate: "",  endDate: "", },
                                calendar: { open: false, viewDate: this.toISODate(new Date()),},
                                layout: {editing: false,
                                    widgets: savedLayout.widgets,
                                    order: savedLayout.order,
                                    dragged: false,
                                    dragOver: false},
                               });
        onWillStart(() => this.loadDashboard());
    }

    getSavedLayout() {
        try {
            const saved = JSON.parse(window.localStorage.getItem(DASHBOARD_LAYOUT_STORAGE_KEY) || "{}");
            const widgets = { ...DEFAULT_WIDGETS, ...(saved.widgets || {}) };
            const savedOrder = Array.isArray(saved.order)? saved.order.filter((key) => WIDGET_KEYS.includes(key)): [];
            const order = [...savedOrder, ...DEFAULT_ORDER.filter((key) => !savedOrder.includes(key))];
            return { widgets, order};
        } catch {
            return { widgets: { ...DEFAULT_WIDGETS }, order: [...DEFAULT_ORDER] };
        }
    }

    saveLayout() {
        try {
            window.localStorage.setItem(
                DASHBOARD_LAYOUT_STORAGE_KEY,
                JSON.stringify({widgets: this.state.layout.widgets, order: this.state.layout.order, }));
        } catch {
        }
    }

    toISODate(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, "0");
        const day = String(date.getDate()).padStart(2, "0");
        return `${year}-${month}-${day}`;
    }

    parseISODate(value) {
        if (!value) {
            return new Date();
        }
        const [year, month, day] = value.split("-").map(Number);
        return new Date(year, month - 1, day || 1, 12, 0, 0);
    }

    monthStart(value) {
        const date = this.parseISODate(value);
        return this.toISODate(new Date(date.getFullYear(), date.getMonth(), 1, 12, 0, 0));
    }

    addDays(value, days) {
        const date = this.parseISODate(value);
        date.setDate(date.getDate() + days);
        return this.toISODate(date);
    }

    async loadDashboard() {
        this.state.loading = true;
        this.state.error = false;
        try {
            const data = await this.orm.call("decoration.dashboard", "get_dashboard_data", [this.state.filters.startDate || false,this.state.filters.endDate || false,]);
            this.state.data = data;
            this.state.filters.startDate = data.filters.start_date;
            this.state.filters.endDate = data.filters.end_date;
            if (!this.state.calendar.viewDate) { this.state.calendar.viewDate = this.monthStart(data.filters.start_date);}
        } catch (error) {
            console.error("Unable to load decoration dashboard", error);
            this.state.error = true;
        } finally {
            this.state.loading = false;
        }
    }

    async applyDateRange() {
        const { startDate, endDate } = this.state.filters;
        if (!startDate || !endDate) {
            this.notification.add(_t("Select both a start date and an end date."), { title: _t("Date range required"),type: "warning",});
            return false;
        }
        if (startDate > endDate) {
            this.notification.add(_t("The start date must be earlier than or equal to the end date."), {title: _t("Invalid date range"), type: "warning", });
            return false;
        }
        await this.loadDashboard();
        return true;
    }

    async resetDateRange() {
        this.state.filters.startDate = "";
        this.state.filters.endDate = "";
        this.state.calendar.open = false;
        await this.loadDashboard();
        this.state.calendar.viewDate = this.monthStart(this.state.filters.startDate);
    }

    toggleCalendar() {
        const willOpen = !this.state.calendar.open;
        this.state.calendar.open = willOpen;
        if (willOpen) {
            this.state.calendar.viewDate = this.monthStart(this.state.filters.startDate || this.toISODate(new Date()));
        }
    }

    closeCalendar() {
        this.state.calendar.open = false;
    }

    previousCalendarMonth() {
        const date = this.parseISODate(this.state.calendar.viewDate);
        date.setMonth(date.getMonth() - 1, 1);
        this.state.calendar.viewDate = this.toISODate(date);
    }

    nextCalendarMonth() {
        const date = this.parseISODate(this.state.calendar.viewDate);
        date.setMonth(date.getMonth() + 1, 1);
        this.state.calendar.viewDate = this.toISODate(date);
    }

    selectCalendarDate(value) {
        const { startDate, endDate } = this.state.filters;
        if (!startDate || endDate || value < startDate) {
            this.state.filters.startDate = value;
            this.state.filters.endDate = "";
            return;
        }
        this.state.filters.endDate = value;
    }

    async applyCalendarRange() {
        const applied = await this.applyDateRange();
        if (applied) {
            this.state.calendar.open = false;
        }
    }

    chooseDatePreset(preset) {
        const today = this.toISODate(new Date());
        const todayDate = this.parseISODate(today);
        let startDate = today;
        let endDate = today;
        if (preset === "week") {
            const mondayOffset = (todayDate.getDay() + 6) % 7;
            startDate = this.addDays(today, -mondayOffset);
            endDate = this.addDays(startDate, 6);
        } else if (preset === "next7") {
            endDate = this.addDays(today, 6);
        } else if (preset === "month") {
            startDate = this.toISODate(new Date(todayDate.getFullYear(), todayDate.getMonth(), 1, 12, 0, 0));
            endDate = this.toISODate(new Date(todayDate.getFullYear(), todayDate.getMonth() + 1, 0, 12, 0, 0));
        }
        this.state.filters.startDate = startDate;
        this.state.filters.endDate = endDate;
        this.state.calendar.viewDate = this.monthStart(startDate);
    }

    calendarMonthTitle() {
        return new Intl.DateTimeFormat(undefined, {month: "long", year: "numeric"}).format(this.parseISODate(this.state.calendar.viewDate));
    }

    calendarDays() {
        const currentMonth = this.parseISODate(this.state.calendar.viewDate);
        const year = currentMonth.getFullYear();
        const month = currentMonth.getMonth();
        const firstDay = new Date(year, month, 1, 12, 0, 0);
        const mondayIndex = (firstDay.getDay() + 6) % 7;
        const gridStart = new Date(year, month, 1 - mondayIndex, 12, 0, 0);
        const today = this.toISODate(new Date());
        const start = this.state.filters.startDate;
        const end = this.state.filters.endDate;
        return Array.from({ length: 42 }, (_, index) => {
            const date = new Date(gridStart);
            date.setDate(gridStart.getDate() + index);
            const value = this.toISODate(date);
            return {
                value,
                day: date.getDate(),
                isCurrentMonth: date.getMonth() === month,
                isToday: value === today,
                isStart: value === start,
                isEnd: value === end,
                isRange: Boolean(start && end && value > start && value < end),
            };
        });
    }

    calendarDayClass(day) {
        return [
            !day.isCurrentMonth ? "is-outside" : "",
            day.isToday ? "is-today" : "",
            day.isStart ? "is-start" : "",
            day.isEnd ? "is-end" : "",
            day.isRange ? "is-in-range" : "",
        ]
            .filter(Boolean)
            .join(" ");
    }

    dateRangeLabel() {
        const { startDate, endDate } = this.state.filters;
        if (!startDate) {
            return _t("Select dates");
        }
        if (!endDate) {
            return `${this.formatCompactDate(startDate)} — ${_t("Select end date")}`;
        }
        return `${this.formatCompactDate(startDate)} — ${this.formatCompactDate(endDate)}`;
    }

    formatCompactDate(value) {
        if (!value) {
            return _t("Not selected");
        }
        return new Intl.DateTimeFormat(undefined, {
            day: "2-digit",
            month: "short",
            year: "numeric",
        }).format(this.parseISODate(value));
    }

    toggleLayoutEditor() {
        this.state.layout.editing = !this.state.layout.editing;
        this.state.calendar.open = false;
    }

    closeLayoutEditor() {
        this.state.layout.editing = false;
        this.state.layout.dragged = false;
        this.state.layout.dragOver = false;
    }

    layoutItems() {
        const labels = {
            schedule: { label: _t("Project schedule"), description: _t("Upcoming decoration projects"), icon: "fa-calendar" },
            workload: { label: _t("Setup load"), description: _t("Seven-day project capacity"), icon: "fa-bar-chart" },
            pipeline: { label: _t("Project pipeline"), description: _t("Order workflow health"), icon: "fa-exchange" },
            eventTypes: { label: _t("Popular event types"), description: _t("Demand by event category"), icon: "fa-star" },
            alerts: { label: _t("Operations alerts"), description: _t("Tasks needing attention"), icon: "fa-bell-o" },
            packages: { label: _t("Package performance"), description: _t("Most selected decoration packages"), icon: "fa-gift" },
        };
        return this.state.layout.order.map((key) => ({  key,...labels[key], visible: this.state.layout.widgets[key],}));
    }

    visibleWidgets() {
        return this.state.layout.order.filter((key) => this.state.layout.widgets[key]);
    }

    toggleWidget(widgetName) {
        this.state.layout.widgets[widgetName] = !this.state.layout.widgets[widgetName];
        this.saveLayout();
    }

    startDrag(event, widgetName) {
        this.state.layout.dragged = widgetName;
        this.state.layout.dragOver = widgetName;
        if (event.dataTransfer) { event.dataTransfer.effectAllowed = "move"; event.dataTransfer.setData("text/plain", widgetName); }
    }

    dragOver(event, widgetName) {
        event.preventDefault();
        if (this.state.layout.dragged && this.state.layout.dragged !== widgetName) {
            this.state.layout.dragOver = widgetName;
        }
    }

    dropWidget(event, targetName) {
        event.preventDefault();
        const draggedName = this.state.layout.dragged || event.dataTransfer?.getData("text/plain");
        if (!draggedName || draggedName === targetName) {
            this.endDrag();
            return;
        }
        const newOrder = [...this.state.layout.order];
        const fromIndex = newOrder.indexOf(draggedName);
        const targetIndex = newOrder.indexOf(targetName);
        if (fromIndex !== -1 && targetIndex !== -1) {
            newOrder.splice(fromIndex, 1);
            newOrder.splice(targetIndex, 0, draggedName);
            this.state.layout.order = newOrder;
            this.saveLayout();
        }
        this.endDrag();
    }

    endDrag() {
        this.state.layout.dragged = false;
        this.state.layout.dragOver = false;
    }

    moveWidget(widgetName, direction) {
        const currentIndex = this.state.layout.order.indexOf(widgetName);
        const targetIndex = currentIndex + direction;
        if (currentIndex < 0 || targetIndex < 0 || targetIndex >= this.state.layout.order.length) {
            return;
        }
        const newOrder = [...this.state.layout.order];
        [newOrder[currentIndex], newOrder[targetIndex]] = [newOrder[targetIndex], newOrder[currentIndex]];
        this.state.layout.order = newOrder;
        this.saveLayout();
    }

    resetLayout() {
        this.state.layout.widgets = { ...DEFAULT_WIDGETS };
        this.state.layout.order = [...DEFAULT_ORDER];
        this.saveLayout();
    }

    getDateRangeDomain(extraDomain = []) {
        const data = this.state.data;
        if (!data) {
            return extraDomain;
        }
        return [["event_start", ">=", data.range.start_date],["event_start", "<=", data.range.end_date],...extraDomain];
    }

    formatMoney(value) {
        const currency = this.state.data?.currency;
        const amount = Number(value || 0);
        if (!currency) {
            return amount.toLocaleString();
        }
        try {
            return new Intl.NumberFormat(undefined, {style: "currency", currency: currency.name,
                minimumFractionDigits: currency.decimal_places,
                maximumFractionDigits: currency.decimal_places, }).format(amount);
        } catch {
            const formatted = amount.toLocaleString(undefined, {
                minimumFractionDigits: currency.decimal_places,
                maximumFractionDigits: currency.decimal_places,
            });
            return currency.position === "after" ? `${formatted} ${currency.symbol}` : `${currency.symbol}${formatted}`;
        }
    }

    formatDate(value) {
        if (!value) {
            return _t("Date to be set");
        }
        return new Intl.DateTimeFormat(undefined, {
            day: "2-digit",
            month: "short",
            year: "numeric",
        }).format(this.parseISODate(value));
    }

    changeClass(change) {
        return {
            up: "is-positive",
            down: "is-negative",
            flat: "is-neutral",
        }[change?.direction] || "is-neutral";
    }

    changeIcon(change) {
        return {up: "fa-arrow-up",down: "fa-arrow-down",flat: "fa-minus",}[change?.direction] || "fa-minus";
    }

    openOrders(domain = [], title = _t("Decoration Orders")) {
        return this.action.doAction({
            type: "ir.actions.act_window",
            name: title,
            res_model: "decoration.order",
            views: [[false, "list"], [false, "form"]],
            view_mode: "list,form",
            domain,
            target: "current",
        });
    }

    openRangeOrders(states, title) {
        return this.openOrders(this.getDateRangeDomain([["state", "in", states]]), title);
    }

    openRangeOrdersByState(state, title) {
        return this.openOrders(this.getDateRangeDomain([["state", "=", state]]), title);
    }

    openOrder(orderId) {
        return this.action.doAction({
            type: "ir.actions.act_window",
            name: _t("Decoration Order"),
            res_model: "decoration.order",
            res_id: orderId,
            views: [[false, "form"]],
            view_mode: "form",
            target: "current",
        });
    }

    createOrder() {
        return this.action.doAction({
            type: "ir.actions.act_window",
            name: _t("New Decoration Order"),
            res_model: "decoration.order",
            views: [[false, "form"]],
            view_mode: "form",
            target: "current",
        });
    }

    openPackages() {
        return this.action.doAction("eg_decoration_management.action_decoration_package");
    }

    openLeads() {
        const { start_date, end_date } = this.state.data.range;
        const endDate = this.parseISODate(end_date);
        endDate.setDate(endDate.getDate() + 1);
        const exclusiveEnd = this.toISODate(endDate);
        return this.action.doAction({
            type: "ir.actions.act_window",
            name: _t("Decoration Leads"),
            res_model: "crm.lead",
            views: [[false, "kanban"], [false, "list"], [false, "form"]],
            view_mode: "kanban,list,form",
            domain: [
                ["active", "=", true],
                ["decoration_start", ">=", `${start_date} 00:00:00`],
                ["decoration_start", "<", `${exclusiveEnd} 00:00:00`],
                ["probability", "<", 100],
            ],
            target: "current",
        });
    }
}

registry.category("actions").add("eg_decoration_management.decoration_dashboard", DecorationDashboard);
