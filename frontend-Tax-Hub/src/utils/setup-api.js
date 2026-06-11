import { AxiosHeaders } from "axios";
import { api } from "iron-stack-ui";

/**
 * Axios instance defaults to application/json. Strip it for FormData so the
 * browser can set multipart/form-data with the correct boundary.
 */
api.interceptors.request.use((config) => {
  if (config.data instanceof FormData) {
    const headers = AxiosHeaders.from(config.headers);
    headers.delete("Content-Type");
    headers.delete("content-type");
    config.headers = headers;
  }
  return config;
});

export default api;
