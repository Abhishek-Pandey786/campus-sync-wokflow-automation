import { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { getRequests } from "../api/requests";
import { SkeletonCard } from "../components/LoadingSpinner";
import {
  BarChart3,
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  InboxIcon,
} from "lucide-react";

const COLORS = ["#0d9488", "#f59e0b", "#10b981", "#06b6d4", "#8b5cf6", "#ec4899"];

const tooltipStyle = {
  backgroundColor: "#0f172a",
  border: "1px solid rgba(13,148,136,0.3)",
  borderRadius: 10,
  color: "#f1f5f9",
  fontSize: 13,
};

const axisStyle = { fill: "#64748b", fontSize: 11 };
const gridStyle = { strokeDasharray: "3 3", stroke: "rgba(255,255,255,0.05)" };
const axisBorder = { stroke: "rgba(255,255,255,0.08)" };

/** Shown inside a chart card when there's no data yet */
function EmptyChart({ height = 260 }) {
  return (
    <div
      className="flex flex-col items-center justify-center gap-2 text-slate-600"
      style={{ height }}
    >
      <InboxIcon className="w-8 h-8 opacity-40" />
      <p className="text-sm">No data yet — seed requests to see charts</p>
    </div>
  );
}

export default function AnalyticsPage() {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadData = () => {
    setLoading(true);
    setError(null);
    getRequests({ limit: 1000 })
      .then((data) =>
        setRequests(Array.isArray(data) ? data : (data?.items ?? []))
      )
      .catch((e) => {
        setError(
          e?.friendlyMessage ||
          e?.response?.data?.detail ||
          'Failed to load analytics data. Is the backend running?'
        );
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => { loadData(); }, []);

  if (loading) {
    return (
      <div className="space-y-6 animate-fade-in">
        <div className="page-header">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-primary-500/15 flex items-center justify-center">
              <BarChart3 className="w-5 h-5 text-primary-400" />
            </div>
            <h1>Analytics</h1>
          </div>
        </div>
        <SkeletonCard count={4} height="h-20" />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="card animate-pulse h-72" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6 animate-fade-in">
        <div className="page-header">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-primary-500/15 flex items-center justify-center">
              <BarChart3 className="w-5 h-5 text-primary-400" />
            </div>
            <h1>Analytics</h1>
          </div>
        </div>
        <div className="card border border-red-500/25 bg-red-500/[0.05] flex flex-col items-center gap-4 py-12">
          <AlertTriangle className="w-10 h-10 text-red-400" />
          <div className="text-center">
            <p className="text-red-300 font-medium mb-1">Failed to load analytics data</p>
            <p className="text-slate-400 text-sm">{error}</p>
          </div>
          <button
            onClick={loadData}
            className="btn-primary px-6 py-2 rounded-lg text-sm"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const total = requests.length;
  const delayed = requests.filter((r) => r.is_delayed).length;

  // Data sets
  const byType = Object.entries(
    requests.reduce((acc, r) => {
      acc[r.request_type] = (acc[r.request_type] ?? 0) + 1;
      return acc;
    }, {})
  ).map(([name, value]) => ({ name: name.replace("_", " "), value }));

  const delayByType = Object.entries(
    requests.reduce((acc, r) => {
      if (!acc[r.request_type]) acc[r.request_type] = { total: 0, delayed: 0 };
      acc[r.request_type].total++;
      if (r.is_delayed) acc[r.request_type].delayed++;
      return acc;
    }, {})
  ).map(([name, { total, delayed }]) => ({
    name: name.replace("_", " "),
    rate: total ? +((delayed / total) * 100).toFixed(1) : 0,
  }));

  const byPriority = [
    { name: "High (3)", ...countDelayed(requests.filter((r) => r.priority === 3)) },
    { name: "Medium (2)", ...countDelayed(requests.filter((r) => r.priority === 2)) },
    { name: "Low (1)", ...countDelayed(requests.filter((r) => r.priority === 1)) },
  ];

  const statusData = Object.entries(
    requests.reduce((acc, r) => {
      acc[r.status] = (acc[r.status] ?? 0) + 1;
      return acc;
    }, {})
  ).map(([name, value]) => ({ name, value }));

  const summaryCards = [
    { label: "Total",      value: total,            color: "text-primary-400", icon: BarChart3,    iconBg: "bg-primary-500/15" },
    { label: "Delayed",    value: delayed,           color: "text-red-400",     icon: AlertTriangle, iconBg: "bg-red-500/15" },
    { label: "Delay Rate", value: `${total ? ((delayed / total) * 100).toFixed(1) : 0}%`, color: "text-accent-400", icon: TrendingUp, iconBg: "bg-accent-500/15" },
    { label: "On-Time",    value: total - delayed,   color: "text-emerald-400", icon: CheckCircle2, iconBg: "bg-emerald-500/15" },
  ];

  const hasData = total > 0;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="page-header">
        <div className="flex items-center gap-3 mb-1">
          <div className="w-10 h-10 rounded-xl bg-primary-500/15 flex items-center justify-center">
            <BarChart3 className="w-5 h-5 text-primary-400" />
          </div>
          <div>
            <h1>Analytics</h1>
            <p>Based on {total} service request{total !== 1 ? "s" : ""}</p>
          </div>
        </div>
      </div>

      {/* Summary badges */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {summaryCards.map(({ label, value, color, icon: Icon, iconBg }, idx) => (
          <div
            key={label}
            className="card text-center py-5 opacity-0 animate-fade-in"
            style={{ animationDelay: `${idx * 100}ms` }}
          >
            <div className={`w-9 h-9 rounded-xl ${iconBg} flex items-center justify-center mx-auto mb-3`}>
              <Icon className={`w-4 h-4 ${color}`} />
            </div>
            <p className="text-xs text-slate-500 font-medium mb-1">{label}</p>
            <p className={`text-2xl font-bold ${color}`}>{value}</p>
          </div>
        ))}
      </div>

      {/* Charts grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* Requests by Type */}
        <div className="card">
          <h2 className="text-base font-semibold text-white mb-4">Requests by Type</h2>
          {!hasData ? <EmptyChart /> : (
            <ResponsiveContainer width="100%" height={260}>
              <BarChart
                data={byType}
                margin={{ top: 4, right: 10, left: -20, bottom: 0 }}
                style={{ background: "transparent" }}
              >
                <CartesianGrid {...gridStyle} />
                <XAxis dataKey="name" tick={axisStyle} axisLine={axisBorder} tickLine={false} />
                <YAxis tick={axisStyle} axisLine={axisBorder} tickLine={false} />
                <Tooltip contentStyle={tooltipStyle} cursor={{ fill: "rgba(13,148,136,0.06)" }} />
                <Bar dataKey="value" fill="#0d9488" radius={[6, 6, 0, 0]} maxBarSize={50} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Delay Rate by Type */}
        <div className="card">
          <h2 className="text-base font-semibold text-white mb-4">Delay Rate by Type (%)</h2>
          {!hasData ? <EmptyChart /> : (
            <ResponsiveContainer width="100%" height={260}>
              <BarChart
                data={delayByType}
                margin={{ top: 4, right: 10, left: -20, bottom: 0 }}
                style={{ background: "transparent" }}
              >
                <CartesianGrid {...gridStyle} />
                <XAxis dataKey="name" tick={axisStyle} axisLine={axisBorder} tickLine={false} />
                <YAxis tick={axisStyle} unit="%" axisLine={axisBorder} tickLine={false} />
                <Tooltip contentStyle={tooltipStyle} formatter={(v) => `${v}%`} cursor={{ fill: "rgba(245,158,11,0.06)" }} />
                <Bar dataKey="rate" fill="#f59e0b" radius={[6, 6, 0, 0]} maxBarSize={50} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Status Distribution */}
        <div className="card">
          <h2 className="text-base font-semibold text-white mb-4">Status Distribution</h2>
          {!hasData || statusData.length === 0 ? <EmptyChart /> : (
            <ResponsiveContainer width="100%" height={260}>
              <PieChart style={{ background: "transparent" }}>
                <Pie
                  data={statusData}
                  cx="50%"
                  cy="50%"
                  outerRadius={90}
                  innerRadius={52}
                  dataKey="value"
                  strokeWidth={2}
                  stroke="transparent"
                  label={({ name, percent }) =>
                    `${name} ${(percent * 100).toFixed(0)}%`
                  }
                  labelLine={{ stroke: "#475569", strokeWidth: 1 }}
                >
                  {statusData.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={tooltipStyle} />
                <Legend
                  wrapperStyle={{ color: "#94a3b8", fontSize: 12, paddingTop: 8 }}
                />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Delay by Priority Level */}
        <div className="card">
          <h2 className="text-base font-semibold text-white mb-4">Delay by Priority Level</h2>
          {!hasData ? <EmptyChart /> : (
            <ResponsiveContainer width="100%" height={260}>
              <BarChart
                data={byPriority}
                margin={{ top: 4, right: 10, left: -20, bottom: 0 }}
                style={{ background: "transparent" }}
              >
                <CartesianGrid {...gridStyle} />
                <XAxis dataKey="name" tick={axisStyle} axisLine={axisBorder} tickLine={false} />
                <YAxis tick={axisStyle} axisLine={axisBorder} tickLine={false} />
                <Tooltip contentStyle={tooltipStyle} cursor={{ fill: "rgba(255,255,255,0.03)" }} />
                <Bar dataKey="onTime"  fill="#10b981" stackId="a" name="On-Time" radius={[0, 0, 0, 0]} maxBarSize={50} />
                <Bar dataKey="delayed" fill="#ef4444" stackId="a" name="Delayed" radius={[6, 6, 0, 0]} maxBarSize={50} />
                <Legend wrapperStyle={{ color: "#94a3b8", fontSize: 12 }} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

      </div>
    </div>
  );
}

function countDelayed(arr) {
  const delayed = arr.filter((r) => r.is_delayed).length;
  return { onTime: arr.length - delayed, delayed };
}
