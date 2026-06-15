import JSZip from "jszip";
import * as XLSX from "xlsx";
import {
  CLAIMS_BY_HOUR,
  CLAIMS_BY_MONTH,
  CLIMATE_TCO2,
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
} from "./data";

function triggerDownload(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

function csvEscape(value: string | number) {
  const text = String(value);
  if (text.includes(",") || text.includes('"') || text.includes("\n")) {
    return `"${text.replace(/"/g, '""')}"`;
  }
  return text;
}

export function downloadCsv(filename: string, headers: string[], rows: (string | number)[][]) {
  const lines = [headers.map(csvEscape).join(",")];
  for (const row of rows) {
    lines.push(row.map(csvEscape).join(","));
  }
  const blob = new Blob([lines.join("\n")], { type: "text/csv;charset=utf-8;" });
  triggerDownload(blob, filename);
}

function postsRows() {
  return POSTS.map((post) => [
    post.id,
    post.title,
    post.staff,
    post.location,
    post.postedAt,
    post.claims,
    post.views,
    post.claimRate / 100,
    post.firstClaimMin,
    post.allergens,
    post.description,
    post.lbsDiverted,
  ]);
}

export function downloadPostsCsv(periodLabel: string) {
  downloadCsv(`second-course-posts-${slugPeriod(periodLabel)}.csv`, [
    "post_id",
    "title",
    "staff",
    "location",
    "posted_at",
    "claims",
    "views",
    "claim_rate",
    "first_claim_min",
    "allergens",
    "description",
    "lbs_diverted",
  ], postsRows());
}

export function downloadAllDataXlsx(periodLabel: string) {
  const workbook = XLSX.utils.book_new();

  const postsSheet = XLSX.utils.aoa_to_sheet([
    ["post_id", "title", "staff", "location", "posted_at", "claims", "views", "claim_rate", "first_claim_min", "allergens", "description", "lbs_diverted"],
    ...postsRows(),
  ]);
  XLSX.utils.book_append_sheet(workbook, postsSheet, "Posts");

  const staffSheet = XLSX.utils.json_to_sheet(
    STAFF.map((member) => ({
      name: member.name,
      role: member.role,
      posts: member.posts,
      last_post: member.lastPost,
      avg_first_claim_min: member.avgClaimMin,
      utilization: member.utilization,
    })),
  );
  XLSX.utils.book_append_sheet(workbook, staffSheet, "Staff");

  const monthlySheet = XLSX.utils.aoa_to_sheet([
    ["month", "posts", "claims"],
    ...MONTHS.map((month, index) => [month, POSTS_BY_MONTH[index], CLAIMS_BY_MONTH[index]]),
  ]);
  XLSX.utils.book_append_sheet(workbook, monthlySheet, "Monthly");

  const summarySheet = XLSX.utils.json_to_sheet([
    { metric: "university", value: UNIVERSITY },
    { metric: "period", value: periodLabel },
    { metric: "total_posts", value: SUMMARY.totalPosts },
    { metric: "total_claims", value: SUMMARY.totalClaims },
    { metric: "claim_rate", value: SUMMARY.claimRate / 100 },
    { metric: "avg_first_claim_min", value: SUMMARY.avgFirstClaimMin },
    { metric: "lbs_diverted", value: SUMMARY.lbsDiverted },
    { metric: "tco2e_avoided", value: SUMMARY.tco2e },
    { metric: "hauling_savings_usd", value: SUMMARY.haulingSavings },
  ]);
  XLSX.utils.book_append_sheet(workbook, summarySheet, "Summary");

  const hourlySheet = XLSX.utils.aoa_to_sheet([
    ["hour", "claims"],
    ...HOURS.map((hour, index) => [hour, CLAIMS_BY_HOUR[index]]),
  ]);
  XLSX.utils.book_append_sheet(workbook, hourlySheet, "Claims by hour");

  const locationsSheet = XLSX.utils.json_to_sheet(
    LOCATIONS.map((location) => ({
      location: location.name,
      posts: location.posts,
      claim_rate: location.claimRate / 100,
    })),
  );
  XLSX.utils.book_append_sheet(workbook, locationsSheet, "Locations");

  const impactSheet = XLSX.utils.aoa_to_sheet([
    ["month", "lbs_diverted", "tco2e_avoided"],
    ...WASTE_MONTHS.map((month, index) => [month, WASTE_LBS[index], CLIMATE_TCO2[index]]),
  ]);
  XLSX.utils.book_append_sheet(workbook, impactSheet, "Impact");

  const output = XLSX.write(workbook, { bookType: "xlsx", type: "array" });
  triggerDownload(
    new Blob([output], { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" }),
    `second-course-dashboard-${slugPeriod(periodLabel)}.xlsx`,
  );
}

function slugPeriod(periodLabel: string) {
  return periodLabel.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");
}

async function svgToPng(svg: SVGSVGElement): Promise<Blob> {
  const clone = svg.cloneNode(true) as SVGSVGElement;
  if (!clone.getAttribute("xmlns")) {
    clone.setAttribute("xmlns", "http://www.w3.org/2000/svg");
  }
  const rect = svg.getBoundingClientRect();
  const width = Math.max(1, Math.ceil(rect.width));
  const height = Math.max(1, Math.ceil(rect.height));
  clone.setAttribute("width", String(width));
  clone.setAttribute("height", String(height));

  const serialized = new XMLSerializer().serializeToString(clone);
  const svgBlob = new Blob([serialized], { type: "image/svg+xml;charset=utf-8" });
  const url = URL.createObjectURL(svgBlob);

  try {
    const image = await loadImage(url);
    const canvas = document.createElement("canvas");
    canvas.width = width * 2;
    canvas.height = height * 2;
    const context = canvas.getContext("2d");
    if (!context) throw new Error("Canvas unavailable");
    context.scale(2, 2);
    context.fillStyle = "#ffffff";
    context.fillRect(0, 0, width, height);
    context.drawImage(image, 0, 0, width, height);
    return await new Promise((resolve, reject) => {
      canvas.toBlob((blob) => (blob ? resolve(blob) : reject(new Error("PNG export failed"))), "image/png");
    });
  } finally {
    URL.revokeObjectURL(url);
  }
}

function loadImage(url: string) {
  return new Promise<HTMLImageElement>((resolve, reject) => {
    const image = new Image();
    image.onload = () => resolve(image);
    image.onerror = () => reject(new Error("Failed to render chart image"));
    image.src = url;
  });
}

export async function downloadChartsZip(format: "png" | "svg", periodLabel: string) {
  const zip = new JSZip();
  let exported = 0;

  for (const element of document.querySelectorAll<HTMLElement>("[data-chart-export]")) {
    const chartId = element.dataset.chartExport;
    if (!chartId) continue;

    const svg = element.querySelector("svg");
    if (!svg) continue;

    const filename = `${chartId}.${format}`;
    if (format === "svg") {
      const clone = svg.cloneNode(true) as SVGSVGElement;
      if (!clone.getAttribute("xmlns")) {
        clone.setAttribute("xmlns", "http://www.w3.org/2000/svg");
      }
      zip.file(filename, new XMLSerializer().serializeToString(clone));
    } else {
      const png = await svgToPng(svg);
      zip.file(filename, png);
    }
    exported += 1;
  }

  if (exported === 0) {
    throw new Error("No charts found to export. Open the relevant dashboard tabs first.");
  }

  const blob = await zip.generateAsync({ type: "blob" });
  triggerDownload(blob, `second-course-charts-${format}-${slugPeriod(periodLabel)}.zip`);
}

export function downloadFullReport(periodLabel: string) {
  downloadAllDataXlsx(periodLabel);
}
