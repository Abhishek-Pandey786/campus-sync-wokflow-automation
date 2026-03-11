import api from "./client";

export const getWorkflowLogs = (requestId) =>
  api.get(`/workflows/${requestId}/logs`).then((r) => r.data);

export const getWorkflowStatus = (requestId) =>
  api.get(`/workflows/${requestId}/status`).then((r) => r.data);
