import { useEffect, useState } from "react";
import RequestTable from "../components/RequestTable";
import { getRequests } from "../api/requests";
import { getWorkflowLogs } from "../api/workflows";
import {
  FileText,
  Search,
  Filter,
  RotateCcw,
  X,
  ChevronLeft,
  ChevronRight,
  ClipboardList,
  UserCheck,
  ShieldCheck,
  ThumbsUp,
  Cog,
  PartyPopper,
} from "lucide-react";

const REQUEST_TYPES = [
  "all",
  "certificate",
  "hostel",
  "it_support",
  "library",
  "exam",
  "transcript",
];
const STATUSES = ["all", "pending", "processing", "completed", "rejected"];

const STAGE_ICONS = {
  created: ClipboardList,
  assigned: UserCheck,
  verified: ShieldCheck,
  approved: ThumbsUp,
  processed: Cog,
  completed: PartyPopper,
};

const PRIORITY_LABEL = { 1: "Low", 2: "Medium", 3: "High" };
const PRIORITY_CONFIG = {
  1: { color: "text-slate-400", dot: "bg-slate-400" },
  2: { color: "text-amber-400", dot: "bg-amber-400" },
  3: { color: "text-red-400", dot: "bg-red-400" },
};

function RequestDetailModal({ request, onClose }) {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!request) return;
    setLoading(true);
    getWorkflowLogs(request.id)
      .then((data) =>
        setLogs(Array.isArray(data) ? data : (data?.logs ?? []))
      )
      .catch(() => setLogs([]))
      .finally(() => setLoading(false));
  }, [request?.id]);

  if (!request) return null;

  const prioCfg = PRIORITY_CONFIG[request.priority] || PRIORITY_CONFIG[1];

  return (
    <div className="glass-overlay" onClick={onClose}>
      <div
        className="absolute right-0 top-0 w-full max-w-lg h-full bg-slate-950/95 backdrop-blur-2xl border-l border-white/[0.06] overflow-y-auto p-6 shadow-2xl animate-slide-in-right"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-start justify-between mb-6">
          <div>
            <h2 className="text-lg font-bold text-white">
              {request.request_number ?? `#${request.id}`}
            </h2>
            <p className="text-slate-400 text-sm mt-0.5 capitalize">
              {request.request_type?.replace("_", " ")} · {request.title}
            </p>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-lg bg-white/[0.05] hover:bg-white/[0.1] flex items-center justify-center text-slate-400 hover:text-white transition-all"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Meta */}
        <div className="grid grid-cols-2 gap-3 mb-6">
          {[
            [
              "Status",
              <span className="capitalize">{request.status}</span>,
            ],
            [
              "Priority",
              <span
                className={`inline-flex items-center gap-1.5 ${prioCfg.color}`}
              >
                <span
                  className={`w-1.5 h-1.5 rounded-full ${prioCfg.dot}`}
                />
                {PRIORITY_LABEL[request.priority] ?? request.priority}
              </span>,
            ],
            [
              "Stage",
              <span className="capitalize">{request.current_stage}</span>,
            ],
            [
              "Created",
              request.created_at
                ? new Date(request.created_at).toLocaleString()
                : "—",
            ],
          ].map(([label, value]) => (
            <div
              key={label}
              className="bg-white/[0.04] rounded-xl p-3 border border-white/[0.04]"
            >
              <p className="text-xs text-slate-500 mb-1">{label}</p>
              <p className="text-slate-200 text-sm font-medium">{value}</p>
            </div>
          ))}
        </div>

        {/* Timeline */}
        <div>
          <h3 className="text-sm font-semibold text-slate-300 mb-4 flex items-center gap-2">
            <ClipboardList className="w-4 h-4 text-primary-400" />
            Workflow Timeline
          </h3>
          {loading ? (
            <div className="space-y-3">
              {[...Array(3)].map((_, i) => (
                <div
                  key={i}
                  className="h-16 rounded-xl bg-white/[0.03] animate-pulse"
                />
              ))}
            </div>
          ) : logs.length === 0 ? (
            <p className="text-slate-500 text-sm text-center py-8">
              No workflow activity yet.
            </p>
          ) : (
            <ol className="relative border-l-2 border-white/[0.06] space-y-4 pl-6 ml-2">
              {logs.map((log, idx) => {
                const StageIcon = STAGE_ICONS[log.stage] || ClipboardList;
                return (
                  <li key={log.id ?? idx} className="relative">
                    <span className="absolute -left-[1.85rem] top-1 w-6 h-6 rounded-full bg-primary-500/15 border border-primary-500/30 flex items-center justify-center">
                      <StageIcon className="w-3 h-3 text-primary-400" />
                    </span>
                    <div className="bg-white/[0.04] rounded-xl p-3 border border-white/[0.04]">
                      <p className="text-sm font-medium text-slate-200">
                        {log.action}
                      </p>
                      {log.notes && (
                        <p className="text-xs text-slate-400 mt-1">
                          {log.notes}
                        </p>
                      )}
                      <p className="text-xs text-slate-500 mt-1.5">
                        {log.created_at
                          ? new Date(log.created_at).toLocaleString()
                          : ""}
                        {log.handler_workload != null
                          ? ` · Workload: ${log.handler_workload}`
                          : ""}
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
  );
}

export default function RequestsPage() {
  const [allRequests, setAllRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");
  const [page, setPage] = useState(1);
  const [selected, setSelected] = useState(null);
  const PAGE_SIZE = 20;

  useEffect(() => {
    getRequests({ limit: 1000 })
      .then((data) =>
        setAllRequests(Array.isArray(data) ? data : (data?.items ?? []))
      )
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const filtered = allRequests.filter((r) => {
    if (typeFilter !== "all" && r.request_type !== typeFilter) return false;
    if (statusFilter !== "all" && r.status !== statusFilter) return false;
    if (
      search &&
      !r.title?.toLowerCase().includes(search.toLowerCase()) &&
      !String(r.id).includes(search)
    )
      return false;
    return true;
  });

  const totalPages = Math.ceil(filtered.length / PAGE_SIZE);
  const paginated = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  const reset = () => setPage(1);

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="page-header">
        <div className="flex items-center gap-3 mb-1">
          <div className="w-10 h-10 rounded-xl bg-primary-500/15 flex items-center justify-center">
            <FileText className="w-5 h-5 text-primary-400" />
          </div>
          <div>
            <h1>Service Requests</h1>
            <p>
              {filtered.length} of {allRequests.length} requests
              <span className="text-slate-600 ml-2">· click a row for details</span>
            </p>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="flex flex-wrap gap-4 items-end">
          <div className="flex-1 min-w-[200px]">
            <label className="label">Search</label>
            <div className="relative">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input
                type="text"
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value);
                  reset();
                }}
                className="input-field pl-10"
                placeholder="Search by title or ID…"
              />
            </div>
          </div>
          <div>
            <label className="label flex items-center gap-1.5">
              <Filter className="w-3 h-3" /> Type
            </label>
            <select
              value={typeFilter}
              onChange={(e) => {
                setTypeFilter(e.target.value);
                reset();
              }}
              className="input-field"
            >
              {REQUEST_TYPES.map((t) => (
                <option key={t} value={t}>
                  {t === "all" ? "All Types" : t.replace("_", " ")}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="label flex items-center gap-1.5">
              <Filter className="w-3 h-3" /> Status
            </label>
            <select
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value);
                reset();
              }}
              className="input-field"
            >
              {STATUSES.map((s) => (
                <option key={s} value={s}>
                  {s === "all" ? "All Statuses" : s}
                </option>
              ))}
            </select>
          </div>
          <button
            onClick={() => {
              setSearch("");
              setTypeFilter("all");
              setStatusFilter("all");
              reset();
            }}
            className="btn-secondary"
          >
            <RotateCcw className="w-4 h-4" />
            Reset
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="card">
        <RequestTable
          requests={paginated}
          loading={loading}
          onRowClick={setSelected}
        />

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between mt-5 pt-5 border-t border-white/[0.06]">
            <p className="text-sm text-slate-500">
              Page {page} of {totalPages}
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="btn-secondary text-sm px-3 py-1.5"
              >
                <ChevronLeft className="w-4 h-4" />
                Prev
              </button>
              <button
                onClick={() =>
                  setPage((p) => Math.min(totalPages, p + 1))
                }
                disabled={page === totalPages}
                className="btn-secondary text-sm px-3 py-1.5"
              >
                Next
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Detail modal / drawer */}
      {selected && (
        <RequestDetailModal
          request={selected}
          onClose={() => setSelected(null)}
        />
      )}
    </div>
  );
}
