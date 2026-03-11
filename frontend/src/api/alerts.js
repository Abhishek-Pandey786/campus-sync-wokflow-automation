import api from "./client";

/** GET /alerts – list all high-risk requests */
export const getAlerts = () => api.get("/alerts").then((r) => r.data);

/** POST /alerts/scan – admin-triggered scan + email */
export const triggerScan = () => api.post("/alerts/scan").then((r) => r.data);

/** POST /alerts/:id/escalate */
export const escalateRequest = (requestId, notes = "") =>
  api.post(`/alerts/${requestId}/escalate`, { notes }).then((r) => r.data);
