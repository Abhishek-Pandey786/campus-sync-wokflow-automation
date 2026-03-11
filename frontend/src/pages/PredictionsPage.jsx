import { useState } from "react";
import PredictionResult from "../components/PredictionResult";
import { predictDelay } from "../api/predictions";
import {
  Brain,
  Loader2,
  Sparkles,
  CircleAlert,
  CircleCheck,
  TriangleAlert,
  Gauge,
} from "lucide-react";

const REQUEST_TYPES = [
  "certificate",
  "hostel",
  "it_support",
  "library",
  "exam",
  "transcript",
];
const DAYS = [
  "Monday",
  "Tuesday",
  "Wednesday",
  "Thursday",
  "Friday",
  "Saturday",
  "Sunday",
];

const DEFAULT_FORM = {
  request_type: "certificate",
  priority: 3,
  created_hour: 10,
  created_day_of_week: 0,
  handler_workload: 2,
  stage_created_duration: 1,
  stage_assigned_duration: 2,
  stage_verified_duration: 3,
  stage_approved_duration: 4,
  stage_processed_duration: 5,
  final_stage: "completed",
};

export default function PredictionsPage() {
  const [form, setForm] = useState(DEFAULT_FORM);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const set = (key, val) => setForm((f) => ({ ...f, [key]: val }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const payload = {
        ...form,
        priority: Number(form.priority),
        created_hour: Number(form.created_hour),
        created_day_of_week: Number(form.created_day_of_week),
        handler_workload: Number(form.handler_workload),
        stage_created_duration: Number(form.stage_created_duration),
        stage_assigned_duration: Number(form.stage_assigned_duration),
        stage_verified_duration: Number(form.stage_verified_duration),
        stage_approved_duration: Number(form.stage_approved_duration),
        stage_processed_duration: Number(form.stage_processed_duration),
      };
      const data = await predictDelay(payload);
      setResult(data);
    } catch (err) {
      setError(
        err.response?.data?.detail ??
          "Prediction failed. Is the backend running?"
      );
    } finally {
      setLoading(false);
    }
  };

  const loadPreset = (preset) => {
    const presets = {
      low: {
        request_type: "certificate",
        priority: 3,
        created_hour: 10,
        created_day_of_week: 0,
        handler_workload: 2,
        stage_created_duration: 1,
        stage_assigned_duration: 2,
        stage_verified_duration: 3,
        stage_approved_duration: 4,
        stage_processed_duration: 5,
        final_stage: "completed",
      },
      medium: {
        request_type: "hostel",
        priority: 2,
        created_hour: 14,
        created_day_of_week: 3,
        handler_workload: 5,
        stage_created_duration: 9,
        stage_assigned_duration: 9,
        stage_verified_duration: 9,
        stage_approved_duration: 9,
        stage_processed_duration: 9,
        final_stage: "completed",
      },
      high: {
        request_type: "hostel",
        priority: 1,
        created_hour: 17,
        created_day_of_week: 4,
        handler_workload: 10,
        stage_created_duration: 8,
        stage_assigned_duration: 16,
        stage_verified_duration: 20,
        stage_approved_duration: 18,
        stage_processed_duration: 25,
        final_stage: "completed",
      },
    };
    setForm(presets[preset]);
    setResult(null);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="page-header">
        <div className="flex items-center gap-3 mb-1">
          <div className="w-10 h-10 rounded-xl bg-violet-500/15 flex items-center justify-center">
            <Brain className="w-5 h-5 text-violet-400" />
          </div>
          <div>
            <h1>ML Delay Prediction</h1>
            <p>
              Enter request details for a real-time ML-powered delay prediction
            </p>
          </div>
        </div>
      </div>

      {/* Presets */}
      <div className="flex gap-3 flex-wrap items-center">
        <span className="text-sm text-slate-500 font-medium">
          Quick presets:
        </span>
        <button
          onClick={() => loadPreset("low")}
          className="badge-green cursor-pointer text-sm px-3.5 py-1.5 hover:scale-[1.05] transition-transform"
        >
          <CircleCheck className="w-3.5 h-3.5" />
          Low Risk
        </button>
        <button
          onClick={() => loadPreset("medium")}
          className="badge-yellow cursor-pointer text-sm px-3.5 py-1.5 hover:scale-[1.05] transition-transform"
        >
          <CircleAlert className="w-3.5 h-3.5" />
          Medium Risk
        </button>
        <button
          onClick={() => loadPreset("high")}
          className="badge-red cursor-pointer text-sm px-3.5 py-1.5 hover:scale-[1.05] transition-transform"
        >
          <TriangleAlert className="w-3.5 h-3.5" />
          High Risk
        </button>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left: Request Details */}
          <div className="card space-y-5">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4.5 h-4.5 text-primary-400" />
              <h2 className="text-lg font-semibold text-white">
                Request Details
              </h2>
            </div>

            <div>
              <label className="label">Request Type</label>
              <select
                value={form.request_type}
                onChange={(e) => set("request_type", e.target.value)}
                className="input-field"
              >
                {REQUEST_TYPES.map((t) => (
                  <option key={t} value={t}>
                    {t.replace("_", " ")}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="label">
                Priority Level:{" "}
                <span className="text-primary-400 font-bold">
                  {form.priority}
                </span>
              </label>
              <input
                type="range"
                min="1"
                max="3"
                step="1"
                value={form.priority}
                onChange={(e) => set("priority", e.target.value)}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-slate-500 mt-1">
                <span>1 (Low)</span>
                <span>2 (Medium)</span>
                <span>3 (High)</span>
              </div>
            </div>

            <div>
              <label className="label">
                Submission Hour:{" "}
                <span className="text-primary-400 font-bold">
                  {form.created_hour}:00
                </span>
              </label>
              <input
                type="range"
                min="0"
                max="23"
                step="1"
                value={form.created_hour}
                onChange={(e) => set("created_hour", e.target.value)}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-slate-500 mt-1">
                <span>0:00</span>
                <span>12:00</span>
                <span>23:00</span>
              </div>
            </div>

            <div>
              <label className="label">Day of Week</label>
              <select
                value={form.created_day_of_week}
                onChange={(e) =>
                  set("created_day_of_week", e.target.value)
                }
                className="input-field"
              >
                {DAYS.map((d, i) => (
                  <option key={d} value={i}>
                    {d}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="label">
                Handler Workload:{" "}
                <span className="text-primary-400 font-bold">
                  {form.handler_workload}
                </span>
              </label>
              <input
                type="range"
                min="1"
                max="10"
                step="1"
                value={form.handler_workload}
                onChange={(e) => set("handler_workload", e.target.value)}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-slate-500 mt-1">
                <span>1 (Light)</span>
                <span>5</span>
                <span>10 (Heavy)</span>
              </div>
            </div>
          </div>

          {/* Right: Stage Durations */}
          <div className="card space-y-5">
            <div className="flex items-center gap-2">
              <Gauge className="w-4.5 h-4.5 text-accent-400" />
              <h2 className="text-lg font-semibold text-white">
                Expected Stage Durations (hours)
              </h2>
            </div>
            {[
              ["stage_created_duration", "Created Stage"],
              ["stage_assigned_duration", "Assigned Stage"],
              ["stage_verified_duration", "Verified Stage"],
              ["stage_approved_duration", "Approved Stage"],
              ["stage_processed_duration", "Processed Stage"],
            ].map(([key, label]) => (
              <div key={key}>
                <label className="label">{label}</label>
                <div className="flex items-center gap-3">
                  <input
                    type="number"
                    min="0"
                    step="0.5"
                    value={form[key]}
                    onChange={(e) => set(key, e.target.value)}
                    className="input-field w-28"
                  />
                  <span className="text-slate-500 text-sm">hrs</span>
                </div>
              </div>
            ))}

            {/* Total */}
            <div className="pt-3 border-t border-white/[0.06]">
              <div className="flex justify-between text-sm">
                <span className="text-slate-400 font-medium">
                  Total Duration
                </span>
                <span className="font-bold text-gradient text-lg">
                  {(
                    Number(form.stage_created_duration) +
                    Number(form.stage_assigned_duration) +
                    Number(form.stage_verified_duration) +
                    Number(form.stage_approved_duration) +
                    Number(form.stage_processed_duration)
                  ).toFixed(1)}{" "}
                  hrs
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="mt-4 bg-red-500/10 border border-red-500/20 text-red-400 rounded-xl px-4 py-3 text-sm flex items-center gap-2">
            <TriangleAlert className="w-4 h-4 flex-shrink-0" />
            {error}
          </div>
        )}

        {/* Submit */}
        <button
          type="submit"
          disabled={loading}
          className="btn-primary mt-6 px-8 py-3 text-base"
        >
          {loading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Predicting…
            </>
          ) : (
            <>
              <Sparkles className="w-5 h-5" />
              Predict Delay Risk
            </>
          )}
        </button>
      </form>

      {/* Results */}
      <PredictionResult result={result} />
    </div>
  );
}
