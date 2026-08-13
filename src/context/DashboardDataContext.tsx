import { createContext, useCallback, useContext, useEffect, useRef, useState, type ReactNode } from "react";
import {
  fetchAvailablePeriods,
  fetchDashboardData,
  getApiErrorCode,
  getApiErrorKind,
  getApiErrorMessage,
  type ApiErrorKind,
  type AvailablePeriods,
  type DashboardData,
  type DashboardFilters,
  type DashboardPeriod,
} from "../api";
import {
  CLAIMS_BY_HOUR,
  CLAIMS_BY_MONTH,
  CLIMATE_MONTHS,
  CLIMATE_TCO2,
  DATE_RANGE,
  DEFAULT_WEEK_START,
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
  clampFiltersToAvailable,
  parseWeekStart,
  periodLabel,
  resolveWeekStartWithData,
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
  weekStart: DEFAULT_WEEK_START,
};

type DashboardDataState = {
  data: DashboardData;
  filters: DashboardFilters;
  period: DashboardPeriod;
  availablePeriods: AvailablePeriods | null;
  setPeriod: (period: DashboardPeriod) => void;
  setMonth: (month: number) => void;
  setYear: (year: number) => void;
  setWeekStart: (weekStart: string) => void;
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
  availablePeriods: null,
  setPeriod: () => undefined,
  setMonth: () => undefined,
  setYear: () => undefined,
  setWeekStart: () => undefined,
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
  const [availablePeriods, setAvailablePeriods] = useState<AvailablePeriods | null>(null);
  const [retryCount, setRetryCount] = useState(0);
  const hasLoadedRef = useRef(false);
  const availableRef = useRef<AvailablePeriods | null>(null);
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
      const available = availableRef.current;
      if (period === "week") {
        const monday = parseWeekStart(current.weekStart || DEFAULT_WEEK_START);
        const month = monday.getMonth() + 1;
        const year = monday.getFullYear();
        return clampFiltersToAvailable(
          {
            ...current,
            period,
            month,
            year,
            weekStart: resolveWeekStartWithData(
              month,
              year,
              current.weekStart || DEFAULT_WEEK_START,
              available?.weeks,
            ),
          },
          available,
        );
      }
      if (period === "month") {
        return clampFiltersToAvailable(
          { ...current, period, month: current.month || 6, year: current.year || 2026 },
          available,
        );
      }
      if (period === "year") {
        return clampFiltersToAvailable(
          { ...current, period, year: current.year === 2026 ? 2025 : current.year || 2025 },
          available,
        );
      }
      return { ...current, period };
    });
  }, []);

  const setMonth = useCallback((month: number) => {
    setFilters((current) => {
      const available = availableRef.current;
      if (current.period === "week") {
        return clampFiltersToAvailable(
          {
            ...current,
            month,
            weekStart: resolveWeekStartWithData(month, current.year, current.weekStart, available?.weeks),
          },
          available,
        );
      }
      return clampFiltersToAvailable({ ...current, period: "month", month }, available);
    });
  }, []);

  const setYear = useCallback((year: number) => {
    setFilters((current) => {
      const available = availableRef.current;
      if (current.period === "week") {
        return clampFiltersToAvailable(
          {
            ...current,
            year,
            weekStart: resolveWeekStartWithData(current.month, year, current.weekStart, available?.weeks),
          },
          available,
        );
      }
      return clampFiltersToAvailable({ ...current, year }, available);
    });
  }, []);

  const setWeekStart = useCallback((weekStart: string) => {
    setFilters((current) => ({ ...current, period: "week", weekStart }));
  }, []);

  const retry = useCallback(() => {
    setRetryCount((count) => count + 1);
  }, []);

  useEffect(() => {
    let cancelled = false;

    fetchAvailablePeriods()
      .then((periods) => {
        if (cancelled) return;
        availableRef.current = periods;
        setAvailablePeriods(periods);
        setFilters((current) => clampFiltersToAvailable(current, periods));
      })
      .catch(() => {
        if (cancelled) return;
        availableRef.current = null;
        setAvailablePeriods(null);
      });

    return () => {
      cancelled = true;
    };
  }, [retryCount]);

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
              dateRange: periodLabel(filters.period, filters.month, filters.year, filters.weekStart),
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
        availablePeriods,
        setPeriod,
        setMonth,
        setYear,
        setWeekStart,
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
