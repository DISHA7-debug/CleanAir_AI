// ==========================================================
// CleanAir AI — landing page interactions (no backend calls)
// ==========================================================
(() => {
  "use strict";

  // -------- hero headline word-swap --------
  const swaps = ["forecasting it", "attributing its source", "ranking the response", "acting on it"];
  let swapIdx = 0;
  const swapEl = document.getElementById("heroSwap");
  if (swapEl) {
    setInterval(() => {
      swapIdx = (swapIdx + 1) % swaps.length;
      swapEl.style.opacity = 0;
      setTimeout(() => {
        swapEl.textContent = swaps[swapIdx];
        swapEl.style.opacity = 1;
      }, 260);
    }, 2600);
    swapEl.style.transition = "opacity .26s ease";
  }

  // -------- hero stat count-up --------
  function countUp(el) {
    const target = Number(el.dataset.count || 0);
    const suffix = el.dataset.suffix || "";
    const duration = 1100;
    const start = performance.now();
    function tick(now) {
      const p = Math.min(1, (now - start) / duration);
      const eased = 1 - Math.pow(1 - p, 3);
      el.textContent = Math.round(target * eased) + suffix;
      if (p < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  // -------- scroll reveal (IntersectionObserver) --------
  const revealTargets = document.querySelectorAll(
    ".problem-card, .pipeline-node, .feature-card, .showcase-card, .section-tag, .section-title, .section-lede, .chip, .final-cta-inner"
  );
  revealTargets.forEach((el) => el.classList.add("reveal"));

  const io = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-in");
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.15 });
  revealTargets.forEach((el) => io.observe(el));

  const statObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        countUp(entry.target);
        statObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.4 });
  document.querySelectorAll(".hero-stat-value").forEach((el) => statObserver.observe(el));

  // -------- dial: gently drifting illustrative value (purely decorative, no live data) --------
  const dialValue = document.getElementById("dialValue");
  const dialSweep = document.querySelector(".dial-sweep");
  if (dialValue) {
    const base = 312;
    let t = 0;
    setInterval(() => {
      t += 0.15;
      const wobble = Math.round(Math.sin(t) * 14);
      dialValue.textContent = base + wobble;
    }, 700);
  }
})();
