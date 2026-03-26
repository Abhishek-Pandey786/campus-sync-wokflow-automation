import api from "./client";

export const getWorkflowLogs = (requestId) =>
  api.get(`/workflows/${requestId}/logs`).then((r) => r.data);

export const assignRequest = (requestId, adminId) =>
  api.post(`/workflows/${requestId}/assign`, { admin_id: adminId }).then((r) => r.data);

export const advanceStage = (requestId, notes = "") =>
  api.post(`/workflows/${requestId}/advance`, { notes }).then((r) => r.data);

// rejection_notes is a query param per backend definition
export const rejectRequest = (requestId, notes) =>
  api.post(`/workflows/${requestId}/reject`, null, {
    params: { rejection_notes: notes },
  }).then((r) => r.data);
