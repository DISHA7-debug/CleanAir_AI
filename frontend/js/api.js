// ==========================================================
// CleanAir AI — API client
// Thin, faithful wrapper around the FastAPI backend endpoints
// documented in BACKEND_SPEC.md. No renaming, no recomputation
// of anything the backend already computes.
// ==========================================================
const Api = (() => {
  function getBase() {
    const stored = localStorage.getItem("cleanair_api_base");
    return (stored && stored.trim()) || DEFAULT_API_BASE;
  }

  function setBase(url) {
    localStorage.setItem("cleanair_api_base", url.trim().replace(/\/+$/, ""));
  }

  async function req(path, opts = {}) {
    const base = getBase();
    const url = `${base}${path}`;
    let res;
    try {
      res = await fetch(url, { ...opts });
    } catch (e) {
      throw new Error(`Could not reach backend at ${base}. Is it running? (${e.message})`);
    }
    if (!res.ok) {
      let detail = res.statusText;
      try {
        const body = await res.json();
        detail = body.detail || JSON.stringify(body);
      } catch (_) {}
      const err = new Error(detail);
      err.status = res.status;
      throw err;
    }
    return res.json();
  }

  return {
    getBase,
    setBase,
    health: () => req("/"),
    stations: (params = {}) => {
      const qs = new URLSearchParams();
      if (params.city) qs.set("city", params.city);
      if (params.state) qs.set("state", params.state);
      qs.set("limit", params.limit ?? 1000);
      return req(`/stations?${qs.toString()}`);
    },
    station: (id) => req(`/stations/${encodeURIComponent(id)}`),
    cities: () => req("/cities"),
    city: (name) => req(`/cities/${encodeURIComponent(name)}`),
    priorityQueue: (topN = 20) => req(`/priority-queue?top_n=${topN}`),
    priorityQueueAblation: () => req("/priority-queue/ablation"),
    forecast: (stationId) => req(`/forecast/${encodeURIComponent(stationId)}`),
    modelMetrics: () => req("/model/metrics"),
    modelComparison: () => req("/model/comparison"),
    perCityError: () => req("/model/per-city-error"),
    featureImportance: (topN = 15) => req(`/model/feature-importance?top_n=${topN}`),
    confusionMatrix: () => req("/model/confusion-matrix"),
    testPredictions: (stationId) => req(`/model/test-predictions/${encodeURIComponent(stationId)}`),
    hotspotsSummary: () => req("/hotspots/summary"),
    mapData: () => req("/map-data"),
    advisory: (category, lang = "en") => req(`/advisory/${encodeURIComponent(category)}?lang=${lang}`),
    refreshLiveAqi: () => req("/refresh-live-aqi", { method: "POST" })
  };
})();
