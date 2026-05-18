// ─────────────────────────────────────────────────────────────────────────────
// web/shared/components.js
// Reusable UI helpers. Importable from any page.
// ─────────────────────────────────────────────────────────────────────────────

import { loadProfiles, getDefaultProfile } from "./state.js";

// Inject the top navigation bar into a placeholder div on the page.
// Usage: <div id="nav"></div>  +  renderNav()
export function renderNav(activePage = "") {
  const links = [
    ["index.html",        "Dashboard"],
    ["kundli.html",       "Kundli"],
    ["palm.html",         "Palm"],
    ["oracle/index.html", "Oracle"],
    ["tarot.html",        "Tarot"],
    ["numerology.html",   "Numerology"],
    ["horoscope.html",    "Horoscope"],
    ["consultation.html", "Chat"],
    ["profiles.html",     "Profiles"],
  ];
  // Figure out the prefix to use for links so this works from both the root
  // and from sub-folders like /oracle/.
  const prefix = window.location.pathname.includes("/oracle/") ? "../" : "";
  const html = `
    <nav class="border-b border-slate-800 bg-slate-950 sticky top-0 z-10">
      <div class="max-w-5xl mx-auto px-4 py-3 flex flex-wrap items-center gap-x-5 gap-y-2 text-sm">
        <a href="${prefix}index.html" class="font-bold text-purple-300 text-base mr-4">✦ Myastro</a>
        ${links.map(([href, label]) => {
          const isActive = activePage === label.toLowerCase();
          return `<a href="${prefix}${href}"
            class="${isActive ? "text-purple-300 font-semibold" : "text-slate-400 hover:text-purple-200"}">
            ${label}
          </a>`;
        }).join("")}
      </div>
    </nav>
  `;
  const slot = document.getElementById("nav");
  if (slot) slot.outerHTML = html;
}

// Render a <select> filled with the user's saved profiles.
// On change, calls onChange(profile_object).
// Returns: { element, getSelected() }
export function renderProfilePicker(slotId, { onChange = () => {}, defaultToFirst = true } = {}) {
  const slot = document.getElementById(slotId);
  const profiles = loadProfiles();
  if (profiles.length === 0) {
    slot.innerHTML = `
      <div class="rounded-lg border border-amber-700 bg-amber-950/40 p-3 text-sm">
        No saved profiles. <a href="profiles.html" class="underline text-amber-300">Add one →</a>
      </div>`;
    return { getSelected: () => null };
  }
  const defaultId = (getDefaultProfile() || profiles[0]).id;
  slot.innerHTML = `
    <select id="${slotId}_select" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm">
      ${profiles.map(p => `
        <option value="${p.id}" ${p.id === defaultId ? "selected" : ""}>
          ${p.name} — ${p.date} ${p.time} • ${p.place}
        </option>
      `).join("")}
    </select>
  `;
  const sel = document.getElementById(`${slotId}_select`);
  const getSelected = () => profiles.find(p => p.id === sel.value) || null;
  sel.addEventListener("change", () => onChange(getSelected()));
  if (defaultToFirst) onChange(getSelected());
  return { getSelected };
}

// Convert a markdown string to HTML using the `marked` CDN library (loaded
// via <script> in each page).
export function renderMarkdown(md) {
  if (!md) return "";
  if (window.marked) {
    return window.marked.parse(md);
  }
  // Fallback if marked.js didn't load — show raw with line breaks
  return `<pre class="whitespace-pre-wrap">${escapeHtml(md)}</pre>`;
}

export function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

// Render a "result card" with markdown body + optional metadata block.
// Used by every feature to show the AI's response uniformly.
export function renderResult(slotId, markdown, metadata = null) {
  const slot = document.getElementById(slotId);
  let meta = "";
  if (metadata && Object.keys(metadata).length) {
    meta = `
      <details class="mt-4 text-xs text-slate-500">
        <summary class="cursor-pointer hover:text-slate-300">Show technical details</summary>
        <pre class="mt-2 p-2 bg-slate-950 rounded overflow-auto">${escapeHtml(JSON.stringify(metadata, null, 2))}</pre>
      </details>
    `;
  }
  slot.innerHTML = `
    <div class="prose prose-invert prose-slate max-w-none">
      ${renderMarkdown(markdown)}
    </div>
    ${meta}
  `;
  slot.classList.remove("hidden");
  slot.scrollIntoView({ behavior: "smooth", block: "start" });
}

// Render a spinner / "thinking" state. Toggled by show=true/false.
export function setLoading(slotId, show, label = "Thinking...") {
  const slot = document.getElementById(slotId);
  if (!show) {
    slot.classList.add("hidden");
    return;
  }
  slot.classList.remove("hidden");
  slot.innerHTML = `
    <div class="flex items-center gap-3 p-4 rounded-lg bg-slate-900 border border-slate-800">
      <div class="w-5 h-5 border-2 border-purple-400 border-t-transparent rounded-full animate-spin"></div>
      <span class="text-slate-300 text-sm">${escapeHtml(label)}</span>
    </div>
  `;
}

// Render an error message in a slot.
export function renderError(slotId, err) {
  const slot = document.getElementById(slotId);
  slot.classList.remove("hidden");
  slot.innerHTML = `
    <div class="p-4 rounded-lg border border-rose-800 bg-rose-950/40 text-rose-300 text-sm">
      <div class="font-semibold mb-1">Error</div>
      <pre class="whitespace-pre-wrap text-xs">${escapeHtml(String(err?.message || err))}</pre>
    </div>
  `;
}
