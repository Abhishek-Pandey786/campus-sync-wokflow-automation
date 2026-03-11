import {
  ClipboardList,
  AlertTriangle,
  Clock,
  CheckCircle2,
  TrendingUp,
  TrendingDown,
  Zap,
  BarChart3,
} from "lucide-react";

const iconMap = {
  "📋": ClipboardList,
  "⚠️": AlertTriangle,
  "⏳": Clock,
  "✅": CheckCircle2,
  "📈": TrendingUp,
  "📉": TrendingDown,
  "⚡": Zap,
  "📊": BarChart3,
};

const gradientMap = {
  blue: "from-primary-500/20 to-primary-600/5",
  green: "from-emerald-500/20 to-emerald-600/5",
  yellow: "from-amber-500/20 to-amber-600/5",
  red: "from-red-500/20 to-red-600/5",
  purple: "from-violet-500/20 to-violet-600/5",
};

const iconBgMap = {
  blue: "bg-primary-500/15 text-primary-400",
  green: "bg-emerald-500/15 text-emerald-400",
  yellow: "bg-amber-500/15 text-amber-400",
  red: "bg-red-500/15 text-red-400",
  purple: "bg-violet-500/15 text-violet-400",
};

const accentBorderMap = {
  blue: "border-l-primary-500",
  green: "border-l-emerald-500",
  yellow: "border-l-amber-500",
  red: "border-l-red-500",
  purple: "border-l-violet-500",
};

const textColorMap = {
  blue: "text-primary-400",
  green: "text-emerald-400",
  yellow: "text-amber-400",
  red: "text-red-400",
  purple: "text-violet-400",
};

export default function StatsCard({
  title,
  value,
  subtitle,
  icon,
  color = "blue",
}) {
  const IconComponent = iconMap[icon] || ClipboardList;

  return (
    <div
      className={`card border-l-[3px] ${accentBorderMap[color]} hover:scale-[1.02] transition-all duration-300 group overflow-hidden`}
    >
      {/* Gradient glow */}
      <div
        className={`absolute inset-0 bg-gradient-to-br ${gradientMap[color]} opacity-0 group-hover:opacity-100 transition-opacity duration-500 rounded-2xl`}
      />

      <div className="relative">
        <div className="flex items-center justify-between mb-3">
          <p className="text-sm font-medium text-slate-400">{title}</p>
          <div
            className={`w-10 h-10 rounded-xl ${iconBgMap[color]} flex items-center justify-center transition-transform group-hover:scale-110`}
          >
            <IconComponent className="w-5 h-5" />
          </div>
        </div>
        <p className={`text-3xl font-bold ${textColorMap[color]}`}>{value}</p>
        {subtitle && (
          <p className="text-xs text-slate-500 mt-1.5">{subtitle}</p>
        )}
      </div>
    </div>
  );
}
