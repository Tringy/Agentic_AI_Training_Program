import type { APIError } from "@/types";

const FALLBACK_CODE = "HTTP_ERROR";

export function parseApiError(responseBody: unknown): APIError {
  if (typeof responseBody === "object" && responseBody !== null) {
    const maybe = responseBody as Partial<APIError> & { detail?: unknown };
    if (
      typeof maybe.detail === "string" &&
      typeof maybe.error_code === "string" &&
      typeof maybe.retryable === "boolean" &&
      typeof maybe.request_id === "string"
    ) {
      return {
        detail: maybe.detail,
        error_code: maybe.error_code,
        retryable: maybe.retryable,
        request_id: maybe.request_id,
      };
    }

    if (typeof maybe.detail === "string") {
      return {
        detail: maybe.detail,
        error_code: FALLBACK_CODE,
        retryable: false,
        request_id: "unknown",
      };
    }
  }

  return {
    detail: "Request failed",
    error_code: FALLBACK_CODE,
    retryable: false,
    request_id: "unknown",
  };
}
