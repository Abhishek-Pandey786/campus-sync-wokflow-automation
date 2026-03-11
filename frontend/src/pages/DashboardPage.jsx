import { useEffect, useState } from "react";
import StatsCard from "../components/StatsCard";
import { SkeletonCard } from "../components/LoadingSpinner";
import { getRequests } from "../api/requests";
import { getModelInfo } from "../api/predictions";
import client from "../api/client";
import {
  Activity,
  Cpu,
  Layers,
  CheckCircle2,
  XCircle,
} from "lucide-react";

export default function DashboardPage() {
  const [requests, setRequests] = useState([]);
  const [modelInfo, setModelInfo] = useState(null);
  const [apiOnline, setApiOnline] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const [reqs, model, health] = await Promise.allSettled([
          getRequests({ limit: 1000 }),
          getModelInfo(),
          client.get("/health"),
        ]);

        if (reqs.status === "fulfilled") {
          const data = Array.isArray(reqs.value)
            ? reqs.value
            : (reqs.value?.items ?? []);
          setRequests(data);
        }
        if (model.status === "fulfilled") setModelInfo(model.value);
        if (health.status === "fulfilled") setApiOnline(true);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const total = requests.length;
  const delayed = requests.filter((r) => r.is_delayed).length;
  const delayPct = total ? ((delayed / total) * 100).toFixed(1) : "0.0";
  const pending = requests.filter((r) => r.status === "pending").length;
  const completed = requests.filter((r) => r.status === "completed").length;

  // Request type breakdown
  const typeCounts = requests.reduce((acc, r) => {
    acc[r.request_type] = (acc[r.request_type] ?? 0) + 1;
    return acc;
  }, {});

  const typeColors = [
    "from-primary-500 to-primary-600",
    "from-violet-500 to-violet-600",
    "from-emerald-500 to-emerald-600",
    "from-amber-500 to-amber-600",
    "from-cyan-500 to-cyan-600",
    "from-rose-500 to-rose-600",
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="page-header">
        <div className="flex items-center gap-3 mb-1">
          <div className="w-10 h-10 rounded-xl bg-primary-500/15 flex items-center justify-center">
            <Layers className="w-5 h-5 text-primary-400" />
          </div>
          <div>
            <h1>Dashboard</h1>
            <p>ML-Powered Service Request Management</p>
          </div>
        </div>
      </div>

      {/* Status bar */}
      <div className="flex items-center gap-4 flex-wrap">
        <div className="flex items-center gap-2 text-sm">
          <span
            className={`w-2 h-2 rounded-full ${
              apiOnline ? "bg-emerald-400 animate-pulse" : "bg-red-400"
            }`}
          />
          <span className="text-slate-400">
            API {apiOnline ? "Online" : "Offline"}
          </span>
        </div>
        {modelInfo && (
          <div className="flex items-center gap-2 text-sm text-slate-500">
            <Cpu className="w-3.5 h-3.5" />
            <span>
              {modelInfo.model_type ?? "Logistic Regression"} model loaded
            </span>
          </div>
        )}
      </div>

      {/* Stats grid */}
      {loading ? (
        <SkeletonCard count={4} />
      ) : (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <StatsCard
            title="Total Requests"
            value={total}
            icon="📋"
            color="blue"
            subtitle="All time"
          />
          <StatsCard
            title="Delayed Rate"
            value={`${delayPct}%`}
            icon="⚠️"
            color="yellow"
            subtitle={`${delayed} of ${total}`}
          />
          <StatsCard
            title="Pending"
            value={pending}
            icon="⏳"
            color="purple"
            subtitle="Awaiting action"
          />
          <StatsCard
            title="Completed"
            value={completed}
            icon="✅"
            color="green"
            subtitle="Successfully resolved"
          />
        </div>
      )}

      {/* Model info + breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* ML Model card */}
        <div className="card">
          <div className="flex items-center gap-3 mb-5">
            <div className="w-9 h-9 rounded-xl bg-violet-500/15 flex items-center justify-center">
              <Cpu className="w-4.5 h-4.5 text-violet-400" />
            </div>
            <h2 className="text-lg font-semibold text-white">
              ML Model Status
            </h2>
          </div>
          <div className="space-y-3.5">
            <Row
              label="Model"
              value={modelInfo?.model_type ?? "Logistic Regression"}
            />
            <Row label="Accuracy" value="98.68%" highlight="green" />
            <Row label="F1 Score" value="97.56%" highlight="green" />
            <Row
              label="Features"
              value={modelInfo?.feature_count ?? 19}
            />
            <Row
              label="Status"
              value={
                modelInfo?.model_loaded ? (
                  <span className="inline-flex items-center gap-1.5 text-emerald-400">
                    <CheckCircle2 className="w-4 h-4" /> Loaded
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1.5 text-red-400">
                    <XCircle className="w-4 h-4" /> Not loaded
                  </span>
                )
              }
            />
          </div>
        </div>

        {/* Request type breakdown */}
        <div className="card">
          <div className="flex items-center gap-3 mb-5">
            <div className="w-9 h-9 rounded-xl bg-primary-500/15 flex items-center justify-center">
              <Activity className="w-4.5 h-4.5 text-primary-400" />
            </div>
            <h2 className="text-lg font-semibold text-white">
              Request Types
            </h2>
          </div>
          <div className="space-y-3">
            {Object.entries(typeCounts)
              .sort((a, b) => b[1] - a[1])
              .map(([type, count], idx) => {
                const pct = total
                  ? Math.round((count / total) * 100)
                  : 0;
                return (
                  <div key={type} className="group">
                    <div className="flex items-center justify-between text-sm mb-1.5">
                      <span className="capitalize text-slate-300 font-medium">
                        {type.replace("_", " ")}
                      </span>
                      <span className="text-slate-500 text-xs">
                        {count} ({pct}%)
                      </span>
                    </div>
                    <div className="w-full bg-white/[0.06] rounded-full h-2">
                      <div
                        className={`bg-gradient-to-r ${
                          typeColors[idx % typeColors.length]
                        } h-2 rounded-full transition-all duration-700`}
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                );
              })}
          </div>
        </div>
      </div>
    </div>
  );
}

function Row({ label, value, highlight }) {
  return (
    <div className="flex justify-between items-center py-1.5 border-b border-white/[0.04] last:border-0">
      <span className="text-slate-400 text-sm">{label}</span>
      <span
        className={`font-medium text-sm ${
          highlight === "green" ? "text-emerald-400" : "text-slate-200"
        }`}
      >
        {value}
      </span>
    </div>
  );
}
