// ==========================================================
// CleanAir AI — shared config
// ==========================================================
const DEFAULT_API_BASE = "http://localhost:8000";

// AQI category -> color (mirrors CSS custom properties in style.css)
const AQI_COLORS = {
  "good": "#4c9c72",
  "satisfactory": "#8fae55",
  "moderate": "#cfa53f",
  "poor": "#cd7f47",
  "very poor": "#bd5750",
  "severe": "#8c5bb0"
};

function aqiColor(category) {
  if (!category) return "#5f6f90";
  const key = String(category).trim().toLowerCase();
  return AQI_COLORS[key] || "#5f6f90";
}

// Rough AQI-category breath-ring pulse speed: worse category => faster pulse
const AQI_PULSE_SECONDS = {
  "good": 3.2,
  "satisfactory": 2.9,
  "moderate": 2.5,
  "poor": 2.1,
  "very poor": 1.7,
  "severe": 1.2
};

function aqiPulseSeconds(category) {
  if (!category) return 2.4;
  const key = String(category).trim().toLowerCase();
  return AQI_PULSE_SECONDS[key] || 2.4;
}

function fmtNum(v, digits = 1) {
  if (v === null || v === undefined || v === "" || Number.isNaN(Number(v))) return "—";
  const n = Number(v);
  if (Number.isInteger(n) && digits === 0) return n.toLocaleString("en-IN");
  return n.toLocaleString("en-IN", { maximumFractionDigits: digits, minimumFractionDigits: 0 });
}

function fmtPct(v, digits = 1) {
  if (v === null || v === undefined || v === "" || Number.isNaN(Number(v))) return "—";
  return `${Number(v).toLocaleString("en-IN", { maximumFractionDigits: digits })}%`;
}

function escapeHtml(str) {
  if (str === null || str === undefined) return "";
  return String(str)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function titleCase(key) {
  return String(key)
    .replaceAll("_", " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}
