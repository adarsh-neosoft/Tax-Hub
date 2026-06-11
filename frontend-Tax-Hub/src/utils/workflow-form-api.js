import { api } from "iron-stack-ui";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api";

function authHeaders() {
  const token = localStorage.getItem("token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

/**
 * Submit workflow form.
 * - No files: JSON via axios (same client as rest of app, auth handled automatically)
 * - With files: native fetch + FormData (avoids axios multipart header issues)
 */
export async function submitWorkflowForm({ url, method, payload, files = [] }) {
  if (files.length === 0) {
    if (method === "patch") {
      return api.patch(url, payload);
    }
    return api.post(url, payload);
  }

  const body = new FormData();
  body.append("payload", JSON.stringify(payload));
  files.forEach(([key, file]) => body.append(key, file));

  const response = await fetch(`${API_BASE_URL}${url}`, {
    method: method.toUpperCase(),
    headers: authHeaders(),
    body,
    credentials: "include",
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = new Error(data.detail || "Save failed");
    error.response = { data, status: response.status };
    throw error;
  }

  return { data, status: response.status };
}
