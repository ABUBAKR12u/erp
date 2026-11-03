const $ = (id) => document.getElementById(id);
const state = {
    token: sessionStorage.getItem("erp_access_token"), refresh: sessionStorage.getItem("erp_refresh_token"),
    options: null, user: null, view: "overview", mode: "table", branch: "", filters: {},
    rows: [], total: 0, page: 1, pages: 1, size: 20, request: 0, selected: new Set(),
    editor: null, confirm: null, dragging: null, dashboard: null,
};
const money = new Intl.NumberFormat("ru-RU", { maximumFractionDigits: 2 });
const months = ["yanvar", "fevral", "mart", "aprel", "may", "iyun", "iyul", "avgust", "sentabr", "oktabr", "noyabr", "dekabr"];
const shortMonths = ["yan", "fev", "mar", "apr", "may", "iyn", "iyl", "avg", "sen", "okt", "noy", "dek"];
const tones = ["mint", "lilac", "peach", "blue", "rose"];
const studentStatuses = { sinovda: "Sinovda", faol: "Faol", muzlatilgan: "Muzlatilgan", bitirgan: "Bitirgan", ketgan: "Ketgan" };
const groupStatuses = { rejalashtirilgan: "Rejalashtirilgan", faol: "Faol", tugagan: "Tugagan", bekor_qilingan: "Bekor qilingan" };
const sessionStatuses = { rejalashtirilgan: "Rejalashtirilgan", otilgan: "O‘tilgan", bekor_qilingan: "Bekor qilingan" };
const weekdays = { 1: "Dushanba", 2: "Seshanba", 3: "Chorshanba", 4: "Payshanba", 5: "Juma", 6: "Shanba", 7: "Yakshanba" };
const timeLabel = (value) => String(value || "").slice(0, 5);
const isoToday = () => new Intl.DateTimeFormat("en-CA", { timeZone: "Asia/Tashkent", year: "numeric", month: "2-digit", day: "2-digit" }).format(new Date());
const paths = {
    schedules: '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 3v4m10-4v4M3 11h18m-13 4h2m4 0h2m-8 3h2"/>',
    sessions: '<rect x="3" y="4" width="18" height="17" rx="2"/><path d="M7 2v4m10-4v4M3 10h18m-13 6 3 3 5-6"/>',
    home: '<path d="m3 10 9-7 9 7v10H3Z"/><path d="M9 20v-7h6v7"/>',
    dashboard: '<rect x="3" y="3" width="7" height="9" rx="1.5"/><rect x="14" y="3" width="7" height="5" rx="1.5"/><rect x="3" y="16" width="7" height="5" rx="1.5"/><rect x="14" y="12" width="7" height="9" rx="1.5"/>',
    leads: '<path d="M12 3v4m0 10v4M3 12h4m10 0h4"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    students: '<path d="m2 9 10-5 10 5-10 5Z"/><path d="M6 11v6c4 3 8 3 12 0v-6m4-2v7"/>',
    groups: '<circle cx="9" cy="8" r="3"/><path d="M3 20v-2a6 6 0 0 1 12 0v2M16 5a3 3 0 0 1 0 6m2 3a5 5 0 0 1 3 4v2"/>',
    courses: '<path d="M12 5C8 2 5 3 3 4v16c3-2 6-1 9 1 3-2 6-3 9-1V4c-3-1-6-2-9 1Zm0 0v16"/>',
    employees: '<rect x="3" y="6" width="18" height="15" rx="2"/><path d="M8 6V3h8v3m-4 0v15M3 12h18"/>',
    teachers: '<circle cx="8" cy="7" r="3"/><path d="M2 21v-3a6 6 0 0 1 12 0v3m0-18h7v12h-4m0-8h1m-1 4h1"/>',
    branches: '<path d="M4 21V4h11v17M15 10h5v11M8 8h3m-3 4h3m-3 4h3M2 21h20"/>',
    rooms: '<path d="M5 21V3h12v18M3 21h18M13 12h.1"/><path d="m8 3 9 2"/>',
    sources: '<path d="m3 11 15-6v14L3 14Zm3 4 2 6h4l-2-5M21 9v6"/>',
    statuses: '<rect x="3" y="4" width="4" height="16" rx="1"/><rect x="10" y="4" width="4" height="11" rx="1"/><rect x="17" y="4" width="4" height="6" rx="1"/>',
    roles: '<path d="m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6Z"/><path d="m8 12 3 3 5-6"/>',
    assignments: '<circle cx="8" cy="8" r="3"/><path d="M2 21v-2a6 6 0 0 1 9-5m4 1 2 2 5-6"/>',
    search: '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/>',
    plus: '<path d="M12 5v14M5 12h14"/>', close: '<path d="m6 6 12 12M6 18 18 6"/>',
    arrow: '<path d="M5 12h14m-5-5 5 5-5 5"/>', chevron: '<path d="m7 10 5 5 5-5"/>',
    left: '<path d="m14 6-6 6 6 6"/>', right: '<path d="m10 6 6 6-6 6"/>',
    edit: '<path d="m15 5 4 4M4 20l5-1L20 8a2.8 2.8 0 0 0-4-4L5 15l-1 5Z"/>',
    trash: '<path d="M3 6h18M9 6V3h6v3M5 6l1 15h12l1-15M10 10v7m4-7v7"/>',
    more: '<circle cx="5" cy="12" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/>',
    refresh: '<path d="M20 7v5h-5M4 17v-5h5M5 8a8 8 0 0 1 13-3l2 3M4 16l2 3a8 8 0 0 0 13-3"/>',
    grid: '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>',
    table: '<path d="M8 5h13M8 12h13M8 19h13M3 5h.1M3 12h.1M3 19h.1"/>',
    check: '<path d="m5 12 4 4L19 6"/>', clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    phone: '<path d="m5 3 4 1 1 5-3 2c2 4 3 5 7 7l2-3 5 1 1 4c-1 5-10 2-15-3S0 4 5 3Z"/>',
    pin: '<path d="M19 10c0 5-7 11-7 11S5 15 5 10a7 7 0 0 1 14 0Z"/><circle cx="12" cy="10" r="2"/>',
    eye: '<path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/>',
    download: '<path d="M12 3v12m-5-5 5 5 5-5M4 17v4h16v-4"/>',
    menu: '<path d="M4 6h16M4 12h16M4 18h16"/>', logout: '<path d="M9 4H4v16h5m6-13 5 5-5 5M9 12h11"/>',
    info: '<circle cx="12" cy="12" r="9"/><path d="M12 11v6m0-10h.1"/>',
};
function icon(name) { return `<svg viewBox="0 0 24 24" aria-hidden="true">${paths[name] || paths.grid}</svg>`; }
function esc(value) { return String(value ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]); }
function fullName(person) { return person ? [person.first_name, person.last_name].filter(Boolean).join(" ") : "Biriktirilmagan"; }
function initials(name) { return String(name || "M").split(/\s+/).filter(Boolean).slice(0, 2).map((s) => s[0]).join("").toUpperCase(); }
function toneId(value) { return [...String(value || "")].reduce((sum, ch) => sum + ch.charCodeAt(0), 0) % 5; }
function avatar(name, size = "") { return `<span class="avatar ${size} tone-${toneId(name)}" aria-hidden="true">${esc(initials(name))}</span>`; }
function dateLabel(value) { if (!value) return "Belgilanmagan"; const [y, m, d] = value.slice(0, 10).split("-"); return `${Number(d)} ${shortMonths[Number(m) - 1] || ""} ${y}`; }
function setMessage(id, value = "") { $(id).textContent = value; $(id).hidden = !value; }
function toast(text, error = false) { const item = document.createElement("div"); item.className = `toast${error ? " error" : ""}`; item.innerHTML = icon(error ? "info" : "check") + `<span>${esc(text)}</span>`; $("toasts").append(item); setTimeout(() => item.remove(), error ? 6500 : 4200); }
function jsonRequest(method, value) { return { method, headers: { "Content-Type": "application/json" }, body: JSON.stringify(value) }; }
function queryPath(path, values) { const query = new URLSearchParams(); for (const [key, val] of Object.entries(values)) if (val !== "" && val !== null && val !== undefined) query.set(key, val); return `${path}${query.size ? "?" + query : ""}`; }
function hasRole(...roles) { return Boolean(state.user?.is_superadmin || state.user?.roles.some((role) => roles.includes(role.code))); }
let refreshPromise = null;
function showLogin(error = "") {
    state.token = state.refresh = null; state.request++;
    sessionStorage.removeItem("erp_access_token"); sessionStorage.removeItem("erp_refresh_token");
    document.querySelectorAll("dialog[open]").forEach((dialog) => dialog.close());
    SmartSelect.active?.close(); closeRowMenu();
    $("app-view").hidden = true; $("login-view").hidden = false; setMessage("login-error", error);
}
async function api(path, options = {}, retry = false) {
    const { auth = true, ...request } = options;
    const headers = new Headers(request.headers);
    if (auth && state.token) headers.set("Authorization", `Bearer ${state.token}`);
    let response;
    try { response = await fetch(path, { ...request, headers }); }
    catch { throw new Error("Serverga ulanish amalga oshmadi. Ulanishni tekshirib, qayta urinib ko‘ring."); }
    const data = await response.json().catch(() => null);
    const authError = auth && response.status === 401 && /token|authenticated|inactive/i.test(String(data?.detail || ""));
    if (authError && !retry && state.refresh) {
        if (!refreshPromise) refreshPromise = fetch("/auth/refresh", jsonRequest("POST", { refresh_token: state.refresh })).then(async (result) => {
            if (!result.ok) throw new Error("Kirish muddati tugadi. Qayta kiring.");
            const tokens = await result.json(); state.token = tokens.access_token;
            sessionStorage.setItem("erp_access_token", state.token);
        }).finally(() => { refreshPromise = null; });
        try { await refreshPromise; return await api(path, options, true); }
        catch (error) { showLogin(error.message); throw error; }
    }
    if (!response.ok) {
        if (authError) showLogin("Kirish muddati tugadi. Qayta kiring.");
        let detail = data?.detail;
        if (Array.isArray(detail)) detail = detail.map((item) => `${item.loc?.filter((s) => s !== "body").join(" / ") || "Maydon"}: ${item.msg}`).join(". ");
        if (response.status === 429) detail = "Urinishlar ko‘payib ketdi. Bir ozdan keyin yana urinib ko‘ring.";
        if (response.status === 403 && detail === "Permission Denied") detail = "Bu amal uchun hisobingizda ruxsat yo‘q.";
        throw new Error(typeof detail === "string" ? detail : "Amal bajarilmadi. Qayta urinib ko‘ring.");
    }
    return data;
}

class SmartSelect {
    static instances = new Map();
    static active = null;
    constructor(select) {
        this.select = select; this.required = select.required; select.required = false;
        this.wrapper = document.createElement("div"); this.wrapper.className = "smart-select";
        select.before(this.wrapper); this.wrapper.append(select);
        this.button = document.createElement("button"); this.button.type = "button"; this.button.className = "select-trigger";
        this.button.id = `${select.id}-trigger`; this.button.setAttribute("role", "combobox"); this.button.setAttribute("aria-haspopup", "listbox"); this.button.setAttribute("aria-expanded", "false");
        this.label = select.dataset.label || document.querySelector(`label[for="${select.id}"]`)?.textContent.replace("*", "").trim() || "Tanlash";
        this.button.setAttribute("aria-label", this.label);
        this.button.setAttribute("aria-controls", `${select.id}-listbox`);
        this.button.setAttribute("aria-required", String(this.required));
        document.querySelector(`label[for="${select.id}"]`)?.setAttribute("for", this.button.id);
        this.wrapper.append(this.button);
        select.addEventListener("change", () => this.refresh());
        this.button.addEventListener("click", () => this.panel ? this.close() : this.open());
        this.button.addEventListener("keydown", (event) => {
            if (["ArrowDown", "ArrowUp", "Enter", " "].includes(event.key)) { event.preventDefault(); this.open(); }
        });
        SmartSelect.instances.set(select, this); this.refresh();
    }
    refresh() {
        this.button.disabled = this.select.disabled;
        const selected = this.select.selectedOptions[0];
        this.button.innerHTML = `<span class="select-value">${esc(selected?.textContent || "Tanlang")}</span>${icon("chevron")}`;
        this.button.classList.toggle("placeholder", !this.select.value);
        this.button.setAttribute("aria-invalid", "false");
        if (this.panel) this.renderOptions();
    }
    open() {
        if (this.select.disabled || this.panel) return;
        SmartDate.active?.close();
        SmartTime.active?.close();
        SmartSelect.active?.close(); SmartSelect.active = this;
        this.panel = document.createElement("div"); this.panel.className = "select-popover";
        this.panel.innerHTML = `<div class="select-search-wrap">${icon("search")}<input aria-label="${esc(this.label)} variantlarini qidirish" placeholder="Qidirish…" autocomplete="off"></div><div class="select-options" role="listbox" aria-label="${esc(this.label)} variantlari"></div>`;
        (this.select.closest("dialog") || document.body).append(this.panel);
        this.search = this.panel.querySelector("input"); this.list = this.panel.querySelector(".select-options");
        this.list.id = `${this.select.id}-listbox`;
        this.button.setAttribute("aria-expanded", "true");
        this.search.addEventListener("input", () => { this.index = 0; this.renderOptions(); });
        this.panel.addEventListener("click", (event) => { const option = event.target.closest("[data-option]"); if (option) this.choose(Number(option.dataset.option)); });
        this.panel.addEventListener("keydown", (event) => {
            if (event.key === "Escape") { event.preventDefault(); event.stopPropagation(); this.close(true); }
            if (["ArrowDown", "ArrowUp"].includes(event.key)) {
                event.preventDefault(); this.index = Math.max(0, Math.min(this.filtered.length - 1, (this.index ?? -1) + (event.key === "ArrowDown" ? 1 : -1)));
                this.highlight();
            }
            if (event.key === "Enter") { event.preventDefault(); if (this.filtered.length) this.choose(this.filtered[this.index ?? 0].index); }
            if (event.key === "Tab") this.close();
        });
        this.index = 0; this.renderOptions();
        const bounds = this.button.getBoundingClientRect();
        const available = innerHeight - bounds.bottom;
        const height = Math.min(available < 200 ? bounds.top - 12 : available - 12, 310);
        this.panel.style.width = `${Math.max(bounds.width, 210)}px`;
        this.panel.style.left = `${Math.max(8, Math.min(bounds.left, innerWidth - Math.max(bounds.width, 210) - 8))}px`;
        this.panel.style.top = available < 200 ? "auto" : `${bounds.bottom + 6}px`;
        if (available < 200) this.panel.style.bottom = `${innerHeight - bounds.top + 6}px`;
        this.list.style.maxHeight = `${Math.max(90, height - 52)}px`;
        this.search.focus();
    }
    renderOptions() {
        const term = (this.search?.value || "").toLocaleLowerCase();
        this.filtered = [...this.select.options].map((option, index) => ({ option, index })).filter(({ option }) => !option.disabled && `${option.textContent} ${option.dataset.hint || ""}`.toLocaleLowerCase().includes(term));
        this.list.innerHTML = this.filtered.length ? this.filtered.map(({ option, index }, position) => `<button type="button" class="select-option${position === this.index ? " focused" : ""}" role="option" aria-selected="${option.selected}" data-option="${index}">${option.dataset.avatar ? avatar(option.dataset.avatar, "small") : ""}<span>${esc(option.textContent)}${option.dataset.hint ? `<small class="cell-sub">${esc(option.dataset.hint)}</small>` : ""}</span>${option.selected ? icon("check") : ""}</button>`).join("") : '<div class="select-empty">Mos variant topilmadi</div>';
    }
    highlight() {
        [...this.list.querySelectorAll(".select-option")].forEach((button, index) => button.classList.toggle("focused", index === this.index));
        this.list.querySelector(".focused")?.scrollIntoView({ block: "nearest" });
    }
    choose(index) { this.select.selectedIndex = index; this.select.dispatchEvent(new Event("change", { bubbles: true })); this.close(true); }
    close(focus = false) { this.panel?.remove(); this.panel = null; this.button.setAttribute("aria-expanded", "false"); if (SmartSelect.active === this) SmartSelect.active = null; if (focus) this.button.focus(); }
}
function calendarDate(value) { return new Date(`${value}T12:00:00Z`); }
function calendarISO(date) { return date.toISOString().slice(0, 10); }
function shiftCalendarDay(value, days) { const date = calendarDate(value); date.setUTCDate(date.getUTCDate() + days); return calendarISO(date); }
function readableDate(value) { if (!value) return "Sanani tanlang"; const [year, month, day] = value.split("-"); return `${Number(day)} ${shortMonths[Number(month) - 1]}, ${year}`; }
class SmartDate {
    static instances = new Map();
    static active = null;
    static sequence = 0;
    constructor(input) {
        this.input = input; this.required = input.required; input.required = false;
        if (!input.id) input.id = `calendar-input-${++SmartDate.sequence}`;
        this.label = input.getAttribute("aria-label") || document.querySelector(`label[for="${input.id}"]`)?.textContent.replace("*", "").trim() || input.closest("label")?.textContent.trim() || "Sana";
        input.classList.add("calendar-native"); input.tabIndex = -1; input.setAttribute("aria-hidden", "true");
        this.wrapper = document.createElement("div"); this.wrapper.className = "date-picker";
        input.before(this.wrapper); this.wrapper.append(input);
        this.button = document.createElement("button"); this.button.type = "button"; this.button.className = "date-trigger";
        this.button.id = `${input.id}-trigger`; this.button.setAttribute("role", "combobox");
        this.button.setAttribute("aria-label", this.label); this.button.setAttribute("aria-haspopup", "dialog");
        this.button.setAttribute("aria-expanded", "false"); this.button.setAttribute("aria-controls", `${input.id}-calendar`);
        this.button.setAttribute("aria-required", String(this.required)); this.wrapper.append(this.button);
        document.querySelector(`label[for="${input.id}"]`)?.setAttribute("for", this.button.id);
        this.button.addEventListener("click", () => this.panel ? this.close(true) : this.open());
        this.button.addEventListener("keydown", (event) => { if (["ArrowDown", "ArrowUp"].includes(event.key)) { event.preventDefault(); this.open(); } });
        input.addEventListener("change", () => this.refresh());
        SmartDate.instances.set(input, this); this.refresh();
    }
    refresh() {
        this.button.disabled = this.input.disabled;
        this.button.innerHTML = `<span>${esc(readableDate(this.input.value))}</span>${icon("schedules")}`;
        this.button.classList.toggle("placeholder", !this.input.value);
        this.button.setAttribute("aria-invalid", "false");
    }
    allowed(value) { return (!this.input.min || value >= this.input.min) && (!this.input.max || value <= this.input.max); }
    open() {
        if (this.input.disabled || this.panel) return;
        SmartTime.active?.close();
        SmartSelect.active?.close(); SmartDate.active?.close(); SmartDate.active = this;
        this.focusDate = this.input.value || isoToday();
        if (this.input.min && this.focusDate < this.input.min) this.focusDate = this.input.min;
        if (this.input.max && this.focusDate > this.input.max) this.focusDate = this.input.max;
        const date = calendarDate(this.focusDate); this.year = date.getUTCFullYear(); this.month = date.getUTCMonth(); this.view = "days";
        this.panel = document.createElement("div"); this.panel.className = "calendar-popover";
        this.panel.id = `${this.input.id}-calendar`; this.panel.setAttribute("role", "dialog"); this.panel.setAttribute("aria-label", `${this.label} — kalendar`);
        (this.input.closest("dialog") || document.body).append(this.panel);
        this.button.setAttribute("aria-expanded", "true");
        this.panel.addEventListener("click", (event) => this.handleClick(event));
        this.panel.addEventListener("keydown", (event) => this.handleKey(event));
        this.render(); this.position(); this.focusCell();
    }
    position() {
        const bounds = this.button.getBoundingClientRect(), width = Math.min(310, innerWidth - 24);
        this.panel.style.width = `${width}px`;
        this.panel.style.left = `${Math.max(12, Math.min(bounds.left, innerWidth - width - 12))}px`;
        const height = this.panel.offsetHeight, below = innerHeight - bounds.bottom - 12;
        this.panel.style.top = `${Math.max(12, below >= height || bounds.top < height ? Math.min(bounds.bottom + 8, innerHeight - height - 12) : bounds.top - height - 8)}px`;
        this.panel.style.maxHeight = `${innerHeight - 24}px`;
    }
    render() {
        const monthLabel = `${months[this.month][0].toUpperCase()}${months[this.month].slice(1)}`;
        const first = new Date(Date.UTC(this.year, this.month, 1)), offset = (first.getUTCDay() + 6) % 7;
        const start = new Date(first); start.setUTCDate(1 - offset);
        const yearStart = Math.floor(this.year / 12) * 12;
        let body;
        if (this.view === "days") body = `<div class="calendar-weekdays" aria-hidden="true">${["Du", "Se", "Ch", "Pa", "Ju", "Sh", "Ya"].map((day) => `<span>${day}</span>`).join("")}</div><div class="calendar-grid" role="grid" aria-label="${monthLabel} ${this.year}">${Array.from({ length: 42 }, (_, i) => {
            const date = new Date(start); date.setUTCDate(start.getUTCDate() + i); const value = calendarISO(date), selected = value === this.input.value;
            return `<button type="button" role="gridcell" class="calendar-day${date.getUTCMonth() !== this.month ? " outside" : ""}${value === isoToday() ? " today" : ""}${selected ? " selected" : ""}" data-date="${value}" aria-label="${dateLabel(value)}" aria-selected="${selected}" ${value === isoToday() ? 'aria-current="date"' : ""} tabindex="${value === this.focusDate ? 0 : -1}" ${this.allowed(value) ? "" : "disabled"}>${date.getUTCDate()}</button>`;
        }).join("")}</div>`;
        else if (this.view === "months") body = `<div class="calendar-choices">${months.map((month, index) => `<button type="button" data-month="${index}" class="${index === this.month ? "selected" : ""}" ${this.allowedMonth(this.year, index) ? "" : "disabled"}>${month[0].toUpperCase()}${month.slice(1)}</button>`).join("")}</div>`;
        else body = `<div class="calendar-choices">${Array.from({ length: 12 }, (_, i) => yearStart + i).map((year) => `<button type="button" data-year="${year}" class="${year === this.year ? "selected" : ""}" ${(this.input.min && year < Number(this.input.min.slice(0, 4))) || (this.input.max && year > Number(this.input.max.slice(0, 4))) ? "disabled" : ""}>${year}</button>`).join("")}</div>`;
        this.panel.innerHTML = `<div class="calendar-kicker">${esc(this.label)}</div><div class="calendar-header"><button type="button" class="icon-button" data-calendar-step="-1" aria-label="Oldingi ${this.view === "days" ? "oy" : this.view === "months" ? "yil" : "yillar"}">${icon("left")}</button><div><button type="button" class="calendar-heading" data-calendar-view="months">${this.view === "years" ? `${yearStart}–${yearStart + 11}` : this.view === "days" ? monthLabel : "Oy tanlang"}</button>${this.view !== "years" ? `<button type="button" class="calendar-year" data-calendar-view="years" aria-label="Yilni tanlash">${this.year}${icon("chevron")}</button>` : ""}</div><button type="button" class="icon-button" data-calendar-step="1" aria-label="Keyingi ${this.view === "days" ? "oy" : this.view === "months" ? "yil" : "yillar"}">${icon("right")}</button></div>${body}<div class="calendar-footer"><button type="button" data-calendar-today ${this.allowed(isoToday()) ? "" : "disabled"}>Bugun</button>${!this.required ? '<button type="button" data-calendar-clear>Tozalash</button>' : '<span>Sanani tanlang</span>'}<button class="icon-button" type="button" data-calendar-close aria-label="Kalendarni yopish">${icon("close")}</button></div>`;
    }
    allowedMonth(year, month) { const first = calendarISO(new Date(Date.UTC(year, month, 1))), last = calendarISO(new Date(Date.UTC(year, month + 1, 0))); return (!this.input.min || last >= this.input.min) && (!this.input.max || first <= this.input.max); }
    focusCell() { (this.panel.querySelector('[tabindex="0"]:not(:disabled), .calendar-choices .selected:not(:disabled)') || this.panel.querySelector(".calendar-day:not(:disabled), .calendar-choices button:not(:disabled)") || this.panel.querySelector("button")).focus(); }
    step(direction) {
        if (this.view === "days") { const date = new Date(Date.UTC(this.year, this.month + direction, 1)); this.year = date.getUTCFullYear(); this.month = date.getUTCMonth(); }
        else this.year += direction * (this.view === "years" ? 12 : 1);
        this.year = Math.max(100, Math.min(9998, this.year));
        if (this.view === "days") this.focusDate = calendarISO(new Date(Date.UTC(this.year, this.month, Math.min(calendarDate(this.focusDate).getUTCDate(), new Date(Date.UTC(this.year, this.month + 1, 0)).getUTCDate()))));
        this.render(); this.position();
    }
    handleClick(event) {
        const button = event.target.closest("button"); if (!button || button.disabled) return;
        if (button.dataset.date) return this.choose(button.dataset.date);
        if (button.dataset.calendarStep) { this.step(Number(button.dataset.calendarStep)); this.panel.querySelector(`[data-calendar-step="${button.dataset.calendarStep}"]`).focus(); return; }
        if (button.dataset.calendarView) this.view = button.dataset.calendarView;
        if (button.dataset.month != null) { this.month = Number(button.dataset.month); this.view = "days"; }
        if (button.dataset.year) { this.year = Number(button.dataset.year); this.view = "months"; }
        if (button.hasAttribute("data-calendar-today")) return this.choose(isoToday());
        if (button.hasAttribute("data-calendar-clear")) return this.choose("");
        if (button.hasAttribute("data-calendar-close")) return this.close(true);
        this.render(); this.position(); this.focusCell();
    }
    handleKey(event) {
        if (event.key === "Escape") { event.preventDefault(); event.stopPropagation(); this.close(true); return; }
        if (event.key === "Tab") { const buttons = [...this.panel.querySelectorAll("button:not(:disabled)")]; if ((!event.shiftKey && event.target === buttons.at(-1)) || (event.shiftKey && event.target === buttons[0])) this.close(); return; }
        if (!event.target.dataset.date) return;
        const moves = { ArrowLeft: -1, ArrowRight: 1, ArrowUp: -7, ArrowDown: 7 };
        let value = event.target.dataset.date;
        if (event.key in moves) value = shiftCalendarDay(value, moves[event.key]);
        else if (["Home", "End"].includes(event.key)) { const day = (calendarDate(value).getUTCDay() + 6) % 7; value = shiftCalendarDay(value, event.key === "Home" ? -day : 6 - day); }
        else if (["PageUp", "PageDown"].includes(event.key)) { event.preventDefault(); this.step(event.key === "PageUp" ? -1 : 1); this.focusCell(); return; }
        else return;
        event.preventDefault(); if (!this.allowed(value)) return;
        this.focusDate = value; const date = calendarDate(value); this.year = date.getUTCFullYear(); this.month = date.getUTCMonth(); this.render(); this.focusCell();
    }
    choose(value) { if (value && !this.allowed(value)) return; this.input.value = value; this.refresh(); this.close(true); this.input.dispatchEvent(new Event("change", { bubbles: true })); }
    close(focus = false) { this.panel?.remove(); this.panel = null; this.button.setAttribute("aria-expanded", "false"); if (SmartDate.active === this) SmartDate.active = null; if (focus && this.button.isConnected) this.button.focus(); }
}
function enhanceDates(root = document) {
    for (const [input, instance] of SmartDate.instances) if (!input.isConnected) { instance.close(); SmartDate.instances.delete(input); }
    root.querySelectorAll('input[type="date"]').forEach((input) => SmartDate.instances.has(input) ? SmartDate.instances.get(input).refresh() : new SmartDate(input));
}
function parseClock(value) {
    const text = String(value ?? "").trim();
    let hour, minute;
    if (/^\d{1,4}$/.test(text)) { hour = text.length <= 2 ? text : text.slice(0, -2); minute = text.length <= 2 ? "0" : text.slice(-2); }
    else if (/^\d{1,2}:\d{1,2}$/.test(text)) [hour, minute] = text.split(":");
    else return null;
    if (Number(hour) > 23 || Number(minute) > 59) return null;
    return `${String(Number(hour)).padStart(2, "0")}:${String(Number(minute)).padStart(2, "0")}`;
}
function canonicalMoney(value) {
    const text = String(value ?? "").replace(/\s/g, "");
    if (!text) return "";
    const match = /^(\d*)(?:[.,](\d{0,2}))?$/.exec(text);
    if (!match || !/\d/.test(text)) return null;
    const integer = (match[1] || "0").replace(/^0+(?=\d)/, "");
    if (integer.length > 12) return null;
    return integer + (match[2] ? `.${match[2]}` : "");
}
function formatMoneyInput(value, final = false) {
    let text = String(value ?? "").replace(/\s/g, "");
    if (!text) return "";
    if (final) { const canonical = canonicalMoney(text); if (canonical == null) return String(value); text = canonical; }
    if (!/^\d*(?:[.,]\d*)?$/.test(text)) return String(value);
    let [integer, fraction] = text.split(/[.,]/);
    if (final && fraction != null) fraction = fraction.padEnd(2, "0");
    return integer.replace(/\B(?=(\d{3})+(?!\d))/g, " ") + (fraction != null ? `,${fraction}` : "");
}
function suggestGroupEnd(start, monthsCount) {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(start || "") || !Number.isInteger(Number(monthsCount)) || Number(monthsCount) < 1) return null;
    const date = new Date(`${start}T12:00:00Z`);
    if (!Number.isFinite(date.getTime()) || date.toISOString().slice(0, 10) !== start) return null;
    const target = new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth() + Number(monthsCount), 1, 12));
    if (target.getUTCFullYear() > 9999) return null;
    const last = new Date(Date.UTC(target.getUTCFullYear(), target.getUTCMonth() + 1, 0, 12)).getUTCDate();
    target.setUTCDate(Math.min(date.getUTCDate(), last));
    return target.toISOString().slice(0, 10);
}
class SmartTime {
    static instances = new Map();
    static active = null;
    constructor(input) {
        this.input = input; this.required = input.required; input.required = false;
        this.label = document.querySelector(`label[for="${input.id}"]`)?.textContent.replace("*", "").trim() || "Vaqt";
        this.wrapper = document.createElement("div"); this.wrapper.className = "time-picker";
        input.before(this.wrapper); this.wrapper.append(input); input.classList.add("time-native"); input.tabIndex = -1; input.setAttribute("aria-hidden", "true");
        this.display = document.createElement("input"); this.display.id = `${input.id}-text`; this.display.type = "text"; this.display.inputMode = "numeric";
        this.display.autocomplete = "off"; this.display.maxLength = 5; this.display.placeholder = "HH:MM"; this.display.className = "time-text";
        this.display.setAttribute("aria-label", this.label); this.display.setAttribute("aria-required", String(this.required));
        this.button = document.createElement("button"); this.button.type = "button"; this.button.className = "time-trigger"; this.button.innerHTML = icon("clock");
        this.button.setAttribute("aria-label", `${this.label} — tanlash`); this.button.setAttribute("aria-haspopup", "dialog"); this.button.setAttribute("aria-expanded", "false"); this.button.setAttribute("aria-controls", `${input.id}-clock`);
        this.wrapper.append(this.display, this.button); document.querySelector(`label[for="${input.id}"]`)?.setAttribute("for", this.display.id);
        input.addEventListener("change", () => this.refresh());
        this.button.addEventListener("click", () => this.panel ? this.close(true) : this.open());
        this.display.addEventListener("input", () => { const value = parseClock(this.display.value) || "", changed = this.input.value !== value; this.input.value = value; this.display.setAttribute("aria-invalid", "false"); this.wrapper.classList.remove("invalid"); if (changed) this.input.dispatchEvent(new Event("change", { bubbles: true })); });
        this.display.addEventListener("blur", () => this.commit());
        this.display.addEventListener("keydown", (event) => {
            if (event.altKey && event.key === "ArrowDown") { event.preventDefault(); return this.open(); }
            if (["ArrowUp", "ArrowDown"].includes(event.key)) { event.preventDefault(); const value = parseClock(this.display.value) || "00:00"; let minutes = Number(value.slice(0, 2)) * 60 + Number(value.slice(3)); minutes = Math.max(0, Math.min(1439, minutes + (event.key === "ArrowUp" ? 1 : -1) * (event.shiftKey ? 15 : 1))); this.display.value = `${String(Math.floor(minutes / 60)).padStart(2, "0")}:${String(minutes % 60).padStart(2, "0")}`; this.commit(); }
        });
        SmartTime.instances.set(input, this); this.refresh();
    }
    refresh() { if (document.activeElement !== this.display && (!this.display.value || parseClock(this.display.value))) this.display.value = timeLabel(this.input.value); this.display.disabled = this.input.disabled; this.button.disabled = this.input.disabled; }
    commit() { const value = parseClock(this.display.value); if (value) this.display.value = value; const changed = this.input.value !== (value || ""); this.input.value = value || ""; if (changed) this.input.dispatchEvent(new Event("change", { bubbles: true })); return value; }
    validate() {
        const empty = !this.display.value.trim(), value = this.commit();
        if ((empty && !this.required) || (value && this.input.checkValidity())) return;
        this.wrapper.classList.add("invalid"); this.display.setAttribute("aria-invalid", "true"); this.display.focus();
        throw new Error(empty ? `${this.label} maydonini to‘ldiring.` : `${this.label}: vaqtni 24 soatlik formatda kiriting, masalan 14:30.`);
    }
    open() {
        if (this.input.disabled || this.panel) return;
        SmartSelect.active?.close(); SmartDate.active?.close(); SmartTime.active?.close(); SmartTime.active = this;
        const value = parseClock(this.display.value) || "09:00"; this.hour = Number(value.slice(0, 2)); this.minute = Number(value.slice(3));
        this.panel = document.createElement("div"); this.panel.className = "time-popover"; this.panel.id = `${this.input.id}-clock`;
        this.panel.setAttribute("role", "dialog"); this.panel.setAttribute("aria-label", `${this.label} — vaqt`);
        (this.input.closest("dialog") || document.body).append(this.panel); this.button.setAttribute("aria-expanded", "true");
        this.panel.addEventListener("click", (event) => {
            const button = event.target.closest("button"); if (!button) return;
            if (button.dataset.hour != null || button.dataset.minute != null) { const key = button.dataset.hour != null ? "hour" : "minute"; this[key] = Number(button.dataset[key]); this.updateSelection(); return; }
            if (button.hasAttribute("data-time-close")) return this.close(true);
            if (button.hasAttribute("data-time-apply")) { this.display.value = this.draft(); this.commit(); this.close(true); }
            if (button.hasAttribute("data-time-clear")) { this.display.value = ""; this.commit(); this.close(true); }
        });
        this.panel.addEventListener("keydown", (event) => {
            if (event.key === "Escape") { event.preventDefault(); event.stopPropagation(); this.close(true); return; }
            const grid = event.target.closest(".time-values"); if (!grid) return;
            const buttons = [...grid.querySelectorAll("button")], index = buttons.indexOf(event.target), columns = getComputedStyle(grid).gridTemplateColumns.split(/\s+/).length;
            const move = { ArrowRight: 1, ArrowLeft: -1, ArrowDown: columns, ArrowUp: -columns }[event.key];
            if (move != null) { event.preventDefault(); buttons[Math.max(0, Math.min(buttons.length - 1, index + move))].focus(); }
        });
        this.panel.innerHTML = `<div class="time-popover-heading"><div><span>${esc(this.label)}</span><strong class="time-preview">${this.draft()}</strong></div><button type="button" class="icon-button" data-time-close aria-label="Soat tanlovini yopish">${icon("close")}</button></div><div class="time-columns">${[["hour", "Soat", 24], ["minute", "Daqiqa", 60]].map(([key, label, count]) => `<div><div class="time-column-label">${label}</div><div class="time-values ${key}" role="group" aria-label="${label}" data-time-grid="${key}">${Array.from({ length: count }, (_, i) => `<button type="button" data-${key}="${i}" aria-label="${String(i).padStart(2, "0")} ${key === "hour" ? "soat" : "daqiqa"}" aria-pressed="${this[key] === i}" class="${this[key] === i ? "selected" : ""}">${String(i).padStart(2, "0")}</button>`).join("")}</div></div>`).join("")}</div><div class="time-popover-footer"><span>24 soat · Toshkent</span>${this.required ? "" : '<button class="text-button" type="button" data-time-clear>Tozalash</button>'}<button class="button primary" type="button" data-time-apply>Tanlash ${icon("check")}</button></div>`;
        const rect = this.wrapper.getBoundingClientRect(), width = Math.min(326, innerWidth - 24); this.panel.style.width = `${width}px`;
        this.panel.style.left = `${Math.max(12, Math.min(rect.left, innerWidth - width - 12))}px`;
        const height = this.panel.offsetHeight, below = innerHeight - rect.bottom - 12;
        this.panel.style.top = `${Math.max(12, below >= height || rect.top < height ? Math.min(rect.bottom + 8, innerHeight - height - 12) : rect.top - height - 8)}px`;
        this.panel.style.maxHeight = `${innerHeight - 24}px`;
        this.panel.querySelectorAll(".time-values .selected").forEach((button) => button.scrollIntoView({ block: "nearest" }));
        this.panel.querySelector(".hour .selected").focus();
    }
    draft() { return `${String(this.hour).padStart(2, "0")}:${String(this.minute).padStart(2, "0")}`; }
    updateSelection() { this.panel.querySelector(".time-preview").textContent = this.draft(); for (const key of ["hour", "minute"]) this.panel.querySelectorAll(`[data-${key}]`).forEach((button) => { const selected = Number(button.dataset[key]) === this[key]; button.classList.toggle("selected", selected); button.setAttribute("aria-pressed", String(selected)); }); }
    close(focus = false) { this.panel?.remove(); this.panel = null; this.button.setAttribute("aria-expanded", "false"); if (SmartTime.active === this) SmartTime.active = null; if (focus && this.display.isConnected) this.display.focus(); }
}
class MoneyInput {
    static instances = new Map();
    constructor(input) {
        this.input = input; this.label = document.querySelector(`label[for="${input.id}"]`)?.textContent.replace("*", "").trim() || "Summa";
        input.type = "text"; input.inputMode = "decimal"; input.autocomplete = "off"; input.classList.add("money-input");
        input.placeholder = input.required ? "0" : "Masalan, 1 250 000";
        const wrapper = document.createElement("div"); wrapper.className = "money-field"; input.before(wrapper); wrapper.append(input);
        const unit = document.createElement("span"); unit.className = "money-unit"; unit.textContent = "so‘m"; unit.setAttribute("aria-hidden", "true"); wrapper.append(unit);
        input.value = formatMoneyInput(input.value, true);
        input.addEventListener("focus", () => { if (input.value === "0") input.select(); });
        input.addEventListener("beforeinput", (event) => {
            const at = input.selectionStart; if (at !== input.selectionEnd) return;
            if (event.inputType === "deleteContentBackward" && input.value[at - 1] === " ") { event.preventDefault(); input.setRangeText("", Math.max(0, at - 2), at, "end"); input.dispatchEvent(new Event("input", { bubbles: true })); }
            if (event.inputType === "deleteContentForward" && input.value[at] === " ") { event.preventDefault(); input.setRangeText("", at, at + 2, "end"); input.dispatchEvent(new Event("input", { bubbles: true })); }
        });
        input.addEventListener("input", () => {
            const significant = input.value.slice(0, input.selectionStart).replace(/\s/g, "").length;
            input.value = formatMoneyInput(input.value); let at = 0, count = 0;
            while (at < input.value.length && count < significant) { if (!/\s/.test(input.value[at])) count++; at++; }
            input.setSelectionRange(at, at); input.setAttribute("aria-invalid", "false");
        });
        input.addEventListener("blur", () => { input.value = formatMoneyInput(input.value, true); });
        MoneyInput.instances.set(input, this);
    }
    value() {
        const value = canonicalMoney(this.input.value);
        if (value !== null) return value;
        this.input.setAttribute("aria-invalid", "true"); this.input.focus();
        throw new Error(`${this.label}: summani raqam bilan kiriting; ko‘pi bilan 12 ta butun va 2 ta kasr raqami bo‘lishi mumkin.`);
    }
}
function enhanceTimes(root = document) {
    for (const [input, instance] of SmartTime.instances) if (!input.isConnected) { instance.close(); SmartTime.instances.delete(input); }
    root.querySelectorAll('input[type="time"]').forEach((input) => SmartTime.instances.has(input) ? SmartTime.instances.get(input).refresh() : new SmartTime(input));
}
function enhanceMoney(root = document) {
    for (const input of MoneyInput.instances.keys()) if (!input.isConnected) MoneyInput.instances.delete(input);
    root.querySelectorAll('input[name="price"], input[name="monthly_budget"]').forEach((input) => { if (!MoneyInput.instances.has(input)) new MoneyInput(input); });
}
function enhanceSelects(root = document) {
    for (const [select, instance] of SmartSelect.instances) if (!select.isConnected) { instance.close(); SmartSelect.instances.delete(select); }
    root.querySelectorAll("select").forEach((select) => SmartSelect.instances.has(select) ? SmartSelect.instances.get(select).refresh() : new SmartSelect(select));
    enhanceDates(root);
    enhanceTimes(root); enhanceMoney(root);
}
function fillSelect(select, options, placeholder, value = "") {
    const blank = new Option(placeholder, "");
    const nodes = options.map((item) => { const option = new Option(item.label ?? item.name, item.value ?? item.id); if (item.avatar) option.dataset.avatar = item.avatar; if (item.hint) option.dataset.hint = item.hint; return option; });
    select.replaceChildren(blank, ...nodes); select.value = String(value ?? "");
    SmartSelect.instances.get(select)?.refresh();
}
document.addEventListener("pointerdown", (event) => { const active = SmartSelect.active; if (active && !active.wrapper.contains(event.target) && !active.panel?.contains(event.target)) active.close(); if (rowMenu && !rowMenu.contains(event.target) && !event.target.closest("[data-menu]")) closeRowMenu(); });
document.addEventListener("pointerdown", (event) => { const active = SmartDate.active; if (active && !active.wrapper.contains(event.target) && !active.panel?.contains(event.target)) active.close(); });
document.addEventListener("pointerdown", (event) => { const active = SmartTime.active; if (active && !active.wrapper.contains(event.target) && !active.panel?.contains(event.target)) active.close(); });
window.addEventListener("resize", () => { SmartSelect.active?.close(); SmartDate.active?.close(); SmartTime.active?.close(); closeRowMenu(); });
document.addEventListener("scroll", (event) => { if (SmartDate.active && !SmartDate.active.panel?.contains(event.target)) SmartDate.active.close(); if (SmartTime.active && !SmartTime.active.panel?.contains(event.target)) SmartTime.active.close(); }, true);

const field = (key, label, type = "text", extra = {}) => ({ key, label, type, ...extra });
const section = (label) => ({ type: "section", label });
const enumOptions = (values) => Object.entries(values).map(([value, label]) => ({ value, label }));
const moduleDefinitions = {
    schedules: { title: "Haftalik jadval", singular: "Jadval", add: "Jadval qo‘shish", icon: "schedules", group: "O‘QUV JARAYONI", path: "/group-schedules/", paged: true, mode: "week", modes: ["week", "table"], read: ["boss", "admin"], write: ["boss", "admin"], description: "Hafta ritmi: qaysi guruh, qaysi kun, qaysi xonada.", fields: [field("group_id", "Guruh", "select", { source: "groups", required: true, full: true }), field("weekday", "Hafta kuni", "select", { choices: enumOptions(weekdays), required: true, default: "1" }), field("room_id", "Xona", "select", { source: "rooms", required: true }), field("start_time", "Boshlanish vaqti", "time", { required: true, default: "14:00" }), field("end_time", "Tugash vaqti", "time", { required: true, default: "16:00", helper: "Vaqtni 24 soatlik formatda tanlang." })] },
    sessions: { title: "Darslar", singular: "Dars", add: "Dars qo‘shish", icon: "sessions", group: "O‘QUV JARAYONI", path: "/lesson-sessions/", paged: true, mode: "agenda", modes: ["agenda", "table"], read: ["boss", "admin"], write: ["boss", "admin"], description: "Aniq sana, o‘tilgan mavzu va darsning o‘z tarixi.", fields: [section("DARS VA JOY"), field("group_id", "Guruh", "select", { source: "groups", required: true, full: true }), field("date", "Dars sanasi", "date", { required: true }), field("teacher_id", "Dars o‘tadigan o‘qituvchi", "select", { source: "teachers", required: true }), field("start_time", "Boshlanish vaqti", "time", { required: true, default: "14:00" }), field("end_time", "Tugash vaqti", "time", { required: true, default: "16:00", helper: "Vaqtni 24 soatlik formatda tanlang." }), field("room_id", "Xona", "select", { source: "rooms", required: true }), field("status", "Dars holati", "select", { choices: enumOptions(sessionStatuses), required: true, default: "rejalashtirilgan" }), section("MAVZU VA XULOSA"), field("topic", "Dars mavzusi", "text", { max: 200, full: true, placeholder: "Masalan, Python: ro‘yxatlar va sikllar" }), field("note", "Dars haqida izoh", "textarea", { max: 5000, full: true, placeholder: "Nimalar o‘tildi? Keyingi dars uchun nimalar kerak?" })] },
    leads: { title: "Lidlar", singular: "Lid", add: "Yangi lid", icon: "leads", group: "CRM VA QABUL", path: "/leads/", paged: true, mode: "kanban", modes: ["kanban", "table"], read: ["boss", "admin", "manager"], write: ["boss", "admin"], description: "Birinchi qiziqishdan o‘quvchingiz bo‘lgunigacha.", fields: [section("ASOSIY MA’LUMOTLAR"), field("first_name", "Ism", "text", { required: true, max: 60 }), field("last_name", "Familiya", "text", { max: 60 }), field("phone", "Telefon", "tel", { required: true, placeholder: "+998 90 123 45 67" }), field("branch_id", "Filial", "select", { source: "branches", required: true }), section("QIZIQISH VA ALOQA"), field("course_id", "Qiziqqan kursi", "select", { source: "courses" }), field("source_id", "Qayerdan keldi?", "select", { source: "sources" }), field("status_id", "Qabul bosqichi", "select", { source: "statuses" }), field("assigned_to", "Mas’ul xodim", "select", { source: "employees" }), field("comment", "Suhbat va izoh", "textarea", { full: true, placeholder: "Qaysi yo‘nalishga qiziqyapti? Qachon bog‘lanish qulay?" }), field("lost_reason", "Yo‘qotilish sababi", "text", { full: true, max: 200, helper: "Lid yo‘qotilgan bo‘lsa, sababini yozishingiz mumkin." })] },
    students: { title: "O‘quvchilar", singular: "O‘quvchi", add: "O‘quvchi qo‘shish", icon: "students", group: "O‘QUV JARAYONI", path: "/students/", paged: true, mode: "table", modes: ["table", "grid"], write: ["boss", "admin"], description: "Ismlar, aloqa, holat va o‘quvchi haqida kerakli ma’lumotlar.", fields: [section("SHAXSIY MA’LUMOTLAR"), field("first_name", "Ism", "text", { required: true, max: 60 }), field("last_name", "Familiya", "text", { required: true, max: 60 }), field("phone", "O‘quvchi telefoni", "tel", { required: true }), field("parent_phone", "Ota-ona telefoni", "tel", { required: true }), field("birth_date", "Tug‘ilgan sana", "date"), field("branch_id", "Filial", "select", { source: "branches", required: true }), section("QABUL MA’LUMOTLARI"), field("source_id", "Qabul manbasi", "select", { source: "sources" }), field("lead_id", "Bog‘langan lid", "select", { source: "leads" }), field("status", "O‘quvchi holati", "select", { choices: enumOptions(studentStatuses), editOnly: true, full: true })] },
    groups: { title: "Guruhlar", singular: "Guruh", add: "Guruh ochish", icon: "groups", group: "O‘QUV JARAYONI", path: "/groups/", paged: true, mode: "grid", modes: ["grid", "table"], read: ["boss", "admin"], write: ["boss", "admin"], description: "Har bir guruhning o‘qituvchisi, xonasi va rivojlanish maydoni.", fields: [section("GURUHNING ASOSI"), field("name", "Guruh nomi", "text", { required: true, full: true, max: 80, placeholder: "Masalan, PY-26-01" }), field("branch_id", "Filial", "select", { source: "branches", required: true }), field("course_id", "Kurs", "select", { source: "courses", required: true }), field("teacher_id", "O‘qituvchi", "select", { source: "teachers", required: true }), field("room_id", "Xona", "select", { source: "rooms", required: true }), section("MUDDAT VA SHARTLAR"), field("start_date", "Boshlanish sanasi", "date", { required: true }), field("end_date", "Tugash sanasi", "date", { helper: "Kurs va boshlanish sanasi asosida tavsiya beriladi." }), field("max_students", "O‘quvchilar chegarasi", "number", { required: true, min: 1, max: 32767, helper: "Xona sig‘imidan oshmasligi kerak." }), field("price", "Oylik narx, so‘m", "number", { min: 0, step: "0.01", helper: "Bo‘sh qoldirilsa, kursning standart narxi olinadi." }), field("status", "Guruh holati", "select", { choices: enumOptions(groupStatuses), required: true, default: "rejalashtirilgan", full: true })] },
    courses: { title: "Kurslar", singular: "Kurs", add: "Kurs qo‘shish", icon: "courses", group: "O‘QUV JARAYONI", path: "/courses/", mode: "grid", modes: ["grid", "table"], write: ["boss", "admin"], description: "Markazingiz taklif qiladigan yo‘nalishlar va o‘quv dasturlari.", fields: [field("name", "Kurs nomi", "text", { required: true, full: true, max: 120, placeholder: "Masalan, Python Backend" }), field("description", "Kurs haqida", "textarea", { full: true }), field("duration_months", "Davomiyligi, oy", "number", { min: 1 }), field("lessons_count", "Jami darslar", "number", { min: 1 }), field("price", "Oylik narx, so‘m", "number", { required: true, min: 0, step: "0.01", default: 0 }), field("min_age", "Eng kichik yosh", "number", { min: 0, max: 100 })] },
    employees: { title: "Jamoa", singular: "Xodim", add: "Xodim qo‘shish", icon: "employees", group: "JAMOA VA TASHKILOT", path: "/employees/", mode: "grid", modes: ["grid", "table"], activePair: true, read: ["boss", "admin"], write: ["boss", "admin"], description: "Markazingizni oldinga boshlaydigan odamlar.", fields: [section("SHAXSIY MA’LUMOTLAR"), field("first_name", "Ism", "text", { required: true, max: 60 }), field("last_name", "Familiya", "text", { required: true, max: 60 }), field("phone", "Telefon / login", "tel", { required: true }), field("email", "Elektron pochta", "email"), field("birth_date", "Tug‘ilgan sana", "date", { required: true }), field("photo_url", "Rasm havolasi", "url"), section("ISH JOYI VA KIRISH"), field("branch_id", "Asosiy filial", "select", { required: true, source: "branches" }), field("position", "Lavozim", "text", { required: true, max: 80 }), field("hired_at", "Ishga kirgan sana", "date", { required: true }), field("password", "Parol", "password", { createRequired: true, helper: "Tahrirlashda bo‘sh qoldirsangiz, avvalgi parol saqlanadi." })] },
    teachers: { title: "O‘qituvchilar", singular: "O‘qituvchi profili", add: "O‘qituvchi biriktirish", icon: "teachers", group: "JAMOA VA TASHKILOT", path: "/teacher-profiles/", mode: "grid", modes: ["grid", "table"], read: ["boss", "admin"], write: ["boss", "admin"], description: "Bilim beradigan ustozlar va ularning yo‘nalishlari.", fields: [field("employee_id", "Jamoa a’zosi", "select", { required: true, source: "employees", full: true, createOnly: true, helper: "Avval xodim Jamoa bo‘limida yaratilgan bo‘lishi kerak." }), field("specialization", "Mutaxassislik", "text", { full: true, max: 120, placeholder: "Masalan, Python / IELTS / Grafik dizayn" }), field("experience_years", "Tajriba, yil", "number", { min: 0, max: 80 }), field("max_groups", "Bir vaqtdagi guruhlar limiti", "number", { min: 0, max: 32767 }), field("bio", "Ustoz haqida", "textarea", { full: true })] },
    branches: { title: "Filiallar", singular: "Filial", add: "Filial qo‘shish", icon: "branches", group: "JAMOA VA TASHKILOT", path: "/branches/", mode: "grid", modes: ["grid", "table"], read: ["boss", "admin"], write: ["boss"], noDelete: true, description: "Ta’limga yaqinroq bo‘ladigan yangi manzillar.", fields: [field("name", "Filial nomi", "text", { required: true, max: 120 }), field("code", "Qisqa kodi", "text", { required: true, max: 20, placeholder: "CHL / YNS / SRG" }), field("address", "To‘liq manzil", "textarea", { required: true, full: true }), field("phone", "Filial telefoni", "tel", { required: true }), field("city", "Shahar", "text", { required: true, max: 60 }), field("opened_at", "Ochilgan sana", "date", { required: true }), field("is_active", "Filial faol", "checkbox", { default: true, helper: "Faol filial yangi qabul va guruhlar uchun ochiq." })] },
    rooms: { title: "Xonalar", singular: "Xona", add: "Xona qo‘shish", icon: "rooms", group: "JAMOA VA TASHKILOT", path: "/rooms/", mode: "grid", modes: ["grid", "table"], activePair: true, read: ["boss", "admin"], write: ["boss", "admin"], description: "Darslar uchun qulay joy va har bir o‘rin hisobi.", fields: [field("branch_id", "Filial", "select", { source: "branches", required: true, full: true }), field("name", "Xona nomi yoki raqami", "text", { required: true, max: 60, placeholder: "Masalan, 201 yoki Oxford" }), field("capacity", "Sig‘imi, o‘rin", "number", { required: true, min: 1, max: 32767 }), field("is_active", "Xona foydalanishda", "checkbox", { default: true, full: true })] },
    sources: { title: "Qabul manbalari", singular: "Manba", add: "Manba qo‘shish", icon: "sources", group: "CRM SOZLAMALARI", path: "/lead_source/", mode: "grid", modes: ["grid", "table"], read: ["boss", "admin", "manager"], write: ["boss", "admin", "manager"], description: "O‘quvchilaringiz sizni qayerdan topayotganini biling.", fields: [field("name", "Manba nomi", "text", { required: true, max: 80, full: true, placeholder: "Instagram, Telegram, tanish orqali…" }), field("monthly_budget", "Oylik reklama budjeti, so‘m", "number", { min: 0, step: "0.01", default: 0, full: true })] },
    statuses: { title: "Qabul bosqichlari", singular: "Bosqich", add: "Bosqich qo‘shish", icon: "statuses", group: "CRM SOZLAMALARI", path: "/lead_statuses/", mode: "workflow", modes: ["workflow", "table"], noDelete: true, read: ["boss", "admin", "manager"], write: ["boss", "admin"], description: "Murojaatdan natijagacha — markazingizga mos qabul yo‘li.", fields: [field("name", "Bosqich nomi", "text", { required: true, max: 60, full: true }), field("is_won", "Muvaffaqiyatli yakun", "checkbox", { full: true, helper: "O‘quvchiga aylangan lidlar uchun yakuniy bosqich." }), field("is_lost", "Yo‘qotilgan lid", "checkbox", { full: true, helper: "Qabul davom etmaydigan murojaatlar uchun." })] },
    roles: { title: "Rollar", singular: "Rol", add: "Rol yaratish", icon: "roles", group: "TIZIM VA RUXSATLAR", path: "/role/", mode: "grid", modes: ["grid", "table"], read: ["boss", "admin"], write: ["boss"], description: "Har bir jamoa a’zosi uchun aniq vazifa va ruxsatlar.", fields: [field("name", "Rol nomi", "text", { required: true, full: true, max: 80 }), field("code", "Tizim kodi", "text", { required: true, full: true, max: 40, helper: "Masalan: admin, manager, teacher, accountant. Ruxsatlar kod bo‘yicha ishlaydi." })] },
    assignments: { title: "Xodim ruxsatlari", singular: "Ruxsat", add: "Rol biriktirish", icon: "assignments", group: "TIZIM VA RUXSATLAR", path: "/employee-roles/", mode: "table", modes: ["table"], read: ["boss"], write: ["boss"], description: "Kim, qaysi rol bilan, qaysi filialda ishlashini belgilang.", fields: [field("employee_id", "Xodim", "select", { source: "employees", required: true, full: true, createOnly: true }), field("role_id", "Rol", "select", { source: "roles", required: true, full: true }), field("branch_id", "Ruxsat amal qiladigan filial", "select", { source: "branches", full: true, placeholder: "Barcha filiallar", helper: "Bo‘sh qoldirilsa, rol barcha filiallarda amal qiladi." })] },
};

function canRead(key) { const def = moduleDefinitions[key]; return !def?.read || hasRole(...def.read); }
function canWrite(key = state.view) { return hasRole(...(moduleDefinitions[key]?.write || ["boss", "admin"])); }
function lookup(source, id) { return state.options?.[source]?.find((row) => row.id === Number(id)); }
function protectedAssignment(row) { return state.view === "assignments" && lookup("employees", row.employee_id)?.is_superadmin && ["boss", "admin"].includes(lookup("roles", row.role_id)?.code); }
function protectedAdminPill() { return `<span class="pill no-dot blue">${icon("roles")}Asosiy admin</span>`; }
function keyOf(row, module = state.view) { return String(module === "assignments" ? `${row.employee_id}:${row.role_id}` : module === "teachers" ? row.employee_id : row.id); }
function recordName(row, module = state.view) {
    if (["schedules", "sessions"].includes(module)) return `${row.group?.name || lookup("groups", row.group_id)?.name || "Guruh"} · ${module === "schedules" ? weekdays[row.weekday] : dateLabel(row.date)}`;
    if (module === "teachers" || module === "assignments") return fullName(lookup("employees", row.employee_id));
    return row.name || fullName(row);
}
function activePill(value) { return `<span class="pill ${value ? "green" : "gray"}">${value ? "Faol" : "Faol emas"}</span>`; }
function statusPill(value, type = "student") {
    const names = type === "group" ? groupStatuses : type === "session" ? sessionStatuses : studentStatuses;
    const tone = { faol: "green", otilgan: "green", sinovda: "amber", rejalashtirilgan: "amber", muzlatilgan: "purple", bitirgan: "blue", tugagan: "blue", ketgan: "gray", bekor_qilingan: "red" }[value] || "gray";
    return `<span class="pill ${tone}">${esc(names[value] || value || "Belgilanmagan")}</span>`;
}
function leadStatus(row) { const status = row.status || lookup("statuses", row.status_id); return status ? `<span class="pill ${status.is_won ? "green" : status.is_lost ? "red" : "purple"}">${esc(status.name)}</span>` : '<span class="pill gray">Bosqichsiz</span>'; }
function personCell(row, module = state.view) {
    const name = recordName(row, module);
    return `<div class="person-cell">${avatar(name)}<span><button class="cell-link" type="button" data-detail="${esc(keyOf(row, module))}">${esc(name)}</button><span class="cell-sub">${esc(row.phone || lookup("employees", row.employee_id)?.phone || `ID ${row.id ?? row.employee_id}`)}</span></span></div>`;
}
function namedCell(row, subtitle = "") { return `<button class="cell-link" type="button" data-detail="${esc(keyOf(row))}">${esc(row.name)}</button>${subtitle ? `<span class="cell-sub">${esc(subtitle)}</span>` : ""}`; }
function branchLabel(row) { return esc(row.branch?.name || lookup("branches", row.branch_id)?.name || (row.branch_id == null ? "Barcha filiallar" : `Filial #${row.branch_id}`)); }
function capacityCell(row) { const percent = Math.min(100, row.current_students / row.max_students * 100); return `<strong>${row.current_students}</strong> <span class="muted">/ ${row.max_students}</span><div class="capacity-track"><span style="width:${percent}%"></span></div>`; }
const columns = {
    schedules: [["Guruh", (r) => `<button class="cell-link" type="button" data-detail="${r.id}">${esc(r.group.name)}</button><span class="cell-sub">${branchLabel(r.group)}</span>`], ["Hafta kuni", (r) => esc(weekdays[r.weekday])], ["Vaqt", (r) => `<span class="time-label">${timeLabel(r.start_time)}–${timeLabel(r.end_time)}</span>`], ["Xona", (r) => esc(r.room.name)], ["O‘qituvchi", (r) => esc(fullName(r.group.teacher))], ["Guruh holati", (r) => statusPill(r.group.status, "group")]],
    sessions: [["Dars / guruh", (r) => `<button class="cell-link" type="button" data-detail="${r.id}">${esc(r.group.name)}</button><span class="cell-sub">${esc(r.topic || "Mavzu hali kiritilmagan")}</span>`], ["Sana", (r) => dateLabel(r.date)], ["Vaqt", (r) => `<span class="time-label">${timeLabel(r.start_time)}–${timeLabel(r.end_time)}</span>`], ["O‘qituvchi", (r) => esc(fullName(r.teacher))], ["Xona", (r) => `${esc(r.room.name)}<span class="cell-sub">${branchLabel(r.group)}</span>`], ["Holati", (r) => statusPill(r.status, "session")]],
    students: [["O‘quvchi", (r) => personCell(r)], ["Filial", (r) => branchLabel(r)], ["Ota-ona telefoni", (r) => esc(r.parent_phone)], ["Manba", (r) => esc(r.source?.name || "To‘g‘ridan-to‘g‘ri")], ["Balans", (r) => `<span class="${Number(r.balance) < 0 ? "balance-negative" : "balance-positive"}">${money.format(r.balance)} so‘m</span>`], ["Holati", (r) => statusPill(r.status)]],
    groups: [["Guruh / kurs", (r) => namedCell(r, r.course.name)], ["Filial / xona", (r) => `${branchLabel(r)}<span class="cell-sub">${esc(r.room.name)}</span>`], ["O‘qituvchi", (r) => `<div class="person-cell">${avatar(fullName(r.teacher), "small")} ${esc(fullName(r.teacher))}</div>`], ["O‘quvchilar", capacityCell], ["Oylik narx", (r) => `${money.format(r.effective_price)}<span class="cell-sub">so‘m${r.price === null ? " · kurs narxi" : ""}</span>`], ["Holati", (r) => statusPill(r.status, "group")]],
    leads: [["Lid", (r) => personCell(r)], ["Qiziqqan kursi", (r) => esc(r.course?.name || "Aniqlanmagan")], ["Manba", (r) => esc(r.source?.name || "Belgilanmagan")], ["Mas’ul", (r) => esc(r.assignee ? fullName(r.assignee) : "Biriktirilmagan")], ["Bosqich", leadStatus], ["Murojaat sanasi", (r) => dateLabel(r.created_at)]],
    courses: [["Kurs", (r) => namedCell(r, r.description || "")], ["Davomiyligi", (r) => r.duration_months ? `${r.duration_months} oy` : "Belgilanmagan"], ["Darslar", (r) => r.lessons_count ? `${r.lessons_count} ta` : "Belgilanmagan"], ["Oylik narx", (r) => `${money.format(r.price)} so‘m`], ["Yosh chegarasi", (r) => r.min_age != null ? `${r.min_age}+ yosh` : "Belgilanmagan"], ["Holati", (r) => activePill(r.is_active)]],
    employees: [["Xodim", (r) => personCell(r)], ["Lavozim", (r) => esc(r.position)], ["Filial", branchLabel], ["Rollar", (r) => r.employee_role.map((er) => `<span class="pill no-dot purple">${esc(er.role?.name || lookup("roles", er.role_id)?.name || "Rol")}</span>`).join(" ") || "Biriktirilmagan"], ["Ishga kirgan", (r) => dateLabel(r.hired_at)], ["Holati", (r) => r.is_superadmin ? protectedAdminPill() : activePill(r.is_active)]],
    teachers: [["Ustoz", (r) => personCell(r)], ["Yo‘nalish", (r) => esc(r.specialization || "Belgilanmagan")], ["Tajriba", (r) => r.experience_years != null ? `${r.experience_years} yil` : "Belgilanmagan"], ["Guruhlar limiti", (r) => r.max_groups ?? "Cheklanmagan"], ["Filial", (r) => branchLabel(lookup("employees", r.employee_id) || {})]],
    branches: [["Filial", (r) => namedCell(r, r.city)], ["Kodi", (r) => `<span class="code-label">${esc(r.code)}</span>`], ["Manzil", (r) => esc(r.address)], ["Telefon", (r) => esc(r.phone)], ["Ochilgan", (r) => dateLabel(r.opened_at)], ["Holati", (r) => activePill(r.is_active)]],
    rooms: [["Xona", (r) => namedCell(r)], ["Filial", branchLabel], ["Sig‘imi", (r) => `${r.capacity} o‘rin`], ["Holati", (r) => activePill(r.is_active)]],
    sources: [["Manba", (r) => namedCell(r)], ["Oylik budjet", (r) => `${money.format(r.monthly_budget || 0)} so‘m`], ["Holati", (r) => activePill(r.is_active)]],
    statuses: [["Bosqich", (r) => namedCell(r)], ["Tartib", (r) => `<span class="code-label">${String(r.position).padStart(2, "0")}</span>`], ["Natija", (r) => `<span class="pill ${r.is_won ? "green" : r.is_lost ? "red" : "purple"}">${r.is_won ? "Muvaffaqiyatli" : r.is_lost ? "Yo‘qotilgan" : "Jarayonda"}</span>`]],
    roles: [["Rol", (r) => namedCell(r)], ["Tizim kodi", (r) => `<span class="code-label">${esc(r.code)}</span>`], ["Turi", (r) => `<span class="pill ${r.is_system ? "purple" : "gray"}">${r.is_system ? "Tizim roli" : "Maxsus rol"}</span>`]],
    assignments: [["Xodim", (r) => personCell(r)], ["Rol", (r) => `<span class="pill purple no-dot">${esc(lookup("roles", r.role_id)?.name || r.role_id)}</span>`], ["Amal qilish doirasi", branchLabel]],
};
function rowButtons(row) { const key = esc(keyOf(row)); return `<div class="row-actions">${canWrite() && !protectedAssignment(row) ? `<button type="button" class="icon-button" data-edit="${key}" aria-label="${esc(recordName(row))} — tahrirlash">${icon("edit")}</button>` : ""}<button type="button" class="icon-button" data-menu="${key}" aria-label="${esc(recordName(row))} — amallar">${icon("more")}</button></div>`; }
function recordCard(row, index) {
    const module = state.view, tone = tones[index % 5], key = esc(keyOf(row));
    const menu = `<button class="icon-button" type="button" data-menu="${key}" aria-label="${esc(recordName(row))} — amallar">${icon("more")}</button>`;
    const title = `<button class="cell-link" type="button" data-detail="${key}"><h3>${esc(recordName(row))}</h3></button>`;
    if (["employees", "teachers", "students"].includes(module)) {
        const person = module === "teachers" ? lookup("employees", row.employee_id) : row;
        const description = module === "employees" ? row.position : module === "teachers" ? row.specialization || "Mutaxassislik belgilanmagan" : row.source?.name || "To‘g‘ridan-to‘g‘ri qabul";
        const status = module === "students" ? statusPill(row.status) : person?.is_superadmin ? protectedAdminPill() : activePill(person?.is_active);
        return `<article class="entity-card team-card"><div class="entity-top">${avatar(recordName(row))}${menu}</div>${title}<p class="entity-description">${esc(description)}</p><div class="entity-meta"><span>${icon("pin")}${branchLabel(person || row)}</span></div>${status}<div class="entity-bottom"><span>${module === "teachers" ? `${row.experience_years ?? "—"} yil tajriba` : esc(person?.phone || "")}</span><button class="text-button" type="button" data-detail="${key}">Profil ${icon("arrow")}</button></div></article>`;
    }
    if (module === "groups") return `<article class="entity-card"><div class="entity-top"><span class="entity-icon ${tone}">${icon("groups")}</span>${menu}</div>${title}<p class="entity-description">${esc(row.course.name)}<br>${esc(fullName(row.teacher))}</p><div class="entity-meta"><span>${icon("pin")}${branchLabel(row)}</span><span>${icon("rooms")}${esc(row.room.name)}</span></div><div class="person-cell"><span>${row.current_students} <span class="muted">/ ${row.max_students} o‘quvchi</span></span><span style="margin-left:auto">${statusPill(row.status, "group")}</span></div><div class="capacity-track wide"><span style="width:${Math.min(100, row.current_students / row.max_students * 100)}%"></span></div><div class="entity-bottom"><span class="entity-price">${money.format(row.effective_price)} <small>so‘m / oy</small></span><button class="text-button" data-detail="${key}" type="button">${icon("arrow")}</button></div></article>`;
    if (module === "courses") return `<article class="entity-card"><div class="entity-top"><span class="entity-icon ${tone}">${icon("courses")}</span>${menu}</div>${title}<p class="entity-description">${esc(row.description || "Kurs tavsifi hali kiritilmagan.")}</p><div class="entity-meta"><span>${icon("clock")}${row.duration_months ? `${row.duration_months} oy` : "Muddat belgilanmagan"}</span><span>${icon("courses")}${row.lessons_count ?? "—"} dars</span>${row.min_age != null ? `<span>${row.min_age}+ yosh</span>` : ""}</div>${activePill(row.is_active)}<div class="entity-bottom"><span class="entity-price">${money.format(row.price)} <small>so‘m / oy</small></span><button class="text-button" type="button" data-detail="${key}">${icon("arrow")}</button></div></article>`;
    if (module === "branches") return `<article class="entity-card"><div class="entity-top"><span class="entity-icon ${tone}">${icon("branches")}</span>${menu}</div><span class="code-label">${esc(row.code)}</span><div style="margin-top:13px">${title}</div><p class="entity-description">${esc(row.address)}</p><div class="entity-meta"><span>${icon("pin")}${esc(row.city)}</span><span>${icon("phone")}${esc(row.phone)}</span></div><div class="entity-bottom">${activePill(row.is_active)}<span>${dateLabel(row.opened_at)}</span></div></article>`;
    if (module === "rooms") return `<article class="entity-card"><div class="entity-top"><span class="pill no-dot ${tone === "mint" ? "green" : "purple"}">${branchLabel(row)}</span>${menu}</div><div class="room-number">${esc(row.name)}</div><div class="entity-meta"><span>${icon("students")}${row.capacity} o‘rinli xona</span></div><div class="entity-bottom">${activePill(row.is_active)}<button class="text-button" type="button" data-detail="${key}">Batafsil ${icon("arrow")}</button></div></article>`;
    if (module === "sources") return `<article class="entity-card"><div class="entity-top"><span class="entity-icon ${tone}">${icon("sources")}</span>${menu}</div>${title}<p class="entity-description">Oylik reklama budjeti</p><div class="entity-price">${money.format(row.monthly_budget || 0)} <small>so‘m</small></div><div class="entity-bottom">${activePill(row.is_active)}<button class="text-button" type="button" data-detail="${key}">Batafsil ${icon("arrow")}</button></div></article>`;
    return `<article class="entity-card"><div class="entity-top"><span class="entity-icon ${tone}">${icon(module)}</span>${menu}</div>${title}<p class="entity-description">${esc(row.code || "")}</p><div class="entity-bottom"><span class="pill ${row.is_system ? "purple" : "gray"}">${row.is_system ? "Tizim roli" : "Maxsus rol"}</span><button class="text-button" type="button" data-detail="${key}">Batafsil ${icon("arrow")}</button></div></article>`;
}
function filtersFor(module) {
    if (["schedules", "sessions"].includes(module)) return [{ key: "group_id", label: "Barcha guruhlar", options: sourceOptions("groups") }, { key: module === "schedules" ? "weekday" : "status", label: module === "schedules" ? "Haftaning barcha kunlari" : "Barcha holatlar", options: enumOptions(module === "schedules" ? weekdays : sessionStatuses) }, { key: "teacher_id", label: "Barcha o‘qituvchilar", options: sourceOptions("teachers") }];
    if (module === "students") return [{ key: "status", label: "Barcha holatlar", options: enumOptions(studentStatuses) }, { key: "debt", label: "Barcha balanslar", options: [{ value: "debt", label: "Qarzdorlar" }, { value: "positive", label: "Musbat balans" }] }];
    if (module === "groups") return [{ key: "status", label: "Barcha holatlar", options: enumOptions(groupStatuses) }, { key: "course_id", label: "Barcha kurslar", options: sourceOptions("courses") }];
    if (module === "leads") return [{ key: "status_id", label: "Barcha bosqichlar", options: sourceOptions("statuses") }, { key: "assigned_to", label: "Barcha mas’ullar", options: sourceOptions("employees") }];
    if (["courses", "employees", "rooms", "sources", "branches"].includes(module)) return [{ key: "is_active", label: "Barcha holatlar", options: [{ value: "true", label: "Faol" }, { value: "false", label: "Faol emas" }] }];
    if (module === "assignments") return [{ key: "role_id", label: "Barcha rollar", options: sourceOptions("roles") }];
    return [];
}
function sourceOptions(source, values = {}, current = null) {
    let rows = state.options?.[source === "teachers" ? "employees" : source] || [];
    if (source === "teachers") rows = rows.filter((r) => r.is_teacher || r.id === Number(current));
    if (state.editor?.module === "groups") {
        if (["teachers", "rooms"].includes(source)) rows = rows.filter((r) => r.branch_id === Number(values.branch_id) || (r.id === Number(current) && values.branch_id === state.editor.row?.branch_id));
        if (["teachers", "rooms", "branches", "courses"].includes(source)) rows = rows.filter((r) => r.is_active || r.id === Number(current));
    }
    if (source === "groups" && state.branch) rows = rows.filter((r) => r.branch_id === Number(state.branch) || r.id === Number(current));
    if (["schedules", "sessions"].includes(state.editor?.module)) {
        const group = lookup("groups", values.group_id);
        if (["rooms", "teachers"].includes(source)) rows = rows.filter((r) => group && r.branch_id === group.branch_id && (r.is_active || r.id === Number(current)));
        if (source === "groups") rows = rows.filter((r) => ["faol", "rejalashtirilgan"].includes(r.status) || r.id === Number(current));
    }
    return rows.map((r) => ({ value: r.id, label: r.name || fullName(r), avatar: r.first_name ? fullName(r) : undefined, hint: source === "rooms" ? `${r.capacity} o‘rin · ${lookup("branches", r.branch_id)?.name || ""}` : r.phone || (source === "courses" ? `${money.format(r.price)} so‘m / oy` : "") }));
}
function filterRows(rows) {
    const search = (state.filters.search || "").trim().toLocaleLowerCase();
    return rows.filter((row) => {
        if (state.view === "branches" && state.branch && row.id !== Number(state.branch)) return false;
        if (state.branch && (row.branch_id ?? lookup("employees", row.employee_id)?.branch_id) != null && Number(row.branch_id ?? lookup("employees", row.employee_id)?.branch_id) !== Number(state.branch)) return false;
        if (search && !`${recordName(row)} ${JSON.stringify(row)}`.toLocaleLowerCase().includes(search)) return false;
        for (const [key, value] of Object.entries(state.filters)) {
            if (!value || key === "search") continue;
            if (key === "is_active" && String(row.is_active) !== value) return false;
            if (key === "role_id" && row.role_id !== Number(value)) return false;
        }
        return true;
    });
}
function timetableControls() {
    if (!["schedules", "sessions"].includes(state.view)) return "";
    if (state.view === "sessions") return lessonPlannerControls();
    return `<div class="timetable-controls"><div class="timetable-caption">${icon("schedules")}<span>Doimiy haftalik reja<small>Vaqtlar Toshkent vaqti bilan · UTC+5</small></span></div><p>Guruhning o‘qish muddati davomida amal qiladi.</p>${canWrite() ? `<button type="button" class="button secondary" data-action="generate-sessions">${icon("sessions")}Jadvaldan darslar yaratish</button>` : ""}</div>`;
}
function lessonPeriod(preset) {
    if (preset === "all") return { date_from: "", date_to: "" };
    const today = isoToday(), monday = shiftCalendarDay(today, -((calendarDate(today).getUTCDay() + 6) % 7));
    return preset === "today" ? { date_from: today, date_to: today } : { date_from: monday, date_to: shiftCalendarDay(monday, 6) };
}
function currentLessonPeriod() { return ["all", "today", "week"].find((key) => { const period = lessonPeriod(key); return (state.filters.date_from || "") === period.date_from && (state.filters.date_to || "") === period.date_to; }); }
function lessonPlannerControls() {
    const period = currentLessonPeriod();
    const anchor = state.filters.date_from || isoToday(), month = months[Number(anchor.slice(5, 7)) - 1];
    return `<div class="lesson-planner-tools"><div class="lesson-hero-top"><span class="lesson-hero-eyebrow"><i></i>O‘QUV JARAYONI <span>/</span> TAQVIM</span><div class="list-actions"><div class="view-toggle" role="group" aria-label="Ko‘rinish">${[["agenda", "sessions", "Kunlik darslar"], ["table", "table", "Jadval"]].map(([mode, glyph, label]) => `<button type="button" data-mode="${mode}" class="${state.mode === mode ? "active" : ""}" aria-label="${label} ko‘rinishi" aria-pressed="${state.mode === mode}">${icon(glyph)}</button>`).join("")}</div><button class="icon-button" type="button" data-action="refresh" aria-label="Ro‘yxatni yangilash">${icon("refresh")}</button></div></div><div class="lesson-hero-main"><div class="lesson-hero-copy"><div class="lesson-hero-count"><span id="list-count">—</span> TA DARS</div><h2>Darslar<br><span>taqvimi.</span></h2><p>Jadval, mavzu va dars holati — bir ekranda.</p>${canWrite() ? `<button type="button" class="button planner-generate" data-action="generate-sessions" aria-label="Jadvaldan darslar yaratish">${icon("plus")}<span>Jadvaldan darslar yaratish</span>${icon("arrow")}</button>` : ""}</div><button type="button" class="lesson-date-poster" data-open-date="date_from" aria-label="Sana kalendarini ochish"><span class="poster-binding" aria-hidden="true"><i></i><i></i></span><span id="lesson-anchor-label">${state.filters.date_from ? "Davr boshi" : "Bugun"}</span><strong id="lesson-anchor-day">${anchor.slice(8)}</strong><span class="poster-bottom"><span id="lesson-anchor-month">${esc(month)} ${anchor.slice(0, 4)}</span>${icon("arrow")}</span></button><span class="lesson-hero-orbit" aria-hidden="true"><i></i><i></i><i></i></span></div><div class="lesson-date-controls"><div class="period-presets" role="group" aria-label="Darslar davri">${[["all", "Barchasi"], ["today", "Bugun"], ["week", "Shu hafta"]].map(([key, label]) => `<button type="button" data-lesson-period="${key}" aria-pressed="${period === key}" class="${period === key ? "active" : ""}">${label}</button>`).join("")}</div><div class="lesson-range-fields"><label><span>Dan</span><input type="date" data-filter="date_from" aria-label="Davr boshlanishi" value="${esc(state.filters.date_from || "")}"></label><span class="range-join">${icon("arrow")}</span><label><span>Gacha</span><input type="date" data-filter="date_to" aria-label="Davr tugashi" value="${esc(state.filters.date_to || "")}"></label></div><span class="range-help">TOSHKENT / UTC+5</span></div></div>`;
}
function lessonShell() {
    $("page-content").innerHTML = `<section class="panel data-panel session-panel">${lessonPlannerControls()}<div class="toolbar lesson-filterbar"><div class="search-field">${icon("search")}<input id="record-search" data-filter="search" placeholder="Guruh yoki mavzuni qidirish…" aria-label="Ro‘yxatdan qidirish" autocomplete="off" value="${esc(state.filters.search || "")}"></div>${filtersFor("sessions").map((filter) => `<select id="filter-${filter.key}" data-filter="${filter.key}" data-label="${esc(filter.label)}"><option value="">${esc(filter.label)}</option>${filter.options.map((option) => `<option value="${esc(option.value)}" ${String(state.filters[filter.key]) === String(option.value) ? "selected" : ""}>${esc(option.label)}</option>`).join("")}</select>`).join("")}<button class="text-button" type="button" data-action="clear-filters" ${Object.values(state.filters).some(Boolean) ? "" : "hidden"}>Tozalash ${icon("close")}</button></div><div id="bulk-bar" class="bulk-bar" hidden></div><div id="records"></div><div class="table-footer"><span id="result-count" role="status"></span><div class="pagination"><button class="icon-button" type="button" id="previous-page" data-page="-1" aria-label="Oldingi sahifa">${icon("left")}</button><span class="page-position" id="page-position">1 / 1</span><button class="icon-button" type="button" id="next-page" data-page="1" aria-label="Keyingi sahifa">${icon("right")}</button></div></div></section>`;
    enhanceSelects($("page-content")); syncLessonControls();
}
function syncLessonControls() {
    if (state.view !== "sessions") return;
    const period = currentLessonPeriod();
    const anchor = state.filters.date_from || isoToday();
    if ($("lesson-anchor-day")) { $("lesson-anchor-day").textContent = anchor.slice(8); $("lesson-anchor-month").textContent = `${months[Number(anchor.slice(5, 7)) - 1]} ${anchor.slice(0, 4)}`; $("lesson-anchor-label").textContent = !state.filters.date_from ? "Bugun" : state.filters.date_from === state.filters.date_to ? "Tanlangan kun" : "Davr boshi"; }
    document.querySelectorAll("[data-lesson-period]").forEach((button) => { button.classList.toggle("active", button.dataset.lessonPeriod === period); button.setAttribute("aria-pressed", String(button.dataset.lessonPeriod === period)); });
    for (const key of ["date_from", "date_to"]) { const input = document.querySelector(`input[data-filter="${key}"]`); if (input) { input.value = state.filters[key] || ""; input.min = key === "date_to" ? state.filters.date_from || "" : ""; input.max = ""; SmartDate.instances.get(input)?.refresh(); } }
}
function lessonMinutes(row) { const minutes = (value) => Number(value.slice(0, 2)) * 60 + Number(value.slice(3, 5)); return Math.max(0, minutes(row.end_time) - minutes(row.start_time)); }
function durationLabel(minutes) { return [Math.floor(minutes / 60) ? `${Math.floor(minutes / 60)} soat` : "", minutes % 60 ? `${minutes % 60} daqiqa` : ""].filter(Boolean).join(" ") || "0 daqiqa"; }
function lessonEntry(row) {
    const now = new Date(), start = new Date(`${row.date}T${timeLabel(row.start_time)}:00+05:00`), end = new Date(`${row.date}T${timeLabel(row.end_time)}:00+05:00`);
    const live = row.status === "rejalashtirilgan" && now >= start && now < end, finished = row.status === "rejalashtirilgan" && now >= end;
    const name = esc(row.group.name), key = esc(row.id);
    return `<article class="lesson-entry tone-${toneId(row.group_id)}${row.status === "bekor_qilingan" ? " cancelled" : ""}${live ? " is-live" : ""}"><div class="lesson-time-block"><span class="lesson-time-kicker">DARS VAQTI</span><time datetime="${row.date}T${timeLabel(row.start_time)}:00+05:00">${timeLabel(row.start_time)}</time><span class="lesson-time-divider"></span><span class="lesson-end-time">${timeLabel(row.end_time)}</span><small>${durationLabel(lessonMinutes(row))}</small></div><div class="lesson-entry-main"><div class="lesson-group-line"><span class="lesson-group-mark" aria-hidden="true">${esc(initials(row.group.name))}</span><button class="cell-link" type="button" data-detail="${key}">${name}</button>${live ? '<span class="lesson-live">Hozir davom etmoqda</span>' : ""}</div><h4 class="lesson-entry-topic${row.topic ? "" : " no-topic"}">${esc(row.topic || "Mavzu hali kiritilmagan")}</h4><div class="lesson-entry-meta"><span class="lesson-teacher">${avatar(fullName(row.teacher), "small")}<span>${esc(fullName(row.teacher))}</span></span><span class="lesson-place">${icon("rooms")}<span>${esc(row.room.name)}</span></span><span class="lesson-branch">${branchLabel(row.group)}</span></div></div><div class="lesson-entry-actions"><div class="lesson-status-line">${statusPill(row.status, "session")}<button class="icon-button" type="button" data-menu="${key}" aria-label="${esc(recordName(row))} — amallar">${icon("more")}</button></div>${finished && canWrite() ? `<button class="button lesson-finish" type="button" data-session-complete="${key}">${icon("check")}Darsni yakunlash</button>` : `<button class="button lesson-open" type="button" data-detail="${key}">Batafsil ${icon("arrow")}</button>`}</div></article>`;
}
function lessonAgenda(rows) {
    const dates = [...new Set(rows.map((r) => r.date))], totalMinutes = rows.filter((r) => r.status !== "bekor_qilingan").reduce((sum, row) => sum + lessonMinutes(row), 0);
    return `<div class="lesson-board"><div class="lesson-board-caption"><span>Darslar oqimi <i class="flow-line" aria-hidden="true"></i></span><span>Sahifada <b>${rows.length} ta dars</b><i></i><b>${durationLabel(totalMinutes)}</b></span></div>${dates.map((date) => {
        const dayRows = rows.filter((r) => r.date === date), today = date === isoToday(), weekday = weekdays[calendarDate(date).getUTCDay() || 7];
        return `<section class="lesson-day${today ? " is-today" : ""}"><div class="lesson-day-heading"><time class="lesson-date-stamp" datetime="${date}"><strong>${Number(date.slice(8))}</strong><span>${shortMonths[Number(date.slice(5, 7)) - 1]}</span></time><div><h3>${weekday}${today ? '<span class="today-label">Bugun</span>' : ""}</h3><p>${months[Number(date.slice(5, 7)) - 1]} ${date.slice(0, 4)}</p></div><span class="lesson-day-line"></span><span class="lesson-day-count">${dayRows.length} ta dars</span></div><div class="lesson-day-entries">${dayRows.map(lessonEntry).join("")}</div></section>`;
    }).join("")}</div>`;
}
function emptyLessonAgenda() {
    const filtered = Object.values(state.filters).some(Boolean);
    return `<div class="lesson-empty"><div class="lesson-empty-art" aria-hidden="true"><div class="empty-calendar-top"><i></i><i></i></div><div class="empty-calendar-days">${Array.from({ length: 15 }, (_, i) => `<span${i === 7 ? ' class="marked"' : ""}>${i === 7 ? icon("check") : ""}</span>`).join("")}</div></div><h3>${filtered ? "Bu tanlovda dars topilmadi" : "Yangi darslar uchun joy tayyor"}</h3><p>${filtered ? "Boshqa sana, guruh yoki holatni tanlab ko‘ring." : "Haftalik jadvaldan darslar yarating yoki alohida dars qo‘shing."}</p><div>${filtered ? '<button class="button secondary" type="button" data-action="clear-filters">Filtrlarni tozalash</button>' : ""}${canWrite() ? `<button class="button primary" type="button" data-action="create">${icon("plus")}Dars qo‘shish</button>` : ""}</div></div>`;
}
function timetableCard(row) {
    return `<article class="timetable-card tone-${toneId(row.group_id)}"><div class="timetable-card-top"><span class="time-label">${timeLabel(row.start_time)}<span>–</span>${timeLabel(row.end_time)}</span><button class="icon-button" type="button" data-menu="${row.id}" aria-label="${esc(recordName(row))} — amallar">${icon("more")}</button></div><div class="schedule-card-body"><button class="cell-link timetable-name" type="button" data-detail="${row.id}">${esc(row.group.name)}</button><div class="schedule-teacher">${avatar(fullName(row.group.teacher), "small")}<span><small>O‘qituvchi</small><strong>${esc(fullName(row.group.teacher))}</strong></span></div><div class="schedule-room">${icon("rooms")}<span>${esc(row.room.name)}</span><b>${durationLabel(lessonMinutes(row))}</b></div><div class="schedule-dates"><span>Amal qilish muddati</span><p>${dateLabel(row.group.start_date)}<i>→</i>${row.group.end_date ? dateLabel(row.group.end_date) : "Davom etmoqda"}</p></div>${!["faol", "rejalashtirilgan"].includes(row.group.status) ? statusPill(row.group.status, "group") : ""}</div></article>`;
}
function renderTimetable(rows) {
    if (state.mode === "week") return `<div class="week-board${state.filters.weekday ? " single-day" : ""}">${Object.entries(weekdays).filter(([day]) => !state.filters.weekday || String(state.filters.weekday) === day).map(([day, name]) => {
        const slots = rows.filter((r) => String(r.weekday) === day);
        return `<section class="week-day${slots.length ? " has-slots" : ""}${Number(day) >= 6 ? " weekend" : ""}"><div class="week-day-heading"><span class="week-day-label"><h3>${name}</h3><small>${slots.length ? `${slots.length} ta vaqt oralig‘i` : "Shu sahifada bo‘sh"}</small></span>${canWrite() ? `<button class="icon-button" type="button" data-create-day="${day}" aria-label="${name} kuniga jadval qo‘shish">${icon("plus")}</button>` : ""}</div>${slots.length ? slots.map((row) => timetableCard(row)).join("") : `<div class="day-free">${canWrite() ? `<button type="button" class="free-day-add" data-create-day="${day}" aria-label="${name}: vaqt belgilash">${icon("plus")}Vaqt belgilang</button>` : ""}</div>`}</section>`;
    }).join("")}</div>`;
    return lessonAgenda(rows);
}
function listShell() {
    if (state.view === "sessions") return lessonShell();
    const def = moduleDefinitions[state.view];
    $("page-content").innerHTML = `<section class="panel data-panel${state.view === "schedules" ? " schedule-panel" : ""}"><div class="list-top"><div class="list-title"><h2>${esc(def.title)}</h2><span id="list-count" class="count-badge">—</span></div><div class="list-actions">${def.modes.length > 1 ? `<div class="view-toggle" role="group" aria-label="Ko‘rinish">${def.modes.map((mode) => `<button type="button" data-mode="${mode}" class="${state.mode === mode ? "active" : ""}" aria-label="${mode === "table" ? "Jadval" : mode === "kanban" ? "Kanban" : mode === "workflow" ? "Bosqichlar" : mode === "week" ? "Haftalik" : mode === "agenda" ? "Kunlik darslar" : "Kartochkalar"} ko‘rinishi" aria-pressed="${state.mode === mode}">${icon(mode === "kanban" || mode === "workflow" ? "statuses" : mode === "week" ? "schedules" : mode === "agenda" ? "sessions" : mode)}</button>`).join("")}</div>` : ""}<button class="icon-button bordered" type="button" data-action="refresh" aria-label="Ro‘yxatni yangilash">${icon("refresh")}</button></div></div><div class="toolbar"><div class="search-field">${icon("search")}<input id="record-search" data-filter="search" placeholder="${esc(def.title)} bo‘yicha qidirish…" aria-label="Ro‘yxatdan qidirish" autocomplete="off" value="${esc(state.filters.search || "")}"></div>${filtersFor(state.view).map((filter) => `<select id="filter-${filter.key}" data-filter="${filter.key}" data-label="${esc(filter.label)}"><option value="">${esc(filter.label)}</option>${filter.options.map((option) => `<option value="${esc(option.value)}" ${String(state.filters[filter.key]) === String(option.value) ? "selected" : ""}>${esc(option.label)}</option>`).join("")}</select>`).join("")}<button class="text-button" type="button" data-action="clear-filters" ${Object.values(state.filters).some(Boolean) ? "" : "hidden"}>Tozalash</button></div>${timetableControls()}<div id="bulk-bar" class="bulk-bar" hidden></div><div id="records"></div><div class="table-footer"><span id="result-count" role="status"></span><div class="pagination"><button class="icon-button" type="button" id="previous-page" data-page="-1" aria-label="Oldingi sahifa">${icon("left")}</button><span class="page-position" id="page-position">1 / 1</span><button class="icon-button" type="button" id="next-page" data-page="1" aria-label="Keyingi sahifa">${icon("right")}</button></div></div></section>`;
    enhanceSelects($("page-content")); syncLessonControls();
}
function renderRecords() {
    const def = moduleDefinitions[state.view];
    const rows = def.paged ? state.rows : filterRows(state.rows);
    if (!def.paged) { state.total = rows.length; state.pages = Math.max(1, Math.ceil(rows.length / state.size)); state.page = Math.min(state.page, state.pages); }
    const visible = def.paged ? rows : rows.slice((state.page - 1) * state.size, state.page * state.size);
    state.visible = visible;
    $("list-count").textContent = state.total;
    $("page-position").textContent = `${state.page} / ${Math.max(1, state.pages)}`;
    $("previous-page").disabled = state.page <= 1; $("next-page").disabled = state.page >= state.pages;
    const start = state.total ? (state.page - 1) * state.size + 1 : 0;
    $("result-count").textContent = `${state.total} ta yozuvdan ${start}–${Math.min(state.page * state.size, state.total)} ko‘rsatilmoqda`;
    document.querySelector('[data-action="clear-filters"]').hidden = !Object.values(state.filters).some(Boolean);
    if (state.view === "schedules" && state.mode === "week") {
        $("records").innerHTML = renderTimetable(visible);
    } else if (!visible.length) {
        $("records").innerHTML = `<div class="empty-state"><div class="empty-symbol">${icon(def.icon)}</div><h3>${Object.values(state.filters).some(Boolean) ? "Mos natija topilmadi" : "Bu yerda yangi boshlanish bor"}</h3><p>${Object.values(state.filters).some(Boolean) ? "Qidiruv yoki filtrlarni o‘zgartirib ko‘ring." : `${esc(def.singular)} qo‘shib, markazingiz ma’lumotlarini to‘ldirishni boshlang.`}</p>${canWrite() ? `<button type="button" class="button secondary" data-action="create">${icon("plus")}${esc(def.add)}</button>` : ""}</div>`;
        if (state.view === "sessions" && state.mode === "agenda") $("records").innerHTML = emptyLessonAgenda();
    } else if (["week", "agenda"].includes(state.mode)) {
        $("records").innerHTML = renderTimetable(visible);
    } else if (state.mode === "kanban") {
        const stages = [...state.options.statuses];
        if (visible.some((row) => !row.status)) stages.push({ id: "", name: "Bosqichsiz", position: 999 });
        $("records").innerHTML = `<div class="kanban-board">${stages.map((stage, i) => {
            const cards = visible.filter((row) => String(row.status?.id ?? "") === String(stage.id));
            return `<section class="kanban-column" data-stage="${stage.id}"><div class="kanban-heading"><span class="source-square ${tones[i % 5]}"></span>${esc(stage.name)}<b>${cards.length}</b>${canWrite() ? `<button type="button" data-create-stage="${stage.id}" aria-label="${esc(stage.name)} bosqichiga lid qo‘shish">+</button>` : ""}</div>${cards.length ? cards.map((row) => `<article class="kanban-card" draggable="${canWrite() && !row.student}" data-drag="${row.id}"><div class="kanban-card-top"><span class="pill no-dot ${stage.is_won ? "green" : stage.is_lost ? "red" : "purple"}">${esc(row.course?.name || "Kurs tanlanmagan")}</span><button class="icon-button" type="button" data-menu="${row.id}" aria-label="${esc(fullName(row))} — amallar">${icon("more")}</button></div><button class="cell-link" type="button" data-detail="${row.id}">${esc(fullName(row))}</button><span class="kanban-phone">${esc(row.phone)}</span>${row.comment ? `<p class="kanban-note">${esc(row.comment)}</p>` : ""}<div class="kanban-card-bottom"><span>${esc(row.source?.name || "Manba belgilanmagan")}</span>${row.assignee ? avatar(fullName(row.assignee)) : `<span>${dateLabel(row.created_at)}</span>`}</div></article>`).join("") : '<div class="column-empty">Bu sahifada lid yo‘q</div>'}</section>`;
        }).join("")}</div>`;
    } else if (state.mode === "workflow") {
        $("records").innerHTML = `<div class="workflow-list">${visible.sort((a, b) => a.position - b.position).map((row) => `<div class="workflow-step"><span class="workflow-number">${String(row.position).padStart(2, "0")}</span><span><strong>${esc(row.name)}</strong><small>${row.is_won ? "O‘quvchiga aylangan murojaatlar" : row.is_lost ? "Davom etmagan murojaatlar" : "Qabul jarayonidagi bosqich"}</small></span><span class="pill ${row.is_won ? "green" : row.is_lost ? "red" : "purple"}">${row.is_won ? "Muvaffaqiyatli" : row.is_lost ? "Yo‘qotilgan" : "Jarayonda"}</span>${rowButtons(row)}</div>`).join("")}</div>`;
    } else if (state.mode === "grid") {
        $("records").innerHTML = `<div class="card-grid">${visible.map(recordCard).join("")}</div>`;
    } else {
        $("records").innerHTML = `<div class="table-wrap"><table aria-label="${esc(def.title)}"><thead><tr><th class="select-column"><input type="checkbox" id="select-page" aria-label="Sahifadagi yozuvlarni tanlash"></th>${columns[state.view].map(([label]) => `<th>${esc(label)}</th>`).join("")}<th><span class="sr-only">Amallar</span></th></tr></thead><tbody>${visible.map((row) => `<tr class="${state.selected.has(keyOf(row)) ? "selected" : ""}"><td class="select-column"><input type="checkbox" data-select="${esc(keyOf(row))}" aria-label="${esc(recordName(row))} yozuvini tanlash" ${state.selected.has(keyOf(row)) ? "checked" : ""}></td>${columns[state.view].map(([, render]) => `<td>${render(row)}</td>`).join("")}<td>${rowButtons(row)}</td></tr>`).join("")}</tbody></table></div>`;
    }
    updateSelection();
}
async function loadRecords() {
    const module = state.view, def = moduleDefinitions[module], request = ++state.request;
    if (!$("records")) listShell();
    $("records").innerHTML = '<div class="empty-small">Ma’lumotlar yuklanmoqda…</div>';
    setMessage("page-error"); closeRowMenu();
    try {
        let data;
        if (def.paged) {
            const params = { page: state.page, size: state.size, search: state.filters.search, branch_id: state.branch, ...state.filters };
            if (params.debt === "debt") params.max_balance = -0.01;
            if (params.debt === "positive") params.min_balance = 0.01;
            delete params.debt;
            data = await api(queryPath(def.path, params));
        } else if (def.activePair) {
            const results = await Promise.all([api(`${def.path}?is_active=true`), api(`${def.path}?is_active=false`)]);
            data = results.flat();
        } else data = await api(def.path);
        if (request !== state.request || state.view !== module) return;
        state.rows = def.paged ? data.items : data;
        if (def.paged) { state.total = data.total; state.pages = Math.max(1, data.pages); if (state.page > state.pages) { state.page = state.pages; return loadRecords(); } }
        renderRecords();
    } catch (error) { if (request === state.request) { setMessage("page-error", error.message); $("records").innerHTML = `<div class="empty-small">Ro‘yxat yuklanmadi. ${esc(error.message)}</div>`; } }
}
function updateSelection() {
    if (!$("bulk-bar")) return;
    const count = state.selected.size;
    $("bulk-bar").hidden = count === 0;
    $("bulk-bar").innerHTML = `${count} ta yozuv tanlandi <button class="text-button" type="button" data-action="export-selected">${icon("download")} Tanlanganlarni eksport qilish</button><button class="icon-button" type="button" data-action="clear-selection" aria-label="Tanlovni tozalash">${icon("close")}</button>`;
    if ($("select-page")) { $("select-page").checked = count > 0 && state.visible.every((row) => state.selected.has(keyOf(row))); $("select-page").indeterminate = count > 0 && !$("select-page").checked; }
}

async function refreshOptions() {
    state.options = await api("/workspace/options"); state.user = state.options.user;
    $("account-name").textContent = state.user.name;
    $("account-role").textContent = state.user.is_superadmin ? "Asosiy administrator" : state.user.roles.map((r) => r.name).join(", ") || state.user.position || "Jamoa a’zosi";
    $("account-avatar").textContent = initials(state.user.name); $("top-avatar").textContent = initials(state.user.name);
    const globalAccess = state.user.is_superadmin || state.user.roles.some((role) => ["boss", "admin"].includes(role.code) && role.branch_id == null);
    if (!globalAccess && state.options.branches.length && !state.options.branches.some((branch) => String(branch.id) === state.branch)) state.branch = String(state.options.branches[0].id);
    fillSelect($("context-branch"), state.options.branches, "Barcha filiallar", state.branch);
    if (!globalAccess && state.options.branches.length) { $("context-branch").options[0].remove(); SmartSelect.instances.get($("context-branch"))?.refresh(); }
    const checks = [state.options.branches.length, state.options.courses.length, state.options.rooms.length, state.options.employees.some((r) => r.is_teacher), state.options.statuses.length];
    const completed = checks.filter(Boolean).length;
    $("setup-count").textContent = `${completed}/5`; $("setup-progress").style.width = `${completed * 20}%`;
    $("setup-button").querySelector("small").innerHTML = `${completed === 5 ? "Barcha asoslar tayyor" : "Keyingi qadamni boshlang"} <span>↗</span>`;
    $("setup-button").hidden = !hasRole("boss", "admin");
    enhanceSelects($("app-view")); renderNavigation();
}
function renderNavigation() {
    const sections = [["BOSHQARUV", ["overview"]], ["O‘QUV JARAYONI", ["students", "groups", "schedules", "sessions", "courses"]], ["CRM VA QABUL", ["leads"]], ["JAMOA VA TASHKILOT", ["employees", "teachers", "branches", "rooms"]], ["SOZLAMALAR", ["sources", "statuses", "roles", "assignments"]]];
    $("navigation").innerHTML = sections.map(([caption, keys]) => {
        const allowed = keys.filter((key) => key === "overview" || canRead(key));
        return allowed.length ? `<div class="nav-section"><div class="nav-caption">${caption}</div>${allowed.map((key) => `<a class="nav-link ${state.view === key ? "active" : ""}" href="#${key}" ${state.view === key ? 'aria-current="page"' : ""}>${icon(key === "overview" ? "dashboard" : moduleDefinitions[key].icon)}<span>${key === "overview" ? "Umumiy ko‘rinish" : moduleDefinitions[key].title}</span>${key === "leads" ? '<span class="nav-tag">CRM</span>' : ""}</a>`).join("")}</div>` : "";
    }).join("");
}
function renderHeading() {
    document.body.classList.toggle("sessions-theme", state.view === "sessions");
    document.body.classList.toggle("schedules-theme", state.view === "schedules");
    const overview = state.view === "overview", def = moduleDefinitions[state.view];
    $("breadcrumb-current").textContent = overview ? "Umumiy ko‘rinish" : def.title;
    $("section-label").textContent = overview ? "BOSHQARUV MARKAZI" : def.group;
    $("page-heading").innerHTML = `<div><h1>${overview ? `Salom, ${esc(state.user.first_name)}<span class="greeting-dot">.</span>` : esc(def.title)}</h1><p>${overview ? "Markazingizda nimalar bo‘layotganini bir qarashda ko‘ring." : esc(def.description)}</p></div><div class="heading-actions">${overview ? `<button type="button" class="button secondary" data-action="refresh">${icon("refresh")}<span class="button-label">Yangilash</span></button>` : `<button type="button" class="button secondary" data-action="export" title="Ko‘rinayotgan ro‘yxatni CSV formatida olish">${icon("download")}<span class="button-label">Eksport</span></button>`}${(overview && hasRole("admin", "boss")) || (!overview && canWrite()) ? `<button type="button" class="button primary" data-action="${overview ? "quick-lead" : "create"}">${icon("plus")}${overview ? "Yangi lid" : esc(def.add)}</button>` : ""}</div>`;
    $("footer-note").textContent = overview ? "TA’LIM UCHUN YARATILGAN" : `${def.group} / MARKAZ`;
    document.title = `${overview ? "Umumiy ko‘rinish" : def.title} · Markaz`;
}
async function navigate(key, reset = true) {
    if (key !== "overview" && (!moduleDefinitions[key] || !canRead(key))) key = "overview";
    state.view = key; state.page = 1; state.filters = {}; state.selected.clear(); state.rows = [];
    state.mode = moduleDefinitions[key]?.mode || "table"; state.request++;
    closeRowMenu(); SmartSelect.active?.close(); closeMobileMenu();
    if (location.hash !== `#${key}`) history.replaceState(null, "", `#${key}`);
    renderNavigation(); renderHeading(); setMessage("page-error");
    if (reset) window.scrollTo({ top: 0, behavior: "instant" });
    if (key === "overview") await loadOverview(); else { listShell(); await loadRecords(); }
}
function trendSVG(trend) {
    const width = 560, height = 205, left = 30, top = 14, bottom = 174, plot = width - left - 15;
    const max = Math.max(4, ...trend.flatMap((t) => [t.students, t.leads]));
    const ceiling = Math.ceil(max / 4) * 4;
    const point = (value, index) => [left + index * plot / 5, bottom - value / ceiling * (bottom - top)];
    const line = (key) => trend.map((item, i) => point(item[key], i).join(",")).join(" ");
    return `<svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Oxirgi olti oydagi yangi o‘quvchilar va lidlar"><defs><linearGradient id="chart-fill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#b9d2a0" stop-opacity=".22"/><stop offset="100%" stop-color="#b9d2a0" stop-opacity="0"/></linearGradient></defs>${[0, 1, 2, 3, 4].map((i) => { const y = bottom - i / 4 * (bottom - top); return `<line class="chart-grid" x1="${left}" x2="${width - 15}" y1="${y}" y2="${y}"/><text x="${left - 9}" y="${y + 3}" text-anchor="end">${ceiling * i / 4}</text>`; }).join("")}<polygon points="${left},${bottom} ${line("students")} ${width - 15},${bottom}" fill="url(#chart-fill)"/><polyline points="${line("leads")}" fill="none" stroke="#9270d1" stroke-width="2" stroke-linejoin="round"/><polyline points="${line("students")}" fill="none" stroke="#74a536" stroke-width="2.4" stroke-linejoin="round"/>${trend.map((item, i) => { const [x, y] = point(item.students, i); return `<circle cx="${x}" cy="${y}" r="3" fill="#fff" stroke="#74a536" stroke-width="1.8"><title>${item.month}: ${item.students} o‘quvchi, ${item.leads} lid</title></circle><text x="${x}" y="198" text-anchor="middle">${shortMonths[Number(item.month.slice(5)) - 1]}</text>`; }).join("")}</svg>`;
}
async function loadOverview() {
    const request = ++state.request;
    $("page-content").innerHTML = '<div class="skeleton-grid"><div class="skeleton"></div><div class="skeleton"></div><div class="skeleton"></div><div class="skeleton"></div><div class="skeleton full"></div></div>';
    try {
        const data = await api(queryPath("/workspace/overview", { branch_id: state.branch }));
        if (request !== state.request || state.view !== "overview") return;
        state.dashboard = data;
        const metrics = [["O‘quvchilar", data.students, "students", "mint", `${data.active_students} nafar faol o‘quvchi`], ["Guruhlar", data.groups, "groups", "lilac", `${data.active_groups} ta faol guruh`], ["Yangi imkoniyatlar", data.leads, "leads", "peach", "Barcha qabul murojaatlari"], ["O‘quv yo‘nalishlari", data.active_courses, "courses", "blue", "Qabul uchun ochiq kurslar"]];
        const sources = data.sources.map((source) => ({ ...source, name: lookup("sources", source.id)?.name || "Manbasiz murojaat" })).sort((a, b) => b.count - a.count).slice(0, 5);
        const success = data.statuses.filter((s) => lookup("statuses", s.id)?.is_won).reduce((n, s) => n + s.count, 0);
        const occupancy = data.seats ? Math.round(data.occupied / data.seats * 100) : 0;
        $("page-content").innerHTML = `<section class="metric-grid" aria-label="Markaz ko‘rsatkichlari">${metrics.map(([label, number, type, tone, footer], index) => `<article class="metric-card${index === 0 ? " featured" : ""}"><div class="metric-top"><span>${label}</span><span class="metric-icon ${tone}">${icon(type)}</span></div><strong class="metric-number">${money.format(number)}</strong><div class="metric-footer">${index < 2 ? '<strong>●</strong>' : ""}${footer}</div></article>`).join("")}</section><div class="dashboard-grid"><section class="panel"><div class="panel-header"><div><h2>Yangi ro‘yxatdan o‘tishlar</h2><p>O‘quvchilar va murojaatlarning oylar bo‘yicha o‘sishi</p></div><span class="period-label">Oxirgi 6 oy</span></div><div class="chart-legend"><span><i class="legend-dot"></i>O‘quvchilar</span><span><i class="legend-dot purple"></i>Lidlar</span></div><div class="trend-chart">${trendSVG(data.trend)}</div>${!data.trend.some((p) => p.students || p.leads) ? '<p class="chart-empty">Yangi yozuvlar qo‘shilgach, o‘sish shu yerda ko‘rinadi.</p>' : ""}</section><section class="panel"><div class="panel-header"><div><h2>Qabul manbalari</h2><p>Lidlaringiz qayerdan kelmoqda?</p></div>${canRead("sources") ? `<a href="#sources" class="text-button" aria-label="Manbalarni ochish">${icon("arrow")}</a>` : ""}</div><div class="source-list">${sources.length ? sources.map((source, i) => `<div class="source-row"><div class="source-row-head"><span class="source-square ${tones[i % 5]}"></span>${esc(source.name)}<b>${source.count}</b></div><div class="bar-track"><div class="bar-fill ${tones[i % 5]}" style="width:${Math.round(source.count / Math.max(1, data.leads) * 100)}%"></div></div></div>`).join("") : '<p class="empty-small">Manba ko‘rsatilgan lidlar paydo bo‘lishini kutyapmiz.</p>'}</div><div class="source-summary"><span>Muvaffaqiyatli qabul</span><strong>${success} <span style="font-size:9px;font-weight:400">ta lid</span></strong></div></section></div><div class="dashboard-grid"><section class="panel"><div class="panel-header"><div><h2>So‘nggi murojaatlar</h2><p>Markazingizga yangi qiziqish bildirganlar</p></div>${canRead("leads") ? `<a href="#leads" class="text-button">Barchasi ${icon("arrow")}</a>` : ""}</div>${data.recent_leads.length ? `<div class="table-wrap"><table aria-label="So‘nggi murojaatlar"><thead><tr><th>Ism va telefon</th><th>Kurs</th><th>Bosqich</th></tr></thead><tbody>${data.recent_leads.map((row) => `<tr><td><div class="person-cell">${avatar(fullName(row))}<span><span class="person-name">${esc(fullName(row))}</span><span class="cell-sub">${esc(row.phone)}</span></span></div></td><td>${esc(lookup("courses", row.course_id)?.name || "Aniqlanmagan")}</td><td>${leadStatus(row)}</td></tr>`).join("")}</tbody></table></div>` : '<div class="empty-small">Hozircha murojaatlar yo‘q. Yangi lid qo‘shishdan boshlang.</div>'}</section><div><section class="panel occupancy-panel"><div class="occupancy-ring"><svg viewBox="0 0 100 100" aria-hidden="true"><circle cx="50" cy="50" r="40" stroke="#f0dfbe"/><circle cx="50" cy="50" r="40" stroke="#c69538" stroke-dasharray="${occupancy * 2.513} 251.3"/></svg><span>${occupancy}%</span></div><div class="occupancy-copy"><h3>O‘sish uchun joy bor</h3><p>${data.occupied} / ${data.seats} o‘rin band.<br>Faol va rejalashtirilgan guruhlar.</p>${canRead("groups") ? `<a href="#groups" class="text-button">Guruhlarni ko‘rish ${icon("arrow")}</a>` : ""}</div></section><section class="panel" style="margin-top:15px"><div class="panel-header"><div><h2>Keyingi ishni boshlang</h2><p>Ko‘p ishlatiladigan amallar</p></div></div><div class="quick-actions">${["students", "groups", "leads", "courses"].filter((key) => canRead(key) && canWrite(key)).map((key) => `<button type="button" class="quick-action" data-quick-create="${key}">${icon(key)}<span>${moduleDefinitions[key].add}</span><span>↗</span></button>`).join("") || '<p class="empty-small">Bo‘limlarni chap menyudan oching.</p>'}</div></section></div></div>`;
    } catch (error) { if (request === state.request) { setMessage("page-error", error.message); $("page-content").innerHTML = '<div class="panel empty-state"><h3>Ma’lumotlar yuklanmadi</h3><p>Serverga ulanishni tekshirib, sahifani yangilang.</p><button class="button secondary" type="button" data-action="refresh">Qayta urinish</button></div>'; } }
}

function rowValues(module, row = {}) {
    const values = { ...row };
    if (["schedules", "sessions"].includes(module)) for (const key of ["start_time", "end_time"]) if (values[key]) values[key] = timeLabel(values[key]);
    if (["students", "leads"].includes(module)) {
        values.branch_id = row.branch?.id;
        values.source_id = row.source?.id;
        values.lead_id = row.lead?.id;
    }
    if (module === "leads") {
        values.course_id = row.course?.id; values.status_id = row.status?.id; values.assigned_to = row.assignee?.id;
    }
    return values;
}
function editableFields(module, editing) { return moduleDefinitions[module].fields.filter((f) => (!f.editOnly || editing) && (!f.createOnly || !editing)); }
async function openEditor(module = state.view, row = null, prefill = {}, afterLead = null) {
    if (!canWrite(module)) return toast("Bu amal uchun hisobingizda ruxsat yo‘q.", true);
    if (module === "assignments" && row && protectedAssignment(row)) return toast("Asosiy administratorning boshqaruv roli himoyalangan.", true);
    if ((module === "employees" || module === "sources") && row && !row.is_active) return toast("Tahrirlashdan oldin yozuvni amallar menyusidan faollashtiring.", true);
    try { await refreshOptions(); } catch (error) { return toast(error.message, true); }
    const def = moduleDefinitions[module];
    const values = { ...rowValues(module, row || {}), ...prefill };
    if (["schedules", "sessions"].includes(module) && !row && !values.group_id && state.filters.group_id) values.group_id = Number(state.filters.group_id);
    if (module === "sessions" && !row && !values.date) values.date = state.filters.date_from || isoToday();
    if (!row && module === "leads" && values.status_id == null && !("status_id" in prefill)) values.status_id = state.options.statuses.find((status) => !status.is_won && !status.is_lost)?.id;
    const fields = editableFields(module, Boolean(row));
    if (!row && values.branch_id == null && state.branch) values.branch_id = Number(state.branch);
    if (!row && values.branch_id == null && state.options.branches.length === 1 && fields.some((f) => f.key === "branch_id" && f.required)) values.branch_id = state.options.branches[0].id;
    state.editor = { module, row, fields, values, afterLead };
    $("detail-dialog").close(); $("confirm-dialog").close(); closeRowMenu();
    $("editor-kicker").textContent = def.group;
    $("editor-title").textContent = row ? `${def.singular}ni tahrirlash` : def.add;
    $("editor-description").textContent = row ? `${recordName(row, module)} ma’lumotlarini yangilang.` : afterLead ? "Lid ma’lumotlari ko‘chirildi. O‘quvchi profilini to‘ldiring." : "Kerakli ma’lumotlarni kiriting va saqlang.";
    $("editor-fields").innerHTML = fields.map((f) => {
        if (f.type === "section") return `<div class="form-section">${esc(f.label)}</div>`;
        const value = values[f.key] ?? f.default ?? "";
        const required = f.required || (f.createRequired && !row) || f.key === "status";
        const label = `<label for="edit-${f.key}">${esc(f.label)}${required ? '<span class="required">*</span>' : ""}</label>`;
        const helper = f.helper ? `<small id="hint-${f.key}">${esc(f.helper)}</small>` : "";
        if (f.type === "checkbox") return `<div class="field ${f.full ? "full" : ""}"><div class="checkbox-field"><input id="edit-${f.key}" name="${f.key}" data-editor-field="${f.key}" type="checkbox" ${value ? "checked" : ""}><span>${label}${helper}</span></div></div>`;
        const attributes = `id="edit-${f.key}" name="${f.key}" data-editor-field="${f.key}" ${required ? "required" : ""} ${f.max && f.type !== "number" ? `maxlength="${f.max}"` : ""} ${f.helper ? `aria-describedby="hint-${f.key}"` : ""}`;
        let input;
        if (f.type === "select") input = `<select ${attributes}></select>`;
        else if (f.type === "textarea") input = `<textarea ${attributes} placeholder="${esc(f.placeholder || "")}">${esc(value)}</textarea>`;
        else input = `<input ${attributes} type="${f.type}" value="${esc(f.type === "password" ? "" : value)}" placeholder="${esc(f.placeholder || "")}" ${f.min != null ? `min="${f.min}"` : ""} ${f.max && f.type === "number" ? `max="${f.max}"` : ""} ${f.type === "number" ? `step="${f.step || "1"}"` : ""} ${f.type === "password" ? 'autocomplete="new-password" minlength="8"' : ""} ${module === "roles" && row?.is_system && f.key === "code" ? "readonly" : ""}>`;
        return `<div class="field ${f.full ? "full" : ""}">${label}${input}${helper}</div>`;
    }).join("");
    fields.filter((f) => f.type === "select").forEach((f) => {
        const select = $(`edit-${f.key}`), value = values[f.key] ?? f.default ?? "";
        fillSelect(select, f.choices || sourceOptions(f.source, values, value), f.placeholder || (f.required || f.key === "status" ? "Tanlang" : "Tanlanmagan"), value);
        if (module === "groups" && row?.current_students && ["branch_id", "course_id"].includes(f.key)) select.disabled = true;
        if (module === "students" && afterLead && ["branch_id", "lead_id"].includes(f.key)) select.disabled = true;
    });
    enhanceSelects($("editor-fields")); updateEditorHints();
    setMessage("editor-error"); $("editor-save").disabled = false;
    $("editor-save").innerHTML = `${row ? "O‘zgarishlarni saqlash" : "Saqlash"} <span>↗</span>`;
    $("editor-dialog").showModal();
}
function updateEditorHints(changed = "") {
    const editor = state.editor; if (!editor) return;
    if (["schedules", "sessions"].includes(editor.module)) {
        const group = lookup("groups", $("edit-group_id").value), values = { group_id: group?.id };
        for (const key of editor.module === "sessions" ? ["room_id", "teacher_id"] : ["room_id"]) {
            const select = $(`edit-${key}`), source = key === "room_id" ? "rooms" : "teachers";
            const current = changed === "group_id" ? group?.[key] : select.value || (!editor.row ? group?.[key] : "");
            fillSelect(select, sourceOptions(source, values, current), group ? "Tanlang" : "Avval guruhni tanlang", current);
        }
        if (editor.module === "sessions") { $("edit-date").min = group?.start_date || ""; $("edit-date").max = group?.end_date || ""; }
        $("editor-description").textContent = group ? `${fullName(lookup("employees", group.teacher_id))} · ${dateLabel(group.start_date)} — ${group.end_date ? dateLabel(group.end_date) : "davom etmoqda"}. Xona, guruh va o‘qituvchi bandligi tekshiriladi.` : "Avval guruhni tanlang. Vaqtlar Toshkent vaqti bilan kiritiladi.";
    }
    if (editor.module === "groups") {
        const values = { branch_id: Number($("edit-branch_id").value) };
        if (changed === "branch_id") for (const key of ["teacher_id", "room_id"]) {
            const f = editor.fields.find((item) => item.key === key), select = $(`edit-${key}`);
            fillSelect(select, sourceOptions(f.source, values, select.value), "Tanlang", select.value);
        }
        const room = lookup("rooms", $("edit-room_id").value), course = lookup("courses", $("edit-course_id").value);
        $("edit-max_students").max = room ? Math.min(room.capacity, 32767) : 32767;
        $("edit-max_students").min = Math.max(1, editor.row?.current_students || 0);
        $("hint-max_students").textContent = room ? `Xona sig‘imi: ${room.capacity} o‘rin. Hozir ${editor.row?.current_students || 0} o‘quvchi bor.` : "Avval xonani tanlang.";
        $("hint-price").textContent = course ? `Bo‘sh qoldirilsa: ${money.format(course.price)} so‘m / oy — kurs narxi.` : "Bo‘sh qoldirilsa, kursning standart narxi olinadi.";
        $("edit-end_date").min = $("edit-start_date").value;
        const recommended = suggestGroupEnd($("edit-start_date").value, course?.duration_months), hint = $("hint-end_date");
        if (hint) {
            hint.className = "end-date-suggestion";
            hint.innerHTML = recommended ? `<span><strong>${dateLabel(recommended)}</strong><small>Boshlanish + ${course.duration_months} oy</small></span><button type="button" data-use-end-date="${recommended}" ${$("edit-end_date").value === recommended ? "disabled" : ""}>${$("edit-end_date").value === recommended ? `${icon("check")}Tanlangan` : `Qo‘llash ${icon("arrow")}`}</button>` : !course ? "Kursni tanlang — tugash sanasini tavsiya qilamiz." : !course.duration_months ? "Kurs davomiyligi belgilanmagan. Sanani qo‘lda tanlang." : "Boshlanish sanasini tanlang — tugash sanasini tavsiya qilamiz.";
        }
    }
    if (editor.module === "statuses" && ["is_won", "is_lost"].includes(changed) && $(`edit-${changed}`).checked) $(changed === "is_won" ? "edit-is_lost" : "edit-is_won").checked = false;
    if (["schedules", "sessions"].includes(editor.module)) {
        const start = $("edit-start_time").value, end = $("edit-end_time").value, hint = $("hint-end_time");
        if (hint) { hint.textContent = start && end ? end > start ? `Davomiyligi: ${durationLabel(lessonMinutes({ start_time: start, end_time: end }))}` : "Tugash vaqti boshlanishdan keyin bo‘lishi kerak." : "Vaqtni 24 soatlik formatda tanlang."; hint.classList.toggle("invalid-hint", Boolean(start && end && end <= start)); }
    }
    enhanceDates($("editor-fields"));
    enhanceTimes($("editor-fields"));
}
function editorPayload() {
    const payload = {};
    for (const f of state.editor.fields) {
        if (!f.key) continue;
        const element = $(`edit-${f.key}`), required = f.required || (f.createRequired && !state.editor.row) || f.key === "status";
        SmartTime.instances.get(element)?.validate();
        const amount = MoneyInput.instances.get(element);
        let value = amount ? amount.value() : f.type === "checkbox" ? element.checked : f.type === "password" ? element.value : element.value.trim();
        if (required && (value === "" || value == null)) {
            const select = SmartSelect.instances.get(element) || SmartDate.instances.get(element);
            if (select) { select.button.setAttribute("aria-invalid", "true"); select.button.focus(); }
            else element.focus();
            throw new Error(`${f.label} maydonini to‘ldiring.`);
        }
        if (!element.checkValidity()) { const date = SmartDate.instances.get(element); if (date) { date.button.setAttribute("aria-invalid", "true"); date.button.focus(); } else element.reportValidity(); throw new Error(`${f.label} qiymatini tekshiring.`); }
        if (f.type === "select") value = value === "" ? null : f.choices ? value : Number(value);
        else if (f.type === "number") value = value === "" ? null : ["price", "monthly_budget"].includes(f.key) ? value : Number(value);
        else if (f.type !== "checkbox" && !required && value === "" && f.key !== "photo_url") value = null;
        payload[f.key] = value;
    }
    if (payload.start_time && payload.end_time && payload.end_time <= payload.start_time) { SmartTime.instances.get($("edit-end_time"))?.display.focus(); throw new Error("Tugash vaqti boshlanishdan keyin bo‘lishi kerak."); }
    return payload;
}
function recordPath(module, row) { const def = moduleDefinitions[module]; return module === "assignments" ? `${def.path}${row.employee_id}/${row.role_id}` : `${def.path}${keyOf(row, module)}`; }
async function saveEditor(event) {
    event.preventDefault(); setMessage("editor-error");
    const editor = state.editor, def = moduleDefinitions[editor.module];
    let payload; try { payload = editorPayload(); } catch (error) { return setMessage("editor-error", error.message); }
    $("editor-save").disabled = true;
    try {
        await api(editor.row ? recordPath(editor.module, editor.row) : def.path, jsonRequest(editor.row ? "PUT" : "POST", payload));
        await refreshOptions();
        if (editor.afterLead) {
            const student = state.options.students.find((r) => r.phone === payload.phone);
            if (student) await api(`/leads/${editor.afterLead.id}?student_id=${student.id}`, { method: "PATCH" });
        }
        $("editor-dialog").close();
        toast(editor.afterLead ? "O‘quvchi yaratildi va lid bilan bog‘landi." : `${def.singular} ${editor.row ? "yangilandi" : "qo‘shildi"}.`);
        state.selected.clear();
        if (state.view === "overview") await loadOverview();
        else if (state.view === editor.module) { if (!editor.row) state.page = 1; await loadRecords(); }
        else await navigate(editor.module);
    } catch (error) { setMessage("editor-error", error.message); }
    finally { $("editor-save").disabled = false; }
}

function detailValue(f, values) {
    const value = values[f.key];
    if (value == null || value === "") return "Belgilanmagan";
    if (f.type === "select") return esc(f.choices?.find((o) => String(o.value) === String(value))?.label || sourceOptions(f.source).find((o) => Number(o.value) === Number(value))?.label || value);
    if (f.type === "time") return timeLabel(value);
    if (f.type === "checkbox") return value ? "Ha" : "Yo‘q";
    if (f.type === "date") return dateLabel(value);
    if (["price", "monthly_budget"].includes(f.key)) return `${money.format(value)} so‘m`;
    return esc(value);
}
function openDetail(row) {
    const module = state.view, def = moduleDefinitions[module], name = recordName(row), values = rowValues(module, row);
    const fields = def.fields.filter((f) => f.key && !["password", "photo_url", "comment", "description", "bio", "lost_reason", "note"].includes(f.key));
    const phone = row.phone || lookup("employees", row.employee_id)?.phone;
    let badge = row.is_superadmin ? protectedAdminPill() : row.status && module === "leads" ? leadStatus(row) : row.status ? statusPill(row.status, module === "groups" ? "group" : module === "sessions" ? "session" : "student") : typeof row.is_active === "boolean" ? activePill(row.is_active) : "";
    const note = row.comment || row.description || row.bio || row.note;
    $("detail-content").innerHTML = `<div class="detail-cover"><span class="section-kicker">${esc(def.group)}</span><span class="detail-number">#${esc(keyOf(row))}</span><button class="icon-button" data-close="detail-dialog" type="button" aria-label="Profilni yopish">${icon("close")}</button></div><div class="detail-intro">${avatar(name, "large")}<h2 id="detail-title">${esc(name)}</h2><p>${esc(module === "teachers" ? row.specialization || "O‘qituvchi" : module === "employees" ? row.position : def.singular)}</p><div class="detail-badges">${badge}${row.created_at ? `<span class="pill gray no-dot">${dateLabel(row.created_at)}</span>` : ""}</div></div><div class="detail-body"><div class="detail-heading">Ma’lumotlar</div><dl class="detail-grid">${fields.map((f) => `<div class="${f.full ? "full" : ""}"><dt>${esc(f.label)}</dt><dd>${detailValue(f, values)}</dd></div>`).join("")}${module === "students" ? `<div><dt>Joriy balans</dt><dd class="${Number(row.balance) < 0 ? "balance-negative" : "balance-positive"}">${money.format(row.balance)} so‘m</dd></div>` : ""}${module === "groups" ? `<div><dt>O‘quvchilar</dt><dd>${row.current_students} / ${row.max_students}</dd></div><div><dt>Amaldagi oylik narx</dt><dd>${money.format(row.effective_price)} so‘m</dd></div>` : ""}</dl>${note ? `<div class="detail-heading">${module === "teachers" ? "Ustoz haqida" : "Izoh"}</div><div class="detail-note">${esc(note)}</div>` : ""}${row.lost_reason ? `<div class="detail-heading" style="margin-top:20px">Yo‘qotilish sababi</div><div class="detail-note">${esc(row.lost_reason)}</div>` : ""}</div><div class="detail-actions">${module === "groups" ? `<button type="button" class="button secondary" data-group-view="schedules" data-group-id="${row.id}">${icon("schedules")}Haftalik jadval</button><button type="button" class="button secondary" data-group-view="sessions" data-group-id="${row.id}">${icon("sessions")}Darslar</button>` : ""}${canWrite() && !protectedAssignment(row) ? `<button type="button" class="button primary" data-edit="${esc(keyOf(row))}">${icon("edit")}Tahrirlash</button>` : ""}${phone ? `<a class="button secondary" href="tel:${phone.replace(/[^+0-9]/g, "")}">${icon("phone")}Telefon qilish</a>` : ""}${module === "leads" && !row.student && canWrite() ? `<button class="button secondary" type="button" data-convert="${row.id}">O‘quvchiga aylantirish</button>` : ""}</div>`;
    $("detail-dialog").showModal();
}
let rowMenu = null;
function closeRowMenu() { rowMenu?.remove(); rowMenu = null; }
function showRowMenu(button, row) {
    const def = moduleDefinitions[state.view], module = state.view;
    closeRowMenu();
    const actions = [{ key: "detail", label: "Batafsil ko‘rish", icon: "eye" }];
    if (canWrite()) {
        if (!protectedAssignment(row) && !(["employees", "sources"].includes(module) && !row.is_active)) actions.push({ key: "edit", label: "Tahrirlash", icon: "edit" });
        if (["groups", "students", "sessions"].includes(module)) actions.push({ key: "status", label: "Holatini o‘zgartirish", icon: "refresh" });
        if (module === "leads" && !row.student) actions.push({ key: "convert", label: "O‘quvchiga aylantirish", icon: "students" });
        if (["courses", "sources", "employees"].includes(module) && !row.is_superadmin) {
            if (module !== "employees" || !row.is_active) actions.push({ key: "toggle", label: row.is_active ? "Faolsizlantirish" : "Faollashtirish", icon: "refresh" });
        }
        if (!def.noDelete && !row.is_superadmin && !protectedAssignment(row) && !(module === "roles" && row.is_system) && !(["groups", "sessions"].includes(module) && row.status === "bekor_qilingan") && !(["rooms", "employees"].includes(module) && !row.is_active)) actions.push({ key: "delete", label: module === "sessions" ? "Darsni bekor qilish" : module === "groups" ? "Guruhni bekor qilish" : module === "students" ? "Ketgan deb belgilash" : ["rooms", "employees"].includes(module) ? "Faolsizlantirish" : "O‘chirish", icon: "trash", destructive: true });
    }
    rowMenu = document.createElement("div"); rowMenu.className = "row-menu"; rowMenu.setAttribute("role", "menu");
    rowMenu.innerHTML = actions.map((a) => `<button type="button" role="menuitem" data-row-action="${a.key}" data-row-key="${esc(keyOf(row))}" class="${a.destructive ? "destructive" : ""}">${icon(a.icon)}${a.label}</button>`).join("");
    document.body.append(rowMenu);
    const bounds = button.getBoundingClientRect();
    rowMenu.style.left = `${Math.max(8, Math.min(bounds.right - 200, innerWidth - 210))}px`;
    rowMenu.style.top = `${Math.max(8, Math.min(bounds.bottom + 6, innerHeight - rowMenu.offsetHeight - 12))}px`;
    rowMenu.querySelector("button").focus();
    rowMenu.addEventListener("keydown", (event) => { const buttons = [...rowMenu.querySelectorAll("button")]; const i = buttons.indexOf(document.activeElement); if (event.key === "Escape") { closeRowMenu(); button.focus(); } if (["ArrowDown", "ArrowUp"].includes(event.key)) { event.preventDefault(); buttons[(i + (event.key === "ArrowDown" ? 1 : buttons.length - 1)) % buttons.length].focus(); } });
}
function openConfirm({ title, description, submit = "Tasdiqlash", danger = false, extra = "", action }) {
    $("detail-dialog").close(); closeRowMenu();
    state.confirm = action;
    $("confirm-title").textContent = title; $("confirm-description").textContent = description;
    $("confirm-extra").innerHTML = extra; $("confirm-symbol").innerHTML = icon(danger ? "trash" : "refresh");
    $("confirm-submit").className = `button ${danger ? "danger" : "primary"}`; $("confirm-submit").textContent = submit; $("confirm-submit").disabled = false;
    setMessage("confirm-error"); enhanceSelects($("confirm-dialog")); $("confirm-dialog").showModal();
}
function changeStatus(row) {
    const module = state.view, statuses = module === "groups" ? groupStatuses : module === "sessions" ? sessionStatuses : studentStatuses;
    openConfirm({ title: "Holatni o‘zgartirish", description: `${recordName(row)} uchun yangi holatni tanlang.`, submit: "Holatni saqlash", extra: `<div class="field"><label for="new-status">Yangi holat</label><select id="new-status">${enumOptions(statuses).map((o) => `<option value="${o.value}" ${row.status === o.value ? "selected" : ""}>${o.label}</option>`).join("")}</select></div>`, action: async () => api(`${recordPath(module, row)}/status`, jsonRequest("PATCH", { status: $("new-status").value })) });
}
async function openGenerateSessions() {
    await refreshOptions();
    const groups = state.options.groups.filter((g) => ["faol", "rejalashtirilgan"].includes(g.status) && (!state.branch || g.branch_id === Number(state.branch)));
    if (!groups.length) return toast("Avval faol yoki rejalashtirilgan guruh yarating.", true);
    openConfirm({ title: "Jadvaldan darslar yaratish", description: "Tanlangan davrdagi hafta kunlari bo‘yicha darslar yaratiladi. Mavjud va bekor qilingan darslar qayta yaratilmaydi. Butun davr birga tekshiriladi.", submit: "Darslarni yaratish", extra: `<div class="generation-fields"><div class="field"><label for="generate-group">Guruh</label><select id="generate-group" required><option value="">Guruhni tanlang</option>${groups.map((g) => `<option value="${g.id}" ${String(g.id) === state.filters.group_id ? "selected" : ""}>${esc(g.name)}</option>`).join("")}</select></div><div class="generation-dates"><div class="field"><label for="generate-from">Boshlanish sanasi</label><input id="generate-from" type="date" required value="${isoToday()}"></div><div class="field"><label for="generate-to">Tugash sanasi</label><input id="generate-to" type="date" required value="${isoToday()}"></div></div><p class="generation-hint">1–93 kun tanlang. O‘qituvchi va xona haftalik jadvaldan olinadi.</p></div>`, action: async () => {
        const body = { group_id: Number($("generate-group").value), date_from: $("generate-from").value, date_to: $("generate-to").value };
        if (!body.group_id || !body.date_from || !body.date_to) throw new Error("Guruh va sanalarni to‘ldiring.");
        const result = await api("/lesson-sessions/generate", jsonRequest("POST", body));
        toast(`${result.created} ta yangi dars. ${result.skipped} ta mavjud dars saqlandi.`);
        if (state.view !== "sessions") await navigate("sessions");
        state.filters = { group_id: String(body.group_id), date_from: body.date_from, date_to: body.date_to }; state.page = 1; listShell();
    } });
    updateGenerateBounds();
}
function updateGenerateBounds() {
    const group = lookup("groups", $("generate-group")?.value);
    if (!group) return;
    for (const key of ["generate-from", "generate-to"]) {
        const input = $(key); input.min = group.start_date; input.max = group.end_date || "";
        if (!input.value || input.value < group.start_date) input.value = group.start_date;
        if (group.end_date && input.value > group.end_date) input.value = group.end_date;
    }
    enhanceDates($("confirm-dialog"));
}
function deleteRecord(row) {
    const module = state.view, soft = ["groups", "students", "employees", "rooms", "sessions"].includes(module);
    openConfirm({ title: module === "sessions" ? "Darsni bekor qilish" : module === "groups" ? "Guruhni bekor qilish" : module === "students" ? "O‘quvchini ketgan deb belgilash" : soft ? "Yozuvni faolsizlantirish" : "Yozuvni o‘chirish", description: `${recordName(row)}. ${module === "schedules" ? "Faqat haftalik reja o‘chiriladi. Avval yaratilgan darslar saqlanadi." : soft ? "Ma’lumotlar tarixda saqlanadi." : "Yozuv o‘chiriladi. Davom etishdan oldin to‘g‘ri yozuvni tanlaganingizni tekshiring."}`, danger: true, submit: soft ? "Tasdiqlash" : "O‘chirish", action: () => api(recordPath(module, row), { method: "DELETE" }) });
}
function toggleRecord(row) {
    const module = state.view, active = !row.is_active;
    openConfirm({ title: active ? "Faollashtirish" : "Faolsizlantirish", description: `${recordName(row)} holati ${active ? "faol" : "faol emas"} qilib belgilanadi.`, submit: "Saqlash", action: () => api(queryPath(recordPath(module, row), module === "courses" ? { body: active } : module === "sources" ? { lead_source: active } : { is_active: active }), { method: "PATCH" }) });
}
function convertLead(row) {
    const students = state.options.students.filter((s) => s.branch_id === row.branch?.id);
    openConfirm({ title: "O‘quvchiga aylantirish", description: `${fullName(row)} — ${row.phone}. Mavjud o‘quvchiga bog‘lang yoki yangi profil yarating.`, submit: "Bog‘lash", extra: `<div class="field"><label for="convert-student">Mavjud o‘quvchi</label><select id="convert-student"><option value="">O‘quvchini tanlang</option>${students.map((s) => `<option value="${s.id}">${esc(fullName(s))} · ${esc(s.phone)}</option>`).join("")}</select></div><button class="text-button" type="button" data-convert-create="${row.id}" style="margin-top:15px">${icon("plus")}Yangi o‘quvchi profili</button>`, action: () => { if (!$("convert-student").value) throw new Error("O‘quvchini tanlang yoki yangi profil yarating."); return api(`/leads/${row.id}?student_id=${$("convert-student").value}`, { method: "PATCH" }); } });
}
async function moveLead(row, stage) {
    if (!canWrite("leads") || row.student) return;
    try {
        const payload = rowValues("leads", row); payload.status_id = stage ? Number(stage) : null;
        const allowed = Object.fromEntries(moduleDefinitions.leads.fields.filter((f) => f.key).map((f) => [f.key, payload[f.key] ?? null]));
        await api(`/leads/${row.id}`, jsonRequest("PUT", allowed)); toast("Lid yangi bosqichga o‘tkazildi.");
        if (state.view === "leads") await loadRecords();
    } catch (error) { toast(error.message, true); }
}

function exportRows(selectedOnly = false) {
    const rows = (state.visible || []).filter((row) => !selectedOnly || state.selected.has(keyOf(row)));
    if (!rows.length) return toast("Eksport qilish uchun ro‘yxatda yozuv bo‘lishi kerak.", true);
    const csvValue = (value) => { let text = String(value ?? "").replace(/\s+/g, " ").trim(); if (/^[=+@-]/.test(text)) text = "'" + text; return '"' + text.replace(/"/g, '""') + '"'; };
    const cells = columns[state.view];
    const content = [cells.map(([title]) => csvValue(title)).join(","), ...rows.map((row) => cells.map(([, render]) => { const cell = document.createElement("div"); cell.innerHTML = render(row); cell.querySelectorAll(".avatar").forEach((el) => el.remove()); cell.querySelectorAll(".cell-sub").forEach((el) => el.prepend(document.createTextNode(" · "))); return csvValue(cell.textContent); }).join(","))].join("\r\n");
    const url = URL.createObjectURL(new Blob(["\uFEFF" + content], { type: "text/csv;charset=utf-8" }));
    const exportDate = `${today.year}-${String(today.month).padStart(2, "0")}-${String(today.day).padStart(2, "0")}`;
    const link = document.createElement("a"); link.href = url; link.download = `markaz-${state.view}-${exportDate}.csv`; link.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
    toast(`${rows.length} ta yozuv CSV fayliga olindi.`);
}
function syncMobileMenu() {
    const mobile = matchMedia("(max-width: 760px)").matches;
    if (!mobile) { $("sidebar").classList.remove("open"); $("sidebar-shade").hidden = true; }
    const open = $("sidebar").classList.contains("open");
    $("sidebar").inert = mobile && !open;
    if (mobile && !open) $("sidebar").setAttribute("aria-hidden", "true"); else $("sidebar").removeAttribute("aria-hidden");
    $("mobile-menu").setAttribute("aria-expanded", String(open));
    $("mobile-menu").setAttribute("aria-label", open ? "Menyuni yopish" : "Menyuni ochish");
    $("mobile-menu").innerHTML = icon(open ? "close" : "menu");
}
function closeMobileMenu() { $("sidebar").classList.remove("open"); $("sidebar-shade").hidden = true; syncMobileMenu(); }
function openAccount() {
    const user = state.user;
    $("detail-content").innerHTML = `<div class="detail-cover"><span class="section-kicker">SIZNING ISH MAYDONINGIZ</span><button type="button" class="icon-button" data-close="detail-dialog" aria-label="Profilni yopish">${icon("close")}</button></div><div class="detail-intro">${avatar(user.name, "large")}<h2 id="detail-title">${esc(user.name)}</h2><p>${esc(user.position || "Jamoa a’zosi")}</p><div class="detail-badges">${user.is_superadmin ? protectedAdminPill() : ""}${user.roles.map((r) => `<span class="pill purple no-dot">${esc(r.name)}</span>`).join("")}</div></div><div class="detail-body"><dl class="detail-grid"><div><dt>Telefon / login</dt><dd>${esc(user.phone)}</dd></div><div><dt>Asosiy filial</dt><dd>${esc(lookup("branches", user.branch_id)?.name || "Belgilanmagan")}</dd></div><div class="full"><dt>Elektron pochta</dt><dd>${esc(user.email || "Kiritilmagan")}</dd></div></dl><div class="detail-heading">Ruxsat doirasi</div>${user.roles.map((r) => `<div class="shortcut-row"><span>${esc(r.name)}</span><span>${esc(user.is_superadmin || r.branch_id == null ? "Barcha filiallar" : lookup("branches", r.branch_id)?.name || `Filial #${r.branch_id}`)}</span></div>`).join("") || '<p class="detail-note">Sizga hali rol biriktirilmagan. Administratorga murojaat qiling.</p>'}</div><div class="detail-actions"><button class="button secondary" type="button" data-action="logout">${icon("logout")}Hisobdan chiqish</button></div>`;
    $("detail-dialog").showModal();
}
function openSetup() {
    const checks = [["branches", "Birinchi filial", state.options.branches.length], ["courses", "O‘quv yo‘nalishlari", state.options.courses.length], ["rooms", "Dars xonalari", state.options.rooms.length], ["teachers", "O‘qituvchi profillari", state.options.employees.some((r) => r.is_teacher)], ["statuses", "Qabul bosqichlari", state.options.statuses.length]];
    $("detail-content").innerHTML = `<div class="dialog-header"><div><span class="section-kicker">BIRINCHI QADAMLAR</span><h2 id="detail-title">Markazni ishga tayyorlang</h2><p>Guruhlar va qabul uchun kerakli asosiy ma’lumotlar.</p></div><button class="icon-button" data-close="detail-dialog" type="button" aria-label="Yopish">${icon("close")}</button></div><div class="detail-body">${checks.map(([key, label, done], i) => `<div class="workflow-step"><span class="workflow-number">${done ? icon("check") : String(i + 1).padStart(2, "0")}</span><span><strong>${label}</strong><small>${done ? "Ma’lumot kiritilgan" : "To‘ldirish kerak"}</small></span><button class="text-button" type="button" data-open-view="${key}" style="margin-left:auto">Ochish ${icon("arrow")}</button></div>`).join("")}</div>`;
    $("detail-dialog").showModal();
}
function openShortcuts() {
    $("detail-content").innerHTML = `<div class="dialog-header"><div><span class="section-kicker">KICHIK QULAYLIKLAR</span><h2 id="detail-title">Tezroq ishlang</h2></div><button type="button" class="icon-button" data-close="detail-dialog" aria-label="Yopish">${icon("close")}</button></div><div class="shortcut-list"><div class="shortcut-row"><span>Bo‘limni tezkor topish</span><kbd>Ctrl K</kbd></div><div class="shortcut-row"><span>Yangi yozuv yaratish</span><kbd>N</kbd></div><div class="shortcut-row"><span>Ro‘yxatdan qidirish</span><kbd>/</kbd></div><div class="shortcut-row"><span>Oynani yopish</span><kbd>Esc</kbd></div><p>Tanlash maydonlarida qidiruv yozishingiz mumkin. Variantlar orasida ↑ ↓ bilan yurib, Enter bilan tanlang. Kanban kartochkasini boshqa ustunga sudrab, lidning bosqichini yangilang.</p><p>Eksport ko‘rinayotgan sahifadagi yoki belgilangan yozuvlarni CSV fayliga oladi.</p></div>`;
    $("detail-dialog").showModal();
}
function renderCommandResults() {
    const search = $("command-input").value.trim().toLocaleLowerCase();
    const entries = [{ key: "overview", name: "Umumiy ko‘rinish", icon: "dashboard", group: "Boshqaruv" }, ...Object.entries(moduleDefinitions).filter(([key]) => canRead(key)).map(([key, def]) => ({ key, name: def.title, icon: def.icon, group: def.group }))];
    const matching = entries.filter((entry) => entry.name.toLocaleLowerCase().includes(search));
    $("command-results").innerHTML = matching.length ? matching.map((entry) => `<button type="button" class="command-result" data-open-view="${entry.key}">${icon(entry.icon)}${esc(entry.name)}<small>${esc(entry.group)}</small></button>`).join("") : '<p class="empty-small">Mos bo‘lim topilmadi.</p>';
}
function openCommand() { if ($("editor-dialog").open || $("confirm-dialog").open) return; $("command-input").value = ""; renderCommandResults(); $("command-dialog").showModal(); $("command-input").focus(); }
async function startApp() {
    await refreshOptions();
    $("login-view").hidden = true; $("app-view").hidden = false; $("login-password").value = "";
    await navigate(location.hash.slice(1) || "overview");
}
async function refreshCurrent() { if (state.view === "overview") await loadOverview(); else await loadRecords(); }
function applyFilters() { state.page = 1; state.selected.clear(); syncLessonControls(); if (moduleDefinitions[state.view]?.paged) loadRecords(); else renderRecords(); }
let filterTimer;
$("login-form").addEventListener("submit", async (event) => {
    event.preventDefault(); const button = event.submitter; button.disabled = true; setMessage("login-error");
    try {
        const body = new URLSearchParams(new FormData(event.currentTarget));
        const tokens = await api("/auth/login", { method: "POST", body, auth: false });
        state.token = tokens.access_token; state.refresh = tokens.refresh_token;
        sessionStorage.setItem("erp_access_token", state.token); sessionStorage.setItem("erp_refresh_token", state.refresh);
        await startApp();
    } catch (error) { showLogin(error.message); }
    finally { button.disabled = false; }
});
$("editor-form").addEventListener("submit", saveEditor);
document.querySelectorAll("dialog").forEach((dialog) => dialog.addEventListener("close", () => {
    if (SmartSelect.active?.select.closest("dialog") === dialog) SmartSelect.active.close();
    if (SmartDate.active?.input.closest("dialog") === dialog) SmartDate.active.close();
    if (SmartTime.active?.input.closest("dialog") === dialog) SmartTime.active.close();
    if (dialog.id === "editor-dialog") state.editor = null;
}));
$("confirm-form").addEventListener("submit", async (event) => {
    event.preventDefault(); $("confirm-submit").disabled = true; setMessage("confirm-error");
    try { await state.confirm(); $("confirm-dialog").close(); toast("O‘zgarish saqlandi."); await refreshOptions(); state.selected.clear(); await refreshCurrent(); }
    catch (error) { setMessage("confirm-error", error.message); }
    finally { $("confirm-submit").disabled = false; }
});
document.addEventListener("input", (event) => {
    if (event.target.dataset.filter === "search") {
        state.filters.search = event.target.value; clearTimeout(filterTimer); filterTimer = setTimeout(applyFilters, 280);
    }
    if (event.target.id === "command-input") renderCommandResults();
});
document.addEventListener("change", (event) => {
    const element = event.target;
    if (element.id === "generate-group") updateGenerateBounds();
    if (element.dataset.filter && element.dataset.filter !== "search") { state.filters[element.dataset.filter] = element.value; if (element.dataset.filter === "date_from" && state.filters.date_to && element.value > state.filters.date_to) state.filters.date_to = ""; clearTimeout(filterTimer); applyFilters(); }
    if (element.id === "context-branch") { state.branch = element.value; state.page = 1; state.selected.clear(); refreshCurrent(); }
    if (element.dataset.editorField) updateEditorHints(element.dataset.editorField);
    if (element.dataset.select) {
        if (element.checked) state.selected.add(element.dataset.select); else state.selected.delete(element.dataset.select);
        element.closest("tr")?.classList.toggle("selected", element.checked); updateSelection();
    }
    if (element.id === "select-page") { state.selected.clear(); if (element.checked) state.visible.forEach((row) => state.selected.add(keyOf(row))); renderRecords(); }
});
document.addEventListener("click", async (event) => {
    const target = event.target.closest("button, a"); if (!target) return;
    try {
        if (target.dataset.close) { $(target.dataset.close).close(); SmartSelect.active?.close(); return; }
        if (target.matches("a.nav-link")) closeMobileMenu();
        if (target.dataset.openView) { document.querySelectorAll("dialog[open]").forEach((dialog) => dialog.close()); await navigate(target.dataset.openView); return; }
        if (target.dataset.quickCreate) return openEditor(target.dataset.quickCreate);
        if (target.dataset.useEndDate) { const input = $("edit-end_date"); input.value = target.dataset.useEndDate; input.dispatchEvent(new Event("change", { bubbles: true })); SmartDate.instances.get(input)?.button.focus(); return; }
        if (target.dataset.openDate) { SmartDate.instances.get(document.querySelector(`input[data-filter="${target.dataset.openDate}"]`))?.open(); return; }
        if (target.dataset.lessonPeriod) { Object.assign(state.filters, lessonPeriod(target.dataset.lessonPeriod)); applyFilters(); return; }
        if (target.dataset.createDay) return openEditor("schedules", null, { weekday: target.dataset.createDay });
        if (target.dataset.groupView) { $("detail-dialog").close(); await navigate(target.dataset.groupView); state.filters = { group_id: target.dataset.groupId }; listShell(); await loadRecords(); return; }
        if (target.dataset.sessionComplete) { const session = state.rows.find((r) => String(r.id) === target.dataset.sessionComplete); if (session) { changeStatus(session); $("new-status").value = "otilgan"; enhanceSelects($("confirm-dialog")); } return; }
        if (target.dataset.mode) { state.mode = target.dataset.mode; document.querySelectorAll("[data-mode]").forEach((button) => { button.classList.toggle("active", button.dataset.mode === state.mode); button.setAttribute("aria-pressed", String(button.dataset.mode === state.mode)); }); renderRecords(); return; }
        if (target.dataset.page) { const page = state.page + Number(target.dataset.page); if (page < 1 || page > state.pages) return; state.page = page; state.selected.clear(); moduleDefinitions[state.view].paged ? await loadRecords() : renderRecords(); return; }
        const key = target.dataset.detail ?? target.dataset.edit ?? target.dataset.menu ?? target.dataset.convert ?? target.dataset.rowKey ?? target.dataset.convertCreate;
        const row = key !== undefined ? state.rows.find((r) => keyOf(r) === String(key)) : null;
        if (row && target.dataset.detail !== undefined) return openDetail(row);
        if (row && target.dataset.edit !== undefined) return openEditor(state.view, row);
        if (row && target.dataset.menu !== undefined) return showRowMenu(target, row);
        if (row && target.dataset.convert !== undefined) return convertLead(row);
        if (row && target.dataset.convertCreate !== undefined) return openEditor("students", null, { first_name: row.first_name, last_name: row.last_name, phone: row.phone, branch_id: row.branch?.id, source_id: row.source?.id, lead_id: row.id }, row);
        if (target.dataset.createStage !== undefined) return openEditor("leads", null, { status_id: target.dataset.createStage ? Number(target.dataset.createStage) : null });
        if (row && target.dataset.rowAction) {
            closeRowMenu();
            const action = target.dataset.rowAction;
            if (action === "detail") return openDetail(row);
            if (action === "edit") return openEditor(state.view, row);
            if (action === "delete") return deleteRecord(row);
            if (action === "toggle") return toggleRecord(row);
            if (action === "status") return changeStatus(row);
            if (action === "convert") return convertLead(row);
        }
        const action = target.dataset.action;
        if (action === "create") await openEditor();
        if (action === "quick-lead") await openEditor("leads");
        if (action === "generate-sessions") await openGenerateSessions();
        if (action === "refresh") { await refreshOptions(); await refreshCurrent(); }
        if (action === "clear-filters") { state.filters = {}; state.page = 1; state.selected.clear(); listShell(); await loadRecords(); }
        if (action === "clear-selection") { state.selected.clear(); renderRecords(); }
        if (action === "export" || action === "export-selected") exportRows(action === "export-selected");
        if (action === "logout") { closeMobileMenu(); showLogin(); }
    } catch (error) { toast(error.message, true); }
});
document.addEventListener("dragstart", (event) => {
    const card = event.target.closest("[data-drag]"); if (!card || card.draggable === false) return;
    state.dragging = card.dataset.drag; event.dataTransfer.setData("text/plain", card.dataset.drag); event.dataTransfer.effectAllowed = "move"; card.classList.add("dragging");
});
document.addEventListener("dragover", (event) => { const column = event.target.closest("[data-stage]"); if (column && state.dragging) { event.preventDefault(); event.dataTransfer.dropEffect = "move"; column.classList.add("drag-over"); } });
document.addEventListener("dragleave", (event) => { const column = event.target.closest("[data-stage]"); if (column && !column.contains(event.relatedTarget)) column.classList.remove("drag-over"); });
document.addEventListener("drop", async (event) => { const column = event.target.closest("[data-stage]"); if (!column || !state.dragging) return; event.preventDefault(); const row = state.rows.find((r) => String(r.id) === state.dragging); state.dragging = null; document.querySelectorAll(".drag-over,.dragging").forEach((el) => el.classList.remove("drag-over", "dragging")); if (row && String(row.status?.id ?? "") !== column.dataset.stage) await moveLead(row, column.dataset.stage); });
document.addEventListener("dragend", () => { state.dragging = null; document.querySelectorAll(".drag-over,.dragging").forEach((el) => el.classList.remove("drag-over", "dragging")); });
document.addEventListener("keydown", (event) => {
    if (event.target.closest(".calendar-popover, .time-popover")) return;
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k" && state.user && !$("app-view").hidden) { event.preventDefault(); openCommand(); return; }
    if (event.key === "Escape") closeRowMenu();
    if (event.key === "Escape" && $("sidebar").classList.contains("open")) { closeMobileMenu(); $("mobile-menu").focus(); }
    if (event.target.closest("input,textarea,[contenteditable=true]") || document.querySelector("dialog[open]") || $("app-view").hidden) return;
    if (event.key === "/" && $("record-search")) { event.preventDefault(); $("record-search").focus(); }
    if (event.key.toLowerCase() === "n" && !event.ctrlKey && !event.metaKey) { event.preventDefault(); openEditor(state.view === "overview" ? "leads" : state.view); }
});
$("command-input").addEventListener("keydown", (event) => {
    if (event.key === "ArrowDown") { event.preventDefault(); $("command-results").querySelector("button")?.focus(); }
    if (event.key === "Enter") { event.preventDefault(); $("command-results").querySelector("button")?.click(); }
});
$("command-results").addEventListener("keydown", (event) => { const buttons = [...$("command-results").querySelectorAll("button")], index = buttons.indexOf(document.activeElement); if (["ArrowDown", "ArrowUp"].includes(event.key) && buttons.length) { event.preventDefault(); buttons[(index + (event.key === "ArrowDown" ? 1 : buttons.length - 1)) % buttons.length].focus(); } });
$("command-button").addEventListener("click", openCommand);
$("account-button").addEventListener("click", openAccount);
$("setup-button").addEventListener("click", openSetup);
$("shortcuts-button").addEventListener("click", openShortcuts);
$("workspace-switch").addEventListener("click", () => { closeMobileMenu(); SmartSelect.instances.get($("context-branch"))?.open(); });
$("mobile-menu").addEventListener("click", () => { const open = $("sidebar").classList.toggle("open"); $("sidebar-shade").hidden = !open; syncMobileMenu(); if (open) $("sidebar").querySelector(".nav-link.active")?.focus(); });
$("sidebar-shade").addEventListener("click", closeMobileMenu);
$("sidebar-close").innerHTML = icon("close");
$("sidebar-close").addEventListener("click", () => { closeMobileMenu(); $("mobile-menu").focus(); });
$("toggle-password").innerHTML = icon("eye");
$("toggle-password").addEventListener("click", () => { const input = $("login-password"), show = input.type === "password"; input.type = show ? "text" : "password"; $("toggle-password").setAttribute("aria-label", show ? "Parolni yashirish" : "Parolni ko‘rsatish"); $("toggle-password").setAttribute("aria-pressed", String(show)); });
$("mobile-menu").innerHTML = icon("menu"); $("command-icon").innerHTML = icon("search"); $("palette-search-icon").innerHTML = icon("search");
document.querySelectorAll(".close-dialog").forEach((button) => { button.innerHTML = icon("close"); });
const today = Object.fromEntries(new Intl.DateTimeFormat("en-GB", { day: "numeric", month: "numeric", year: "numeric", timeZone: "Asia/Tashkent" }).formatToParts(new Date()).map((part) => [part.type, part.value]));
$("today").textContent = `${Number(today.day)} ${months[Number(today.month) - 1]} ${today.year}`;
window.addEventListener("hashchange", () => { if (state.user && !$("app-view").hidden) navigate(location.hash.slice(1)); });
enhanceSelects();
syncMobileMenu();
window.addEventListener("resize", syncMobileMenu);
if (state.token) startApp().catch((error) => showLogin(error.message));
