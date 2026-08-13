(() => {
  "use strict";

  const NS = "http://www.w3.org/2000/svg";
  const $ = (id) => document.getElementById(id);
  const svgEl = (name, attrs = {}) => {
    const el = document.createElementNS(NS, name);
    Object.entries(attrs).forEach(([k, v]) => el.setAttribute(k, v));
    return el;
  };
  const fmt = (n, digits = 3) => Number(n).toLocaleString("fr-FR", { maximumFractionDigits: digits });

  fetch("data/exploration.json")
    .then((r) => {
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    })
    .then((data) => {
      renderXIV(data.section_xiv);
      renderGenealogy(data.genealogy);
      renderIsotopes(data.nc_cc, data.sources.nc_cc);
      renderNBody(data.nbody);
    })
    .catch((err) => {
      const target = $("xiv-summary");
      if (target) target.innerHTML = `<p>Impossible de charger les données interactives : ${String(err)}</p>`;
    });

  function renderXIV(xiv) {
    const open = xiv.open.map((x) => `<code>${x}</code>`).join(" · ");
    $("xiv-summary").innerHTML = `
      <article class="metric"><strong>${xiv.passed} / ${xiv.total}</strong><span>conditions remplies</span><small>porte fail-closed</small></article>
      <article class="metric"><strong>${xiv.total - xiv.passed}</strong><span>conditions ouvertes</span><small>${open}</small></article>
      <article class="metric"><strong>${xiv.first_threshold_satisfied ? "oui" : "non"}</strong><span>premier seuil satisfait</span><small>aucun relèvement automatique</small></article>`;
  }

  function renderGenealogy(g) {
    const strip = $("genealogy-strip");
    const detail = $("genealogy-detail");
    g.stages.forEach((stage, index) => {
      const b = document.createElement("button");
      b.type = "button";
      b.className = "stage-button";
      b.setAttribute("role", "listitem");
      b.innerHTML = `<span>${stage.order}</span><strong>${stage.stage_id}</strong><small>${stage.label}</small>`;
      b.addEventListener("click", () => showStage(stage, b));
      strip.appendChild(b);
      if (index === 0) setTimeout(() => b.click(), 0);
    });

    function showStage(stage, button) {
      strip.querySelectorAll("button").forEach((b) => b.classList.remove("active"));
      button.classList.add("active");
      const incoming = g.links.filter((l) => l.to_stage === stage.stage_id);
      const outgoing = g.links.filter((l) => l.from_stage === stage.stage_id);
      const links = [...incoming.map((l) => `← ${l.from_stage} · ${l.relation}`), ...outgoing.map((l) => `→ ${l.to_stage} · ${l.relation}`)];
      detail.innerHTML = `
        <p class="eyebrow">${stage.stage_id} · stade ${stage.order}</p>
        <h3>${stage.label}</h3>
        <dl class="detail-list"><dt>Ancrage empirique</dt><dd>${stage.empirical_anchor}</dd><dt>Porteur d'histoire</dt><dd><code>${stage.history_carrier}</code></dd><dt>Classe de preuve</dt><dd><code>${stage.evidence_class}</code></dd></dl>
        <h4>Relations adjacentes</h4><ul>${links.map((x) => `<li>${x}</li>`).join("") || "<li>Aucune relation adjacente</li>"}</ul>`;
    }
  }

  function renderIsotopes(nccc, source) {
    const select = $("isotope-select");
    const keys = Object.keys(nccc.systems);
    keys.forEach((key) => {
      const o = document.createElement("option");
      o.value = key;
      o.textContent = key;
      select.appendChild(o);
    });
    $("nccc-source").textContent = `Source : ${source}`;
    select.addEventListener("change", () => drawIsotope(select.value));
    drawIsotope(keys.includes("50Ti") ? "50Ti" : keys[0]);
    select.value = keys.includes("50Ti") ? "50Ti" : keys[0];

    function drawIsotope(key) {
      const s = nccc.systems[key];
      $("isotope-stats").innerHTML = `<strong>${key}</strong> · Cohen d (CC − NC) = <strong>${fmt(s.cohen_d_cc_minus_nc, 2)}</strong> · n(CC)=${s.cc_n} · n(NC)=${s.nc_n} · classification globale ${nccc.leave_one_out_correct}/${nccc.leave_one_out_total}`;
      const svg = $("isotope-plot");
      svg.replaceChildren();
      const width = 920, height = 420, left = 90, right = 35, top = 40, bottom = 65;
      const vals = s.points.flatMap((p) => p.uncertainty == null ? [p.value] : [p.value - p.uncertainty, p.value + p.uncertainty]);
      let min = Math.min(...vals), max = Math.max(...vals);
      if (min === max) { min -= 1; max += 1; }
      const pad = (max - min) * 0.08;
      min -= pad; max += pad;
      const x = (v) => left + (v - min) / (max - min) * (width - left - right);
      const yNC = 145, yCC = 285;

      const axis = svgEl("line", { x1: left, y1: height - bottom, x2: width - right, y2: height - bottom, class: "axis-line" });
      svg.appendChild(axis);
      for (let i = 0; i <= 5; i++) {
        const value = min + (max - min) * i / 5;
        const xx = x(value);
        svg.appendChild(svgEl("line", { x1: xx, y1: top, x2: xx, y2: height - bottom, class: "grid-line" }));
        const t = svgEl("text", { x: xx, y: height - 28, class: "axis-text", "text-anchor": "middle" });
        t.textContent = fmt(value, 3); svg.appendChild(t);
      }
      [["NC", yNC], ["CC", yCC]].forEach(([label, yy]) => {
        const t = svgEl("text", { x: 35, y: yy + 5, class: "reservoir-label" }); t.textContent = label; svg.appendChild(t);
      });

      const groups = { NC: s.points.filter((p) => p.reservoir === "NC"), CC: s.points.filter((p) => p.reservoir === "CC") };
      Object.entries(groups).forEach(([reservoir, pts]) => {
        const baseY = reservoir === "NC" ? yNC : yCC;
        pts.forEach((p, i) => {
          const jitter = ((i % 7) - 3) * 9;
          const yy = baseY + jitter;
          if (p.uncertainty != null) {
            svg.appendChild(svgEl("line", { x1: x(p.value - p.uncertainty), y1: yy, x2: x(p.value + p.uncertainty), y2: yy, class: `error-line ${reservoir.toLowerCase()}` }));
          }
          const c = svgEl("circle", { cx: x(p.value), cy: yy, r: 5.5, class: `plot-point ${reservoir.toLowerCase()}` });
          const title = svgEl("title"); title.textContent = `${p.sample} · ${reservoir} · ${p.value}${p.uncertainty == null ? "" : ` ± ${p.uncertainty}`}`; c.appendChild(title); svg.appendChild(c);
        });
      });
      const label = svgEl("text", { x: (left + width - right) / 2, y: height - 5, class: "axis-title", "text-anchor": "middle" });
      label.textContent = key; svg.appendChild(label);
    }
  }

  function renderNBody(nbody) {
    const select = $("nbody-select");
    nbody.scenarios.forEach((s) => {
      const o = document.createElement("option"); o.value = s.id; o.textContent = s.label; select.appendChild(o);
    });
    const show = () => {
      const s = nbody.scenarios.find((x) => x.id === select.value) || nbody.scenarios[0];
      $("nbody-detail").innerHTML = `
        <p class="eyebrow">${nbody.evidence_level} · ${nbody.criteria_passed}/${nbody.criteria_total} critères</p>
        <h3>${s.label}</h3>
        <div class="mini-metrics"><div><span>RMSE vs baseline</span><strong>${fmt(s.rmse_vs_baseline, 6)}</strong></div><div><span>Corrélation</span><strong>${fmt(s.correlation_vs_baseline, 4)}</strong></div><div><span>Δ excentricité moyen</span><strong>${fmt(s.mean_eccentricity_delta, 6)}</strong></div><div><span>σ / baseline</span><strong>${fmt(s.std_ratio_vs_baseline, 4)}</strong></div></div>
        <p>Le résultat certifié de la campagne exige un effet interventionnel minimal ≥ 1000 fois les écarts numériques ; la valeur certifiée courante est <strong>${fmt(nbody.certified_min_effect_to_numeric_noise, 1)}×</strong>.</p>
        <p class="scope-note">${nbody.warning}</p>`;
    };
    select.addEventListener("change", show); select.value = nbody.scenarios[0].id; show();
  }

  // Modèle jouet indépendant des données ORI-C.
  const hist = $("history-range"), arch = $("arch-range"), force = $("force-range"), abl = $("ablation-toggle");
  [hist, arch, force, abl].forEach((el) => el && el.addEventListener("input", drawSandbox));
  drawSandbox();

  function drawSandbox() {
    if (!hist) return;
    $("history-out").value = Number(hist.value).toFixed(2);
    $("arch-out").value = Number(arch.value).toFixed(2);
    $("force-out").value = Number(force.value).toFixed(2);
    const h = abl.checked ? 0.5 : Number(hist.value);
    const a = Number(arch.value), f = Number(force.value);

    // Deux histoires complémentaires. La trace historique modifie les deux rigidités.
    const configs = [
      { name: "Histoire A", h, cls: "hist-a" },
      { name: "Histoire B", h: 1 - h, cls: "hist-b" },
    ];
    configs.forEach((c) => {
      c.k1 = 0.5 + a * (0.45 + 1.15 * c.h);
      c.k2 = 0.5 + a * (1.60 - 1.05 * c.h);
      c.x = f / (c.k1 + c.k2);
      c.range = 0.35 / Math.sqrt(c.k1 * c.k2);
    });

    const svg = $("sandbox-plot"); svg.replaceChildren();
    const width = 920, height = 420, left = 80, right = 50;
    const all = configs.flatMap((c) => [c.x - c.range, c.x + c.range]);
    let min = Math.min(-1, ...all), max = Math.max(1, ...all);
    const x = (v) => left + (v - min) / (max - min) * (width - left - right);
    const y = [145, 285];
    svg.appendChild(svgEl("line", { x1: x(0), y1: 55, x2: x(0), y2: 350, class: "zero-line" }));
    configs.forEach((c, i) => {
      const yy = y[i];
      const label = svgEl("text", { x: 20, y: yy + 5, class: "reservoir-label" }); label.textContent = c.name; svg.appendChild(label);
      svg.appendChild(svgEl("line", { x1: x(c.x - c.range), y1: yy, x2: x(c.x + c.range), y2: yy, class: `future-range ${c.cls}` }));
      svg.appendChild(svgEl("circle", { cx: x(c.x), cy: yy, r: 10, class: `sandbox-point ${c.cls}` }));
      const t = svgEl("text", { x: x(c.x), y: yy - 22, class: "axis-text", "text-anchor": "middle" }); t.textContent = `x=${c.x.toFixed(3)} · possibles ±${c.range.toFixed(3)}`; svg.appendChild(t);
    });
    const diff = Math.abs(configs[0].x - configs[1].x);
    $("sandbox-readout").innerHTML = `Écart sous même forçage : <strong>${diff.toFixed(4)}</strong> · ${abl.checked ? "trace ablatée : architectures réinitialisées" : "trace historique active"}`;
  }
})();
