import { useState } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import {
  Mail, Lock, User, ArrowRight, GraduationCap,
  Loader2, Eye, EyeOff, ShieldCheck, BookOpen,
  Brain, BarChart3, Shield,
} from "lucide-react";

/* ── Shared input row — MUST be outside the component to keep focus stable ── */
function InputRow({ icon: Icon, label, type = "text", value, onChange, placeholder, required = true, right }) {
  return (
    <div>
      <label className="label">{label}</label>
      <div className="relative">
        <Icon className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
        <input
          type={type} value={value} onChange={onChange}
          className={`input-field pl-10 ${right ? "pr-10" : ""}`}
          placeholder={placeholder} required={required}
        />
        {right}
      </div>
    </div>
  );
}

export default function LoginPage() {
  const { login, register, isAuthenticated, loading, error } = useAuth();

  /* ── Role & sub-tab state ── */
  const [role, setRole] = useState("admin");       // "admin" | "student"
  const [studentTab, setStudentTab] = useState("login"); // "login" | "register"

  /* ── Admin fields (prefilled for demo) ── */
  const [adminEmail, setAdminEmail]       = useState("admin@university.edu");
  const [adminPassword, setAdminPassword] = useState("Admin@123");

  /* ── Student Sign-In fields ── */
  const [stuEmail, setStuEmail]       = useState("");
  const [stuPassword, setStuPassword] = useState("");

  /* ── Student Sign-Up fields ── */
  const [regName, setRegName]       = useState("");
  const [regEmail, setRegEmail]     = useState("");
  const [regPassword, setRegPassword] = useState("");
  const [regConfirm, setRegConfirm] = useState("");
  const [showPwd, setShowPwd]       = useState(false);
  const [regError, setRegError]     = useState(null);

  if (isAuthenticated) return <Navigate to="/" replace />;

  /* ── Handlers ── */
  const handleAdminLogin = async (e) => {
    e.preventDefault();
    await login(adminEmail, adminPassword);
  };

  const handleStudentLogin = async (e) => {
    e.preventDefault();
    await login(stuEmail, stuPassword);
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setRegError(null);
    if (regPassword !== regConfirm) { setRegError("Passwords do not match."); return; }
    if (regPassword.length < 8) { setRegError("Password must be at least 8 characters."); return; }
    await register({ fullName: regName, email: regEmail, password: regPassword });
  };

  const PasswordToggle = (
    <button type="button" onClick={() => setShowPwd(!showPwd)}
      className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition-colors">
      {showPwd ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
    </button>
  );

  /* ─────────────────────────── JSX ─────────────────────────── */
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-teal-950/50 flex items-center justify-center px-4 relative overflow-hidden">
      {/* Background effects */}
      <div className="absolute inset-0 dot-grid opacity-60" />
      <div className="absolute top-1/4 -left-32 w-[500px] h-[500px] bg-primary-500/8 rounded-full blur-3xl animate-float" />
      <div className="absolute bottom-1/4 -right-32 w-[500px] h-[500px] bg-accent-500/6 rounded-full blur-3xl animate-float" style={{ animationDelay: "3s" }} />

      <div className="w-full max-w-md relative z-10 animate-fade-in">
        {/* ── Brand Header ── */}
        <div className="text-center mb-8">
          <div className="relative inline-flex items-center justify-center w-20 h-20 mb-5">
            <div className="absolute inset-0 rounded-2xl border-2 border-dashed border-primary-500/30 animate-spin-slow" />
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center shadow-glow-teal">
              <GraduationCap className="w-9 h-9 text-white" />
            </div>
          </div>
          <h1 className="text-3xl font-bold text-white tracking-tight">
            Campus<span className="text-gradient">Sync</span>
          </h1>
          <p className="text-slate-400 mt-2 text-sm">Smart Campus Workflow Management</p>
        </div>

        {/* ── Role Selector Pill ── */}
        <div className="flex rounded-2xl bg-slate-800/80 backdrop-blur-sm p-1.5 mb-6 border border-white/[0.06]">
          {[
            { key: "admin",   label: "Admin Portal",   icon: ShieldCheck },
            { key: "student", label: "Student Portal",  icon: BookOpen },
          ].map(({ key, label, icon: Icon }) => (
            <button key={key} onClick={() => setRole(key)}
              className={`flex-1 flex items-center justify-center gap-2 py-2.5 text-sm font-semibold rounded-xl transition-all duration-300 ${
                role === key
                  ? key === "admin"
                    ? "bg-gradient-to-r from-primary-500 to-primary-600 text-white shadow-lg shadow-primary-500/25"
                    : "bg-gradient-to-r from-accent-500 to-accent-600 text-white shadow-lg shadow-accent-500/25"
                  : "text-slate-400 hover:text-white"
              }`}>
              <Icon className="w-4 h-4" />
              {label}
            </button>
          ))}
        </div>

        {/* ── Card ── */}
        <div className="card p-8">

          {/* ════════════ ADMIN PORTAL ════════════ */}
          {role === "admin" && (
            <div className="animate-fade-in">
              {/* Header */}
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 rounded-xl bg-primary-500/15 flex items-center justify-center">
                  <ShieldCheck className="w-5 h-5 text-primary-400" />
                </div>
                <div>
                  <h2 className="text-lg font-bold text-white">Administrator</h2>
                  <p className="text-xs text-slate-500">University administration access</p>
                </div>
              </div>

              {error && (
                <div className="bg-red-500/10 border border-red-500/20 text-red-400 rounded-xl px-4 py-3 text-sm mb-5 flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-red-400 flex-shrink-0" />
                  {error}
                </div>
              )}

              <form onSubmit={handleAdminLogin} className="space-y-5">
                <InputRow icon={Mail} label="Email address" type="email"
                  value={adminEmail} onChange={(e) => setAdminEmail(e.target.value)}
                  placeholder="admin@university.edu" />
                <InputRow icon={Lock} label="Password" type="password"
                  value={adminPassword} onChange={(e) => setAdminPassword(e.target.value)}
                  placeholder="••••••••" />
                <button type="submit" disabled={loading} className="btn-primary w-full py-3 text-base mt-1">
                  {loading
                    ? <><Loader2 className="w-4 h-4 animate-spin" /> Signing in…</>
                    : <><ShieldCheck className="w-4 h-4" /> Sign In as Admin <ArrowRight className="w-4 h-4" /></>}
                </button>
              </form>

              <div className="mt-5 pt-5 border-t border-white/[0.06] text-xs text-slate-500 text-center">
                Demo: <span className="text-slate-400">admin@university.edu</span> / <span className="text-slate-400">Admin@123</span>
              </div>
            </div>
          )}

          {/* ════════════ STUDENT PORTAL ════════════ */}
          {role === "student" && (
            <div className="animate-fade-in">
              {/* Header */}
              <div className="flex items-center gap-3 mb-5">
                <div className="w-10 h-10 rounded-xl bg-accent-500/15 flex items-center justify-center">
                  <BookOpen className="w-5 h-5 text-accent-400" />
                </div>
                <div>
                  <h2 className="text-lg font-bold text-white">Student Access</h2>
                  <p className="text-xs text-slate-500">Submit & track your university requests</p>
                </div>
              </div>

              {/* Sub-tabs: Sign In | Sign Up */}
              <div className="flex rounded-xl bg-slate-800 p-1 mb-6">
                {[
                  { key: "login",    label: "Sign In" },
                  { key: "register", label: "Sign Up" },
                ].map(({ key, label }) => (
                  <button key={key} onClick={() => setStudentTab(key)}
                    className={`flex-1 py-2 text-sm font-semibold rounded-lg transition-all duration-200 ${
                      studentTab === key
                        ? "bg-accent-500 text-white shadow-sm"
                        : "text-slate-400 hover:text-white"
                    }`}>
                    {label}
                  </button>
                ))}
              </div>

              {/* ── Student Sign In ── */}
              {studentTab === "login" && (
                <>
                  {error && (
                    <div className="bg-red-500/10 border border-red-500/20 text-red-400 rounded-xl px-4 py-3 text-sm mb-5 flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-red-400 flex-shrink-0" />
                      {error}
                    </div>
                  )}
                  <form onSubmit={handleStudentLogin} className="space-y-5">
                    <InputRow icon={Mail} label="Email address" type="email"
                      value={stuEmail} onChange={(e) => setStuEmail(e.target.value)}
                      placeholder="student@university.edu" />
                    <InputRow icon={Lock} label="Password" type="password"
                      value={stuPassword} onChange={(e) => setStuPassword(e.target.value)}
                      placeholder="••••••••" />
                    <button type="submit" disabled={loading} className="btn-primary w-full py-3 text-base mt-1" style={{ background: "linear-gradient(135deg, var(--accent-500), var(--accent-600))" }}>
                      {loading
                        ? <><Loader2 className="w-4 h-4 animate-spin" /> Signing in…</>
                        : <><BookOpen className="w-4 h-4" /> Sign In as Student <ArrowRight className="w-4 h-4" /></>}
                    </button>
                  </form>
                  <p className="mt-4 text-xs text-slate-500 text-center">
                    New student? Switch to <button type="button" onClick={() => setStudentTab("register")} className="text-accent-400 hover:underline font-medium">Sign Up</button> to create your account.
                  </p>
                </>
              )}

              {/* ── Student Sign Up ── */}
              {studentTab === "register" && (
                <>
                  {(error || regError) && (
                    <div className="bg-red-500/10 border border-red-500/20 text-red-400 rounded-xl px-4 py-3 text-sm mb-5 flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-red-400 flex-shrink-0" />
                      {regError || error}
                    </div>
                  )}
                  <form onSubmit={handleRegister} className="space-y-4">
                    <InputRow icon={User} label="Full Name" value={regName}
                      onChange={(e) => setRegName(e.target.value)} placeholder="e.g. Priya Sharma" />
                    <InputRow icon={Mail} label="Email address" type="email" value={regEmail}
                      onChange={(e) => setRegEmail(e.target.value)} placeholder="student@university.edu" />
                    <InputRow icon={Lock} label="Password" type={showPwd ? "text" : "password"}
                      value={regPassword} onChange={(e) => setRegPassword(e.target.value)}
                      placeholder="Min 8 chars, A-z, 0-9" right={PasswordToggle} />
                    <InputRow icon={Lock} label="Confirm Password" type={showPwd ? "text" : "password"}
                      value={regConfirm} onChange={(e) => setRegConfirm(e.target.value)}
                      placeholder="Repeat password" />
                    <button type="submit" disabled={loading} className="btn-primary w-full py-3 text-base mt-1" style={{ background: "linear-gradient(135deg, var(--accent-500), var(--accent-600))" }}>
                      {loading
                        ? <><Loader2 className="w-4 h-4 animate-spin" /> Creating account…</>
                        : <><User className="w-4 h-4" /> Create Student Account <ArrowRight className="w-4 h-4" /></>}
                    </button>
                  </form>
                  <p className="mt-4 text-xs text-slate-500 text-center">
                    Already have an account? <button type="button" onClick={() => setStudentTab("login")} className="text-accent-400 hover:underline font-medium">Sign In</button>
                  </p>
                </>
              )}
            </div>
          )}
        </div>

        {/* ── Feature Highlights ── */}
        <div className="grid grid-cols-3 gap-3 mt-6">
          {[
            { icon: Brain,     label: "AI Predictions",     color: "text-primary-400" },
            { icon: BarChart3, label: "Real-time Analytics", color: "text-accent-400" },
            { icon: Shield,    label: "Role-Based Access",   color: "text-emerald-400" },
          ].map(({ icon: Icon, label, color }) => (
            <div key={label} className="flex flex-col items-center gap-1.5 py-3 px-2 rounded-xl bg-white/[0.03] border border-white/[0.04]">
              <Icon className={`w-4 h-4 ${color}`} />
              <span className="text-[10px] text-slate-500 font-medium text-center leading-tight">{label}</span>
            </div>
          ))}
        </div>

        <p className="text-center text-xs text-slate-600 mt-5">Christ University · MCA · CampusSync</p>
      </div>
    </div>
  );
}
