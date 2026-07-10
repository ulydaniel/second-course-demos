import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";
import {
  fetchDashboardData,
  getApiErrorCode,
  getApiErrorKind,
  getApiErrorMessage,
  type ApiErrorKind,
  type DashboardData,
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

type DashboardDataState = {
  data: DashboardData;
  loading: boolean;
  error: string | null;
  errorKind: ApiErrorKind | null;
  errorCode: string | null;
  fromApi: boolean;
  retry: () => void;
};

const DashboardDataContext = createContext<DashboardDataState>({
  data: fallbackData,
  loading: true,
  error: null,
  errorKind: null,
  errorCode: null,
  fromApi: false,
  retry: () => undefined,
});

export function DashboardDataProvider({ children }: { children: ReactNode }) {
  const [retryCount, setRetryCount] = useState(0);
  const [state, setState] = useState<Omit<DashboardDataState, "retry">>({
    data: fallbackData,
    loading: true,
    error: null,
    errorKind: null,
    errorCode: null,
    fromApi: false,
  });

  const retry = useCallback(() => {
    setRetryCount((count) => count + 1);
  }, []);

  useEffect(() => {
    let cancelled = false;

    setState((current) => ({
      ...current,
      loading: true,
      error: null,
      errorKind: null,
      errorCode: null,
    }));

    fetchDashboardData()
      .then((data) => {
        if (!cancelled) {
          setState({
            data,
            loading: false,
            error: null,
            errorKind: null,
            errorCode: null,
            fromApi: true,
          });
        }
      })
      .catch((error: unknown) => {
        if (!cancelled) {
          setState({
            data: fallbackData,
            loading: false,
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
  }, [retryCount]);

  return (
    <DashboardDataContext.Provider value={{ ...state, retry }}>{children}</DashboardDataContext.Provider>
  );
}

export function useDashboardData() {
  return useContext(DashboardDataContext);
}
