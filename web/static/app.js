const fmtPct = (value) => {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "";
  const pct = Number(value) * 100;
  if (pct > 0 && pct < 0.05) return "<0.1%";
  if (pct < 0 && pct > -0.05) return "-<0.1%";
  return `${pct.toFixed(1)}%`;
};

const fmtNum = (value, digits = 3) => {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "";
  return Number(value).toFixed(digits);
};

const fmtRet = (value) => fmtPct(value);

const fmtMoney = (value) => {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "暂无";
  const number = Number(value);
  const sign = number < 0 ? "-" : "";
  const abs = Math.abs(number);
  if (abs >= 1e8) return `${sign}${(abs / 1e8).toFixed(2)}亿`;
  if (abs >= 1e4) return `${sign}${(abs / 1e4).toFixed(2)}万`;
  return `${sign}${abs.toFixed(0)}`;
};

let currentDashboard = null;

const escapeHtml = (value) => String(value ?? "")
  .replaceAll("&", "&amp;")
  .replaceAll("<", "&lt;")
  .replaceAll(">", "&gt;")
  .replaceAll('"', "&quot;")
  .replaceAll("'", "&#039;");

const marketLabel = {
  US: "美国",
  CN: "中国",
};

const sectorLabel = {
  Internet: "互联网",
  Semiconductor: "半导体",
  "New Energy": "新能源",
  Healthcare: "医药",
  Financials: "金融",
  "Real Estate Chain": "地产链",
  Energy: "能源",
  Materials: "材料",
  Industrials: "工业",
  Utilities: "公用事业",
};

const idSectorLabel = {
  INTERNET: "互联网",
  SEMICONDUCTOR: "半导体",
  NEW_ENERGY: "新能源",
  HEALTHCARE: "医药",
  FINANCIALS: "金融",
  REAL_ESTATE_CHAIN: "地产链",
  ENERGY: "能源",
  MATERIALS: "材料",
  INDUSTRIALS: "工业",
  UTILITIES: "公用事业",
};

const regimeLabel = {
  upper_tail: "上尾强势",
  lower_tail: "下尾弱势",
  middle: "中间区间",
};

const statusLabel = {
  ok: "正常",
};

const interpretationLabel = {
  possible_flow_follow_through: "可能继续扩散",
  already_confirming_move: "已经开始确认",
  possible_downside_spillover: "可能下跌传导",
};

function assetCodeLabel(value) {
  if (!value || typeof value !== "string" || !value.includes("_")) return value ?? "";
  const [market, ...sectorParts] = value.split("_");
  const sectorKey = sectorParts.join("_");
  const readableMarket = marketLabel[market] || market;
  const readableSector = idSectorLabel[sectorKey] || sectorKey.replaceAll("_", " ");
  return `${readableMarket}${readableSector}`;
}

const columnLabel = {
  id: "板块",
  source_id: "来源",
  target_id: "目标",
  left_id: "左板块",
  right_id: "右板块",
  left_sector: "行业",
  sector: "行业",
  market: "市场",
  regime: "状态",
  source_regime: "来源状态",
  target_regime: "目标状态",
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
  if (["id", "source_id", "target_id", "left_id", "right_id"].includes(key)) return escapeHtml(assetCodeLabel(value));
  if (key === "regime" || key === "source_regime" || key === "target_regime") {
    const safeValue = escapeHtml(value || "");
    return `<span class="badge ${safeValue}">${escapeHtml(regimeLabel[value] || value || "")}</span>`;
  }
  if (key === "market") return escapeHtml(marketLabel[value] || value || "");
  if (key === "sector" || key === "left_sector") return escapeHtml(sectorLabel[value] || value || "");
  if (key === "status") return escapeHtml(statusLabel[value] || value || "");
  if (key === "interpretation") return escapeHtml(interpretationLabel[value] || value || "");
  if (key.includes("return")) return fmtRet(value);
  if (key.includes("percentile") || key.includes("dependence") || key.includes("pearson") || key.includes("spearman") || key.includes("strength")) return fmtPct(value);
  if (["score", "relation_metric", "standardized_residual", "garch_sigma", "alpha", "beta", "persistence", "omega"].includes(key)) return fmtNum(value);
  return escapeHtml(value ?? "");
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

function rankArrowClass(value) {
  if (typeof value !== "string") return "";
  if (value.startsWith("↑")) return "rank-up";
  if (value.startsWith("↓")) return "rank-down";
  return "rank-flat";
}

function renderFundFlow(fundFlow) {
  const statsTarget = document.getElementById("fundFlowStats");
  const tableTarget = document.getElementById("fundFlowTable");
  const methodTarget = document.getElementById("fundFlowMethod");
  if (!fundFlow || !fundFlow.available) {
    methodTarget.textContent = fundFlow?.method || "未配置真实资金流来源。";
    statsTarget.innerHTML = "";
    tableTarget.innerHTML = '<div class="empty">未配置真实资金流金额、板块总规模和来源说明</div>';
    return;
  }

  methodTarget.textContent = fundFlow.method;
  const largestInflow = fundFlow.largest_inflow?.label || "暂无";
  const largestOutflow = fundFlow.largest_outflow?.label || "暂无";
  const netClass = Number(fundFlow.net_flow_amount || 0) >= 0 ? "flow-positive" : "flow-negative";
  const stats = [
    { label: "日期", value: fundFlow.as_of_date || "暂无" },
    { label: "真实净流入", value: fmtMoney(fundFlow.net_flow_amount), className: netClass },
    { label: "真实流入合计", value: fmtMoney(fundFlow.total_inflow_amount), className: "flow-positive" },
    { label: "真实流出合计", value: fmtMoney(fundFlow.total_outflow_amount), className: "flow-negative" },
    { label: "最大流入", value: largestInflow, className: "flow-positive" },
    { label: "最大流出", value: largestOutflow, className: "flow-negative" },
  ];
  statsTarget.innerHTML = stats.map((stat) => (
    `<div class="flow-stat"><span>${stat.label}</span><strong class="${stat.className || ""}">${escapeHtml(stat.value)}</strong></div>`
  )).join("");

  const rows = fundFlow.rows || [];
  if (rows.length === 0) {
    tableTarget.innerHTML = '<div class="empty">暂无真实资金流入流出数据</div>';
    return;
  }
  const body = rows.map((row) => {
    const amount = Number(row.flow_amount || 0);
    const flowClass = amount >= 0 ? "flow-positive" : "flow-negative";
    const returnClass = Number(row.latest_return || 0) >= 0 ? "flow-positive" : "flow-negative";
    const arrow = row.rank_arrow || "";
    const sourceText = [row.flow_source, row.total_size_source].filter(Boolean).join(" / ");
    return `
      <tr>
        <td>${row.rank}</td>
        <td>${escapeHtml(row.label || assetCodeLabel(row.id))}</td>
        <td class="${flowClass}">${fmtMoney(row.flow_amount)}</td>
        <td class="${flowClass}">${fmtPct(row.flow_ratio)}</td>
        <td>${fmtMoney(row.total_size)}</td>
        <td class="${returnClass}">${fmtPct(row.latest_return)}</td>
        <td><span class="rank-arrow ${rankArrowClass(arrow)}">${escapeHtml(arrow)}</span></td>
        <td>${row.previous_rank ?? row.rank}</td>
        <td>${escapeHtml(sourceText || "未注明")}</td>
      </tr>
    `;
  }).join("");
  tableTarget.innerHTML = `
    <table>
      <thead>
        <tr>
          <th>排名</th>
          <th>板块</th>
          <th>真实流入/流出金额</th>
          <th>占板块总规模</th>
          <th>板块总规模</th>
          <th>当日收益</th>
          <th>排名变化</th>
          <th>昨日排名</th>
          <th>来源</th>
        </tr>
      </thead>
      <tbody>${body}</tbody>
    </table>
  `;
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

function renderAlertCards(alerts) {
  const opportunity = alerts?.opportunity || { count: 0, items: [] };
  const risk = alerts?.risk || { count: 0, items: [] };
  const volatility = alerts?.volatility || { count: 0, items: [] };
  document.getElementById("opportunityCount").textContent = opportunity.count ?? opportunity.items?.length ?? 0;
  document.getElementById("riskCount").textContent = risk.count ?? risk.items?.length ?? 0;
  document.getElementById("volatilityCount").textContent = volatility.count ?? volatility.items?.length ?? 0;
  document.getElementById("opportunitySummary").textContent = opportunity.summary || "查看下一步可能承接资金扩散的板块";
  document.getElementById("riskSummary").textContent = risk.summary || "查看下跌传导和短线过热回调风险";
  document.getElementById("volatilitySummary").textContent = volatility.summary || "查看 GARCH 波动率显著偏离常态的板块";
  document.getElementById("openOpportunity").disabled = !opportunity.items || opportunity.items.length === 0;
  document.getElementById("openRisk").disabled = !risk.items || risk.items.length === 0;
  document.getElementById("openVolatility").disabled = !volatility.items || volatility.items.length === 0;
}

function renderAlertItem(item) {
  const reasons = (item.reasons || []).map((reason) => `<li>${escapeHtml(reason)}</li>`).join("");
  const relationLabel = item.type === "volatility" ? "波动分位" : "历史关系";
  const relation = item.relation_metric === null || item.relation_metric === undefined
    ? ""
    : `<span>${relationLabel} ${fmtPct(item.relation_metric)}</span>`;
  const score = item.score === null || item.score === undefined
    ? ""
    : `<span>信号分数 ${fmtNum(item.score)}</span>`;
  return `
    <article class="alert-item ${escapeHtml(item.type || "")}">
      <div class="alert-item-head">
        <span>${escapeHtml(item.subtype || "提示")}</span>
        <strong>${escapeHtml(item.title || "")}</strong>
      </div>
      <p>${escapeHtml(item.summary || "")}</p>
      <div class="alert-metrics">${relation}${score}</div>
      <ul>${reasons}</ul>
      <p class="alert-watch">${escapeHtml(item.watch || "")}</p>
    </article>
  `;
}

function openSignalDialog(type) {
  const group = currentDashboard?.alerts?.[type];
  if (!group || !group.items || group.items.length === 0) return;
  const dialog = document.getElementById("signalDialog");
  const eyebrow = {
    opportunity: "资金扩散观察",
    risk: "风险与回调观察",
    volatility: "GARCH 波动率异常检测",
  };
  document.getElementById("signalDialogEyebrow").textContent = eyebrow[type] || "信号提示";
  document.getElementById("signalDialogTitle").textContent = group.title || "提示";
  document.getElementById("signalDialogSummary").textContent = group.summary || "";
  document.getElementById("signalDialogList").innerHTML = group.items.map(renderAlertItem).join("");
  dialog.hidden = false;
  document.body.classList.add("modal-open");
}

function closeSignalDialog() {
  document.getElementById("signalDialog").hidden = true;
  document.body.classList.remove("modal-open");
}

function renderDashboard(data) {
  currentDashboard = data;
  renderFundFlow(data.fundFlow);
  renderKpis(data.summary);
  renderAlertCards(data.alerts);
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
  document.getElementById("openOpportunity").addEventListener("click", () => openSignalDialog("opportunity"));
  document.getElementById("openRisk").addEventListener("click", () => openSignalDialog("risk"));
  document.getElementById("openVolatility").addEventListener("click", () => openSignalDialog("volatility"));
  document.getElementById("closeSignalDialog").addEventListener("click", closeSignalDialog);
  document.getElementById("signalDialog").addEventListener("click", (event) => {
    if (event.target.id === "signalDialog") closeSignalDialog();
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeSignalDialog();
  });
  loadDashboard().catch((error) => {
    document.getElementById("statusText").textContent = `读取失败：${error.message}`;
  });
});
