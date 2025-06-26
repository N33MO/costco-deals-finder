export const API_BASE = import.meta.env.VITE_API_URL ?? '';

export async function apiFetch(input: string, init?: RequestInit) {
  const url = `${API_BASE}${input}`;
  return fetch(url, init);
}
