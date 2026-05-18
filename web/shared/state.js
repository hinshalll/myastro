// ─────────────────────────────────────────────────────────────────────────────
// web/shared/state.js
// Profile management via localStorage. Same data model the future mobile app
// and Supabase will use — just stored client-side for now.
//
// A profile looks like:
//   {
//     id:    "p-1737059234567",     ← auto-generated unique ID
//     name:  "Hinshal",
//     date:  "2000-03-16",          ← ISO date
//     time:  "20:35",               ← HH:MM 24h
//     place: "Shimla",
//     lat:   31.1048,
//     lon:   77.1734,
//     tz:    "Asia/Kolkata",
//     gender: "M",                  ← M / F / O
//     exact_time: true,
//     is_default: false,
//   }
// ─────────────────────────────────────────────────────────────────────────────

const STORAGE_KEY = "myastro_profiles";

export function loadProfiles() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
  } catch {
    return [];
  }
}

export function saveProfiles(profiles) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(profiles));
}

export function getProfileById(id) {
  return loadProfiles().find(p => p.id === id) || null;
}

export function getDefaultProfile() {
  const list = loadProfiles();
  return list.find(p => p.is_default) || list[0] || null;
}

export function addProfile(profile) {
  const list = loadProfiles();
  // Strip any existing default flag if this is the first profile being added
  // (the first profile is auto-default).
  if (list.length === 0) profile.is_default = true;
  profile.id = profile.id || `p-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`;
  list.push(profile);
  saveProfiles(list);
  return profile;
}

export function updateProfile(id, patch) {
  const list = loadProfiles();
  const idx = list.findIndex(p => p.id === id);
  if (idx < 0) return null;
  list[idx] = { ...list[idx], ...patch };
  saveProfiles(list);
  return list[idx];
}

export function deleteProfile(id) {
  let list = loadProfiles().filter(p => p.id !== id);
  // If we just deleted the default, promote the first remaining one.
  if (list.length > 0 && !list.some(p => p.is_default)) {
    list[0].is_default = true;
  }
  saveProfiles(list);
}

export function setDefault(id) {
  const list = loadProfiles().map(p => ({ ...p, is_default: p.id === id }));
  saveProfiles(list);
}

// Strip the localStorage-only fields before sending to the backend.
export function toBackendProfile(p) {
  if (!p) return null;
  const { id, is_default, ...rest } = p;
  return rest;
}
