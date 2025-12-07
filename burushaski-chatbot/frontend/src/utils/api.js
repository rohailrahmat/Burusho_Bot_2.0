const API_BASE = import.meta?.env?.VITE_API_BASE || "http://127.0.0.1:8000";

async function request(path, opts = {}) {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, opts);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Request failed ${res.status}: ${text}`);
  }
  return res.json();
}

export async function searchDictionary(q, limit = 20) {
  const path = `/api/dictionary/search?q=${encodeURIComponent(q)}&limit=${limit}`;
  return request(path, { method: "GET" });
}

export async function getWordById(id) {
  return request(`/api/dictionary/item/${id}`);
}

export async function getByBurushaski(text) {
  return request(`/api/dictionary/by-burushaski?text=${encodeURIComponent(text)}`);
}

export async function translate(text, source = "burushaski", target = "english") {
  const body = { text, source, target };
  return request(`/api/translate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export default { searchDictionary, getWordById, getByBurushaski, translate };
