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
import { BarChart3, TrendingUp, AlertTriangle, CheckCircle2 } from "lucide-react";

const COLORS = ["#6366f1", "#8b5cf6", "#10b981", "#f59e0b", "#06b6d4", "#ec4899"];

const chartTooltipStyle = {
  backgroundColor: "rgba(15, 23, 42, 0.95)",
  border: "1px solid rgba(255, 255, 255, 0.08)",
  borderRadius: 12,
  color: "#f1f5f9",
  backdropFilter: "blur(12px)",
};

export default function AnalyticsPage() {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getRequests({ limit: 1000 })
      .then((data) =>
        setRequests(Array.isArray(data) ? data : (data?.items ?? []))
      )
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

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

  // --- Derived data ---
  const total = requests.length;
  const delayed = requests.filter((r) => r.is_delayed).length;

  // Requests by type
  const byType = Object.entries(
    requests.reduce((acc, r) => {
      acc[r.request_type] = (acc[r.request_type] ?? 0) + 1;
      return acc;
    }, {})
  ).map(([name, value]) => ({ name: name.replace("_", " "), value }));

  // Delay rate by type
  const delayByType = Object.entries(
    requests.reduce((acc, r) => {
      if (!acc[r.request_type])
        acc[r.request_type] = { total: 0, delayed: 0 };
      acc[r.request_type].total++;
      if (r.is_delayed) acc[r.request_type].delayed++;
      return acc;
    }, {})
  ).map(([name, { total, delayed }]) => ({
    name: name.replace("_", " "),
    rate: total ? +((delayed / total) * 100).toFixed(1) : 0,
  }));

  // By priority
  const byPriority = [
    {
      name: "High (3)",
      ...countDelayed(requests.filter((r) => r.priority === 3)),
    },
    {
      name: "Medium (2)",
      ...countDelayed(requests.filter((r) => r.priority === 2)),
    },
    {
      name: "Low (1)",
      ...countDelayed(requests.filter((r) => r.priority === 1)),
    },
  ];

  // Status breakdown for pie
  const statusData = Object.entries(
    requests.reduce((acc, r) => {
      acc[r.status] = (acc[r.status] ?? 0) + 1;
      return acc;
    }, {})
  ).map(([name, value]) => ({ name, value }));

  const summaryCards = [
    {
      label: "Total",
      value: total,
      color: "text-primary-400",
      icon: BarChart3,
      iconBg: "bg-primary-500/15",
    },
    {
      label: "Delayed",
      value: delayed,
      color: "text-red-400",
      icon: AlertTriangle,
      iconBg: "bg-red-500/15",
    },
    {
      label: "Delay Rate",
      value: `${total ? ((delayed / total) * 100).toFixed(1) : 0}%`,
      color: "text-amber-400",
      icon: TrendingUp,
      iconBg: "bg-amber-500/15",
    },
    {
      label: "On-Time",
      value: total - delayed,
      color: "text-emerald-400",
      icon: CheckCircle2,
      iconBg: "bg-emerald-500/15",
    },
  ];

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
            <p>Based on {total} service requests</p>
          </div>
        </div>
      </div>

      {/* Summary badges */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {summaryCards.map(
          ({ label, value, color, icon: Icon, iconBg }) => (
            <div key={label} className="card text-center py-5">
              <div
                className={`w-9 h-9 rounded-xl ${iconBg} flex items-center justify-center mx-auto mb-3`}
              >
                <Icon className={`w-4.5 h-4.5 ${color}`} />
              </div>
              <p className="text-xs text-slate-500 font-medium mb-1">
                {label}
              </p>
              <p className={`text-2xl font-bold ${color}`}>{value}</p>
            </div>
          )
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Requests by Type */}
        <div className="card">
          <h2 className="text-base font-semibold text-white mb-4">
            Requests by Type
          </h2>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart
              data={byType}
              margin={{ top: 0, right: 10, left: -20, bottom: 0 }}
            >
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="rgba(255,255,255,0.04)"
              />
              <XAxis
                dataKey="name"
                tick={{ fill: "#64748b", fontSize: 11 }}
                axisLine={{ stroke: "rgba(255,255,255,0.06)" }}
              />
              <YAxis
                tick={{ fill: "#64748b", fontSize: 11 }}
                axisLine={{ stroke: "rgba(255,255,255,0.06)" }}
              />
              <Tooltip contentStyle={chartTooltipStyle} />
              <Bar dataKey="value" fill="#6366f1" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Delay Rate by Type */}
        <div className="card">
          <h2 className="text-base font-semibold text-white mb-4">
            Delay Rate by Type (%)
          </h2>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart
              data={delayByType}
              margin={{ top: 0, right: 10, left: -20, bottom: 0 }}
            >
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="rgba(255,255,255,0.04)"
              />
              <XAxis
                dataKey="name"
                tick={{ fill: "#64748b", fontSize: 11 }}
                axisLine={{ stroke: "rgba(255,255,255,0.06)" }}
              />
              <YAxis
                tick={{ fill: "#64748b", fontSize: 11 }}
                unit="%"
                axisLine={{ stroke: "rgba(255,255,255,0.06)" }}
              />
              <Tooltip
                contentStyle={chartTooltipStyle}
                formatter={(v) => `${v}%`}
              />
              <Bar dataKey="rate" fill="#f59e0b" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Status Pie */}
        <div className="card">
          <h2 className="text-base font-semibold text-white mb-4">
            Status Distribution
          </h2>
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie
                data={statusData}
                cx="50%"
                cy="50%"
                outerRadius={90}
                innerRadius={50}
                dataKey="value"
                strokeWidth={0}
                label={({ name, percent }) =>
                  `${name} ${(percent * 100).toFixed(0)}%`
                }
                labelLine={{ stroke: "#475569" }}
              >
                {statusData.map((_, i) => (
                  <Cell
                    key={i}
                    fill={COLORS[i % COLORS.length]}
                  />
                ))}
              </Pie>
              <Tooltip contentStyle={chartTooltipStyle} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Delay by Priority */}
        <div className="card">
          <h2 className="text-base font-semibold text-white mb-4">
            Delay by Priority Level
          </h2>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart
              data={byPriority}
              margin={{ top: 0, right: 10, left: -20, bottom: 0 }}
            >
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="rgba(255,255,255,0.04)"
              />
              <XAxis
                dataKey="name"
                tick={{ fill: "#64748b", fontSize: 11 }}
                axisLine={{ stroke: "rgba(255,255,255,0.06)" }}
              />
              <YAxis
                tick={{ fill: "#64748b", fontSize: 11 }}
                axisLine={{ stroke: "rgba(255,255,255,0.06)" }}
              />
              <Tooltip contentStyle={chartTooltipStyle} />
              <Bar
                dataKey="onTime"
                fill="#10b981"
                stackId="a"
                name="On-Time"
                radius={[0, 0, 0, 0]}
              />
              <Bar
                dataKey="delayed"
                fill="#ef4444"
                stackId="a"
                name="Delayed"
                radius={[6, 6, 0, 0]}
              />
              <Legend
                wrapperStyle={{ color: "#94a3b8", fontSize: 12 }}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

function countDelayed(arr) {
  const delayed = arr.filter((r) => r.is_delayed).length;
  return { onTime: arr.length - delayed, delayed };
}
