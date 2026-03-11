import { Loader2 } from "lucide-react";

export default function LoadingSpinner({
  text = "Loading…",
  size = "default",
  fullPage = false,
}) {
  const sizeClasses = {
    small: "w-4 h-4",
    default: "w-6 h-6",
    large: "w-10 h-10",
  };

  const content = (
    <div className="flex flex-col items-center justify-center gap-3">
      <Loader2
        className={`${sizeClasses[size]} text-primary-400 animate-spin`}
      />
      {text && (
        <p className="text-sm text-slate-400 animate-pulse">{text}</p>
      )}
    </div>
  );

  if (fullPage) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        {content}
      </div>
    );
  }

  return content;
}

export function SkeletonCard({ count = 4, height = "h-32" }) {
  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {[...Array(count)].map((_, i) => (
        <div
          key={i}
          className={`card ${height} animate-pulse`}
          style={{ animationDelay: `${i * 100}ms` }}
        >
          <div className="h-3 w-20 bg-white/[0.06] rounded mb-3" />
          <div className="h-8 w-16 bg-white/[0.08] rounded" />
        </div>
      ))}
    </div>
  );
}
