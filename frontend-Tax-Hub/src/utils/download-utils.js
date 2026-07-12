/**
 * Extract a sensible filename from a URL path.
 */
export function getFilenameFromUrl(url) {
  const parts = url.split("/");
  return parts[parts.length - 1] || "download";
}

/**
 * Download a file showing the native "Save As" dialog (File System Access API).
 *
 * @param {string} url - URL to fetch the file from
 * @param {object} options
 * @param {string} options.suggestedName - Fallback filename if it can't be inferred from the URL
 * @param {object} options.headers - Extra headers to include in the request
 */
export async function downloadFileWithDialog(url, options = {}) {
  const filename = options.suggestedName || getFilenameFromUrl(url);

  // Build headers: include auth Bearer token for non-media URLs
  const headers = { ...(options.headers || {}) };
  if (!url.startsWith("/media/")) {
    const token = localStorage.getItem("token");
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
  }

  // Try the modern File System Access API (shows native Save As dialog)
  if ("showSaveFilePicker" in window) {
    const ext = filename.includes(".") ? `.${filename.split(".").pop()}` : "";
    const fileTypes = ext
      ? [
          {
            description:
              ext === ".xlsx"
                ? "Excel Workbook"
                : `${ext.toUpperCase()} File`,
            accept: { "application/octet-stream": [ext] },
          },
        ]
      : [];

    const handle = await window.showSaveFilePicker({
      suggestedName: filename,
      types: fileTypes,
      excludeAcceptAllOption: true,
    });
    const writable = await handle.createWritable();
    const response = await fetch(url, { headers });
    if (!response.ok) {
      throw new Error(
        `Server returned ${response.status} ${response.statusText}`
      );
    }
    const blob = await response.blob();
    await writable.write(blob);
    await writable.close();
    return;
  }

  // Fallback: trigger download via anchor element
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}
