import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import Navbar from "./components/Navbar";
import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";
import RequestsPage from "./pages/RequestsPage";
import PredictionsPage from "./pages/PredictionsPage";
import AnalyticsPage from "./pages/AnalyticsPage";
import AlertsPage from "./pages/AlertsPage";

function Layout({ children }) {
  return (
    <div className="min-h-screen bg-slate-950 ambient-bg">
      <Navbar />
      <main className="z-content max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  );
}

/** Redirect students away from admin-only pages */
function AdminOnly({ children }) {
  const { isAdmin, isAuthenticated } = useAuth();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (!isAdmin) return <Navigate to="/requests" replace />;
  return children;
}

/** Students land on /requests; admins on / */
function HomeRedirect() {
  const { isAdmin } = useAuth();
  return isAdmin ? <DashboardPage /> : <Navigate to="/requests" replace />;
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />

          {/* Home — admin gets dashboard, student redirected to /requests */}
          <Route path="/" element={
            <ProtectedRoute>
              <Layout><HomeRedirect /></Layout>
            </ProtectedRoute>
          } />

          {/* Shared — both roles */}
          <Route path="/requests" element={
            <ProtectedRoute>
              <Layout><RequestsPage /></Layout>
            </ProtectedRoute>
          } />
          <Route path="/predictions" element={
            <ProtectedRoute>
              <Layout><PredictionsPage /></Layout>
            </ProtectedRoute>
          } />

          {/* Admin-only pages */}
          <Route path="/analytics" element={
            <AdminOnly>
              <Layout><AnalyticsPage /></Layout>
            </AdminOnly>
          } />
          <Route path="/alerts" element={
            <AdminOnly>
              <Layout><AlertsPage /></Layout>
            </AdminOnly>
          } />

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
