import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";
import {
  fetchMe,
  getToken,
  login as loginRequest,
  logout as logoutRequest,
  register as registerRequest,
  setToken,
  type DashboardUser,
  type LoginResponse,
  type RegisterPayload,
} from "../api/auth";

type AuthState = {
  user: DashboardUser | null;
  loading: boolean;
  login: (email: string) => Promise<LoginResponse>;
  register: (payload: RegisterPayload) => Promise<LoginResponse>;
  logout: () => Promise<void>;
  isApproved: boolean;
  isAdministrator: boolean;
  /** Approved administrator or editor — can edit campus resources in the student app. */
  canEditResources: boolean;
};

const AuthContext = createContext<AuthState>({
  user: null,
  loading: true,
  login: async () => {
    throw new Error("AuthProvider is missing");
  },
  register: async () => {
    throw new Error("AuthProvider is missing");
  },
  logout: async () => undefined,
  isApproved: false,
  isAdministrator: false,
  canEditResources: false,
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<DashboardUser | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    if (!getToken()) {
      setLoading(false);
      return;
    }

    fetchMe()
      .then((me) => {
        if (!cancelled) {
          setUser(me);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setToken(null);
          setUser(null);
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const login = useCallback(async (email: string) => {
    const result = await loginRequest(email);
    setUser(result.user);
    return result;
  }, []);

  const register = useCallback(async (payload: RegisterPayload) => {
    const result = await registerRequest(payload);
    setUser(result.user);
    return result;
  }, []);

  const logout = useCallback(async () => {
    await logoutRequest();
    setUser(null);
  }, []);

  const isApproved = user?.status === "approved";
  const role = user?.dashboardRole;
  const value: AuthState = {
    user,
    loading,
    login,
    register,
    logout,
    isApproved: Boolean(isApproved),
    isAdministrator: Boolean(isApproved && role === "administrator"),
    canEditResources: Boolean(
      isApproved && (role === "administrator" || role === "editor"),
    ),
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
