import { Navigate } from "react-router-dom";
import type { ReactNode } from "react";
import { useAuth } from "../context/AuthContext";

export function ProtectedRoute({
  children,
  requireAdmin = false,
}: {
  children: ReactNode;
  requireAdmin?: boolean;
}) {
  const { loading, isApproved, isAdministrator } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-cream px-4 py-10">
        <div className="mx-auto max-w-5xl font-sans text-black/80">Checking access…</div>
      </div>
    );
  }

  if (!isApproved) {
    return <Navigate to="/portal" replace />;
  }

  if (requireAdmin && !isAdministrator) {
    return <Navigate to="/portal" replace />;
  }

  return <>{children}</>;
}
