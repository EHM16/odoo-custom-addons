/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

/* Animated stat counters: count up when scrolled into view */
publicWidget.registry.PlannerCounters = publicWidget.Widget.extend({
    selector: ".o_planner_site",

    start() {
        const counters = this.el.querySelectorAll("[data-planner-counter]");
        if (counters.length) {
            this.observer = new IntersectionObserver(
                (entries) => entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        this._animate(entry.target);
                        this.observer.unobserve(entry.target);
                    }
                }),
                { threshold: 0.4 });
            counters.forEach((el) => this.observer.observe(el));
        }
        return this._super(...arguments);
    },

    destroy() {
        this.observer?.disconnect();
        this._super(...arguments);
    },

    _animate(el) {
        const target = parseInt(el.dataset.plannerCounter) || 0;
        if (reducedMotion || !target) {
            el.textContent = target.toLocaleString();
            return;
        }
        const duration = 1400;
        const start = performance.now();
        const step = (now) => {
            const progress = Math.min((now - start) / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3);
            el.textContent = Math.round(target * eased).toLocaleString();
            if (progress < 1) {
                requestAnimationFrame(step);
            }
        };
        requestAnimationFrame(step);
    },
});

/* Subtle hero parallax */
publicWidget.registry.PlannerParallax = publicWidget.Widget.extend({
    selector: ".o_planner_hero",

    start() {
        this.bg = this.el.querySelector("[data-planner-parallax]");
        if (this.bg && !reducedMotion) {
            this.factor = parseFloat(this.bg.dataset.plannerParallax) || 0.3;
            this._onScroll = this._onScroll.bind(this);
            window.addEventListener("scroll", this._onScroll, { passive: true });
        }
        return this._super(...arguments);
    },

    destroy() {
        if (this._onScroll) {
            window.removeEventListener("scroll", this._onScroll);
        }
        this._super(...arguments);
    },

    _onScroll() {
        window.requestAnimationFrame(() => {
            this.bg.style.transform =
                `translateY(${window.scrollY * this.factor}px)`;
        });
    },
});

/* Multi-step inquiry form */
publicWidget.registry.PlannerInquiryForm = publicWidget.Widget.extend({
    selector: ".o_planner_inquiry_form",
    events: {
        "click .o_planner_next": "_onNext",
        "click .o_planner_prev": "_onPrev",
        "change .o_planner_type_option input": "_onTypeChange",
        "submit": "_onSubmit",
    },

    start() {
        this.steps = [...this.el.querySelectorAll(".o_planner_form_step")];
        this.bar = document.querySelectorAll(".o_planner_steps_bar .o_planner_steps_step");
        this.fill = document.querySelector(".o_planner_steps_fill");
        this.current = 0;
        this._updateFill();
        return this._super(...arguments);
    },

    _show(index) {
        this.current = Math.max(0, Math.min(index, this.steps.length - 1));
        this.steps.forEach((step, i) =>
            step.classList.toggle("d-none", i !== this.current));
        this.bar.forEach((chip, i) => {
            chip.classList.toggle("active", i === this.current);
            chip.classList.toggle("done", i < this.current);
        });
        this._updateFill();
        this.el.scrollIntoView({ behavior: reducedMotion ? "auto" : "smooth", block: "start" });
    },

    _updateFill() {
        if (!this.fill || !this.bar.length) {
            return;
        }
        const ratio = this.bar.length > 1 ? this.current / (this.bar.length - 1) : 0;
        this.fill.style.width = `${Math.round(ratio * 76)}%`;
    },

    _onNext() {
        const inputs = this.steps[this.current].querySelectorAll("input, select, textarea");
        for (const input of inputs) {
            if (!input.reportValidity()) {
                return;
            }
        }
        this._show(this.current + 1);
    },

    _onPrev() {
        this._show(this.current - 1);
    },

    _onTypeChange(ev) {
        const name = ev.currentTarget.name;
        this.el.querySelectorAll(`.o_planner_type_option input[name="${name}"]`).forEach((input) => {
            input.closest(".o_planner_type_option").classList.toggle("o_selected", input.checked);
        });
    },

    _onSubmit(ev) {
        const btn = this.el.querySelector(".o_planner_submit");
        if (btn && this.el.checkValidity()) {
            btn.classList.add("o_planner_submitting");
        }
    },
});

/* Thank-you page: checkmark reveal + confetti burst */
publicWidget.registry.PlannerThanksFx = publicWidget.Widget.extend({
    selector: ".o_planner_thanks_wrap",

    start() {
        if (!reducedMotion) {
            this._launchConfetti();
        }
        return this._super(...arguments);
    },

    _launchConfetti() {
        const field = this.el.querySelector(".o_planner_confetti_field");
        if (!field) {
            return;
        }
        const colors = ["#C9A227", "#1E1B24", "#714B67", "#F6F3EE", "#E8C766"];
        const count = 46;
        for (let i = 0; i < count; i++) {
            const piece = document.createElement("span");
            piece.className = "o_planner_confetti_piece";
            const left = Math.random() * 100;
            const delay = Math.random() * 0.6;
            const duration = 2.6 + Math.random() * 1.8;
            const drift = `${(Math.random() * 160 - 80)}px`;
            const spin = `${Math.round(360 + Math.random() * 360)}deg`;
            piece.style.left = `${left}%`;
            piece.style.background = colors[i % colors.length];
            piece.style.animationDelay = `${delay}s`;
            piece.style.animationDuration = `${duration}s`;
            piece.style.setProperty("--o-confetti-drift", drift);
            piece.style.setProperty("--o-confetti-spin", spin);
            if (i % 3 === 0) {
                piece.style.borderRadius = "50%";
            }
            field.appendChild(piece);
        }
        window.setTimeout(() => { field.innerHTML = ""; }, 5200);
    },
});
