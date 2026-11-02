export function getApiErrorMessage(error, fallback) {
  const detail = error.response?.data?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail) && detail.length > 0) {
    return detail
      .map((issue) => `${issue.loc?.at(-1) ?? "Field"}: ${issue.msg}`)
      .join(" ");
  }
  if (!error.response) return "The portal could not reach the server. Check your connection and try again.";
  return fallback;
}
