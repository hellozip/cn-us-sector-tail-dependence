const fmtPct = (value) => {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "";
  return `${(Number(value) * 100).toFixed(1)}%`;
};

const fmtNum = (value, digits = 3) => {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "";
  return Number(value).toFixed(digits);
};

const fmtRet = (value) => fmtPct(value);

const columnLabel = {
  id: "板块",
  source_id: "来源",
  target_id: "目标",
  sector: "行业",
  market: "市场",
  regime: "状态",
  latest_return: "当日收益",
  standardized_residual: "标准残差",
  empirical_percentile: "分位数",
  regime_strength: "强度",
  relation_metric: "历史关系",
  score: "分数",
  interpretation: "解释",
  lower_tail_dependence: "下尾",
  upper_tail_dependence: "上尾",
  middle_pearson: "中间 Pearson",
  middle_spearman: "中间 Spearman",
  alpha: "ARCH",
  beta: "GARCH",
  persistence: "持续性",
  status: "状态",
  observations: "样本",
};

function formatCell(key, value) {
  if (key === "regime" || key === "source_regime" || key === "target_regime") {
    return `<span class="badge ${value}">${value || ""}</span>`;
  }
  if (key.includes("return")) return fmtRet(value);
  if (key.includes("percentile") || key.includes("dependence") || key.includes("pearson") || key.includes("spearman") || key.includes("strength")) return fmtPct(value);
  if (["score", "relation_metric", "standardized_residual", "garch_sigma", "alpha", "beta", "persistence", "omega"].includes(key)) return fmtNum(value);
  return value ?? "";
}

function renderTable(targetId, rows, columns, limit = 20) {
  const target = document.getElementById(targetId);
  if (!rows || rows.length === 0) {
    target.innerHTML = '<div class="empty">暂无数据</div>';
    return;
  }
  const view = rows.slice(0, limit);
  const head = columns.map((col) => `<th>${columnLabel[col] || col}</th>`).join("");
  const body = view.map((row) => {
    const cells = columns.map((col) => `<td>${formatCell(col, row[col])}</td>`).join("");
    return `<tr>${cells}</tr>`;
  }).join("");
  target.innerHTML = `<table><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table>`;
}

function renderKpis(summary) {
  const counts = summary.regime_counts || {};
  const kpis = [
    ["最新日期", summary.as_of_date || "暂无"],
    ["上尾板块", counts.upper_tail || 0],
    ["下尾板块", counts.lower_tail || 0],
    ["潜在流向", summary.flow_count || 0],
    ["风险传导", summary.risk_count || 0],
  ];
  document.getElementById("kpis").innerHTML = kpis.map(([label, value]) => (
    `<div class="kpi"><span>${label}</span><strong>${value}</strong></div>`
  )).join("");
}

function renderHeatmaps(heatmaps) {
  const tabs = document.getElementById("heatmapTabs");
  const img = document.getElementById("heatmapImage");
  if (!heatmaps || heatmaps.length === 0) {
    tabs.innerHTML = "暂无热力图";
    img.removeAttribute("src");
    return;
  }
  tabs.innerHTML = heatmaps.map((heatmap, index) => (
    `<button type="button" class="tab ${index === 0 ? "active" : ""}" data-url="${heatmap.url}">${heatmap.label}</button>`
  )).join("");
  img.src = heatmaps[0].url;
  tabs.querySelectorAll(".tab").forEach((button) => {
    button.addEventListener("click", () => {
      tabs.querySelectorAll(".tab").forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      img.src = button.dataset.url;
    });
  });
}

function renderDashboard(data) {
  renderKpis(data.summary);
  renderTable("latestTable", data.latestRegime, ["id", "market", "sector", "latest_return", "standardized_residual", "empirical_percentile", "regime", "regime_strength"], 30);
  renderTable("flowTable", data.flowCandidates, ["source_id", "target_id", "source_regime", "target_regime", "relation_metric", "score", "interpretation"], 18);
  renderTable("riskTable", data.riskCandidates, ["source_id", "target_id", "source_regime", "target_regime", "relation_metric", "score", "interpretation"], 18);
  renderTable("matchedTable", data.matchedSectors, ["left_sector", "left_id", "right_id", "lower_tail_dependence", "upper_tail_dependence", "middle_pearson", "middle_spearman"], 14);
  renderTable("garchTable", data.garchParams, ["id", "status", "alpha", "beta", "persistence", "observations"], 24);
  renderHeatmaps(data.heatmaps);
  document.getElementById("statusText").textContent = `数据源：${data.summary.data_dir}`;
}

async function loadDashboard() {
  const alpha = Number(document.getElementById("alpha").value || 0.05).toFixed(2);
  const response = await fetch(`/api/dashboard?alpha=${encodeURIComponent(alpha)}`);
  if (!response.ok) throw new Error(`dashboard ${response.status}`);
  renderDashboard(await response.json());
}

async function refreshAnalysis() {
  const button = document.getElementById("refreshBtn");
  const status = document.getElementById("statusText");
  button.disabled = true;
  status.textContent = "正在抓取数据并重新估计 GARCH...";
  const payload = {
    start: document.getElementById("startDate").value,
    end: document.getElementById("endDate").value,
    alpha: Number(document.getElementById("alpha").value || 0.05),
    noGarch: document.getElementById("noGarch").checked,
  };
  try {
    const response = await fetch("/api/refresh", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (!result.ok) throw new Error(result.stderr || result.error || "refresh failed");
    renderDashboard(result.dashboard);
    status.textContent = "刷新完成";
  } catch (error) {
    status.textContent = `刷新失败：${error.message}`;
  } finally {
    button.disabled = false;
  }
}

function initDates() {
  const end = new Date();
  const iso = end.toISOString().slice(0, 10);
  document.getElementById("endDate").value = iso;
}

document.addEventListener("DOMContentLoaded", () => {
  initDates();
  document.getElementById("refreshBtn").addEventListener("click", refreshAnalysis);
  loadDashboard().catch((error) => {
    document.getElementById("statusText").textContent = `读取失败：${error.message}`;
  });
});
