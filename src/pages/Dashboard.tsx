import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { ChartExportLibrary } from "../components/ChartExportLibrary";
import {
  ClaimsByHourChart,
  ClaimsOverTimeChart,
  ClaimsVsViewsChart,
  ClimateImpactChart,
  PostsByLocationChart,
  PostsOverTimeChart,
  StaffPostsChart,
  WasteDivertedChart,
} from "../components/Charts";
import { DemandHeatmap } from "../components/DemandHeatmap";
import { ResourcesScreen } from "../components/app/ResourcesScreen";
import {
  fetchDemographics,
  getApiErrorMessage,
  type DashboardPeriod,
  type DemographicsResponse,
} from "../api";
import { DashboardDataProvider, useDashboardData } from "../context/DashboardDataContext";
import {
  ACADEMIC_YEAR_OPTIONS,
  CALENDAR_MONTHS,
  FILTER_YEARS,
  TABS,
  weeksInMonth,
  periodLabel,
  type TabId,
} from "../data";
import {
  downloadAllDataXlsx,
  downloadChartsZip,
  downloadFullReport,
  downloadPostsCsv,
} from "../export";

function StatCard({ value, label, accent }: { value: string; label: string; accent?: "green" | "yellow" }) {
  const color = accent === "green" ? "text-brandGreen" : accent === "yellow" ? "text-scOrange" : "text-black";
  return (
    <div className="card p-4">
      <div className={`stat-value ${color}`}>{value}</div>
      <div className="stat-label">{label}</div>
    </div>
  );
}

function utilizationClass(utilization: "high" | "medium" | "low") {
  if (utilization === "high") return "bg-scGreen/30";
  if (utilization === "medium") return "bg-scYellow/50";
  return "bg-scOrange/30";
}

// Friendlier titles + preferred order for known demographic keys. Any key not
// listed here still renders (the backend surfaces new signup questions
// automatically); unknown keys fall back to a humanized version of the key.
const DEMOGRAPHIC_LABELS: Record<string, string> = {
  role: "Role",
  year: "Year in school",
  major: "Major",
  gradYear: "Graduation year",
  age: "Age",
  genderIdentity: "Gender identity",
  raceEthnicity: "Race / ethnicity",
  firstGen: "First-generation student",
  international: "International student",
  housing: "Housing",
  mealPlan: "Has meal plan",
  foodWorry: "Food insecurity worry",
  calfresh: "CalFresh status",
  dietary: "Dietary needs",
  commute: "Commute",
};
const DEMOGRAPHIC_ORDER = ["year", "major", "housing", "foodWorry", "firstGen", "calfresh"];

function humanizeKey(key: string): string {
  if (DEMOGRAPHIC_LABELS[key]) return DEMOGRAPHIC_LABELS[key];
  return key.replace(/([a-z])([A-Z])/g, "$1 $2").replace(/^./, (c) => c.toUpperCase());
}

function orderedFieldKeys(fields: Record<string, unknown>): string[] {
  const keys = Object.keys(fields);
  const known = DEMOGRAPHIC_ORDER.filter((k) => keys.includes(k));
  const rest = keys.filter((k) => !DEMOGRAPHIC_ORDER.includes(k)).sort();
  return [...known, ...rest];
}

function DemographicsPanel() {
  const [data, setData] = useState<DemographicsResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    fetchDemographics()
      .then((result) => {
        if (!cancelled) {
          setData(result);
          setError(null);
        }
      })
      .catch((fetchError) => {
        if (!cancelled) setError(getApiErrorMessage(fetchError));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (loading) {
    return (
      <div className="callout-neutral">
        <strong className="block mb-1">Student demographics</strong>
        Loading cohort-level aggregates…
      </div>
    );
  }

  if (error) {
    return (
      <div className="callout-warning">
        <strong className="block mb-1">Student demographics unavailable</strong>
        {error}
      </div>
    );
  }

  const fieldKeys = data ? orderedFieldKeys(data.fields) : [];
  const hasData = data && data.respondentCount > 0 && fieldKeys.length > 0;

  return (
    <div className="card p-4 space-y-4">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h2 className="font-display text-lg">Student demographics (cohort-level)</h2>
        {data ? (
          <span className="text-xs text-black/60">
            {data.respondentCount.toLocaleString()} of {data.userCount.toLocaleString()} students
            responded
          </span>
        ) : null}
      </div>
      <p className="text-sm text-black/70 font-sans">
        Aggregated from the student app and scoped to your campus. Individual responses are never
        shown; groups smaller than {data?.minCellSize ?? 5} are suppressed to protect privacy.
      </p>

      {hasData ? (
        <div className="grid gap-4 md:grid-cols-2">
          {fieldKeys.map((key) => {
            const buckets = data!.fields[key];
            const total = buckets.reduce((sum, bucket) => sum + bucket.count, 0) || 1;
            return (
              <div key={key} className="rounded-xl border-2 border-black/10 p-3">
                <h3 className="font-display text-sm mb-2">{humanizeKey(key)}</h3>
                <div className="space-y-1.5">
                  {buckets.slice(0, 8).map((bucket) => {
                    const pct = Math.round((bucket.count / total) * 100);
                    return (
                      <div key={bucket.label}>
                        <div className="flex justify-between text-xs text-black/70">
                          <span className="truncate pr-2">{bucket.label}</span>
                          <span className="shrink-0 tabular-nums">
                            {bucket.count} · {pct}%
                          </span>
                        </div>
                        <div className="h-2 w-full overflow-hidden rounded-full bg-black/5">
                          <div
                            className="h-full rounded-full bg-brandGreen"
                            style={{ width: `${pct}%` }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <p className="text-sm text-black/60 font-sans">
          No demographic responses are available for this campus yet
          {data?.suppressed ? ", or all groups fell below the privacy threshold" : ""}. Breakdowns
          appear here once enough students complete the optional signup survey.
        </p>
      )}
    </div>
  );
}

function TabPanel({ active, id, children }: { active: boolean; id: TabId; children: React.ReactNode }) {
  return (
    <div hidden={!active} id={`panel-${id}`} role="tabpanel" aria-labelledby={`tab-${id}`} className="space-y-6">
      {children}
    </div>
  );
}

export default function Dashboard() {
  return (
    <DashboardDataProvider>
      <DashboardContent />
    </DashboardDataProvider>
  );
}

function DashboardContent() {
  const {
    data,
    period,
    filters,
    setPeriod,
    setMonth,
    setYear,
    setWeekStart,
    loading,
    refreshing,
    error,
    errorKind,
    errorCode,
    fromApi,
    retry,
  } = useDashboardData();
  const { user } = useAuth();
  const { university, summary, locations, posts, staff } = data;
  const [activeTab, setActiveTab] = useState<TabId>("overview");
  const [exportStatus, setExportStatus] = useState<string | null>(null);
  const [exporting, setExporting] = useState(false);
  const label = periodLabel(period, filters.month, filters.year, filters.weekStart);
  const weekOptions = period === "week" ? weeksInMonth(filters.month, filters.year) : [];

  const avgClaimsPerPost =
    posts.length > 0 ? posts.reduce((sum, post) => sum + post.claims, 0) / posts.length : 0;
  const avgViewsPerPost =
    posts.length > 0 ? posts.reduce((sum, post) => sum + post.views, 0) / posts.length : 0;

  const topTimeSlots = [...data.hours]
    .map((hour, index) => ({
      time: hour,
      claims: data.claimsByHour[index] ?? 0,
    }))
    .sort((a, b) => b.claims - a.claims)
    .slice(0, 4)
    .map((slot) => {
      const peak = Math.max(...data.claimsByHour, 1);
      const rate = Math.round((slot.claims / peak) * 100);
      return [slot.time, slot.claims.toFixed(0), `${rate}%`] as const;
    });

  async function runExport(action: () => void | Promise<void>, successMessage: string) {
    setExporting(true);
    setExportStatus(null);
    try {
      await action();
      setExportStatus(successMessage);
    } catch (error) {
      setExportStatus(error instanceof Error ? error.message : "Export failed");
    } finally {
      setExporting(false);
    }
  }

  const lowUtilStaff = staff.filter((member) => member.utilization === "low");

  if (loading) {
    return (
      <div className="min-h-screen bg-cream px-4 py-8">
        <div className="mx-auto max-w-5xl font-sans text-black/80">Loading dashboard data…</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-cream px-4 py-8">
      <div className="relative mx-auto max-w-5xl">
        <div className="pointer-events-none absolute -top-2 right-0 z-10 floating-character hidden md:block">
          <img
            src={`${import.meta.env.BASE_URL}images/SC_apple_transp.png`}
            alt=""
            className="h-32 w-auto drop-shadow-[8px_8px_0_rgba(0,0,0,0.35)]"
          />
        </div>

        <header className="relative z-20 mb-8 space-y-4 pr-0 md:pr-36">
          <div className="space-y-2">
            <img
              src={`${import.meta.env.BASE_URL}images/second-course-logo.png`}
              alt="Second Course"
              className="h-10 w-auto md:h-12"
            />
            <h1 className="font-display text-3xl text-black md:text-4xl">University Dashboard</h1>
            <p className="font-sans text-black/80">{university}</p>
            {user ? (
              <p className="font-sans text-xs text-black/60">
                Signed in as {user.email}
                {user.university ? ` · ${user.university.name}` : ""}
              </p>
            ) : null}
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <select
              className="period-select"
              value={period}
              onChange={(event) => setPeriod(event.target.value as DashboardPeriod)}
              aria-label="Date range"
              disabled={refreshing}
            >
              <option value="week">Week</option>
              <option value="month">Calendar month</option>
              <option value="year">Academic year</option>
            </select>
            {period === "week" ? (
              <>
                <select
                  className="period-select"
                  value={filters.month}
                  onChange={(event) => setMonth(Number(event.target.value))}
                  aria-label="Month"
                  disabled={refreshing}
                >
                  {CALENDAR_MONTHS.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
                <select
                  className="period-select"
                  value={filters.year}
                  onChange={(event) => setYear(Number(event.target.value))}
                  aria-label="Year"
                  disabled={refreshing}
                >
                  {FILTER_YEARS.map((year) => (
                    <option key={year} value={year}>
                      {year}
                    </option>
                  ))}
                </select>
                <select
                  className="period-select"
                  value={filters.weekStart}
                  onChange={(event) => setWeekStart(event.target.value)}
                  aria-label="Week"
                  disabled={refreshing || weekOptions.length === 0}
                >
                  {weekOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </>
            ) : null}
            {period === "month" ? (
              <>
                <select
                  className="period-select"
                  value={filters.month}
                  onChange={(event) => setMonth(Number(event.target.value))}
                  aria-label="Month"
                  disabled={refreshing}
                >
                  {CALENDAR_MONTHS.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
                <select
                  className="period-select"
                  value={filters.year}
                  onChange={(event) => setYear(Number(event.target.value))}
                  aria-label="Year"
                  disabled={refreshing}
                >
                  {FILTER_YEARS.map((year) => (
                    <option key={year} value={year}>
                      {year}
                    </option>
                  ))}
                </select>
              </>
            ) : null}
            {period === "year" ? (
              <select
                className="period-select"
                value={filters.year === 2026 ? 2025 : filters.year}
                onChange={(event) => setYear(Number(event.target.value))}
                aria-label="Academic year"
                disabled={refreshing}
              >
                {ACADEMIC_YEAR_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            ) : null}
            <button
              type="button"
              className="btn-secondary"
              disabled={exporting}
              onClick={() => runExport(() => downloadFullReport(label), "Report downloaded.")}
            >
              Download report
            </button>
          </div>
        </header>

        <div className="mb-4 space-y-2">
          {error ? (
            <div className="callout-warning">
              <strong className="block mb-1">
                {errorKind === "network"
                  ? "Cannot reach API server"
                  : errorKind === "server"
                    ? "Server error"
                    : "API request failed"}
              </strong>
              <p className="mb-2">{error}</p>
              <p className="text-sm text-black/70 mb-2">
                Showing built-in sample data until the API responds. For local development, run{" "}
                <code>uvicorn app.main:app --reload</code> in <code>backend/</code>.
              </p>
              {errorCode ? (
                <p className="text-xs text-black/50 mb-2">Error code: {errorCode}</p>
              ) : null}
              <button type="button" className="btn-secondary" onClick={retry}>
                Retry connection
              </button>
            </div>
          ) : !fromApi ? (
            <div className="callout-warning">
              <strong className="block mb-1">Demo preview</strong>
              Sample data for design review only — not connected to live Second Course metrics.
            </div>
          ) : null}
        </div>

        <div className="mb-6 flex flex-wrap gap-2" role="tablist" aria-label="Dashboard sections">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              type="button"
              role="tab"
              id={`tab-${tab.id}`}
              aria-selected={activeTab === tab.id}
              aria-controls={`panel-${tab.id}`}
              className={`pill ${activeTab === tab.id ? "pill-active" : "bg-white"}`}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {exportStatus ? (
          <div className={`mb-4 callout ${exportStatus.includes("failed") || exportStatus.includes("No charts") ? "callout-warning" : "callout-info"}`}>
            {exportStatus}
          </div>
        ) : null}

        <TabPanel active={activeTab === "overview"} id="overview">
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            <StatCard value={String(summary.totalPosts)} label="Posts (period)" />
            <StatCard value={summary.totalClaims.toLocaleString()} label="Total claims" accent="green" />
            <StatCard value={`${summary.claimRate}%`} label="Claim rate" accent="yellow" />
            <StatCard value={`${summary.avgFirstClaimMin} min`} label="Avg time to first claim" />
          </div>
          <div className="grid gap-4 lg:grid-cols-2">
            <PostsOverTimeChart />
            <ClaimsOverTimeChart />
          </div>
          <div className="grid gap-4 lg:grid-cols-2">
            <ClaimsByHourChart />
            <PostsByLocationChart />
          </div>
          <div className="callout-info">
            <strong className="block mb-1">Smart aggregations</strong>
            Peak demand clusters around lunch (11a–1p) at Alumni Center and Student Union. Evening posts at
            Aztec Recreation underperform — consider timing or staff outreach.
          </div>
          <p className="text-xs text-black/60 font-sans">Source: Second Course · {label}</p>
        </TabPanel>

        <TabPanel active={activeTab === "posts"} id="posts">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <StatCard value={`${summary.claimRate}%`} label="Overall claim rate" accent="yellow" />
            <StatCard value={avgClaimsPerPost.toFixed(1)} label="Avg claims per post" />
            <StatCard value={avgViewsPerPost.toFixed(1)} label="Avg views per post" />
          </div>
          <ClaimsVsViewsChart />
          <h2 className="font-display text-xl">Individual posts</h2>
          <div className="space-y-3">
            {posts.map((post) => (
              <details key={post.id} className="card p-4">
                <summary className="cursor-pointer font-sans text-sm font-semibold">
                  {post.id} — {post.title}
                  <span className="ml-2 text-black/60">{post.claimRate}% claimed</span>
                </summary>
                <div className="mt-3 space-y-2 font-sans text-sm text-black/80">
                  <p>
                    Posted by {post.staff} · {post.location} · {post.posted}
                  </p>
                  <p>{post.description}</p>
                  <div className="flex flex-wrap gap-2">
                    <span className="pill bg-scOrange/20 text-xs">Allergens: {post.allergens}</span>
                    <span className="pill bg-white text-xs">
                      {post.claims} claims / {post.views} views
                    </span>
                    <span className="pill bg-white text-xs">First claim: {post.firstClaimMin} min</span>
                  </div>
                </div>
              </details>
            ))}
          </div>
        </TabPanel>

        <TabPanel active={activeTab === "demand"} id="demand">
          <p className="font-sans text-black/80">
            Demand map shows when and where posts perform best — useful for staffing, outreach, and event planning.
          </p>
          <div className="card p-4">
            <div className="mb-3 flex items-center justify-between gap-2">
              <h2 className="font-display text-lg">Performance by location and time</h2>
              <span className="pill pill-active text-xs">Peak window</span>
            </div>
            <DemandHeatmap />
            <p className="mt-2 text-xs text-black/60 font-sans">Cell value = claim rate index (0–20) · {label}</p>
          </div>
          <div className="grid gap-4 lg:grid-cols-2">
            <div>
              <h3 className="font-display text-lg mb-2">Best-performing time slots</h3>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Time</th>
                    <th>Avg claims</th>
                    <th>Claim rate</th>
                  </tr>
                </thead>
                <tbody>
                  {topTimeSlots.map((row) => (
                    <tr key={row[0]}>
                      <td>{row[0]}</td>
                      <td className="text-right">{row[1]}</td>
                      <td className="text-right">{row[2]}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div>
              <h3 className="font-display text-lg mb-2">Best-performing locations</h3>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Location</th>
                    <th>Posts</th>
                    <th>Claim rate</th>
                  </tr>
                </thead>
                <tbody>
                  {locations.map((location) => (
                    <tr key={location.name}>
                      <td>{location.name}</td>
                      <td className="text-right">{location.posts}</td>
                      <td className="text-right">{location.claimRate}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </TabPanel>

        <TabPanel active={activeTab === "staff"} id="staff">
          <p className="font-sans text-black/80">
            Track which staff post, when they post, and whether units are underutilizing the platform.
          </p>
          {lowUtilStaff.length > 0 ? (
            <div className="callout-warning">
              <strong className="block mb-1">Underutilization detected</strong>
              {lowUtilStaff.map((member) => member.name).join(" and ")} have not posted recently. Consider outreach or
              training to increase campus coverage.
            </div>
          ) : null}
          <h2 className="font-display text-xl">Staff posting activity</h2>
          <div className="card overflow-x-auto p-0">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Staff</th>
                  <th>Role</th>
                  <th>Posts</th>
                  <th>Last post</th>
                  <th>Avg first claim</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {staff.map((member) => (
                  <tr key={member.name}>
                    <td>{member.name}</td>
                    <td>{member.role}</td>
                    <td className="text-right">{member.posts}</td>
                    <td>{member.lastPost}</td>
                    <td className="text-right">{member.avgClaimMin} min</td>
                    <td>
                      <span className={`pill text-xs capitalize ${utilizationClass(member.utilization)}`}>
                        {member.utilization}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <StaffPostsChart />
        </TabPanel>

        <TabPanel active={activeTab === "resources"} id="resources">
          <p className="font-sans text-black/80">
            Campus pantries, events calendar, and the student bulletin — the same Resources
            experience students see in the app.
          </p>
          <ResourcesScreen />
        </TabPanel>

        <TabPanel active={activeTab === "impact"} id="impact">
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            <StatCard value={summary.totalPosts.toLocaleString()} label="Food posts (period)" />
            <StatCard value={`${summary.lbsDiverted.toLocaleString()} lbs`} label="Food diverted (est.)" accent="green" />
            <StatCard value={`$${summary.mealValue.toLocaleString()}`} label="Student meal value (est.)" accent="green" />
            <StatCard value={`$${summary.haulingSavings.toLocaleString()}`} label="Waste hauling savings (est.)" />
          </div>
          <div className="grid gap-4 lg:grid-cols-2">
            <WasteDivertedChart />
            <ClimateImpactChart />
          </div>
          <DemographicsPanel />
          <div className="card p-4">
            <h2 className="font-display text-lg mb-3">Smart aggregation — sustainability snapshot</h2>
            <div className="grid gap-4 md:grid-cols-2 font-sans text-sm text-black/80">
              <div>
                <p className="font-semibold text-black">Grant-ready metrics</p>
                <p>
                  {summary.lbsDiverted.toLocaleString()} lbs diverted · {summary.totalClaims.toLocaleString()} student
                  meals claimed · {summary.claimRate}% utilization of posted food
                </p>
              </div>
              <div>
                <p className="font-semibold text-black">Engagement signal</p>
                <p>
                  Avg time to first claim: {summary.avgFirstClaimMin} min — indicates an active,
                  responsive student network
                </p>
              </div>
            </div>
          </div>
        </TabPanel>

        <TabPanel active={activeTab === "exports"} id="exports">
          <p className="font-sans text-black/80">
            Download raw data for grant reports, sustainability audits, or internal review. Chart exports bundle every
            chart on the dashboard into a single zip file.
          </p>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="card p-4 space-y-3">
              <h2 className="font-display text-lg">Spreadsheet export</h2>
              <p className="text-sm text-black/70 font-sans">
                Posts, staff, monthly trends, locations, and impact estimates as Excel or CSV.
              </p>
              <div className="flex flex-wrap gap-2">
                <button
                  type="button"
                  className="btn-primary"
                  disabled={exporting}
                  onClick={() =>
                    runExport(() => downloadAllDataXlsx(label), "All data downloaded as .xlsx")
                  }
                >
                  Download all data (.xlsx)
                </button>
                <button
                  type="button"
                  className="btn-secondary"
                  disabled={exporting}
                  onClick={() => runExport(() => downloadPostsCsv(label), "Posts downloaded as .csv")}
                >
                  Posts only (.csv)
                </button>
              </div>
            </div>
            <div className="card p-4 space-y-3">
              <h2 className="font-display text-lg">Chart exports</h2>
              <p className="text-sm text-black/70 font-sans">
                PNG or SVG zip of all dashboard charts for presentations and reports.
              </p>
              <div className="flex flex-wrap gap-2">
                <button
                  type="button"
                  className="btn-primary"
                  disabled={exporting}
                  onClick={() =>
                    runExport(() => downloadChartsZip("png", label), "Charts downloaded as PNG zip.")
                  }
                >
                  Export charts (PNG)
                </button>
                <button
                  type="button"
                  className="btn-secondary"
                  disabled={exporting}
                  onClick={() =>
                    runExport(() => downloadChartsZip("svg", label), "Charts downloaded as SVG zip.")
                  }
                >
                  Export charts (SVG)
                </button>
              </div>
            </div>
          </div>
          <div>
            <h3 className="font-display text-lg mb-2">Export preview</h3>
            <pre className="card overflow-x-auto p-4 text-xs font-mono text-black/80">
              {`post_id,title,staff,location,posted_at,claims,views,claim_rate,first_claim_min,allergens,lbs_diverted
${posts
  .slice(0, 2)
  .map(
    (post) =>
      `${post.id},${post.title.replaceAll(",", ";")},${post.staff},${post.location},${post.postedAt},${post.claims},${post.views},${(post.claimRate / 100).toFixed(2)},${post.firstClaimMin},${post.allergens.replaceAll(",", ";")},${post.lbsDiverted}`,
  )
  .join("\n")}`}
            </pre>
          </div>
        </TabPanel>

        <ChartExportLibrary />

        <footer className="mt-10 flex flex-col items-center gap-2 text-sm text-black/70 font-sans">
          <a href="https://www.instagram.com/haveasecondcourse/" className="underline hover:text-black">
            @haveasecondcourse
          </a>
          <a href="mailto:support@secondcourse.co" className="underline hover:text-black">
            support@secondcourse.co
          </a>
        </footer>
      </div>
    </div>
  );
}
