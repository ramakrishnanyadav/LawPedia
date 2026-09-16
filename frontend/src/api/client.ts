/**
 * Shared authenticated API client for LawPedia frontend.
 *
 * Consolidates auth token retrieval and standard fetch options in one place,
 * eliminating the duplicated getAuthToken() pattern across App.tsx,
 * EvidenceGraphView.tsx, and LawyerHandoffView.tsx.
 */

/** Retrieves the current bearer token from localStorage. */
export function getAuthToken(): string {
  return localStorage.getItem('lawpedia_token') || '';
}

/**
 * Performs an authenticated fetch with the standard Authorization header.
 * Throws a TypeError for network failures; caller is responsible for
 * checking response.ok for HTTP-level errors.
 */
export async function apiFetch(
  path: string,
  init: RequestInit = {}
): Promise<Response> {
  const token = getAuthToken();
  const headers = new Headers(init.headers as HeadersInit | undefined);
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  return fetch(path, { ...init, headers });
}

/**
 * Convenience wrapper: performs an authenticated fetch and returns the
 * parsed JSON body. Throws on network error or non-2xx HTTP status.
 */
export async function apiFetchJson<T = unknown>(
  path: string,
  init: RequestInit = {}
): Promise<T> {
  const res = await apiFetch(path, init);
  if (!res.ok) {
    throw new Error(`API error ${res.status}: ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}
