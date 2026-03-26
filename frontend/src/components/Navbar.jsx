import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import {
  LayoutDashboard, FileText, Brain, BarChart3,
  AlertTriangle, Menu, X, LogOut, GraduationCap,
  User, ShieldCheck,
} from "lucide-react";

const ADMIN_NAV = [
  { to: "/",           label: "Dashboard",  icon: LayoutDashboard },
  { to: "/requests",   label: "Requests",   icon: FileText },
  { to: "/predictions",label: "Predictions",icon: Brain },
  { to: "/analytics",  label: "Analytics",  icon: BarChart3 },
  { to: "/alerts",     label: "Alerts",     icon: AlertTriangle },
];

const STUDENT_NAV = [
  { to: "/requests",    label: "My Requests", icon: FileText },
  { to: "/predictions", label: "Predictions", icon: Brain },
];

export default function Navbar() {
  const { user, logout, isAdmin } = useAuth();
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);

  const navLinks = isAdmin ? ADMIN_NAV : STUDENT_NAV;

  return (
    <nav className="sticky top-0 z-40 bg-slate-950/90 backdrop-blur-xl border-b border-white/[0.06]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand */}
          <Link to={isAdmin ? "/" : "/requests"} className="flex items-center gap-2.5 group">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center shadow-glow-teal transition-all group-hover:shadow-lg group-hover:scale-105">
              <GraduationCap className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-bold text-white tracking-tight">
              Campus<span className="text-gradient">Sync</span>
            </span>
          </Link>

          {/* Desktop nav */}
          <div className="hidden md:flex items-center gap-0.5">
            {navLinks.map(({ to, label, icon: Icon }) => {
              const active = location.pathname === to;
              return (
                <Link key={to} to={to}
                  className={`relative flex items-center gap-2 px-3.5 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${
                    active
                      ? "text-white bg-primary-500/10"
                      : "text-slate-400 hover:text-white hover:bg-white/[0.05]"
                  }`}>
                  <Icon className={`w-4 h-4 ${active ? "text-primary-400" : ""}`} />
                  {label}
                  {active && (
                    <span className="absolute bottom-0 left-3 right-3 h-0.5 bg-gradient-to-r from-primary-400 to-accent-400 rounded-full" />
                  )}
                </Link>
              );
            })}
          </div>

          {/* Right side */}
          <div className="flex items-center gap-3">
            {/* User info with role badge */}
            <div className="hidden sm:flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-500/25 to-accent-500/25 border border-white/10 flex items-center justify-center">
                {isAdmin
                  ? <ShieldCheck className="w-4 h-4 text-primary-300" />
                  : <User className="w-4 h-4 text-accent-300" />}
              </div>
              <div className="hidden lg:block">
                <p className="text-sm font-medium text-slate-200 leading-tight">
                  {user?.full_name?.split(" ")[0] || user?.email?.split("@")[0]}
                </p>
                <span className={`text-xs font-semibold px-1.5 py-0.5 rounded-md ${
                  isAdmin
                    ? "bg-primary-500/15 text-primary-400"
                    : "bg-accent-500/15 text-accent-400"
                }`}>
                  {isAdmin ? "Admin" : "Student"}
                </span>
              </div>
            </div>

            {/* Logout */}
            <button onClick={logout}
              className="flex items-center gap-1.5 text-sm text-slate-400 hover:text-red-400 transition-colors px-2 py-1.5 rounded-lg hover:bg-red-500/10">
              <LogOut className="w-4 h-4" />
              <span className="hidden sm:inline">Logout</span>
            </button>

            {/* Mobile toggle */}
            <button onClick={() => setMobileOpen(!mobileOpen)}
              className="md:hidden p-2 text-slate-400 hover:text-white rounded-lg hover:bg-white/[0.05] transition-colors">
              {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="md:hidden border-t border-white/[0.06] bg-slate-950/95 backdrop-blur-xl animate-fade-in">
          <div className="px-4 py-3 space-y-1">
            {navLinks.map(({ to, label, icon: Icon }) => {
              const active = location.pathname === to;
              return (
                <Link key={to} to={to} onClick={() => setMobileOpen(false)}
                  className={`flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-medium transition-all ${
                    active
                      ? "text-white bg-primary-500/10 border-l-2 border-primary-400"
                      : "text-slate-400 hover:text-white hover:bg-white/[0.05]"
                  }`}>
                  <Icon className="w-4 h-4" />
                  {label}
                </Link>
              );
            })}
          </div>
        </div>
      )}
    </nav>
  );
}
