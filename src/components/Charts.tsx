import type { ReactNode } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { useDashboardData } from "../context/DashboardDataContext";
import { prettyPostTitle, shortPostLabel } from "../data";

const CHART_COLORS = ["#6EC100", "#FFDE00", "#FF6E02", "#FD8DFD", "#008B48", "#FE0000"];

export function ChartShell({
  id,
  title,
  caption,
  children,
  className = "",
  plotClassName = "h-48",
}: {
  id: string;
  title: string;
  caption?: string;
  children: ReactNode;
  className?: string;
  plotClassName?: string;
}) {
  return (
    <div className={`chart-export ${className}`} id={id}>
      <h3 className="font-display text-lg text-black mb-3">{title}</h3>
      <div className={`w-full ${plotClassName}`}>{children}</div>
      {caption ? <p className="mt-2 text-xs text-black/60 font-sans">{caption}</p> : null}
    </div>
  );
}

export function PostsOverTimeChart() {
  const { data } = useDashboardData();
  const chartData = data.months.map((month, index) => ({
    month,
    posts: data.postsByMonth[index],
  }));

  return (
    <ChartShell id="chart-posts-over-time" title="Posts over time" caption="Y-axis: post count">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#18181b22" />
          <XAxis dataKey="month" tick={{ fontSize: 11 }} />
          <YAxis tick={{ fontSize: 11 }} />
          <Tooltip />
          <Bar dataKey="posts" name="Posts" fill="#6EC100" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </ChartShell>
  );
}

export function ClaimsOverTimeChart() {
  const { data } = useDashboardData();
  const chartData = data.months.map((month, index) => ({
    month,
    claims: data.claimsByMonth[index],
  }));

  return (
    <ChartShell id="chart-claims-over-time" title="Claims over time" caption="Y-axis: claim count">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#18181b22" />
          <XAxis dataKey="month" tick={{ fontSize: 11 }} />
          <YAxis tick={{ fontSize: 11 }} />
          <Tooltip />
          <Line type="monotone" dataKey="claims" name="Claims" stroke="#008B48" strokeWidth={3} dot={{ r: 3 }} />
        </LineChart>
      </ResponsiveContainer>
    </ChartShell>
  );
}

export function ClaimsByHourChart() {
  const { data } = useDashboardData();
  const chartData = data.hours.map((hour, index) => ({
    hour,
    claims: data.claimsByHour[index],
  }));

  return (
    <ChartShell id="chart-claims-by-hour" title="Claims by time of day" caption="X-axis: hour · Y-axis: claims">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#18181b22" />
          <XAxis dataKey="hour" tick={{ fontSize: 11 }} />
          <YAxis tick={{ fontSize: 11 }} />
          <Tooltip />
          <Bar dataKey="claims" name="Claims" fill="#FFDE00" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </ChartShell>
  );
}

export function PostsByLocationChart() {
  const { data } = useDashboardData();
  const chartData = data.locations.map((location) => ({
    name: location.name,
    value: location.posts,
  }));

  return (
    <ChartShell id="chart-posts-by-location" title="Posts by location" caption="Share of posts by campus location">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie data={chartData} dataKey="value" nameKey="name" innerRadius={45} outerRadius={72} paddingAngle={2}>
            {chartData.map((entry, index) => (
              <Cell key={entry.name} fill={CHART_COLORS[index % CHART_COLORS.length]} stroke="#18181b" strokeWidth={1} />
            ))}
          </Pie>
          <Tooltip />
          <Legend wrapperStyle={{ fontSize: 11 }} />
        </PieChart>
      </ResponsiveContainer>
    </ChartShell>
  );
}

type ClaimViewRow = {
  row: string;
  title: string;
  location: string;
  views: number;
  claims: number;
  rate: number;
};

function ClaimsViewsTooltip({
  active,
  payload,
}: {
  active?: boolean;
  payload?: Array<{ payload: ClaimViewRow }>;
}) {
  if (!active || !payload?.[0]) return null;
  const row = payload[0].payload;
  return (
    <div className="rounded-lg border-2 border-black bg-white px-3 py-2 font-sans text-xs">
      <p className="font-semibold text-black">{row.title}</p>
      {row.location && row.location !== "—" ? <p className="text-black/70">{row.location}</p> : null}
      <p className="mt-1 text-black/80">
        {row.views} views · {row.claims} claims · {row.rate}% claimed
      </p>
    </div>
  );
}

export function ClaimsVsViewsChart() {
  const { data } = useDashboardData();
  const chartData: ClaimViewRow[] = [...data.posts]
    .sort((a, b) => b.views - a.views || b.claims - a.claims)
    .map((post, index) => {
      const title = prettyPostTitle(post);
      return {
        row: `${index + 1}. ${shortPostLabel(title, 28)}`,
        title,
        location: post.location,
        views: post.views,
        claims: post.claims,
        rate: post.claimRate,
      };
    });

  const rowPx = 38;
  const chartHeight = Math.max(220, chartData.length * rowPx + 36);

  return (
    <div className="chart-export" id="chart-claims-vs-views">
      <h3 className="font-display text-lg text-black mb-3">Claims vs views by post</h3>
      {chartData.length === 0 ? (
        <p className="font-sans text-sm text-black/70">No posts in this period to compare.</p>
      ) : (
        <>
          <div className="mb-2 flex flex-wrap gap-4 font-sans text-xs text-black/70">
            <span className="inline-flex items-center gap-1.5">
              <span className="inline-block h-2.5 w-4 rounded-sm border border-black bg-[#EDDBC3]" />
              Views
            </span>
            <span className="inline-flex items-center gap-1.5">
              <span className="inline-block h-2.5 w-4 rounded-sm border border-black bg-scGreen" />
              Claims
            </span>
          </div>
          <div className="max-h-80 overflow-y-auto overflow-x-hidden pr-1">
            <div style={{ height: chartHeight }}>
              <ResponsiveContainer width="100%" height={chartHeight}>
                <BarChart
                  data={chartData}
                  layout="vertical"
                  margin={{ top: 4, right: 16, bottom: 4, left: 4 }}
                  barCategoryGap={10}
                  barGap={2}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#18181b22" />
                  <XAxis type="number" tick={{ fontSize: 11 }} />
                  <YAxis
                    type="category"
                    dataKey="row"
                    width={168}
                    interval={0}
                    tick={{ fontSize: 11 }}
                  />
                  <Tooltip content={<ClaimsViewsTooltip />} />
                  <Bar dataKey="views" name="Views" fill="#EDDBC3" stroke="#18181b" strokeWidth={1} radius={[0, 4, 4, 0]} />
                  <Bar dataKey="claims" name="Claims" fill="#6EC100" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </>
      )}
      <p className="mt-2 text-xs text-black/60 font-sans">
        {chartData.length > 6
          ? `Scroll the chart to see all ${chartData.length} posts. Hover a bar for the full name.`
          : "Hover a bar for the full post name."}{" "}
        Sorted by views.
      </p>
    </div>
  );
}

export function StaffPostsChart() {
  const { data } = useDashboardData();
  const chartData = data.staff.map((member) => ({
    name: member.name,
    posts: member.posts,
  }));
  const rowPx = 36;
  const plotHeight = Math.max(240, chartData.length * rowPx + 32);

  return (
    <ChartShell
      id="chart-staff-posts"
      title="Posts Per Department"
      caption="One bar per posting department — hover a bar for the full name."
      plotClassName="max-h-[36rem] overflow-y-auto"
    >
      <div style={{ height: plotHeight, minHeight: 240 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            layout="vertical"
            margin={{ left: 12, right: 24, top: 8, bottom: 8 }}
            barCategoryGap={10}
            barSize={18}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#18181b22" />
            <XAxis type="number" tick={{ fontSize: 11 }} allowDecimals={false} />
            <YAxis
              type="category"
              dataKey="name"
              width={200}
              interval={0}
              tick={{ fontSize: 11 }}
              tickFormatter={(value: string) =>
                value.length > 28 ? `${value.slice(0, 26)}…` : value
              }
            />
            <Tooltip />
            <Bar dataKey="posts" name="Posts" fill="#FF6E02" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </ChartShell>
  );
}

export function WasteDivertedChart() {
  const { data } = useDashboardData();
  const chartData = data.wasteMonths.map((month, index) => ({
    month,
    lbs: data.wasteLbs[index],
  }));

  return (
    <ChartShell id="chart-waste-diverted" title="Food waste diverted (lbs)" caption="Estimated cumulative trend">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#18181b22" />
          <XAxis dataKey="month" tick={{ fontSize: 11 }} />
          <YAxis tick={{ fontSize: 11 }} />
          <Tooltip />
          <Line type="monotone" dataKey="lbs" name="Lbs diverted" stroke="#6EC100" strokeWidth={3} dot={{ r: 3 }} />
        </LineChart>
      </ResponsiveContainer>
    </ChartShell>
  );
}

export function ClimateImpactChart() {
  const { data } = useDashboardData();
  const chartData = data.climateMonths.map((month, index) => ({
    month,
    tco2e: data.climateTco2[index],
  }));

  return (
    <ChartShell id="chart-climate-impact" title="Estimated climate impact (tCO₂e)" caption="Emissions avoided from landfill diversion">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#18181b22" />
          <XAxis dataKey="month" tick={{ fontSize: 11 }} />
          <YAxis tick={{ fontSize: 11 }} />
          <Tooltip />
          <Line type="monotone" dataKey="tco2e" name="tCO₂e" stroke="#008B48" strokeWidth={3} dot={{ r: 3 }} />
        </LineChart>
      </ResponsiveContainer>
    </ChartShell>
  );
}
