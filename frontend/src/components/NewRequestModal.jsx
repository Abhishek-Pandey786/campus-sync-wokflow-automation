import { useState } from "react";
import { createRequest } from "../api/requests";
import {
  X, FileText, AlignLeft, Tag, AlertCircle,
  Loader2, CheckCircle2, ChevronDown,
} from "lucide-react";

const REQUEST_TYPES = [
  { value: "certificate", label: "📜 Certificate" },
  { value: "hostel",      label: "🏠 Hostel" },
  { value: "it_support",  label: "💻 IT Support" },
  { value: "library",     label: "📚 Library" },
  { value: "exam",        label: "📝 Exam" },
  { value: "transcript",  label: "🎓 Transcript" },
];

const PRIORITIES = [
  { value: 1, label: "Low",    color: "border-slate-500 text-slate-400",    activeBg: "bg-slate-500/20 border-slate-400 text-slate-200" },
  { value: 2, label: "Medium", color: "border-amber-600  text-amber-500",   activeBg: "bg-amber-500/20  border-amber-400  text-amber-200"  },
  { value: 3, label: "High",   color: "border-red-600    text-red-500",     activeBg: "bg-red-500/20    border-red-400    text-red-200"    },
];

export default function NewRequestModal({ onClose, onCreated }) {
  const [form, setForm] = useState({
    request_type: "certificate",
    title:        "",
    description:  "",
    priority:     2,
  });
  const [loading, setLoading]   = useState(false);
  const [success, setSuccess]   = useState(false);
  const [error, setError]       = useState(null);

  const set = (key, val) => setForm((f) => ({ ...f, [key]: val }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.title.trim()) { setError("Please enter a request title."); return; }
    setLoading(true); setError(null);
    try {
      const created = await createRequest({ ...form, priority: Number(form.priority) });
      setSuccess(true);
      setTimeout(() => { onCreated?.(created); onClose(); }, 1400);
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(Array.isArray(detail) ? detail[0]?.msg : (detail ?? "Failed to create request."));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-overlay flex items-end sm:items-center justify-center p-4" onClick={onClose}>
      <div
        className="w-full max-w-lg bg-slate-900 rounded-2xl border border-slate-700/60 shadow-2xl animate-slide-up overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 pt-6 pb-4 border-b border-white/[0.06]">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-primary-500/15 flex items-center justify-center">
              <FileText className="w-4.5 h-4.5 text-primary-400" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">New Service Request</h2>
              <p className="text-xs text-slate-500">Submit a request to the admin office</p>
            </div>
          </div>
          <button onClick={onClose}
            className="w-8 h-8 rounded-lg bg-white/[0.05] hover:bg-white/[0.1] flex items-center justify-center text-slate-400 hover:text-white transition-all">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Success state */}
        {success ? (
          <div className="flex flex-col items-center justify-center py-16 gap-4">
            <div className="w-16 h-16 rounded-2xl bg-emerald-500/15 flex items-center justify-center">
              <CheckCircle2 className="w-8 h-8 text-emerald-400" />
            </div>
            <p className="text-white font-semibold text-lg">Request Submitted!</p>
            <p className="text-slate-400 text-sm">Your request has been created and is pending review.</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="px-6 py-5 space-y-5">
            {/* Error */}
            {error && (
              <div className="bg-red-500/10 border border-red-500/20 text-red-400 rounded-xl px-4 py-3 text-sm flex items-center gap-2">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                {error}
              </div>
            )}

            {/* Request Type */}
            <div>
              <label className="label flex items-center gap-1.5">
                <Tag className="w-3.5 h-3.5" /> Request Type
              </label>
              <div className="relative">
                <select value={form.request_type} onChange={(e) => set("request_type", e.target.value)}
                  className="input-field appearance-none pr-10">
                  {REQUEST_TYPES.map((t) => (
                    <option key={t.value} value={t.value}>{t.label}</option>
                  ))}
                </select>
                <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 pointer-events-none" />
              </div>
            </div>

            {/* Title */}
            <div>
              <label className="label flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5" /> Title
              </label>
              <input type="text" value={form.title} onChange={(e) => set("title", e.target.value)}
                className="input-field" placeholder="e.g. Bonafide Certificate for Visa Application"
                maxLength={200} required />
            </div>

            {/* Description */}
            <div>
              <label className="label flex items-center gap-1.5">
                <AlignLeft className="w-3.5 h-3.5" /> Description
                <span className="text-slate-600 font-normal">(optional)</span>
              </label>
              <textarea value={form.description} onChange={(e) => set("description", e.target.value)}
                className="input-field resize-none" rows={3}
                placeholder="Provide any additional details or context..." />
            </div>

            {/* Priority */}
            <div>
              <label className="label">Priority</label>
              <div className="flex gap-3">
                {PRIORITIES.map((p) => (
                  <button key={p.value} type="button"
                    onClick={() => set("priority", p.value)}
                    className={`flex-1 py-2 rounded-xl border text-sm font-semibold transition-all duration-200 ${
                      form.priority === p.value ? p.activeBg : `border-slate-700 text-slate-500 hover:${p.color}`
                    }`}>
                    {p.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-3 pt-1">
              <button type="button" onClick={onClose} className="btn-secondary flex-1 py-2.5">
                Cancel
              </button>
              <button type="submit" disabled={loading} className="btn-primary flex-1 py-2.5">
                {loading
                  ? <><Loader2 className="w-4 h-4 animate-spin" /> Submitting…</>
                  : <>Submit Request</>}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
