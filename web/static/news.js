const escapeHtml = (value) => String(value ?? "")
  .replaceAll("&", "&amp;")
  .replaceAll("<", "&lt;")
  .replaceAll(">", "&gt;")
  .replaceAll('"', "&quot;")
  .replaceAll("'", "&#039;");

function formatTime(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function statusLabel(status) {
  const labels = {
    ok: "已接入",
    empty: "暂无条目",
    error: "暂不可达",
    source_only: "来源入口",
  };
  return labels[status] || status || "来源入口";
}

function sourceStatusClass(status) {
  if (status === "ok") return "ok";
  if (status === "error") return "error";
  if (status === "empty") return "empty";
  return "source-only";
}

function renderNewsItems(source) {
  const items = source.items || [];
  if (!items.length) {
    const message = source.status === "error"
      ? `该源本次抓取失败：${source.error || "网络或解析异常"}`
      : source.note || "该源需要打开来源查看。";
    return `<div class="news-source-empty">${escapeHtml(message)}</div>`;
  }
  return `
    <div class="news-item-list">
      ${items.map((item) => `
        <article class="news-item">
          <a href="${escapeHtml(item.url || source.source_url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(item.title)}</a>
          <div class="news-item-meta">${escapeHtml(formatTime(item.published_at))}</div>
          ${item.summary ? `<p>${escapeHtml(item.summary)}</p>` : ""}
        </article>
      `).join("")}
    </div>
  `;
}

function renderSource(source) {
  return `
    <article class="news-source-card ${sourceStatusClass(source.status)}">
      <div class="news-source-head">
        <div>
          <span>${escapeHtml(statusLabel(source.status))}</span>
          <h3>${escapeHtml(source.name)}</h3>
        </div>
        <a href="${escapeHtml(source.source_url || source.feed_url || "#")}" target="_blank" rel="noopener noreferrer">打开来源</a>
      </div>
      ${renderNewsItems(source)}
      ${source.feed_url ? `<p class="news-feed-note">公开源：${escapeHtml(source.feed_url)}</p>` : ""}
    </article>
  `;
}

function renderNews(data) {
  const board = document.getElementById("newsBoard");
  const method = document.getElementById("newsMethod");
  method.textContent = `${data.method || ""} 更新时间：${formatTime(data.updated_at) || "暂无"}`;
  board.innerHTML = (data.groups || []).map((group) => `
    <section class="news-section ${escapeHtml(group.id)}">
      <div class="news-section-heading">
        <div>
          <p class="eyebrow">${escapeHtml(group.id === "policy" ? "置顶" : "分层")}</p>
          <h2>${escapeHtml(group.title)}</h2>
          <p>${escapeHtml(group.description)}</p>
        </div>
        <strong>${escapeHtml(group.item_count ?? 0)} 条</strong>
      </div>
      <div class="news-source-grid">
        ${(group.sources || []).map(renderSource).join("")}
      </div>
    </section>
  `).join("");
}

async function loadNews() {
  const button = document.getElementById("refreshNewsBtn");
  const method = document.getElementById("newsMethod");
  button.disabled = true;
  method.textContent = "正在刷新新闻源...";
  try {
    const response = await fetch(`/api/news?ts=${Date.now()}`);
    if (!response.ok) throw new Error(`news ${response.status}`);
    renderNews(await response.json());
  } catch (error) {
    document.getElementById("newsBoard").innerHTML = `<div class="empty">新闻读取失败：${escapeHtml(error.message)}</div>`;
    method.textContent = "新闻源暂时不可用。";
  } finally {
    button.disabled = false;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("refreshNewsBtn").addEventListener("click", loadNews);
  loadNews();
});
