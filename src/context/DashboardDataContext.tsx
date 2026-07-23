import { createContext, useCallback, useContext, useEffect, useRef, useState, type ReactNode } from "react";
import {
  fetchDashboardData,
  getApiErrorCode,
  getApiErrorKind,
  getApiErrorMessage,
  type ApiErrorKind,
  type DashboardData,
  type DashboardFilters,
  type DashboardPeriod,
} from "../api";
import {
  CLAIMS_BY_HOUR,
  CLAIMS_BY_MONTH,
  CLIMATE_MONTHS,
  CLIMATE_TCO2,
  DEMAND_GRID,
  DEMAND_LOCATIONS,
  DEMAND_TIMES,
  HOURS,
  LOCATIONS,
  MONTHS,
  POSTS,
  POSTS_BY_MONTH,
  STAFF,
  SUMMARY,
  UNIVERSITY,
  WASTE_LBS,
  WASTE_MONTHS,
  DATE_RANGE,
  periodLabel,
} from "../data";

const fallbackData: DashboardData = {
  university: UNIVERSITY,
  dateRange: DATE_RANGE,
  summary: SUMMARY,
  months: MONTHS,
  postsByMonth: POSTS_BY_MONTH,
  claimsByMonth: CLAIMS_BY_MONTH,
  hours: HOURS,
  claimsByHour: CLAIMS_BY_HOUR,
  locations: LOCATIONS,
  posts: POSTS,
  demandGrid: DEMAND_GRID,
  demandLocations: DEMAND_LOCATIONS,
  demandTimes: DEMAND_TIMES,
  staff: STAFF,
  wasteMonths: WASTE_MONTHS,
  wasteLbs: WASTE_LBS,
  climateMonths: CLIMATE_MONTHS,
  climateTco2: CLIMATE_TCO2,
};

const DEFAULT_FILTERS: DashboardFilters = {
  period: "year",
  month: 6,
  year: 2025,
};

type DashboardDataState = {
  data: DashboardData;
  filters: DashboardFilters;
  period: DashboardPeriod;
  setPeriod: (period: DashboardPeriod) => void;
  setMonth: (month: number) => void;
  setYear: (year: number) => void;
  loading: boolean;
  refreshing: boolean;
  error: string | null;
  errorKind: ApiErrorKind | null;
  errorCode: string | null;
  fromApi: boolean;
  retry: () => void;
};

const DashboardDataContext = createContext<DashboardDataState>({
  data: fallbackData,
  filters: DEFAULT_FILTERS,
  period: DEFAULT_FILTERS.period,
  setPeriod: () => undefined,
  setMonth: () => undefined,
  setYear: () => undefined,
  loading: true,
  refreshing: false,
  error: null,
  errorKind: null,
  errorCode: null,
  fromApi: false,
  retry: () => undefined,
});

export function DashboardDataProvider({ children }: { children: ReactNode }) {
  const [filters, setFilters] = useState<DashboardFilters>(DEFAULT_FILTERS);
  const [retryCount, setRetryCount] = useState(0);
  const hasLoadedRef = useRef(false);
  const [state, setState] = useState({
    data: fallbackData,
    loading: true,
    refreshing: false,
    error: null as string | null,
    errorKind: null as ApiErrorKind | null,
    errorCode: null as string | null,
    fromApi: false,
  });

  const setPeriod = useCallback((period: DashboardPeriod) => {
    setFilters((current) => {
      if (period === "month") {
        return { ...current, period, month: current.month || 6, year: current.year || 2026 };
      }
      if (period === "year") {
        return { ...current, period, year: current.year === 2026 ? 2025 : current.year || 2025 };
      }
      return { ...current, period };
    });
  }, []);

  const setMonth = useCallback((month: number) => {
    setFilters((current) => ({ ...current, period: "month", month }));
  }, []);

  const setYear = useCallback((year: number) => {
    setFilters((current) => ({ ...current, year }));
  }, []);

  const retry = useCallback(() => {
    setRetryCount((count) => count + 1);
  }, []);

  useEffect(() => {
    let cancelled = false;
    const isRefresh = hasLoadedRef.current;

    setState((current) => ({
      ...current,
      loading: !isRefresh,
      refreshing: isRefresh,
      error: null,
      errorKind: null,
      errorCode: null,
    }));

    fetchDashboardData(filters)
      .then((data) => {
        if (!cancelled) {
          hasLoadedRef.current = true;
          setState({
            data,
            loading: false,
            refreshing: false,
            error: null,
            errorKind: null,
            errorCode: null,
            fromApi: true,
          });
        }
      })
      .catch((error: unknown) => {
        if (!cancelled) {
          hasLoadedRef.current = true;
          setState({
            data: {
              ...fallbackData,
              dateRange: periodLabel(filters.period, filters.month, filters.year),
            },
            loading: false,
            refreshing: false,
            error: getApiErrorMessage(error),
            errorKind: getApiErrorKind(error),
            errorCode: getApiErrorCode(error),
            fromApi: false,
          });
        }
      });

    return () => {
      cancelled = true;
    };
  }, [filters, retryCount]);

  return (
    <DashboardDataContext.Provider
      value={{
        ...state,
        filters,
        period: filters.period,
        setPeriod,
        setMonth,
        setYear,
        retry,
      }}
    >
      {children}
    </DashboardDataContext.Provider>
  );
}

export function useDashboardData() {
  return useContext(DashboardDataContext);
}
