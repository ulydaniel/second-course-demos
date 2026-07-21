export const UNIVERSITY = "San Diego State University";
export const DATE_RANGE = "Aug 2025 – Jun 2026";

export const MONTHS = ["Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun"];
export const POSTS_BY_MONTH = [42, 68, 91, 78, 55, 72, 88, 95, 102, 86, 70];
export const CLAIMS_BY_MONTH = [198, 312, 410, 356, 248, 334, 401, 438, 472, 398, 364];

export const HOURS = ["6a", "8a", "10a", "12p", "2p", "4p", "6p", "8p"];
export const CLAIMS_BY_HOUR = [12, 48, 92, 156, 134, 98, 64, 28];

export const LOCATIONS = [
  { name: "Alumni Center", posts: 312, claimRate: 76 },
  { name: "Student Union", posts: 248, claimRate: 71 },
  { name: "Aztec Recreation", posts: 186, claimRate: 52 },
  { name: "Engineering Quad", posts: 142, claimRate: 64 },
  { name: "Campus Events", posts: 98, claimRate: 58 },
];

export const DEMAND_GRID = [
  [2, 4, 8, 12, 10, 6, 3, 1],
  [3, 6, 14, 18, 15, 9, 4, 2],
  [1, 3, 9, 11, 8, 5, 2, 1],
  [4, 8, 16, 20, 17, 11, 5, 2],
  [2, 5, 11, 14, 12, 7, 3, 1],
];

export const DEMAND_LOCATIONS = ["Alumni Ctr", "Student Union", "Aztec Rec", "Eng. Quad", "Events"];
export const DEMAND_TIMES = ["7–9a", "9–11a", "11a–1p", "1–3p", "3–5p", "5–7p", "7–9p", "9–11p"];

export type Utilization = "high" | "medium" | "low";

export type StaffMember = {
  name: string;
  role: string;
  posts: number;
  lastPost: string;
  avgClaimMin: number;
  utilization: Utilization;
};

export const STAFF: StaffMember[] = [
  { name: "Maria G.", role: "Dining Hall Mgr", posts: 142, lastPost: "Today, 11:40a", avgClaimMin: 9.2, utilization: "high" },
  { name: "James T.", role: "Events Catering", posts: 118, lastPost: "Yesterday, 4:15p", avgClaimMin: 11.8, utilization: "high" },
  { name: "Priya S.", role: "Student Union", posts: 96, lastPost: "3 days ago", avgClaimMin: 14.1, utilization: "medium" },
  { name: "Alex R.", role: "Aztec Recreation", posts: 34, lastPost: "12 days ago", avgClaimMin: 22.4, utilization: "low" },
  { name: "Chris L.", role: "Campus Events", posts: 18, lastPost: "21 days ago", avgClaimMin: 31.6, utilization: "low" },
];

export type PostRecord = {
  id: string;
  title: string;
  staff: string;
  location: string;
  posted: string;
  postedAt: string;
  claims: number;
  views: number;
  claimRate: number;
  firstClaimMin: number;
  allergens: string;
  description: string;
  lbsDiverted: number;
};

export const POSTS: PostRecord[] = [
  {
    id: "P-1042",
    title: "Catered lunch surplus — sandwiches & fruit",
    staff: "Maria G.",
    location: "Alumni Center",
    posted: "Jun 12, 11:35a",
    postedAt: "2026-06-12T11:35",
    claims: 28,
    views: 41,
    claimRate: 68,
    firstClaimMin: 4.2,
    allergens: "Gluten, dairy",
    description: "Assorted wraps, fruit cups, and cookies from a 120-person conference.",
    lbsDiverted: 42,
  },
  {
    id: "P-1038",
    title: "Pizza & salad bar leftovers",
    staff: "James T.",
    location: "Student Union",
    posted: "Jun 11, 1:10p",
    postedAt: "2026-06-11T13:10",
    claims: 44,
    views: 52,
    claimRate: 85,
    firstClaimMin: 3.1,
    allergens: "Gluten, dairy, tree nuts",
    description: "Whole pizzas and mixed greens from a student org mixer.",
    lbsDiverted: 58,
  },
  {
    id: "P-1031",
    title: "Breakfast pastries & coffee service",
    staff: "Priya S.",
    location: "Engineering Quad",
    posted: "Jun 10, 8:50a",
    postedAt: "2026-06-10T08:50",
    claims: 19,
    views: 36,
    claimRate: 53,
    firstClaimMin: 18.7,
    allergens: "Gluten, eggs, dairy",
    description: "Croissants, muffins, and fruit from a morning department meeting.",
    lbsDiverted: 24,
  },
  {
    id: "P-1024",
    title: "Post-game catering trays",
    staff: "Alex R.",
    location: "Aztec Recreation",
    posted: "May 28, 6:20p",
    postedAt: "2026-05-28T18:20",
    claims: 8,
    views: 22,
    claimRate: 36,
    firstClaimMin: 42.0,
    allergens: "None listed",
    description: "Chicken tenders, veggie trays, and bottled water from intramural finals.",
    lbsDiverted: 16,
  },
];

export const WASTE_MONTHS = ["Aug", "Oct", "Dec", "Feb", "Apr", "Jun"];
export const WASTE_LBS = [180, 310, 420, 520, 680, 820];
export const CLIMATE_MONTHS = ["Aug", "Oct", "Dec", "Feb", "Apr", "Jun"];
export const CLIMATE_TCO2 = [0.08, 0.14, 0.19, 0.23, 0.3, 0.36];

export const SUMMARY = {
  totalPosts: 847,
  totalClaims: 4231,
  claimRate: 68,
  avgFirstClaimMin: 12.4,
  lbsDiverted: 3420,
  tco2e: 1.2,
  haulingSavings: 4280,
};

export const CHART_EXPORT_IDS = [
  "chart-posts-over-time",
  "chart-claims-over-time",
  "chart-claims-by-hour",
  "chart-posts-by-location",
  "chart-claims-vs-views",
  "chart-staff-posts",
  "chart-waste-diverted",
  "chart-climate-impact",
  "chart-demand-heatmap",
] as const;

export type ChartExportId = (typeof CHART_EXPORT_IDS)[number];

export type TabId = "overview" | "posts" | "demand" | "staff" | "impact" | "exports";

export const TABS: { id: TabId; label: string }[] = [
  { id: "overview", label: "Overview" },
  { id: "posts", label: "Posts & Claims" },
  { id: "demand", label: "Demand Map" },
  { id: "staff", label: "Staff Activity" },
  { id: "impact", label: "Impact" },
  { id: "exports", label: "Exports" },
];

export function periodLabel(period: string, month?: number, year?: number) {
  if (period === "week") return "Last 7 days";
  if (period === "month") {
    const names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    const m = month && month >= 1 && month <= 12 ? month : 6;
    const y = year ?? 2026;
    return `${names[m - 1]} ${y}`;
  }
  if (year != null) {
    const start = year === 2026 ? 2025 : year;
    return `Aug ${start} – Jun ${start + 1}`;
  }
  return DATE_RANGE;
}

export const CALENDAR_MONTHS = [
  { value: 1, label: "January" },
  { value: 2, label: "February" },
  { value: 3, label: "March" },
  { value: 4, label: "April" },
  { value: 5, label: "May" },
  { value: 6, label: "June" },
  { value: 7, label: "July" },
  { value: 8, label: "August" },
  { value: 9, label: "September" },
  { value: 10, label: "October" },
  { value: 11, label: "November" },
  { value: 12, label: "December" },
] as const;

export const FILTER_YEARS = [2024, 2025, 2026] as const;

export const ACADEMIC_YEAR_OPTIONS = [
  { value: 2024, label: "Aug 2024 – Jun 2025" },
  { value: 2025, label: "Aug 2025 – Jun 2026" },
] as const;
