import {
  Target,
  TrendingUp,
  Shield,
  MessageSquare,
  ListChecks,
} from "lucide-react";

export default function PredictionResult({ result }) {
  if (!result) return null;

  const prob = result.prediction_score;
  const pct = (prob * 100).toFixed(1);

  const riskLevel = prob >= 0.7 ? "high" : prob >= 0.5 ? "medium" : "low";

  const riskConfig = {
    high: {
      color: "text-red-400",
      bg: "from-red-500/20 to-red-600/5",
      ring: "stroke-red-500",
      label: "High Risk",
      glow: "shadow-glow-red",
    },
    medium: {
      color: "text-amber-400",
      bg: "from-amber-500/20 to-amber-600/5",
      ring: "stroke-amber-500",
      label: "Medium Risk",
      glow: "shadow-glow-amber",
    },
    low: {
      color: "text-emerald-400",
      bg: "from-emerald-500/20 to-emerald-600/5",
      ring: "stroke-emerald-500",
      label: "Low Risk",
      glow: "shadow-glow-green",
    },
  };

  const cfg = riskConfig[riskLevel];
  const circumference = 2 * Math.PI * 54;
  const dashOffset = circumference - prob * circumference;

  const stars = { high: "★★★", medium: "★★☆", low: "★☆☆" };
  const starStr = stars[result.confidence] ?? "★☆☆";
  const confLabel =
    result.confidence?.charAt(0).toUpperCase() + result.confidence?.slice(1);

  return (
    <div className="card mt-6 space-y-6 animate-slide-up">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-primary-500/15 flex items-center justify-center">
          <Target className="w-5 h-5 text-primary-400" />
        </div>
        <h2 className="text-xl font-bold text-white">Prediction Results</h2>
      </div>

      {/* Metrics row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {/* Circular gauge */}
        <div
          className={`card bg-gradient-to-br ${cfg.bg} flex flex-col items-center justify-center py-6 ${cfg.glow}`}
        >
          <p className="text-xs text-slate-400 mb-3 font-medium">
            Delay Probability
          </p>
          <div className="relative w-32 h-32">
            <svg className="w-full h-full -rotate-90" viewBox="0 0 120 120">
              <circle
                cx="60"
                cy="60"
                r="54"
                fill="none"
                stroke="currentColor"
                strokeWidth="8"
                className="text-white/[0.06]"
              />
              <circle
                cx="60"
                cy="60"
                r="54"
                fill="none"
                strokeWidth="8"
                strokeLinecap="round"
                className={cfg.ring}
                strokeDasharray={circumference}
                strokeDashoffset={dashOffset}
                style={{ transition: "stroke-dashoffset 1s ease-out" }}
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className={`text-2xl font-bold ${cfg.color}`}>{pct}%</span>
            </div>
          </div>
        </div>

        {/* Status */}
        <div className="card flex flex-col items-center justify-center py-6">
          <p className="text-xs text-slate-400 mb-3 font-medium">Status</p>
          <div
            className={`inline-flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold ${
              result.is_likely_delayed
                ? "bg-red-500/15 text-red-400 border border-red-500/20"
                : "bg-emerald-500/15 text-emerald-400 border border-emerald-500/20"
            }`}
          >
            <TrendingUp className="w-4 h-4" />
            {result.is_likely_delayed ? "Likely Delayed" : "On-Time"}
          </div>
          <p className={`text-sm mt-2 font-medium ${cfg.color}`}>{cfg.label}</p>
        </div>

        {/* Confidence */}
        <div className="card flex flex-col items-center justify-center py-6">
          <p className="text-xs text-slate-400 mb-3 font-medium">Confidence</p>
          <p className="text-2xl font-bold text-accent-400 mb-1">{starStr}</p>
          <p className="text-sm text-slate-300 font-medium">{confLabel}</p>
        </div>
      </div>

      {/* Explanation */}
      <div>
        <div className="flex items-center gap-2 mb-3">
          <MessageSquare className="w-4.5 h-4.5 text-primary-400" />
          <h3 className="text-base font-semibold text-slate-200">
            AI Explanation
          </h3>
        </div>
        <div className="bg-primary-500/[0.12] border border-primary-500/30 rounded-xl p-4 text-sm text-primary-200 leading-relaxed">
          {result.explanation}
        </div>
      </div>

      {/* Contributing Factors */}
      {result.contributing_factors?.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-3">
            <ListChecks className="w-4.5 h-4.5 text-accent-400" />
            <h3 className="text-base font-semibold text-slate-200">
              Contributing Factors
            </h3>
          </div>
          <ul className="space-y-2">
            {result.contributing_factors.map((f, i) => (
              <li
                key={i}
                className="flex items-start gap-3 text-sm text-slate-300 bg-white/[0.08] rounded-xl px-4 py-2.5"
              >
                <span className="w-5 h-5 rounded-full bg-accent-500/15 text-accent-400 flex-shrink-0 flex items-center justify-center text-xs font-bold mt-0.5">
                  {i + 1}
                </span>
                {f}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Recommendation */}
      <div>
        <div className="flex items-center gap-2 mb-3">
          <Shield className="w-4.5 h-4.5 text-emerald-400" />
          <h3 className="text-base font-semibold text-slate-200">
            Recommendation
          </h3>
        </div>
        <div className="bg-emerald-500/[0.12] border border-emerald-500/30 rounded-xl p-4 text-sm text-emerald-200 leading-relaxed">
          {result.recommendation}
        </div>
      </div>
    </div>
  );
}
