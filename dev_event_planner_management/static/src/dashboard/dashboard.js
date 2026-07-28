/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { loadBundle } from "@web/core/assets";
import { Component, onWillStart, onMounted, onWillUnmount, useState, useRef } from "@odoo/owl";

/* ------------------------------------------------------------------ */
/* KPI card                                                            */
/* ------------------------------------------------------------------ */
export class KpiCard extends Component {
    static template = "dev_event_planner_management.KpiCard";
    static props = {
        label: String,
        value: { type: [String, Number] },
        icon: { type: String, optional: true },
        tone: { type: String, optional: true },
        subtitle: { type: String, optional: true },
        trend: { type: Number, optional: true },
        onClick: { type: Function, optional: true },
    };
}

/* ------------------------------------------------------------------ */
/* Chart card (Chart.js from the core web.chartjs_lib bundle)          */
/* ------------------------------------------------------------------ */
export class ChartCard extends Component {
    static template = "dev_event_planner_management.ChartCard";
    static props = {
        title: String,
        type: String,
        data: Object,
        options: { type: Object, optional: true },
    };

    setup() {
        this.canvasRef = useRef("canvas");
        this.chart = null;
        onMounted(() => this.renderChart());
        onWillUnmount(() => this.chart?.destroy());
    }

    renderChart() {
        this.chart?.destroy();
        const ctx = this.canvasRef.el.getContext("2d");
        const data = this.props.data;
        // Modern treatment: vertical gradient fills on bar datasets,
        // rounded corners, soft grid, point-style legend.
        for (const dataset of data.datasets) {
            if ((dataset.type || this.props.type) === "bar"
                    && typeof dataset.backgroundColor === "string") {
                const gradient = ctx.createLinearGradient(0, 0, 0, 240);
                gradient.addColorStop(0, dataset.backgroundColor);
                gradient.addColorStop(1, dataset.backgroundColor + "55");
                dataset.backgroundColor = gradient;
                dataset.borderRadius = 6;
                dataset.borderSkipped = false;
                dataset.maxBarThickness = 34;
            }
            if (dataset.type === "line") {
                dataset.pointRadius = 3;
                dataset.pointHoverRadius = 5;
                dataset.borderWidth = 2;
            }
        }
        const gridColor = "rgba(122, 110, 130, 0.12)";
        const isCartesian = !["doughnut", "pie", "polarArea"].includes(this.props.type);
        this.chart = new Chart(this.canvasRef.el, {
            type: this.props.type,
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                ...(this.props.type === "doughnut" ? { cutout: "68%" } : {}),
                scales: isCartesian ? {
                    x: { grid: { display: false }, border: { display: false } },
                    y: { grid: { color: gridColor }, border: { display: false },
                         ticks: (this.props.options && this.props.options.indexAxis === 'y') ? { autoSkip: false } : { maxTicksLimit: 6 } },
                } : undefined,
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: { usePointStyle: true, pointStyle: "circle",
                                  boxWidth: 8, padding: 16 },
                    },
                    tooltip: {
                        backgroundColor: "#2B2430",
                        padding: 10,
                        cornerRadius: 8,
                        displayColors: false,
                    },
                },
                ...(this.props.options || {}),
            },
        });
    }
}

/* ------------------------------------------------------------------ */
/* Main dashboard client action                                        */
/* ------------------------------------------------------------------ */
export class PlannerDashboard extends Component {
    static template = "dev_event_planner_management.Dashboard";
    static components = { KpiCard, ChartCard };
    static props = { "*": true };

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            loading: true,
            data: null,
            preset: "year",
            typeId: false,
            plannerId: false,
        });
        onWillStart(async () => {
            await loadBundle("web.chartjs_lib");
            await this.loadData();
        });
    }

    presetRange() {
        const now = new Date();
        const iso = (d) => d.toISOString().slice(0, 19).replace("T", " ");
        if (this.state.preset === "month") {
            return [iso(new Date(now.getFullYear(), now.getMonth(), 1)),
                    iso(new Date(now.getFullYear(), now.getMonth() + 1, 1))];
        }
        if (this.state.preset === "quarter") {
            const q = Math.floor(now.getMonth() / 3) * 3;
            return [iso(new Date(now.getFullYear(), q, 1)),
                    iso(new Date(now.getFullYear(), q + 3, 1))];
        }
        if (this.state.preset === "year") {
            return [iso(new Date(now.getFullYear() - 1, now.getMonth(), 1)), false];
        }
        return [false, false];
    }

    async loadData() {
        this.state.loading = true;
        const [dateFrom, dateTo] = this.presetRange();
        this.state.data = await this.orm.call(
            "planner.event", "get_dashboard_data",
            [dateFrom, dateTo,
             this.state.typeId ? [this.state.typeId] : false,
             this.state.plannerId ? [this.state.plannerId] : false]);
        this.state.loading = false;
    }

    async onFilterChange(field, value) {
        this.state[field] = value ? parseInt(value) || value : false;
        await this.loadData();
    }

    async refresh() {
        await this.loadData();
    }

    formatMoney(value) {
        const cur = this.state.data?.currency || { symbol: "", position: "before" };
        const num = Number(value || 0).toLocaleString(undefined, {
            maximumFractionDigits: 0,
        });
        return cur.position === "after" ? `${num} ${cur.symbol}` : `${cur.symbol} ${num}`;
    }

    openEvents(domain, name) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: name,
            res_model: "planner.event",
            views: [[false, "kanban"], [false, "list"], [false, "form"]],
            domain: domain,
        });
    }

    openUpcomingEvents() {
        const today = luxon.DateTime.now().toISODate();
        const future = luxon.DateTime.now().plus({ days: 30 }).toISODate();
        this.openEvents([
            ['stage_id.is_booked_stage', '=', true],
            ['date_start', '>=', today],
            ['date_start', '<=', future]
        ], 'Upcoming Events (Next 30 Days)');
    }

    openBookedRevenueEvents() {
        const today = luxon.DateTime.now();
        // Calculate the first day of the current quarter (e.g. Jan 1, Apr 1, Jul 1, Oct 1)
        const qStartMonth = Math.floor((today.month - 1) / 3) * 3 + 1;
        const quarterStart = luxon.DateTime.local(today.year, qStartMonth, 1).toISODate();
        this.openEvents([
            ['stage_id.is_booked_stage', '=', true],
            ['date_start', '>=', quarterStart],
            ['total_revenue', '>', 0]
        ], 'Booked Revenue (Qtr)');
    }

    openEvent(eventId) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "planner.event",
            views: [[false, "form"]],
            res_id: eventId,
        });
    }

    openShifts() {
        const today = luxon.DateTime.utc().toSQL();
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Unconfirmed Shifts",
            res_model: "planner.event.staff.line",
            views: [[false, "list"], [false, "calendar"]],
            domain: [
                ["state", "in", ["draft", "requested"]],
                ["event_id.stage_id.is_cancelled_stage", "=", false],
                ["date_from", ">=", today]
            ],
        });
    }

    openOverdueTasks() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Overdue Checklist Tasks",
            res_model: "project.task",
            views: [[false, "list"], [false, "form"]],
            domain: [
                ["planner_event_id", "!=", false],
                ["date_deadline", "<", luxon.DateTime.now().toSQL()],
                ["state", "not in", ["1_done", "1_canceled"]],
            ],
        });
    }

    /* ---- chart data builders ---- */
    get revenueChart() {
        const c = this.state.data.charts;
        return {
            labels: c.months,
            datasets: [
                { type: "bar", label: "Revenue", data: c.revenue_by_month,
                  backgroundColor: "#714B67" },
                { type: "line", label: "Contracted cost", data: c.cost_by_month,
                  borderColor: "#E4A900", backgroundColor: "#E4A900", tension: 0.3 },
            ],
        };
    }

    get typeChart() {
        const byType = this.state.data.charts.by_type;
        return {
            labels: Object.keys(byType),
            datasets: [{ data: Object.values(byType),
                backgroundColor: ["#714B67", "#E4A900", "#017E84", "#8F8F8F", "#5B899E", "#B0578D"] }],
        };
    }

    get sourceChart() {
        const bySource = this.state.data.charts.by_source;
        return {
            labels: Object.keys(bySource),
            datasets: [{ label: "Bookings", data: Object.values(bySource),
                backgroundColor: "#017E84" }],
        };
    }

    get funnelChart() {
        const funnel = this.state.data.charts.funnel;
        return {
            labels: funnel.map((s) => s.stage),
            datasets: [{ label: "Events", data: funnel.map((s) => s.count),
                backgroundColor: "#714B67" }],
        };
    }

    get marginChart() {
        const byType = this.state.data.charts.margin_by_type;
        return {
            labels: Object.keys(byType),
            datasets: [{ label: "Margin %", data: Object.values(byType),
                backgroundColor: "#E4A900" }],
        };
    }

    weekLoadTone(count) {
        if (count >= 4) return "o_planner_heat_high";
        if (count >= 2) return "o_planner_heat_mid";
        if (count >= 1) return "o_planner_heat_low";
        return "";
    }
}

registry.category("actions").add(
    "dev_event_planner_management.dashboard", PlannerDashboard);
