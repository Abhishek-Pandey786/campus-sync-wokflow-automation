import { useEffect, useState } from "react";
import RequestTable from "../components/RequestTable";
import NewRequestModal from "../components/NewRequestModal";
import { getRequests } from "../api/requests";
import { getWorkflowLogs, assignRequest, advanceStage, rejectRequest } from "../api/workflows";
import { getMe } from "../api/auth";
import { useAuth } from "../context/AuthContext";
import {
  FileText, Search, Filter, RotateCcw, X,
  ChevronLeft, ChevronRight, ClipboardList,
  UserCheck, ShieldCheck, ThumbsUp, Cog, PartyPopper,
  Plus, ArrowRight, CheckCircle2, XCircle, Loader2,
  AlertCircle,
} from "lucide-react";

const REQUEST_TYPES = ["all","certificate","hostel","it_support","library","exam","transcript"];
const STATUSES      = ["all","pending","in_progress","completed","rejected"];

const STAGE_ICONS = {
  created:   ClipboardList,
  assigned:  UserCheck,
  verified:  ShieldCheck,
  approved:  ThumbsUp,
  processed: Cog,
  completed: PartyPopper,
};

const STAGE_ORDER = ["created","assigned","verified","approved","processed","completed"];

const PRIORITY_LABEL  = { 1: "Low", 2: "Medium", 3: "High" };
const PRIORITY_CONFIG = {
  1: { color: "text-slate-400",  dot: "bg-slate-400" },
  2: { color: "text-amber-400",  dot: "bg-amber-400" },
  3: { color: "text-red-400",    dot: "bg-red-400"   },
};
const STATUS_CONFIG = {
  pending:     "bg-amber-500/15 text-amber-400 border border-amber-500/20",
  in_progress: "bg-primary-500/15 text-primary-400 border border-primary-500/20",
  processing:  "bg-primary-500/15 text-primary-400 border border-primary-500/20",
  completed:   "bg-emerald-500/15 text-emerald-400 border border-emerald-500/20",
  rejected:    "bg-red-500/15 text-red-400 border border-red-500/20",
};

// ──────────────────────────────────────────────────────────────────────────────
// Admin Action Panel  (Assign / Advance / Reject)
// ──────────────────────────────────────────────────────────────────────────────
function AdminActions({ request, adminId, onActionDone }) {
  const [busy, setBusy]         = useState(null); // 'assign' | 'advance' | 'reject'
  const [rejectNote, setRejectNote] = useState("");
  const [showReject, setShowReject] = useState(false);
  const [msg, setMsg]           = useState(null);
  const [err, setErr]           = useState(null);

  const isDone = ["completed","rejected"].includes(request?.status);

  const flash = (m, isErr = false) => {
    if (isErr) setErr(m); else setMsg(m);
    setTimeout(() => { setMsg(null); setErr(null); }, 3000);
  };

  const doAssign = async () => {
    setBusy("assign");
    try {
      const res = await assignRequest(request.id, adminId);
      flash(`✓ ${res.message}`);
      onActionDone();
    } catch (e) {
      flash(e.response?.data?.detail ?? "Assign failed", true);
    } finally { setBusy(null); }
  };

  const doAdvance = async () => {
    setBusy("advance");
    try {
      const res = await advanceStage(request.id, "Advanced by admin");
      flash(`✓ ${res.message}`);
      onActionDone();
    } catch (e) {
      flash(e.response?.data?.detail ?? "Advance failed", true);
    } finally { setBusy(null); }
  };

  const doReject = async () => {
    if (!rejectNote.trim()) { setErr("Enter a rejection reason."); return; }
    setBusy("reject");
    try {
      const res = await rejectRequest(request.id, rejectNote);
      flash(`✓ ${res.message}`);
      setShowReject(false);
      onActionDone();
    } catch (e) {
      flash(e.response?.data?.detail ?? "Reject failed", true);
    } finally { setBusy(null); }
  };

  if (isDone) return null;

  const nextStage = STAGE_ORDER[STAGE_ORDER.indexOf(request.current_stage) + 1];

  return (
    <div className="mt-6 space-y-3">
      <h3 className="text-sm font-semibold text-slate-300 flex items-center gap-2">
        <Cog className="w-4 h-4 text-accent-400" /> Admin Actions
      </h3>

      {/* Feedback */}
      {msg && <p className="text-emerald-400 text-xs bg-emerald-500/10 border border-emerald-500/20 rounded-lg px-3 py-2">{msg}</p>}
      {err && <p className="text-red-400 text-xs bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2 flex items-center gap-1.5"><AlertCircle className="w-3.5 h-3.5 flex-shrink-0"/>{err}</p>}

      <div className="flex flex-wrap gap-2">
        {/* Assign to me (only if not yet assigned) */}
        {request.current_stage === "created" && (
          <button onClick={doAssign} disabled={!!busy}
            className="btn-primary text-sm py-2 px-4">
            {busy === "assign"
              ? <><Loader2 className="w-3.5 h-3.5 animate-spin"/>Assigning…</>
              : <><UserCheck className="w-3.5 h-3.5"/>Assign to Me</>}
          </button>
        )}

        {/* Advance stage */}
        {request.current_stage !== "created" && nextStage && (
          <button onClick={doAdvance} disabled={!!busy}
            className="btn-primary text-sm py-2 px-4">
            {busy === "advance"
              ? <><Loader2 className="w-3.5 h-3.5 animate-spin"/>Advancing…</>
              : <><ArrowRight className="w-3.5 h-3.5"/>Advance to <span className="capitalize ml-1">{nextStage}</span></>}
          </button>
        )}

        {/* Reject */}
        {!showReject && (
          <button onClick={() => setShowReject(true)} disabled={!!busy}
            className="btn-danger text-sm py-2 px-4">
            <XCircle className="w-3.5 h-3.5"/> Reject
          </button>
        )}
      </div>

      {/* Reject reason input */}
      {showReject && (
        <div className="space-y-2 pt-1">
          <textarea
            className="input-field resize-none text-sm"
            rows={2}
            placeholder="Reason for rejection…"
            value={rejectNote}
            onChange={(e) => setRejectNote(e.target.value)}
          />
          <div className="flex gap-2">
            <button onClick={doReject} disabled={!!busy}
              className="btn-danger text-sm py-1.5 px-4">
              {busy === "reject"
                ? <><Loader2 className="w-3.5 h-3.5 animate-spin"/>Rejecting…</>
                : <><XCircle className="w-3.5 h-3.5"/>Confirm Reject</>}
            </button>
            <button onClick={() => { setShowReject(false); setRejectNote(""); }}
              className="btn-secondary text-sm py-1.5 px-3">Cancel</button>
          </div>
        </div>
      )}
    </div>
  );
}

// ──────────────────────────────────────────────────────────────────────────────
// Stage Progress Bar
// ──────────────────────────────────────────────────────────────────────────────
function StagePipeline({ current }) {
  const idx = STAGE_ORDER.indexOf(current);
  return (
    <div className="flex items-center gap-0 mb-6">
      {STAGE_ORDER.map((stage, i) => {
        const done    = i <= idx;
        const active  = i === idx;
        const Icon    = STAGE_ICONS[stage] || ClipboardList;
        return (
          <div key={stage} className="flex items-center flex-1 last:flex-none">
            <div className={`flex flex-col items-center`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 transition-all ${
                active  ? "bg-primary-500 border-primary-400 shadow-glow-teal"
                : done  ? "bg-emerald-500/20 border-emerald-500"
                : "bg-white/[0.04] border-slate-700"
              }`}>
                <Icon className={`w-3.5 h-3.5 ${active ? "text-white" : done ? "text-emerald-400" : "text-slate-600"}`} />
              </div>
              <p className={`text-[9px] mt-1 capitalize font-medium ${
                active ? "text-primary-400" : done ? "text-emerald-400" : "text-slate-600"
              }`}>{stage}</p>
            </div>
            {i < STAGE_ORDER.length - 1 && (
              <div className={`h-0.5 flex-1 mx-0.5 rounded-full mb-4 ${i < idx ? "bg-emerald-500/40" : "bg-slate-800"}`} />
            )}
          </div>
        );
      })}
    </div>
  );
}

// ──────────────────────────────────────────────────────────────────────────────
// Detail Drawer
// ──────────────────────────────────────────────────────────────────────────────
function RequestDetailDrawer({ request: initRequest, onClose, isAdmin, adminId, onRefresh }) {
  const [request, setRequest] = useState(initRequest);
  const [logs, setLogs]       = useState([]);
  const [loading, setLoading] = useState(true);

  const loadLogs = (req) => {
    setLoading(true);
    getWorkflowLogs(req.id)
      .then((data) => setLogs(Array.isArray(data) ? data : (data?.logs ?? [])))
      .catch(() => setLogs([]))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    if (!request) return;
    loadLogs(request);
  }, [request?.id]);

  const handleActionDone = async () => {
    // Refresh the parent list and re-fetch this request's latest state
    onRefresh();
    // Re-fetch logs
    loadLogs(request);
  };

  if (!request) return null;
  const prioCfg = PRIORITY_CONFIG[request.priority] || PRIORITY_CONFIG[1];

  return (
    <div className="glass-overlay" onClick={onClose}>
      <div
        className="absolute right-0 top-0 w-full max-w-lg h-full bg-slate-900 border-l border-slate-700/60 overflow-y-auto shadow-2xl"
        style={{ animation: "slideInRight 0.25s ease-out" }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="sticky top-0 bg-slate-900 border-b border-white/[0.06] px-6 pt-5 pb-4 z-10">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-lg font-bold text-white">{request.request_number ?? `REQ #${request.id}`}</h2>
              <p className="text-slate-400 text-sm mt-0.5 capitalize">
                {request.request_type?.replace("_", " ")} · {request.title}
              </p>
            </div>
            <button onClick={onClose}
              className="w-8 h-8 rounded-lg bg-white/[0.05] hover:bg-white/[0.1] flex items-center justify-center text-slate-400 hover:text-white transition-all">
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        <div className="px-6 py-5">
          {/* Stage pipeline */}
          <StagePipeline current={request.current_stage} />

          {/* Meta grid */}
          <div className="grid grid-cols-2 gap-3 mb-5">
            {[
              ["Status",
                <span className={`inline-flex items-center px-2 py-0.5 rounded-lg text-xs font-semibold ${STATUS_CONFIG[request.status] ?? ""}`}>
                  {request.status?.replace("_"," ")}
                </span>
              ],
              ["Priority",
                <span className={`inline-flex items-center gap-1.5 ${prioCfg.color}`}>
                  <span className={`w-1.5 h-1.5 rounded-full ${prioCfg.dot}`} />
                  {PRIORITY_LABEL[request.priority] ?? request.priority}
                </span>
              ],
              ["Created", request.created_at ? new Date(request.created_at).toLocaleString() : "—"],
              ["Assigned", request.assigned_at ? new Date(request.assigned_at).toLocaleString() : "Not assigned"],
            ].map(([label, value]) => (
              <div key={label} className="bg-white/[0.04] rounded-xl p-3 border border-slate-700/40">
                <p className="text-xs text-slate-500 mb-1">{label}</p>
                <div className="text-slate-200 text-sm font-medium">{value}</div>
              </div>
            ))}
          </div>

          {/* Description */}
          {request.description && (
            <div className="bg-white/[0.04] rounded-xl p-4 border border-slate-700/40 mb-5">
              <p className="text-xs text-slate-500 mb-1.5">Description</p>
              <p className="text-slate-300 text-sm leading-relaxed">{request.description}</p>
            </div>
          )}

          {/* Admin action buttons */}
          {isAdmin && (
            <AdminActions
              request={request}
              adminId={adminId}
              onActionDone={handleActionDone}
            />
          )}

          {/* Workflow Timeline */}
          <div className="mt-6">
            <h3 className="text-sm font-semibold text-slate-300 mb-4 flex items-center gap-2">
              <ClipboardList className="w-4 h-4 text-primary-400" /> Workflow Timeline
            </h3>
            {loading ? (
              <div className="space-y-3">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="h-16 rounded-xl bg-white/[0.03] animate-pulse" />
                ))}
              </div>
            ) : logs.length === 0 ? (
              <p className="text-slate-500 text-sm text-center py-8">No workflow activity yet.</p>
            ) : (
              <ol className="relative border-l-2 border-primary-500/20 space-y-4 pl-6 ml-2">
                {logs.map((log, idx) => {
                  const StageIcon = STAGE_ICONS[log.stage] || ClipboardList;
                  return (
                    <li key={log.id ?? idx} className="relative">
                      <span className="absolute -left-[1.85rem] top-1 w-6 h-6 rounded-full bg-primary-500/15 border border-primary-500/30 flex items-center justify-center">
                        <StageIcon className="w-3 h-3 text-primary-400" />
                      </span>
                      <div className="bg-white/[0.04] rounded-xl p-3 border border-slate-700/40">
                        <div className="flex items-start justify-between gap-2">
                          <p className="text-sm font-medium text-slate-200">{log.action}</p>
                          {log.handler_name && (
                            <span className="text-xs text-slate-500 whitespace-nowrap">{log.handler_name}</span>
                          )}
                        </div>
                        {log.notes && <p className="text-xs text-slate-400 mt-1">{log.notes}</p>}
                        <p className="text-xs text-slate-600 mt-1.5">
                          {log.created_at ? new Date(log.created_at).toLocaleString() : ""}
                        </p>
                      </div>
                    </li>
                  );
                })}
              </ol>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// ──────────────────────────────────────────────────────────────────────────────
// Main Page
// ──────────────────────────────────────────────────────────────────────────────
export default function RequestsPage() {
  const { isAdmin, user } = useAuth();
  const [allRequests, setAllRequests] = useState([]);
  const [loading, setLoading]         = useState(true);
  const [search, setSearch]           = useState("");
  const [typeFilter, setTypeFilter]   = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");
  const [page, setPage]               = useState(1);
  const [selected, setSelected]       = useState(null);
  const [showNewModal, setShowNewModal] = useState(false);
  const PAGE_SIZE = 20;

  const fetchRequests = () => {
    setLoading(true);
    getRequests({ limit: 1000 })
      .then((data) => setAllRequests(Array.isArray(data) ? data : (data?.items ?? [])))
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchRequests(); }, []);

  const filtered = allRequests.filter((r) => {
    if (typeFilter !== "all" && r.request_type !== typeFilter) return false;
    if (statusFilter !== "all" && r.status !== statusFilter) return false;
    if (search && !r.title?.toLowerCase().includes(search.toLowerCase()) && !String(r.id).includes(search)) return false;
    return true;
  });

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const paginated  = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);
  const reset      = () => setPage(1);

  const handleCreated = () => { fetchRequests(); setShowNewModal(false); };

  const handleActionDone = () => {
    fetchRequests();
    // Update the selected request in the drawer too
    if (selected) {
      getRequests({ limit: 1000 }).then((data) => {
        const list = Array.isArray(data) ? data : (data?.items ?? []);
        const updated = list.find((r) => r.id === selected.id);
        if (updated) setSelected(updated);
      }).catch(() => {});
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-start justify-between flex-wrap gap-4">
        <div className="page-header">
          <div className="flex items-center gap-3 mb-1">
            <div className="w-10 h-10 rounded-xl bg-primary-500/15 flex items-center justify-center">
              <FileText className="w-5 h-5 text-primary-400" />
            </div>
            <div>
              <h1>{isAdmin ? "Service Requests" : "My Requests"}</h1>
              <p>
                {filtered.length} of {allRequests.length} request{allRequests.length !== 1 ? "s" : ""}
                <span className="text-slate-600 ml-2">· click a row for details</span>
              </p>
            </div>
          </div>
        </div>

        {!isAdmin && (
          <button onClick={() => setShowNewModal(true)} className="btn-primary">
            <Plus className="w-4 h-4" /> New Request
          </button>
        )}
      </div>

      {/* Filters */}
      <div className="card">
        <div className="flex flex-wrap gap-4 items-end">
          <div className="flex-1 min-w-[200px]">
            <label className="label">Search</label>
            <div className="relative">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input type="text" value={search}
                onChange={(e) => { setSearch(e.target.value); reset(); }}
                className="input-field pl-10" placeholder="Search by title or ID…" />
            </div>
          </div>
          <div>
            <label className="label flex items-center gap-1.5"><Filter className="w-3 h-3" /> Type</label>
            <select value={typeFilter} onChange={(e) => { setTypeFilter(e.target.value); reset(); }} className="input-field">
              {REQUEST_TYPES.map((t) => (
                <option key={t} value={t}>{t === "all" ? "All Types" : t.replace("_", " ")}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="label flex items-center gap-1.5"><Filter className="w-3 h-3" /> Status</label>
            <select value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); reset(); }} className="input-field">
              {STATUSES.map((s) => (
                <option key={s} value={s}>{s === "all" ? "All Statuses" : s.replace("_"," ")}</option>
              ))}
            </select>
          </div>
          <button onClick={() => { setSearch(""); setTypeFilter("all"); setStatusFilter("all"); reset(); }} className="btn-secondary">
            <RotateCcw className="w-4 h-4" /> Reset
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="card">
        <RequestTable requests={paginated} loading={loading} onRowClick={setSelected} />
        {totalPages > 1 && (
          <div className="flex items-center justify-between mt-5 pt-5 border-t border-white/[0.06]">
            <p className="text-sm text-slate-500">Page {page} of {totalPages}</p>
            <div className="flex gap-2">
              <button onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1} className="btn-secondary text-sm px-3 py-1.5">
                <ChevronLeft className="w-4 h-4" /> Prev
              </button>
              <button onClick={() => setPage((p) => Math.min(totalPages, p + 1))} disabled={page === totalPages} className="btn-secondary text-sm px-3 py-1.5">
                Next <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Detail drawer */}
      {selected && (
        <RequestDetailDrawer
          request={selected}
          onClose={() => setSelected(null)}
          isAdmin={isAdmin}
          adminId={user?.id}
          onRefresh={handleActionDone}
        />
      )}

      {/* New request modal */}
      {showNewModal && (
        <NewRequestModal
          onClose={() => setShowNewModal(false)}
          onCreated={handleCreated}
        />
      )}
    </div>
  );
}
