const FUNDAMENTAL_PAGE_URL = "https://hellozip.github.io/us-stock-fundamental-dashboard/static/index.html";

const qqqSourceNote =
  "股票筛选口径：Nasdaq-100/QQQ 口径下，且你的基本面研究驾驶舱已有资料的股票。Nasdaq 成分数据日期为 2026-07-02；QQQ 跟踪 Nasdaq-100，实际持仓会随基金披露变化。";

const stockCatalog = {
  NVDA: {
    name: "NVIDIA",
    cn: "英伟达",
    theme: "AI PC",
    role: "GPU、AI 工厂、训练与推理平台",
  },
  AMD: {
    name: "Advanced Micro Devices",
    cn: "AMD",
    theme: "AI Agent",
    role: "GPU/CPU、AI 加速器、推理算力",
  },
  QCOM: {
    name: "Qualcomm",
    cn: "高通",
    theme: "端侧AI",
    role: "端侧 AI、车载与低功耗推理芯片",
  },
  MRVL: {
    name: "Marvell Technology",
    cn: "Marvell",
    theme: "AI PC",
    role: "AI 网络、定制芯片、高速互联",
  },
  MU: {
    name: "Micron Technology",
    cn: "美光",
    theme: "AI PC",
    role: "HBM、DRAM、NAND 与 AI 内存周期",
  },
  ALAB: {
    name: "Astera Labs",
    cn: "Astera Labs",
    theme: "AI Agent / 光通信",
    role: "PCIe/CXL 连接、AI 服务器高速互联",
  },
  MSFT: {
    name: "Microsoft",
    cn: "微软",
    theme: "AI PC",
    role: "Azure、Copilot、企业 AI 平台",
  },
  CRWV: {
    name: "CoreWeave",
    cn: "CoreWeave",
    theme: "电力基建",
    role: "AI 云算力、GPU 租赁、数据中心容量",
  },
  NBIS: {
    name: "Nebius Group",
    cn: "Nebius",
    theme: "电力基建",
    role: "AI 云、GPU 集群、算力平台扩张",
  },
  LITE: {
    name: "Lumentum",
    cn: "Lumentum",
    theme: "光通信",
    role: "数据中心光器件、激光器、光互联",
  },
  STX: {
    name: "Seagate Technology",
    cn: "希捷",
    theme: "内存",
    role: "大容量存储、AI 数据湖、近线硬盘",
  },
  SNDK: {
    name: "SanDisk",
    cn: "SanDisk",
    theme: "内存",
    role: "NAND/闪存、边缘与数据存储",
  },
  TER: {
    name: "Teradyne",
    cn: "泰瑞达",
    theme: "物理AI",
    role: "半导体测试、机器人、工业自动化测试",
  },
  ISRG: {
    name: "Intuitive Surgical",
    cn: "直觉外科",
    theme: "机器人",
    role: "手术机器人、AI 医疗自动化",
  },
  CRWD: {
    name: "CrowdStrike",
    cn: "CrowdStrike",
    theme: "网络安全",
    role: "AI 安全、身份与终端风控",
  },
  RKLB: {
    name: "Rocket Lab",
    cn: "Rocket Lab",
    theme: "商业航天",
    role: "空天数据、卫星基础设施、边缘载荷",
  },
};

const chainLayers = [
  {
    id: "upstream",
    title: "上游基础层",
    summary: "决定 AI 产业扩张速度的底座，核心是算力、数据、供电和基础设施资本开支。",
    items: [
      [
        "芯片",
        "chip",
        "GPU、AI ASIC、HBM、先进封装和高速互联是训练与推理成本的核心来源。",
        "关注交付周期、价格、库存、先进制程供给和大客户资本开支。",
        "半导体 / 材料 / 工业",
        ["NVDA", "AMD", "QCOM", "MRVL", "MU", "ALAB"],
      ],
      [
        "服务器",
        "server",
        "AI 服务器把芯片、内存、网络、散热和整机集成成可部署算力。",
        "关注整机出货、液冷渗透率、ODM 订单和零部件供应瓶颈。",
        "工业 / 半导体 / 材料",
        ["NVDA", "AMD", "MRVL", "MU", "ALAB"],
      ],
      [
        "云计算",
        "cloud",
        "云厂商把算力资源产品化，承接模型训练、推理和企业 AI 部署需求。",
        "关注云收入增速、AI 资本开支、GPU 利用率和客户迁移趋势。",
        "互联网 / 半导体 / 公用事业",
        ["MSFT", "NVDA", "AMD", "CRWV", "NBIS"],
      ],
      [
        "数据中心",
        "datacenter",
        "数据中心提供机柜、电力、网络、冷却和运维，是 AI 算力落地的物理空间。",
        "关注电力容量、PUE、液冷改造、土地资源和长约租赁需求。",
        "地产链 / 公用事业 / 能源 / 工业",
        ["CRWV", "NBIS", "NVDA", "MRVL", "LITE", "ALAB", "STX"],
      ],
      [
        "算力租赁",
        "compute",
        "把 GPU 集群按时长或任务出租，连接短期算力需求和高成本硬件供给。",
        "关注租赁价格、利用率、回本周期、客户集中度和硬件折旧。",
        "互联网 / 金融 / 半导体",
        ["CRWV", "NBIS", "NVDA", "AMD", "MSFT"],
      ],
      [
        "数据采集与标注",
        "data",
        "高质量数据、标注、清洗和合成数据决定模型训练质量与垂直场景可用性。",
        "关注数据合规、标注成本、私域数据壁垒和行业数据闭环。",
        "互联网 / 医药 / 工业",
        ["MSFT", "CRWD", "STX", "SNDK", "RKLB"],
      ],
    ],
  },
  {
    id: "midstream",
    title: "中游技术/平台层",
    summary: "把算力和数据转化为模型能力、开发工具和可规模化部署的平台。",
    items: [
      [
        "大模型",
        "model",
        "基础模型、多模态模型和行业模型是 AI 能力输出的核心载体。",
        "关注 API 调用量、推理成本、模型迭代速度、开源竞争和商业化价格。",
        "互联网 / 半导体 / 金融",
        ["MSFT", "NVDA", "AMD"],
      ],
      [
        "算法框架",
        "framework",
        "训练框架、编译器、算子库和加速库决定硬件性能能否充分释放。",
        "关注生态占有率、硬件适配、开发者活跃度和性能提升幅度。",
        "半导体 / 互联网",
        ["NVDA", "AMD", "QCOM"],
      ],
      [
        "AI 开发平台",
        "platform",
        "提供模型调用、应用编排、智能体开发、插件和企业集成工具。",
        "关注开发者数量、企业客户续费、插件生态和应用上线速度。",
        "互联网 / 金融 / 工业",
        ["MSFT", "NVDA", "CRWD"],
      ],
      [
        "MLOps",
        "mlops",
        "覆盖模型训练、部署、监控、评估、回滚和治理，让 AI 系统可持续运维。",
        "关注企业部署率、模型治理需求、安全合规和自动化运维效率。",
        "互联网 / 金融 / 医药",
        ["MSFT", "CRWD", "NVDA"],
      ],
      [
        "向量数据库",
        "vector",
        "通过向量检索和 RAG 支持知识库、搜索、推荐和企业私域问答。",
        "关注数据接入量、检索延迟、云数据库集成和企业知识库项目。",
        "互联网 / 金融 / 医药",
        ["MSFT", "NVDA"],
      ],
      [
        "模型训练与推理平台",
        "inference",
        "负责集群调度、训练加速、推理服务、模型压缩和成本优化。",
        "关注推理量增长、单位 token 成本、模型压缩效果和平台锁定能力。",
        "互联网 / 半导体 / 公用事业",
        ["NVDA", "AMD", "MSFT", "QCOM", "MRVL", "CRWV", "NBIS"],
      ],
    ],
  },
  {
    id: "downstream",
    title: "下游应用层",
    summary: "把模型能力转成用户付费、效率提升和行业解决方案，决定商业化弹性。",
    items: [
      [
        "AI 办公",
        "office",
        "文档、表格、会议、邮件和知识管理场景最容易形成高频付费入口。",
        "关注付费转化率、ARPU、企业渗透率和与原有办公套件的绑定。",
        "互联网 / 金融",
        ["MSFT"],
      ],
      [
        "AI 搜索",
        "search",
        "用生成式答案、RAG 和智能体重构搜索入口与广告分发方式。",
        "关注查询份额、广告变现、答案准确性和内容版权成本。",
        "互联网",
        ["MSFT", "NVDA"],
      ],
      [
        "AI 教育",
        "education",
        "个性化辅导、题目讲解、语言学习和教学内容生成提高教育服务效率。",
        "关注获客成本、续费率、合规政策和教学效果可验证性。",
        "互联网 / 消费",
        ["MSFT", "NVDA"],
      ],
      [
        "AI 医疗",
        "medical",
        "覆盖辅助诊断、影像识别、药物研发、病历生成和患者管理。",
        "关注临床验证、监管审批、医院采购周期和数据合规。",
        "医药 / 互联网",
        ["ISRG", "NVDA", "MSFT"],
      ],
      [
        "智能客服",
        "service",
        "用文本、语音和工单自动化降低客服成本，并提升响应速度。",
        "关注替代率、客户满意度、人工接管率和企业续费。",
        "互联网 / 金融",
        ["MSFT", "CRWD"],
      ],
      [
        "自动驾驶",
        "auto",
        "感知、决策、仿真和车端算力共同推动辅助驾驶和无人驾驶演进。",
        "关注装车率、事故率、监管许可、车端芯片和数据闭环。",
        "工业 / 半导体 / 新能源",
        ["NVDA", "QCOM", "AMD"],
      ],
      [
        "工业质检",
        "inspection",
        "视觉模型和边缘推理用于缺陷检测、良率提升和生产线自动化。",
        "关注落地项目数、良率改善、设备回收期和制造业资本开支。",
        "工业 / 半导体 / 材料",
        ["NVDA", "AMD", "TER", "QCOM"],
      ],
      [
        "金融风控",
        "risk",
        "用图模型、异常检测、文本理解和智能审核提升风控与合规效率。",
        "关注坏账率改善、模型可解释性、监管要求和实时决策能力。",
        "金融 / 互联网",
        ["CRWD", "MSFT", "NVDA"],
      ],
      [
        "机器人",
        "robot",
        "大模型、多模态、感知和运动控制推动服务机器人与工业机器人升级。",
        "关注出货量、BOM 成本、场景复购、控制算法和供应链成熟度。",
        "工业 / 半导体 / 材料",
        ["ISRG", "NVDA", "QCOM", "TER"],
      ],
    ],
  },
];

const escapeHtml = (value) => String(value ?? "")
  .replaceAll("&", "&amp;")
  .replaceAll("<", "&lt;")
  .replaceAll(">", "&gt;")
  .replaceAll('"', "&quot;")
  .replaceAll("'", "&#039;");

const nodeMap = new Map();

function fundamentalUrl(ticker) {
  const params = new URLSearchParams({
    ticker,
    q: ticker,
    source: "ai-chain",
  });
  return `${FUNDAMENTAL_PAGE_URL}?${params.toString()}#companies`;
}

function resolveStocks(tickers) {
  const seen = new Set();
  return tickers
    .filter((ticker) => stockCatalog[ticker] && !seen.has(ticker) && seen.add(ticker))
    .map((ticker) => ({ ticker, ...stockCatalog[ticker], url: fundamentalUrl(ticker) }));
}

function stockHint(tickers) {
  if (!tickers.length) return "暂无 QQQ 交集";
  const head = tickers.slice(0, 4).join(" / ");
  const suffix = tickers.length > 4 ? ` +${tickers.length - 4}` : "";
  return `${head}${suffix}`;
}

function renderChain() {
  const board = document.getElementById("aiChainBoard");
  const html = chainLayers.map((layer) => {
    const items = layer.items.map(([name, visual, summary, , , tickers = []]) => {
      const key = `${layer.id}:${name}`;
      const stocks = resolveStocks(tickers);
      return `
        <button class="ai-node ${layer.id}" type="button" data-node="${escapeHtml(key)}" aria-label="查看${escapeHtml(name)}">
          <span class="ai-node-image ${escapeHtml(visual)}" aria-hidden="true"><span></span></span>
          <span class="ai-node-text">
            <strong>${escapeHtml(name)}</strong>
            <small>${escapeHtml(summary)}</small>
            <span class="ai-node-stockline">QQQ交集：${escapeHtml(stockHint(stocks.map((stock) => stock.ticker)))}</span>
          </span>
        </button>
      `;
    }).join("");
    return `
      <article class="chain-layer ${layer.id}">
        <div class="chain-layer-heading">
          <p class="eyebrow">${escapeHtml(layer.title)}</p>
          <h2>${escapeHtml(layer.summary)}</h2>
        </div>
        <div class="ai-node-grid">${items}</div>
      </article>
    `;
  }).join("");
  board.innerHTML = html;
}

function indexNodes() {
  chainLayers.forEach((layer) => {
    layer.items.forEach(([name, visual, summary, watch, related, tickers = []]) => {
      nodeMap.set(`${layer.id}:${name}`, {
        layer,
        name,
        visual,
        summary,
        watch,
        related,
        stocks: resolveStocks(tickers),
      });
    });
  });
}

function renderStockLinks(stocks) {
  if (!stocks.length) {
    return `<p class="stock-source-note">暂无符合 QQQ 口径且已进入基本面库的股票。</p>`;
  }
  return `
    <div class="stock-chip-list">
      ${stocks.map((stock) => `
        <a class="chain-stock-chip" href="${escapeHtml(stock.url)}" target="_blank" rel="noreferrer">
          <span>
            <strong>${escapeHtml(stock.ticker)}</strong>
            <small>${escapeHtml(stock.cn)} · ${escapeHtml(stock.role)}</small>
          </span>
          <em>基本面</em>
        </a>
      `).join("")}
    </div>
    <p class="stock-source-note">${escapeHtml(qqqSourceNote)}</p>
  `;
}

function openChainDialog(key) {
  const node = nodeMap.get(key);
  if (!node) return;
  document.getElementById("chainDialogEyebrow").textContent = node.layer.title;
  document.getElementById("chainDialogTitle").textContent = node.name;
  document.getElementById("chainDialogSummary").textContent = node.summary;
  document.getElementById("chainDialogBody").innerHTML = `
    <div class="chain-dialog-visual ai-node-image ${escapeHtml(node.visual)}" aria-hidden="true"><span></span></div>
    <div class="chain-dialog-section">
      <h3>观察重点</h3>
      <p>${escapeHtml(node.watch)}</p>
    </div>
    <div class="chain-dialog-section">
      <h3>可映射板块</h3>
      <p>${escapeHtml(node.related)}</p>
    </div>
    <div class="chain-dialog-section chain-stock-section">
      <h3>QQQ中相关可点击股票</h3>
      ${renderStockLinks(node.stocks)}
    </div>
    <div class="chain-dialog-section chain-dialog-wide">
      <h3>使用方式</h3>
      <p>先看节点对应的 QQQ 股票，再进入基本面页查看公司逻辑；随后把这些公司与资金流排名、上尾/中部/下尾相关性和波动异常一起看。如果同一产业链节点的多只股票同时走强，说明资金可能在沿该链条扩散；如果强度偏离过大，也要同时留意回调风险。</p>
    </div>
  `;
  document.getElementById("chainDialog").hidden = false;
  document.body.classList.add("modal-open");
}

function closeChainDialog() {
  document.getElementById("chainDialog").hidden = true;
  document.body.classList.remove("modal-open");
}

document.addEventListener("DOMContentLoaded", () => {
  indexNodes();
  renderChain();
  document.getElementById("aiChainBoard").addEventListener("click", (event) => {
    const button = event.target.closest("[data-node]");
    if (!button) return;
    openChainDialog(button.dataset.node);
  });
  document.getElementById("closeChainDialog").addEventListener("click", closeChainDialog);
  document.getElementById("chainDialog").addEventListener("click", (event) => {
    if (event.target.id === "chainDialog") closeChainDialog();
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeChainDialog();
  });
});
