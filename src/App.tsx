import { Navigate, Route, Routes } from "react-router-dom";
import { DemoLayout } from "./components/DemoLayout";
import { ProtectedRoute } from "./components/ProtectedRoute";
import Home from "./pages/Home";
import Dashboard from "./pages/Dashboard";
import MobileApp from "./pages/MobileApp";
import WebApp from "./pages/WebApp";
import Training from "./pages/Training";
import Portal from "./pages/Portal";
import AdminApprovals from "./pages/AdminApprovals";

export default function App() {
  return (
    <Routes>
      <Route path="/portal" element={<Portal />} />
      <Route
        path="/admin"
        element={
          <ProtectedRoute requireAdmin>
            <AdminApprovals />
          </ProtectedRoute>
        }
      />
      <Route element={<DemoLayout />}>
        <Route path="/" element={<Home />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route path="/mobile" element={<MobileApp />} />
        <Route path="/web" element={<WebApp />} />
        <Route path="/training" element={<Training />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
