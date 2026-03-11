import { useEffect, useState, useCallback } from "react";
import { getAlerts, triggerScan, escalateRequest } from "../api/alerts";
import { useAuth } from "../context/AuthContext";
import {
  AlertTriangle,
  AlertOctagon,
  AlertCircle,
  CheckCircle2,
  ShieldAlert,
  Search,
  Rocket,
  Loader2,
  Timer,
  Ban,
} from "lucide-react";

const URGENCY_CONFIG = {
  critical: {
    label: "CRITICAL",
    bg: "bg-red-500/[0.08]",
    border: "border-red-500/25",
    badge: "bg-red-500",
    icon: AlertOctagon,
    iconColor: "text-red-400",
    iconBg: "bg-red-500/15",
    pulse: true,
  },
  high: {
    label: "HIGH",
    bg: "bg-orange-500/[0.06]",
    border: "border-orange-500/20",
    badge: "bg-orange-500",
    icon: AlertTriangle,
    iconColor: "text-orange-400",
    iconBg: "bg-orange-500/15",
    pulse: false,
  },
  medium: {
    label: "MEDIUM",
    bg: "bg-amber-500/[0.05]",
    border: "border-amber-500/15",
    badge: "bg-amber-500",
    icon: AlertCircle,
    iconColor: "text-amber-400",
    iconBg: "bg-amber-500/15",
    pulse: false,
  },
  low: {
    label: "LOW",
    bg: "bg-emerald-500/[0.05]",
    border: "border-emerald-500/15",
    badge: "bg-emerald-500",
    icon: CheckCircle2,
    iconColor: "text-emerald-400",
    iconBg: "bg-emerald-500/15",
    pulse: false,
  },
};

function SlaCountdown({ hours }) {
  if (hours === null || hours === undefined)
    return <span className="text-slate-500">—</span>;
  if (hours <= 0)
    return (
      <span className="inline-flex items-center gap-1.5 text-red-400 font-bold text-sm">
        <Ban className="w-3.5 h-3.5" />
        Breached {Math.abs(hours).toFixed(1)}h ago
      </span>
    );
  return (
    <span
      className={`inline-flex items-center gap-1.5 text-sm font-medium ${
        hours < 6
          ? "text-red-400"
          : hours < 24
            ? "text-orange-400"
            : "text-slate-300"
      }`}
    >
      <Timer className="w-3.5 h-3.5" />
      {hours.toFixed(1)}h left
    </span>
  );
}

function RiskBar({ score }) {
  const pct = Math.round(score * 100);
  const colour =
    pct >= 80
      ? "from-red-500 to-red-600"
      : pct >= 60
        ? "from-orange-400 to-orange-500"
        : "from-amber-400 to-amber-500";
  return (
    <div className="flex items-center gap-2.5">
      <div className="flex-1 bg-white/[0.06] rounded-full h-2 overflow-hidden">
        <div
          className={`bg-gradient-to-r ${colour} h-2 rounded-full transition-all duration-700`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-xs font-mono text-slate-400 w-10 text-right">
        {pct}%
      </span>
    </div>
  );
}

export default function AlertsPage() {
  const { user } = useAuth();
  const isAdmin = user?.role === "admin";

  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);
  const [scanResult, setScanResult] = useState(null);
  const [escalating, setEscalating] = useState(null);
  const [notesMap, setNotesMap] = useState({});
  const [error, setError] = useState(null);

  const fetchAlerts = useCallback(() => {
    setLoading(true);
    setError(null);
    getAlerts()
      .then((data) => setAlerts(Array.isArray(data) ? data : []))
      .catch((e) =>
        setError(e?.response?.data?.detail || "Failed to load alerts")
      )
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    fetchAlerts();
  }, [fetchAlerts]);

  const handleScan = async () => {
    setScanning(true);
    setScanResult(null);
    try {
      const result = await triggerScan();
      setScanResult(result);
      fetchAlerts();
    } catch (e) {
      setError(e?.response?.data?.detail || "Scan failed");
    } finally {
      setScanning(false);
    }
  };

  const handleEscalate = async (requestId) => {
    setEscalating(requestId);
    try {
      await escalateRequest(requestId, notesMap[requestId] || "");
      fetchAlerts();
    } catch (e) {
      setError(e?.response?.data?.detail || "Escalation failed");
    } finally {
      setEscalating(null);
    }
  };

  const countByUrgency = alerts.reduce((acc, a) => {
    acc[a.urgency] = (acc[a.urgency] || 0) + 1;
    return acc;
  }, {});

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-start justify-between flex-wrap gap-4">
        <div className="page-header">
          <div className="flex items-center gap-3 mb-1">
            <div className="w-10 h-10 rounded-xl bg-red-500/15 flex items-center justify-center">
              <ShieldAlert className="w-5 h-5 text-red-400" />
            </div>
            <div>
              <h1>Delay Risk Alerts</h1>
              <p>
                {alerts.length} high-risk request
                {alerts.length !== 1 ? "s" : ""} detected
              </p>
            </div>
          </div>
        </div>
        {isAdmin && (
          <button
            onClick={handleScan}
            disabled={scanning}
            className="btn-primary"
          >
            {scanning ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Scanning…
              </>
            ) : (
              <>
                <Search className="w-4 h-4" />
                Run Alert Scan
              </>
            )}
          </button>
        )}
      </div>

      {/* Scan result banner */}
      {scanResult && (
        <div className="card border border-primary-500/20 bg-primary-500/[0.06]">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5 text-primary-400" />
            <p className="text-primary-300 font-semibold">Scan complete</p>
          </div>
          <p className="text-slate-300 text-sm mt-1.5">
            Scanned <strong>{scanResult.scanned}</strong> active requests
            &bull; Flagged <strong>{scanResult.flagged}</strong> &bull; Emails
            sent <strong>{scanResult.notified}</strong>
          </p>
        </div>
      )}

      {/* Error banner */}
      {error && (
        <div className="card border border-red-500/20 bg-red-500/[0.06]">
          <div className="flex items-center gap-2">
            <AlertOctagon className="w-4 h-4 text-red-400" />
            <p className="text-red-300 text-sm">{error}</p>
          </div>
        </div>
      )}

      {/* Summary badges */}
      {alerts.length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {["critical", "high", "medium", "low"].map((u) => {
            const cfg = URGENCY_CONFIG[u];
            const Icon = cfg.icon;
            return (
              <div
                key={u}
                className={`card border ${cfg.border} ${cfg.bg} flex items-center gap-3 ${
                  cfg.pulse ? "animate-pulse-glow" : ""
                }`}
              >
                <div
                  className={`w-10 h-10 rounded-xl ${cfg.iconBg} flex items-center justify-center`}
                >
                  <Icon className={`w-5 h-5 ${cfg.iconColor}`} />
                </div>
                <div>
                  <p className="text-xs text-slate-500 font-medium">
                    {cfg.label}
                  </p>
                  <p className="text-xl font-bold text-white">
                    {countByUrgency[u] || 0}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Alert cards */}
      {loading ? (
        <div className="card text-center py-16">
          <Loader2 className="w-8 h-8 text-primary-400 animate-spin mx-auto mb-3" />
          <p className="text-slate-400 text-sm">Loading alerts…</p>
        </div>
      ) : alerts.length === 0 ? (
        <div className="card text-center py-16">
          <CheckCircle2 className="w-12 h-12 text-emerald-400 mx-auto mb-3" />
          <p className="text-slate-200 font-semibold">
            No high-risk requests right now
          </p>
          <p className="text-slate-500 text-sm mt-1.5">
            All active requests are within safe SLA bounds.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {alerts.map((alert) => {
            const cfg =
              URGENCY_CONFIG[alert.urgency] || URGENCY_CONFIG.medium;
            const Icon = cfg.icon;
            return (
              <div
                key={alert.request_id}
                className={`card border ${cfg.border} ${cfg.bg} space-y-4 ${
                  cfg.pulse ? "animate-pulse-glow" : ""
                }`}
              >
                {/* Top row */}
                <div className="flex items-start justify-between gap-3 flex-wrap">
                  <div className="flex items-center gap-3">
                    <div
                      className={`w-10 h-10 rounded-xl ${cfg.iconBg} flex items-center justify-center flex-shrink-0`}
                    >
                      <Icon
                        className={`w-5 h-5 ${cfg.iconColor}`}
                      />
                    </div>
                    <div>
                      <p className="font-semibold text-white">
                        {alert.request_number}
                      </p>
                      <p className="text-sm text-slate-400">
                        {alert.request_type
                          .replace("_", " ")
                          .replace(/\b\w/g, (c) => c.toUpperCase())}
                        {" · "}
                        <span className="text-slate-300">
                          {alert.title}
                        </span>
                      </p>
                    </div>
                  </div>
                  <span
                    className={`text-xs font-bold px-2.5 py-1 rounded-lg ${cfg.badge} text-white`}
                  >
                    {cfg.label}
                  </span>
                </div>

                {/* Details grid */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-sm">
                  <div>
                    <p className="text-slate-500 text-xs font-medium mb-1">
                      Student
                    </p>
                    <p className="text-slate-200">{alert.student_name}</p>
                  </div>
                  <div>
                    <p className="text-slate-500 text-xs font-medium mb-1">
                      Stage
                    </p>
                    <p className="text-slate-200 capitalize">
                      {alert.current_stage}
                    </p>
                  </div>
                  <div>
                    <p className="text-slate-500 text-xs font-medium mb-1">
                      SLA Remaining
                    </p>
                    <SlaCountdown hours={alert.hours_remaining} />
                  </div>
                  <div>
                    <p className="text-slate-500 text-xs font-medium mb-1.5">
                      Risk Score
                    </p>
                    <RiskBar score={alert.risk_score} />
                  </div>
                </div>

                {/* Admin escalate section */}
                {isAdmin && (
                  <div className="flex items-center gap-2 flex-wrap pt-3 border-t border-white/[0.06]">
                    <input
                      type="text"
                      placeholder="Escalation notes (optional)"
                      value={notesMap[alert.request_id] || ""}
                      onChange={(e) =>
                        setNotesMap((m) => ({
                          ...m,
                          [alert.request_id]: e.target.value,
                        }))
                      }
                      className="input-field flex-1 min-w-[200px] text-sm py-2"
                    />
                    <button
                      onClick={() =>
                        handleEscalate(alert.request_id)
                      }
                      disabled={escalating === alert.request_id}
                      className="btn-primary text-sm py-2 px-4"
                    >
                      {escalating === alert.request_id ? (
                        <>
                          <Loader2 className="w-3.5 h-3.5 animate-spin" />
                          Escalating…
                        </>
                      ) : (
                        <>
                          <Rocket className="w-3.5 h-3.5" />
                          Escalate
                        </>
                      )}
                    </button>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
