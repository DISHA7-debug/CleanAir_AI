// ==========================================================
// CleanAir AI — application logic
// ==========================================================
(() => {
  "use strict";

  const state = {
    filters: { state: "", city: "", station: "", lang: "en" },
    stationsAll: [],       // full station_advanced_intelligence rows (capped)
    citiesAll: [],         // city_advanced_intelligence_summary rows
    hotspotSummary: null,
    mapDataAll: [],
    loadedTabs: new Set(),
    charts: {},
    leaflet: { map: null, markers: [] },
    priorityQueueRows: []
  };

  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  // -------------------- TOAST --------------------
  let toastTimer = null;
  function toast(msg, ms = 3200) {
    const el = $("#toast");
    el.textContent = msg;
    el.classList.add("is-visible");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => el.classList.remove("is-visible"), ms);
  }

  // -------------------- API BASE / CONNECTION --------------------
  function initApiBase() {
    const input = $("#apiBaseInput");
    input.value = Api.getBase();
    input.addEventListener("change", () => {
      Api.setBase(input.value || DEFAULT_API_BASE);
      checkConnection();
      bootstrapData(true);
    });
    checkConnection();
  }

  async function checkConnection() {
    const statusEl = $("#apiStatus");
    const textEl = $("#apiStatusText");
    statusEl.classList.remove("ok", "bad");
    textEl.textContent = "Checking connection…";
    try {
      await Api.health();
      statusEl.classList.add("ok");
      textEl.textContent = "Connected to backend";
    } catch (e) {
      statusEl.classList.add("bad");
      textEl.textContent = "Backend unreachable";
    }
  }

  // -------------------- SIDEBAR (mobile) --------------------
  function initSidebarToggle() {
    const sidebar = $("#sidebar");
    const scrim = $("#sidebarScrim");
    const open = () => { sidebar.classList.add("is-open"); scrim.classList.add("is-open"); };
    const close = () => { sidebar.classList.remove("is-open"); scrim.classList.remove("is-open"); };
    $("#menuBtn").addEventListener("click", open);
    $("#sidebarClose").addEventListener("click", close);
    scrim.addEventListener("click", close);
  }

  // -------------------- TAB NAV --------------------
  const TAB_TITLES = {
    live: "Live Intelligence",
    maps: "Maps & Hotspots",
    advanced: "Advanced Layers",
    ml: "ML Forecasting",
    queue: "Priority Queue"
  };

  function initTabs() {
    $$(".tabnav-item").forEach((btn) => {
      btn.addEventListener("click", () => activateTab(btn.dataset.tab));
    });
  }

  function activateTab(tab) {
    $$(".tabnav-item").forEach((b) => b.classList.toggle("is-active", b.dataset.tab === tab));
    $$(".tab-panel").forEach((p) => p.classList.toggle("is-active", p.dataset.tabPanel === tab));
    $("#pageTitle").textContent = TAB_TITLES[tab] || "CleanAir AI";
    ensureTabData(tab);
    if (window.innerWidth <= 760) {
      $("#sidebar").classList.remove("is-open");
      $("#sidebarScrim").classList.remove("is-open");
    }
    if (tab === "maps") setTimeout(() => state.leaflet.map && state.leaflet.map.invalidateSize(), 60);
  }

  function ensureTabData(tab) {
    if (state.loadedTabs.has(tab)) {
      // re-render with current filters (cheap, cached data)
      renderTab(tab);
      return;
    }
    state.loadedTabs.add(tab);
    renderTab(tab);
  }

  function renderTab(tab) {
    if (tab === "live") renderLiveTab();
    if (tab === "maps") renderMapsTab();
    if (tab === "advanced") renderAdvancedTab();
    if (tab === "ml") renderMlTab();
    if (tab === "queue") renderQueueTab();
  }

  // -------------------- FILTER HELPERS --------------------
  function filteredStations() {
    return state.stationsAll.filter((s) => {
      if (state.filters.state && (s.state || "").toLowerCase() !== state.filters.state.toLowerCase()) return false;
      if (state.filters.city && (s.city || "").toLowerCase() !== state.filters.city.toLowerCase()) return false;
      if (state.filters.station && s.station_id !== state.filters.station) return false;
      return true;
    });
  }

  // -------------------- FILTERS: populate + cascade --------------------
  function populateFilters() {
    const stateSelect = $("#stateSelect");
    const citySelect = $("#citySelect");
    const stationSelect = $("#stationSelect");

    const states = [...new Set(state.stationsAll.map((s) => s.state).filter(Boolean))].sort();
    stateSelect.innerHTML = `<option value="">All states</option>` +
      states.map((s) => `<option value="${escapeHtml(s)}">${escapeHtml(s)}</option>`).join("");

    refreshCityOptions();
    refreshStationOptions();

    stateSelect.addEventListener("change", () => {
      state.filters.state = stateSelect.value;
      state.filters.city = "";
      state.filters.station = "";
      refreshCityOptions();
      refreshStationOptions();
      onFiltersChanged();
    });
    citySelect.addEventListener("change", () => {
      state.filters.city = citySelect.value;
      state.filters.station = "";
      refreshStationOptions();
      onFiltersChanged();
    });
    stationSelect.addEventListener("change", () => {
      state.filters.station = stationSelect.value;
      onFiltersChanged();
    });
    $("#langSelect").addEventListener("change", (e) => {
      state.filters.lang = e.target.value;
      onFiltersChanged();
    });
  }

  function refreshCityOptions() {
    const citySelect = $("#citySelect");
    const pool = state.filters.state
      ? state.stationsAll.filter((s) => (s.state || "").toLowerCase() === state.filters.state.toLowerCase())
      : state.stationsAll;
    const cities = [...new Set(pool.map((s) => s.city).filter(Boolean))].sort();
    citySelect.innerHTML = `<option value="">All cities</option>` +
      cities.map((c) => `<option value="${escapeHtml(c)}">${escapeHtml(c)}</option>`).join("");
    citySelect.value = state.filters.city;
  }

  function refreshStationOptions() {
    const stationSelect = $("#stationSelect");
    let pool = state.stationsAll;
    if (state.filters.state) pool = pool.filter((s) => (s.state || "").toLowerCase() === state.filters.state.toLowerCase());
    if (state.filters.city) pool = pool.filter((s) => (s.city || "").toLowerCase() === state.filters.city.toLowerCase());
    stationSelect.innerHTML = `<option value="">All stations</option>` +
      pool.map((s) => `<option value="${escapeHtml(s.station_id)}">${escapeHtml(s.station_name)}</option>`).join("");
    stationSelect.value = state.filters.station;
  }

  function onFiltersChanged() {
    // Re-render whichever tab is currently visible + keep others fresh on next visit
    const activeTab = $(".tabnav-item.is-active")?.dataset.tab || "live";
    renderTab(activeTab);
    // Invalidate cached renders for other tabs so they rebuild with new filters when opened
    state.loadedTabs = new Set([activeTab]);
  }

  // -------------------- HEADER METRIC STRIP --------------------
  function renderHeaderMetrics() {
    const summary = state.hotspotSummary;
    $("#mStations").textContent = summary ? fmtNum(summary.total_stations, 0) : fmtNum(state.stationsAll.length, 0);
    $("#mCities").textContent = summary ? fmtNum(summary.total_cities, 0) : "—";
    $("#mStates").textContent = summary ? fmtNum(summary.total_states, 0) : "—";

    const highest = [...state.stationsAll].sort((a, b) => (b.current_aqi || 0) - (a.current_aqi || 0))[0];
    if (highest) {
      $("#mHighestValue").textContent = fmtNum(highest.current_aqi, 0);
      $("#mHighestValue").style.color = aqiColor(highest.current_aqi_category);
      $("#mHighestName").textContent = `${highest.station_name || "—"} · ${highest.city || ""}`;
      const secs = aqiPulseSeconds(highest.current_aqi_category);
      $$("#breathRing span").forEach((s) => {
        s.style.borderColor = aqiColor(highest.current_aqi_category);
        s.style.animationDuration = `${secs}s`;
      });
    }
  }

  // -------------------- TAB 1: LIVE INTELLIGENCE --------------------
  async function renderLiveTab() {
    const grid = $("#stationGrid");
    let rows = filteredStations();
    // avoid rendering hundreds of cards with no filter applied — show top priority stations
    const capped = (!state.filters.city && !state.filters.station && !state.filters.state);
    if (capped) {
      rows = [...rows].sort((a, b) => (b.advanced_priority_score || 0) - (a.advanced_priority_score || 0)).slice(0, 24);
    }

    if (!rows.length) {
      grid.innerHTML = `<div class="empty-state">No stations match the current filters.</div>`;
      return;
    }

    grid.innerHTML = rows.map(stationCardSkeletonHtml).join("");

    // fetch advisories in parallel per unique category (cheap — one call per distinct category, not per station)
    const categories = [...new Set(rows.map((r) => r.current_aqi_category).filter(Boolean))];
    const advisoryMap = {};
    await Promise.all(categories.map(async (cat) => {
      try {
        advisoryMap[cat] = await Api.advisory(cat, state.filters.lang);
      } catch (e) {
        advisoryMap[cat] = { advisory: "Advisory not available for this category." };
      }
    }));

    grid.innerHTML = rows.map((r) => stationCardHtml(r, advisoryMap[r.current_aqi_category])).join("");

    if (capped) {
      const note = document.createElement("p");
      note.className = "fineprint";
      note.style.marginTop = "4px";
      note.textContent = `Showing the ${rows.length} highest-priority stations nationally. Use the sidebar filters to narrow to a state, city, or single station.`;
      grid.after(note);
    }
  }

  function stationCardSkeletonHtml() {
    return `<div class="skeleton-card"></div>`;
  }

  function stationCardHtml(r, advisory) {
    const color = aqiColor(r.current_aqi_category);
    const conf = r.source_attribution_confidence_category || r.source_attribution_confidence || "";
    return `
      <div class="station-card" style="--cat-color:${color}">
        <div class="station-card-top">
          <div>
            <div class="station-name">${escapeHtml(r.station_name || "Unnamed station")}</div>
            <div class="station-loc">${escapeHtml(r.city || "")}, ${escapeHtml(r.state || "")}</div>
          </div>
          <span class="badge" style="--cat-color:${color}">${escapeHtml(r.current_aqi_category || "Unknown")}</span>
        </div>
        <div class="station-aqi">${fmtNum(r.current_aqi, 0)}</div>
        <div class="station-aqi-label">Current AQI · dominant: ${escapeHtml(r.reported_dominant_pollutant || "—")}</div>
        <div class="station-rows">
          <div class="station-row"><span class="k">Pollution source</span><span class="v">${escapeHtml(r.primary_pollution_source || "—")}</span></div>
          <div class="station-row"><span class="k">Source confidence</span><span class="v"><span class="confidence-chip">${escapeHtml(conf || "—")}</span></span></div>
          <div class="station-row"><span class="k">Priority score</span><span class="v">${fmtNum(r.advanced_priority_score)} <span style="color:var(--muted-2)">(${escapeHtml(r.advanced_priority_category || "—")})</span></span></div>
          <div class="station-row"><span class="k">Hotspot status</span><span class="v">${escapeHtml(r.hotspot_status || "—")}</span></div>
        </div>
        <div class="advisory-box">
          <span class="advisory-title">Citizen advisory</span>
          ${escapeHtml(advisory?.advisory || "Advisory not available.")}
        </div>
      </div>`;
  }

  // -------------------- TAB 2: MAPS & HOTSPOTS --------------------
  function initLeaflet() {
    const map = L.map("leafletMap", { zoomControl: true, attributionControl: true }).setView([22.9, 79.6], 4.6);
    L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
      attribution: '&copy; OpenStreetMap &copy; CARTO',
      maxZoom: 18
    }).addTo(map);
    state.leaflet.map = map;
  }

  function renderMapsTab() {
    if (!state.leaflet.map) initLeaflet();
    const map = state.leaflet.map;

    state.leaflet.markers.forEach((m) => map.removeLayer(m));
    state.leaflet.markers = [];

    let rows = state.mapDataAll.filter((r) => {
      if (state.filters.state && (r.state || "").toLowerCase() !== state.filters.state.toLowerCase()) return false;
      if (state.filters.city && (r.city || "").toLowerCase() !== state.filters.city.toLowerCase()) return false;
      return true;
    });
    if (state.filters.station) {
      const st = state.stationsAll.find((s) => s.station_id === state.filters.station);
      if (st) rows = rows.filter((r) => r.station_name === st.station_name && r.lat === st.lat);
    }

    const scores = rows.map((r) => r.advanced_priority_score || 0);
    const maxScore = Math.max(1, ...scores);

    rows.forEach((r) => {
      if (r.lat == null || r.lon == null) return;
      const color = aqiColor(r.current_aqi_category);
      const radius = 5 + 11 * ((r.advanced_priority_score || 0) / maxScore);
      const marker = L.circleMarker([r.lat, r.lon], {
        radius, color, weight: 1.5, fillColor: color, fillOpacity: 0.55
      }).addTo(map);
      marker.bindPopup(`
        <div class="map-popup-title">${escapeHtml(r.station_name || "Station")}</div>
        <div class="map-popup-aqi" style="color:${color}">${fmtNum(r.current_aqi, 0)}</div>
        <div style="font-size:11.5px;color:#8b93a3;">${escapeHtml(r.current_aqi_category || "—")} · priority rank #${fmtNum(r.advanced_priority_rank, 0)}</div>
        <div style="font-size:11.5px;color:#8b93a3;margin-top:4px;">${escapeHtml(r.primary_pollution_source || "")}</div>
      `);
      state.leaflet.markers.push(marker);
    });

    if (rows.length) {
      const bounds = L.latLngBounds(rows.filter(r => r.lat != null).map((r) => [r.lat, r.lon]));
      if (bounds.isValid()) map.fitBounds(bounds.pad(0.15));
    }

    $("#mapLegend").innerHTML = Object.entries(AQI_COLORS).map(([cat, color]) =>
      `<span><span class="sw" style="background:${color}"></span>${titleCase(cat)}</span>`
    ).join("");

    // Top 15 stations bar chart (national — filters narrow it if applied)
    const topRows = [...filteredStations()].sort((a, b) => (b.current_aqi || 0) - (a.current_aqi || 0)).slice(0, 15);
    renderBarChart("topStationsChart", {
      labels: topRows.map((r) => `${r.station_name}`),
      values: topRows.map((r) => r.current_aqi),
      colors: topRows.map((r) => aqiColor(r.current_aqi_category)),
      horizontal: true,
      yTitle: "Current AQI"
    });
  }

  // -------------------- TAB 3: ADVANCED LAYERS --------------------
  function renderAdvancedTab() {
    const rows = filteredStations();
    const avg = (key) => {
      const vals = rows.map((r) => Number(r[key])).filter((v) => !Number.isNaN(v));
      if (!vals.length) return null;
      return vals.reduce((a, b) => a + b, 0) / vals.length;
    };

    $("#avgSatellite").textContent = fmtNum(avg("satellite_aerosol_proxy_score"));
    const mobility = [avg("urban_pressure_score"), avg("road_density_proxy")].filter((v) => v != null);
    $("#avgMobility").textContent = mobility.length ? fmtNum(mobility.reduce((a, b) => a + b, 0) / mobility.length) : "—";
    $("#avgWeather").textContent = fmtNum(avg("weather_trapping_score"));

    const counts = {};
    rows.forEach((r) => {
      const k = r.landuse_type_proxy || "Unclassified";
      counts[k] = (counts[k] || 0) + 1;
    });
    const entries = Object.entries(counts).sort((a, b) => b[1] - a[1]);
    renderBarChart("landuseChart", {
      labels: entries.map(([k]) => k),
      values: entries.map(([, v]) => v),
      colors: entries.map((_, i) => ["#5470d6", "#4c9c72", "#cfa53f", "#cd7f47", "#8c5bb0", "#bd5750"][i % 6]),
      horizontal: false,
      yTitle: "Stations"
    });
  }

  // -------------------- TAB 4: ML FORECASTING --------------------
  async function renderMlTab() {
    let metrics, comparison, perCityError, featureImportance;
    try {
      [metrics, comparison, perCityError, featureImportance] = await Promise.all([
        Api.modelMetrics(), Api.modelComparison(), Api.perCityError(), Api.featureImportance(15)
      ]);
    } catch (e) {
      $("#mlHeadline").innerHTML = `<div class="empty-state">Could not load model metrics: ${escapeHtml(e.message)}</div>`;
      return;
    }

    const bm = metrics.best_metrics || {};
    $("#mlHeadline").innerHTML = `
      <div class="mini-metric"><span class="mini-metric-label">Best model</span><span class="mini-metric-value">${escapeHtml(metrics.best_model || "—")}</span></div>
      <div class="mini-metric"><span class="mini-metric-label">RMSE / MAE / R²</span><span class="mini-metric-value" style="font-size:16px">${fmtNum(bm.rmse)} / ${fmtNum(bm.mae)} / ${fmtNum(bm.r2, 3)}</span></div>
      <div class="mini-metric"><span class="mini-metric-label">Category accuracy (24h-ahead)</span><span class="mini-metric-value">${fmtPct(metrics.category_accuracy)}</span></div>
      <div class="mini-metric"><span class="mini-metric-label">Hotspot detection F1 (AQI&gt;${fmtNum(metrics.high_aqi_threshold,0)})</span><span class="mini-metric-value">${fmtNum(metrics.high_aqi_f1, 3)}</span></div>
      <div class="mini-metric"><span class="mini-metric-label">Improvement over persistence baseline</span><span class="mini-metric-value">${fmtPct(bm.improvement_over_persistence_percent)}</span></div>
      <div class="mini-metric"><span class="mini-metric-label">High-AQI precision / recall</span><span class="mini-metric-value" style="font-size:16px">${fmtNum(metrics.high_aqi_precision, 3)} / ${fmtNum(metrics.high_aqi_recall, 3)}</span></div>
    `;

    $("#splitMethodology").innerHTML = `Evaluated with a <b>time-based train/test split</b> — the model is trained on earlier
      timestamps and tested on later, unseen ones, so scores reflect genuine forecasting skill rather than
      interpolation. Training mode: <b>${escapeHtml(metrics.training_mode || "—")}</b>. Train rows:
      <b>${fmtNum(metrics.train_rows, 0)}</b> · Test rows: <b>${fmtNum(metrics.test_rows, 0)}</b> · Unique stations:
      <b>${fmtNum(metrics.unique_stations, 0)}</b>. Models tested: ${(metrics.models_tested || []).map(escapeHtml).join(", ") || "—"}.`;

    renderTable("modelComparisonTable", comparison, [
      ["model", "Model"], ["mae", "MAE"], ["rmse", "RMSE"],
      ["r2", "R²"], ["improvement_over_persistence_percent", "% vs baseline"]
    ]);

    renderTable("perCityErrorTable", perCityError.sort((a, b) => (b.mean_absolute_error || 0) - (a.mean_absolute_error || 0)), [
      ["state", "State"], ["city", "City"], ["test_rows", "Test rows"],
      ["mean_absolute_error", "Mean abs. error"], ["max_absolute_error", "Max abs. error"],
      ["mean_actual_aqi", "Mean actual AQI"], ["mean_predicted_aqi", "Mean predicted AQI"]
    ]);

    const fiSorted = [...featureImportance].sort((a, b) => (b.importance || 0) - (a.importance || 0));
    renderBarChart("featureImportanceChart", {
      labels: fiSorted.map((r) => r.feature),
      values: fiSorted.map((r) => r.importance),
      colors: fiSorted.map(() => "#5470d6"),
      horizontal: true,
      yTitle: "Importance"
    });

    const lagShare = metrics.lag_feature_importance_share_percent;
    $("#lagShareNote").innerHTML = `<b style="color:var(--accent)">${fmtPct(lagShare)}</b> of total feature importance
      comes from lag features — i.e. how much of the forecast is essentially "tomorrow looks like today,"
      versus genuinely new signal from weather, source attribution, or geospatial layers.`;
  }

  // -------------------- TAB 5: PRIORITY QUEUE --------------------
  async function renderQueueTab() {
    await Promise.all([renderAblation(), loadAndRenderQueueTable(), renderCityRiskTable()]);
    $("#queueSearch").oninput = () => renderQueueTableFromCache();
    $("#queueTopN").onchange = () => loadAndRenderQueueTable();
    $("#downloadCsvBtn").onclick = downloadQueueCsv;
  }

  async function renderAblation() {
    try {
      const data = await Api.priorityQueueAblation();
      const cols = [
        ["advanced_priority_rank", "Rank"], ["station_name", "Station"], ["city", "City"],
        ["current_aqi", "AQI"], ["advanced_priority_score", "Priority"]
      ];
      renderTable("naiveRankTable", data.naive_ranking, cols);
      renderTable("advancedRankTable", data.advanced_ranking, cols);
      renderTable("surfacedTable", data.newly_surfaced_by_advanced_score, [
        ["station_name", "Station"], ["city", "City"], ["state", "State"],
        ["current_aqi", "AQI"], ["advanced_priority_score", "Priority score"],
        ["hotspot_status", "Hotspot status"], ["primary_pollution_source", "Source"],
        ["recommended_intervention", "Recommended intervention"]
      ]);
    } catch (e) {
      $("#naiveRankTable").parentElement.innerHTML = `<div class="empty-state">${escapeHtml(e.message)}</div>`;
    }
  }

  async function loadAndRenderQueueTable() {
    const topN = Number($("#queueTopN").value || 20);
    try {
      state.priorityQueueRows = await Api.priorityQueue(topN);
      renderQueueTableFromCache();
    } catch (e) {
      $("#priorityQueueTable").innerHTML = `<tr><td class="empty-state">${escapeHtml(e.message)}</td></tr>`;
    }
  }

  function renderQueueTableFromCache() {
    const q = ($("#queueSearch").value || "").toLowerCase();
    let rows = state.priorityQueueRows;
    if (state.filters.state) rows = rows.filter((r) => (r.state || "").toLowerCase() === state.filters.state.toLowerCase());
    if (state.filters.city) rows = rows.filter((r) => (r.city || "").toLowerCase() === state.filters.city.toLowerCase());
    if (q) rows = rows.filter((r) => JSON.stringify(r).toLowerCase().includes(q));

    renderTable("priorityQueueTable", rows, [
      ["advanced_priority_rank", "Rank"], ["state", "State"], ["city", "City"], ["station_name", "Station"],
      ["current_aqi_category", "Category"], ["current_aqi", "AQI"], ["forecast_aqi_next", "Forecast AQI"],
      ["forecast_trend", "Trend"], ["hotspot_status", "Hotspot"], ["advanced_priority_score", "Priority score"],
      ["primary_pollution_source", "Source"], ["recommended_intervention", "Recommended intervention"]
    ], { colorCategoryKey: "current_aqi_category" });
  }

  function downloadQueueCsv() {
    const rows = state.priorityQueueRows;
    if (!rows.length) { toast("Nothing to download yet."); return; }
    const headers = Object.keys(rows[0]);
    const csv = [headers.join(",")].concat(
      rows.map((r) => headers.map((h) => csvEscape(r[h])).join(","))
    ).join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = "cleanair_priority_queue.csv";
    a.click();
    URL.revokeObjectURL(url);
  }

  function csvEscape(v) {
    if (v === null || v === undefined) return "";
    const s = String(v);
    return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
  }

  async function renderCityRiskTable() {
    try {
      let rows = state.citiesAll.length ? state.citiesAll : await Api.cities();
      rows = [...rows].sort((a, b) => (a.city_priority_rank || 999) - (b.city_priority_rank || 999));
      renderTable("cityRiskTable", rows, [
        ["city_priority_rank", "Rank"], ["state", "State"], ["city", "City"], ["stations", "Stations"],
        ["mean_current_aqi", "Mean AQI"], ["max_current_aqi", "Max AQI"],
        ["current_hotspot_stations", "Current hotspots"], ["forecast_hotspot_stations", "Forecast hotspots"],
        ["mean_priority_score", "Mean priority"], ["mean_health_exposure_risk", "Health risk"]
      ]);
    } catch (e) {
      $("#cityRiskTable").innerHTML = `<tr><td class="empty-state">${escapeHtml(e.message)}</td></tr>`;
    }
  }

  // -------------------- GENERIC TABLE / CHART RENDERERS --------------------
  function renderTable(id, rows, columns, opts = {}) {
    const table = $(`#${id}`);
    if (!rows || !rows.length) {
      table.innerHTML = `<tr><td class="empty-state">No rows match the current filters.</td></tr>`;
      return;
    }
    const thead = `<thead><tr>${columns.map(([, label]) => `<th>${escapeHtml(label)}</th>`).join("")}</tr></thead>`;
    const tbody = `<tbody>${rows.map((r) => {
      const rowColor = opts.colorCategoryKey ? aqiColor(r[opts.colorCategoryKey]) : null;
      return `<tr>${columns.map(([key]) => {
        let val = r[key];
        if (typeof val === "number") val = fmtNum(val, Number.isInteger(val) ? 0 : 2);
        const style = (rowColor && key === opts.colorCategoryKey) ? ` style="color:${rowColor};font-weight:600;"` : "";
        return `<td${style}>${escapeHtml(val ?? "—")}</td>`;
      }).join("")}</tr>`;
    }).join("")}</tbody>`;
    table.innerHTML = thead + tbody;
  }

  function renderBarChart(canvasId, { labels, values, colors, horizontal, yTitle }) {
    const ctx = $(`#${canvasId}`);
    if (!ctx) return;
    if (state.charts[canvasId]) state.charts[canvasId].destroy();
    state.charts[canvasId] = new Chart(ctx, {
      type: "bar",
      data: {
        labels,
        datasets: [{ data: values, backgroundColor: colors, borderRadius: 4, maxBarThickness: 26 }]
      },
      options: {
        indexAxis: horizontal ? "y" : "x",
        responsive: true,
        maintainAspectRatio: false,
        animation: { duration: 600, easing: "easeOutQuart" },
        plugins: { legend: { display: false }, tooltip: { backgroundColor: "#171b24", titleColor: "#e8eaee", bodyColor: "#e8eaee", borderColor: "#262c37", borderWidth: 1 } },
        scales: {
          x: { grid: { color: "#1b1f28" }, ticks: { color: "#8b93a3", font: { size: 11 } }, title: horizontal ? { display: !!yTitle, text: yTitle, color: "#8b93a3" } : undefined },
          y: { grid: { color: "#1b1f28" }, ticks: { color: "#8b93a3", font: { size: 11 } }, title: !horizontal ? { display: !!yTitle, text: yTitle, color: "#8b93a3" } : undefined }
        }
      }
    });
  }

  // -------------------- REFRESH BUTTON --------------------
  function initRefreshButton() {
    const btn = $("#refreshBtn");
    btn.addEventListener("click", async () => {
      btn.classList.add("is-loading");
      btn.disabled = true;
      $(".refresh-label", btn).textContent = "Refreshing…";
      try {
        const res = await Api.refreshLiveAqi();
        toast(res.message || "Refreshed.");
        await bootstrapData(true);
      } catch (e) {
        toast(`Refresh failed: ${e.message}`, 4500);
      } finally {
        btn.classList.remove("is-loading");
        btn.disabled = false;
        $(".refresh-label", btn).textContent = "Refresh live AQI";
      }
    });
  }

  // -------------------- BOOTSTRAP --------------------
  async function bootstrapData(isReload = false) {
    try {
      const [stationsRes, citiesRes, summary, mapData] = await Promise.all([
        Api.stations({ limit: 1000 }),
        Api.cities(),
        Api.hotspotsSummary().catch(() => null),
        Api.mapData().catch(() => [])
      ]);
      state.stationsAll = stationsRes.stations || [];
      state.citiesAll = citiesRes || [];
      state.hotspotSummary = summary;
      state.mapDataAll = mapData || [];

      populateFilters();
      renderHeaderMetrics();

      const activeTab = $(".tabnav-item.is-active")?.dataset.tab || "live";
      state.loadedTabs.delete(activeTab);
      ensureTabData(activeTab);

      if (isReload) toast("Dashboard data reloaded.");
    } catch (e) {
      toast(`Could not load data: ${e.message}`, 5000);
      $("#stationGrid").innerHTML = `<div class="empty-state">Could not reach the backend at ${escapeHtml(Api.getBase())}.<br>Confirm the FastAPI server is running, then edit the API base URL in the sidebar.</div>`;
    }
  }

  // -------------------- INIT --------------------
  document.addEventListener("DOMContentLoaded", () => {
    initApiBase();
    initSidebarToggle();
    initTabs();
    initRefreshButton();
    bootstrapData(false);
  });
})();
