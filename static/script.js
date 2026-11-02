const $ = (id) => document.getElementById(id);
const state = {
    token: sessionStorage.getItem("erp_access_token"),
    options: null,
    groups: [],
    page: 1,
    pages: 1,
    size: 10,
    requestId: 0,
    editing: null,
    cancelling: null,
};
const statuses = {
    rejalashtirilgan: "Rejalashtirilgan",
    faol: "Faol",
    tugagan: "Tugagan",
    bekor_qilingan: "Bekor qilingan",
};
const money = new Intl.NumberFormat("ru-RU", { maximumFractionDigits: 2 });
const months = ["yanvar", "fevral", "mart", "aprel", "may", "iyun", "iyul", "avgust", "sentabr", "oktabr", "noyabr", "dekabr"];
let searchTimer;
let toastTimer;

function escapeHTML(value) {
    return String(value ?? "").replace(/[&<>"']/g, (char) => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
    })[char]);
}

function message(id, text = "") {
    $(id).textContent = text;
    $(id).hidden = !text;
}

function formatDate(value) {
    const [year, month, day] = value.split("-");
    return `${Number(day)} ${months[Number(month) - 1].slice(0, 3)} ${year}`;
}

function toast(text) {
    clearTimeout(toastTimer);
    message("toast", text);
    toastTimer = setTimeout(() => message("toast"), 4000);
}

function showLogin(error = "") {
    state.token = null;
    state.requestId++;
    sessionStorage.removeItem("erp_access_token");
    $("group-dialog").close();
    $("cancel-group-dialog").close();
    $("app-view").hidden = true;
    $("login-view").hidden = false;
    message("login-error", error);
}

async function api(path, { auth = true, ...options } = {}) {
    const headers = new Headers(options.headers);
    if (auth && state.token) headers.set("Authorization", `Bearer ${state.token}`);
    let response;
    try {
        response = await fetch(path, { ...options, headers });
    } catch {
        throw new Error("Serverga ulanib bo‘lmadi. Ulanishni tekshirib, qayta urinib ko‘ring.");
    }
    const data = await response.json().catch(() => null);
    if (!response.ok) {
        if (auth && response.status === 401) showLogin("Kirish muddati tugadi. Qayta kiring.");
        let detail = data?.detail;
        if (Array.isArray(detail)) detail = detail.map((item) => item.msg).join(". ");
        if (response.status === 429) detail = "Urinishlar ko‘payib ketdi. Bir ozdan keyin qayta urinib ko‘ring.";
        throw new Error(typeof detail === "string" ? detail : "So‘rov bajarilmadi. Qayta urinib ko‘ring.");
    }
    return data;
}

function jsonRequest(method, body) {
    return { method, headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) };
}

function fillSelect(id, items, placeholder, selected = "", label = (item) => item.name) {
    $(id).replaceChildren(new Option(placeholder, ""), ...items.map((item) => new Option(label(item), item.id)));
    $(id).value = String(selected ?? "");
}

async function loadOptions() {
    state.options = await api("/groups/options");
    const branch = $("filter-branch").value;
    const course = $("filter-course").value;
    fillSelect("filter-branch", state.options.branches, "Barcha filiallar", branch);
    fillSelect("filter-course", state.options.courses, "Barcha kurslar", course);
    $("user-name").textContent = state.options.user.name;
    $("user-avatar").textContent = state.options.user.name.slice(0, 1).toUpperCase();
}

async function openApp() {
    await loadOptions();
    $("login-view").hidden = true;
    $("app-view").hidden = false;
    window.scrollTo(0, 0);
    $("password").value = "";
    await loadGroups();
}

function hasFilters() {
    return [...new FormData($("filters")).values()].some((value) => value.trim());
}

function renderGroup(group) {
    const teacher = `${group.teacher.first_name} ${group.teacher.last_name}`;
    const initials = `${group.teacher.first_name.slice(0, 1)}${group.teacher.last_name.slice(0, 1)}`;
    const percent = Math.min(100, group.current_students / group.max_students * 100);
    const cancelButton = group.status === "bekor_qilingan" ? "" : `<button class="icon-button cancel-action" type="button" data-cancel="${group.id}" aria-label="${escapeHTML(group.name)} guruhini bekor qilish" title="Bekor qilish"><svg><use href="#i-close"/></svg></button>`;
    return `<tr>
        <td><span class="cell-main">${escapeHTML(group.name)}</span><span class="cell-sub">${escapeHTML(group.course.name)}</span></td>
        <td>${escapeHTML(group.branch.name)}<span class="cell-sub">${escapeHTML(group.room.name)} · xona</span></td>
        <td><div class="teacher-cell"><span class="teacher-initial" aria-hidden="true">${escapeHTML(initials)}</span>${escapeHTML(teacher)}</div></td>
        <td><div class="student-count">${group.current_students} <span>/ ${group.max_students}</span></div><div class="capacity-track" aria-hidden="true"><span style="width:${percent}%"></span></div></td>
        <td><span class="cell-main">${money.format(group.effective_price)}</span><span class="cell-sub">so‘m / oy${group.price === null ? " · kurs narxi" : ""}</span></td>
        <td>${formatDate(group.start_date)}<span class="cell-sub">${group.end_date ? formatDate(group.end_date) + " gacha" : "Tugash sanasi belgilanmagan"}</span></td>
        <td><span class="status status-${escapeHTML(group.status)}">${escapeHTML(statuses[group.status] || group.status)}</span></td>
        <td><div class="row-actions"><button class="icon-button" type="button" data-edit="${group.id}" aria-label="${escapeHTML(group.name)} guruhini tahrirlash" title="Tahrirlash"><svg><use href="#i-edit"/></svg></button>${cancelButton}</div></td>
    </tr>`;
}

async function loadGroups() {
    const requestId = ++state.requestId;
    message("page-error");
    const query = new URLSearchParams({ page: state.page, size: state.size });
    for (const [key, value] of new FormData($("filters"))) {
        if (value.trim()) query.set(key, value.trim());
    }
    $("clear-filters").hidden = !hasFilters();
    $("groups-table").hidden = false;
    $("groups-table").setAttribute("aria-busy", "true");
    $("empty-state").hidden = true;
    $("groups-body").innerHTML = '<tr class="loading-row"><td colspan="8">Guruhlar yuklanmoqda…</td></tr>';
    $("previous-page").disabled = true;
    $("next-page").disabled = true;
    try {
        const data = await api(`/groups/?${query}`);
        if (requestId !== state.requestId) return;
        state.groups = data.items;
        state.pages = Math.max(1, data.pages);
        if (state.page > state.pages) {
            state.page = state.pages;
            return loadGroups();
        }
        $("groups-body").innerHTML = data.items.map(renderGroup).join("");
        $("groups-table").parentElement.scrollLeft = 0;
        $("total-count").textContent = data.total;
        $("nav-count").textContent = data.total;
        $("page-number").textContent = `${state.page} / ${state.pages}`;
        $("previous-page").disabled = state.page <= 1;
        $("next-page").disabled = state.page >= state.pages;
        const start = data.total ? (state.page - 1) * state.size + 1 : 0;
        const end = Math.min(state.page * state.size, data.total);
        $("result-count").textContent = `${data.total} ta guruhdan ${start}–${end} ko‘rsatilmoqda`;
        $("empty-state").hidden = data.items.length > 0;
        $("groups-table").hidden = !data.items.length;
        $("empty-description").textContent = hasFilters()
            ? "Bu shartlarga mos guruh topilmadi. Qidiruv yoki filtrlarni o‘zgartiring."
            : "Birinchi guruhni oching va o‘quv jarayonini boshlang.";
        $("empty-add").hidden = hasFilters();
    } catch (error) {
        if (requestId !== state.requestId) return;
        $("groups-body").replaceChildren();
        $("result-count").textContent = "Ro‘yxat yuklanmadi";
        message("page-error", error.message);
    } finally {
        if (requestId === state.requestId) $("groups-table").setAttribute("aria-busy", "false");
    }
}

function includeCurrent(items, current) {
    return current && !items.some((item) => item.id === current.id) ? [...items, current] : items;
}

function updateBranchFields() {
    const branchId = Number($("group-branch").value);
    const group = state.editing?.branch_id === branchId ? state.editing : null;
    const teachers = includeCurrent(state.options.teachers, group?.teacher).filter((item) => item.branch_id === branchId);
    const rooms = includeCurrent(state.options.rooms, group?.room).filter((item) => item.branch_id === branchId);
    fillSelect("group-teacher", teachers, teachers.length ? "O‘qituvchini tanlang" : "Bu filialda o‘qituvchi yo‘q", group?.teacher_id, (item) => `${item.first_name} ${item.last_name}`);
    fillSelect("group-room", rooms, rooms.length ? "Xonani tanlang" : "Bu filialda xona yo‘q", group?.room_id, (item) => `${item.name} · ${item.capacity} o‘rin`);
    updateCapacity();
}

function updateCapacity() {
    const roomId = Number($("group-room").value);
    const room = includeCurrent(state.options.rooms, state.editing?.room).find((item) => item.id === roomId);
    $("max-students").max = room ? Math.min(room.capacity, 32767) : 32767;
    $("capacity-hint").textContent = room ? `Xona sig‘imi: ${room.capacity} o‘rin.` : "Avval xonani tanlang.";
}

function updatePriceHint() {
    const courses = includeCurrent(state.options.courses, state.editing?.course);
    const course = courses.find((item) => item.id === Number($("group-course").value));
    $("price-hint").textContent = course ? `Kurs narxi: ${money.format(course.price)} so‘m / oy. Bo‘sh qoldirsangiz, shu narx olinadi.` : "Bo‘sh qoldirilsa, kurs narxi olinadi.";
}

async function openGroupDialog(group = null) {
    $("add-group").disabled = true;
    try {
        await loadOptions();
        state.editing = group;
        $("group-form").reset();
        message("form-error");
        $("dialog-title").textContent = group ? "Guruhni tahrirlash" : "Yangi guruh";
        $("save-group").textContent = group ? "O‘zgarishlarni saqlash" : "Guruhni saqlash";
        fillSelect("group-branch", includeCurrent(state.options.branches, group?.branch), "Filialni tanlang", group?.branch_id || (state.options.branches.length === 1 ? state.options.branches[0].id : ""));
        fillSelect("group-course", includeCurrent(state.options.courses, group?.course), "Kursni tanlang", group?.course_id);
        updateBranchFields();
        $("group-branch").disabled = Boolean(group?.current_students);
        $("group-course").disabled = Boolean(group?.current_students);
        $("max-students").min = Math.max(1, group?.current_students || 0);
        if (group) {
            for (const field of ["name", "start_date", "end_date", "max_students", "price", "status"]) {
                $("group-form").elements[field].value = group[field] ?? "";
            }
        }
        $("end-date").min = $("start-date").value;
        updatePriceHint();
        if (!state.options.branches.length || !state.options.courses.length || !state.options.teachers.length || !state.options.rooms.length) {
            message("form-error", "Guruh ochish uchun faol filial, kurs, xona va o‘qituvchi profili kerak.");
        }
        $("group-dialog").showModal();
    } catch (error) {
        message("page-error", error.message);
    } finally {
        $("add-group").disabled = false;
    }
}

$("login-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const button = event.submitter;
    button.disabled = true;
    message("login-error");
    try {
        const body = new URLSearchParams(new FormData(event.currentTarget));
        const data = await api("/auth/login", { method: "POST", body, auth: false });
        state.token = data.access_token;
        sessionStorage.setItem("erp_access_token", state.token);
        state.page = 1;
        await openApp();
    } catch (error) {
        showLogin(error.message);
    } finally {
        button.disabled = false;
    }
});

$("group-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const payload = {};
    for (const field of ["name", "status", "start_date"]) payload[field] = form.elements[field].value.trim();
    for (const field of ["branch_id", "course_id", "teacher_id", "room_id", "max_students"]) payload[field] = Number(form.elements[field].value);
    payload.end_date = form.elements.end_date.value || null;
    payload.price = form.elements.price.value || null;
    $("save-group").disabled = true;
    message("form-error");
    try {
        const editing = state.editing;
        await api(editing ? `/groups/${editing.id}` : "/groups/", jsonRequest(editing ? "PUT" : "POST", payload));
        $("group-dialog").close();
        toast(editing ? "Guruh yangilandi." : "Yangi guruh yaratildi.");
        if (!editing) state.page = 1;
        await loadGroups();
    } catch (error) {
        message("form-error", error.message);
    } finally {
        $("save-group").disabled = false;
    }
});

$("groups-body").addEventListener("click", (event) => {
    const edit = event.target.closest("[data-edit]");
    const cancel = event.target.closest("[data-cancel]");
    if (edit) openGroupDialog(state.groups.find((group) => group.id === Number(edit.dataset.edit)));
    if (cancel) {
        state.cancelling = state.groups.find((group) => group.id === Number(cancel.dataset.cancel));
        $("cancel-group-name").textContent = state.cancelling.name;
        message("cancel-error");
        $("cancel-group-dialog").showModal();
    }
});

$("cancel-group-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    $("confirm-cancel").disabled = true;
    message("cancel-error");
    try {
        await api(`/groups/${state.cancelling.id}`, { method: "DELETE" });
        $("cancel-group-dialog").close();
        toast("Guruh bekor qilindi. Tarixi saqlandi.");
        await loadGroups();
    } catch (error) {
        message("cancel-error", error.message);
    } finally {
        $("confirm-cancel").disabled = false;
    }
});

function filterGroups() {
    clearTimeout(searchTimer);
    state.page = 1;
    loadGroups();
}

$("filters").addEventListener("submit", (event) => { event.preventDefault(); filterGroups(); });
$("search").addEventListener("input", () => { clearTimeout(searchTimer); searchTimer = setTimeout(filterGroups, 300); });
for (const id of ["filter-branch", "filter-course", "filter-status"]) $(id).addEventListener("change", filterGroups);
$("clear-filters").addEventListener("click", () => { $("filters").reset(); filterGroups(); });
$("refresh").addEventListener("click", loadGroups);
$("previous-page").addEventListener("click", () => { if (state.page > 1) { state.page--; loadGroups(); } });
$("next-page").addEventListener("click", () => { if (state.page < state.pages) { state.page++; loadGroups(); } });
$("add-group").addEventListener("click", () => openGroupDialog());
$("empty-add").addEventListener("click", () => openGroupDialog());
$("logout").addEventListener("click", () => { $("filters").reset(); showLogin(); });
$("group-branch").addEventListener("change", updateBranchFields);
$("group-course").addEventListener("change", updatePriceHint);
$("group-room").addEventListener("change", updateCapacity);
$("start-date").addEventListener("change", () => { $("end-date").min = $("start-date").value; });
for (const id of ["close-dialog", "cancel-dialog"]) $(id).addEventListener("click", () => $("group-dialog").close());
$("keep-group").addEventListener("click", () => $("cancel-group-dialog").close());
const today = Object.fromEntries(new Intl.DateTimeFormat("en-GB", { day: "numeric", month: "numeric", year: "numeric", timeZone: "Asia/Tashkent" }).formatToParts(new Date()).map((part) => [part.type, part.value]));
$("today").textContent = `${today.day} ${months[Number(today.month) - 1]} ${today.year}`;
if (state.token) openApp().catch((error) => showLogin(error.message));
