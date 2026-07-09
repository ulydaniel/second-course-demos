import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { fetchDashboardData, type DashboardData } from "../api";
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
  fromApi: boolean;
};

const DashboardDataContext = createContext<DashboardDataState>({
  data: fallbackData,
  loading: true,
  error: null,
  fromApi: false,
});

export function DashboardDataProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<DashboardDataState>({
    data: fallbackData,
    loading: true,
    error: null,
    fromApi: false,
  });

  useEffect(() => {
    let cancelled = false;

    fetchDashboardData()
      .then((data) => {
        if (!cancelled) {
          setState({ data, loading: false, error: null, fromApi: true });
        }
      })
      .catch((error: unknown) => {
        if (!cancelled) {
          const message = error instanceof Error ? error.message : "Failed to load dashboard data";
          setState({ data: fallbackData, loading: false, error: message, fromApi: false });
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  return <DashboardDataContext.Provider value={state}>{children}</DashboardDataContext.Provider>;
}

export function useDashboardData() {
  return useContext(DashboardDataContext);
}
