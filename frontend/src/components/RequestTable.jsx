import {
  AlertCircle,
  ArrowUpRight,
  Clock,
  CheckCircle2,
  XCircle,
} from "lucide-react";

const STATUS_CONFIG = {
  pending: {
    class: "badge-yellow",
    icon: Clock,
  },
  processing: {
    class: "badge-blue",
    icon: ArrowUpRight,
  },
  completed: {
    class: "badge-green",
    icon: CheckCircle2,
  },
  rejected: {
    class: "badge-red",
    icon: XCircle,
  },
  cancelled: {
    class: "badge-red",
    icon: XCircle,
  },
};

const PRIORITY_LABEL = { 1: "Low", 2: "Medium", 3: "High" };
const PRIORITY_CONFIG = {
  1: { color: "text-slate-400", bg: "bg-slate-500/10", dot: "bg-slate-400" },
  2: { color: "text-amber-400", bg: "bg-amber-500/10", dot: "bg-amber-400" },
  3: { color: "text-red-400", bg: "bg-red-500/10", dot: "bg-red-400" },
};

export default function RequestTable({ requests, loading, onRowClick }) {
  if (loading) {
    return (
      <div className="space-y-3">
        {[...Array(5)].map((_, i) => (
          <div
            key={i}
            className="h-14 rounded-xl bg-white/[0.08] animate-pulse"
            style={{ animationDelay: `${i * 80}ms` }}
          />
        ))}
      </div>
    );
  }

  if (!requests?.length) {
    return (
      <div className="empty-state text-slate-500">
        <div className="empty-state-icon">
          <AlertCircle className="w-7 h-7 text-primary-500/70" />
        </div>
        <div className="text-center">
          <p className="font-semibold text-slate-300">You're all caught up!</p>
          <p className="text-sm mt-1 text-slate-500">No requests match your current filters.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-white/[0.12]">
            {["ID", "Type", "Title", "Priority", "Status", "Created"].map(
              (h) => (
                <th
                  key={h}
                  className="pb-3 pr-4 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider"
                >
                  {h}
                </th>
              ),
            )}
          </tr>
        </thead>
        <tbody className="divide-y divide-white/[0.08]">
          {requests.map((req) => {
            const statusCfg =
              STATUS_CONFIG[req.status] || STATUS_CONFIG.pending;
            const StatusIcon = statusCfg.icon;
            const prioCfg = PRIORITY_CONFIG[req.priority] || PRIORITY_CONFIG[1];

            return (
              <tr
                key={req.id}
                onClick={() => onRowClick?.(req)}
                className={`table-row-hover ${onRowClick ? "cursor-pointer" : ""}`}
              >
                <td className="py-3.5 pr-4 text-slate-500 font-mono text-xs">
                  #{req.id}
                </td>
                <td className="py-3.5 pr-4 capitalize text-slate-300 font-medium">
                  {req.request_type?.replace("_", " ")}
                </td>
                <td className="py-3.5 pr-4 text-slate-300 max-w-xs truncate">
                  {req.title}
                </td>
                <td className="py-3.5 pr-4">
                  <span
                    className={`inline-flex items-center gap-1.5 text-xs font-medium ${prioCfg.color}`}
                  >
                    <span
                      className={`w-1.5 h-1.5 rounded-full ${prioCfg.dot}`}
                    />
                    {PRIORITY_LABEL[req.priority] ?? req.priority}
                  </span>
                </td>
                <td className="py-3.5 pr-4">
                  <span className={`${statusCfg.class}`}>
                    <StatusIcon className="w-3 h-3" />
                    {req.status}
                  </span>
                </td>
                <td className="py-3.5 pr-4 text-slate-500 text-xs">
                  {req.created_at
                    ? new Date(req.created_at).toLocaleDateString()
                    : "—"}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
