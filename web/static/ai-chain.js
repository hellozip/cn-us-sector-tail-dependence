const FUNDAMENTAL_PAGE_URL = "https://hellozip.github.io/us-stock-fundamental-dashboard/static/index.html";

const qqqSourceNote =
  "股票筛选口径：严格并集 = Nasdaq-100/QQQ 中的产业链相关股票 ∪ 你的基本面资料库中已覆盖的产业链相关股票。Nasdaq 成分数据时间为 Jul 6, 2026 11:24 AM；QQQ 实际持仓会随基金披露变化。";

const stockCatalog = {
  NVDA: {
    name: "NVIDIA",
    cn: "英伟达",
    theme: "AI PC",
    role: "GPU、AI 工厂、训练与推理平台",
    qqq: true,
    research: true,
    officialUrl: "https://www.nvidia.com/",
  },
  AMD: {
    name: "Advanced Micro Devices",
    cn: "AMD",
    theme: "AI Agent",
    role: "GPU/CPU、AI 加速器、推理算力",
    qqq: true,
    research: true,
    officialUrl: "https://www.amd.com/",
  },
  QCOM: {
    name: "Qualcomm",
    cn: "高通",
    theme: "端侧AI",
    role: "端侧 AI、车载与低功耗推理芯片",
    qqq: true,
    research: true,
    officialUrl: "https://www.qualcomm.com/",
  },
  MRVL: {
    name: "Marvell Technology",
    cn: "Marvell",
    theme: "AI PC",
    role: "AI 网络、定制芯片、高速互联",
    qqq: true,
    research: true,
    officialUrl: "https://www.marvell.com/",
  },
  MU: {
    name: "Micron Technology",
    cn: "美光",
    theme: "AI PC",
    role: "HBM、DRAM、NAND 与 AI 内存周期",
    qqq: true,
    research: true,
    officialUrl: "https://www.micron.com/",
  },
  ALAB: {
    name: "Astera Labs",
    cn: "Astera Labs",
    theme: "AI Agent / 光通信",
    role: "PCIe/CXL 连接、AI 服务器高速互联",
    qqq: true,
    research: true,
    officialUrl: "https://www.asteralabs.com/",
  },
  MSFT: {
    name: "Microsoft",
    cn: "微软",
    theme: "AI PC",
    role: "Azure、Copilot、企业 AI 平台",
    qqq: true,
    research: true,
    officialUrl: "https://www.microsoft.com/",
  },
  CRWV: {
    name: "CoreWeave",
    cn: "CoreWeave",
    theme: "电力基建",
    role: "AI 云算力、GPU 租赁、数据中心容量",
    qqq: true,
    research: true,
    officialUrl: "https://www.coreweave.com/",
  },
  NBIS: {
    name: "Nebius Group",
    cn: "Nebius",
    theme: "电力基建",
    role: "AI 云、GPU 集群、算力平台扩张",
    qqq: true,
    research: true,
    officialUrl: "https://nebius.com/",
  },
  LITE: {
    name: "Lumentum",
    cn: "Lumentum",
    theme: "光通信",
    role: "数据中心光器件、激光器、光互联",
    qqq: true,
    research: true,
    officialUrl: "https://www.lumentum.com/",
  },
  STX: {
    name: "Seagate Technology",
    cn: "希捷",
    theme: "内存",
    role: "大容量存储、AI 数据湖、近线硬盘",
    qqq: true,
    research: true,
    officialUrl: "https://www.seagate.com/",
  },
  SNDK: {
    name: "SanDisk",
    cn: "SanDisk",
    theme: "内存",
    role: "NAND/闪存、边缘与数据存储",
    qqq: true,
    research: true,
    officialUrl: "https://www.sandisk.com/",
  },
  TER: {
    name: "Teradyne",
    cn: "泰瑞达",
    theme: "物理AI",
    role: "半导体测试、机器人、工业自动化测试",
    qqq: true,
    research: true,
    officialUrl: "https://www.teradyne.com/",
  },
  ISRG: {
    name: "Intuitive Surgical",
    cn: "直觉外科",
    theme: "机器人",
    role: "手术机器人、AI 医疗自动化",
    qqq: true,
    research: true,
    officialUrl: "https://www.intuitive.com/",
  },
  CRWD: {
    name: "CrowdStrike",
    cn: "CrowdStrike",
    theme: "网络安全",
    role: "AI 安全、身份与终端防护",
    qqq: true,
    research: true,
    officialUrl: "https://www.crowdstrike.com/",
  },
  RKLB: {
    name: "Rocket Lab",
    cn: "Rocket Lab",
    theme: "商业航天",
    role: "空天数据、卫星基础设施、边缘载荷",
    qqq: true,
    research: true,
    officialUrl: "https://www.rocketlabusa.com/",
  },
  DELL: {
    name: "Dell Technologies",
    cn: "戴尔科技",
    theme: "AI PC",
    role: "AI 服务器、企业基础设施、整机交付",
    qqq: false,
    research: true,
    officialUrl: "https://www.dell.com/",
  },
  TSM: {
    name: "Taiwan Semiconductor Manufacturing",
    cn: "台积电",
    theme: "AI Agent",
    role: "先进制程、代工产能、AI 芯片制造",
    qqq: false,
    research: true,
    officialUrl: "https://www.tsmc.com/",
  },
  "000660.KS": {
    name: "SK hynix",
    cn: "海力士",
    theme: "内存",
    role: "HBM、DRAM、高端内存供给",
    qqq: false,
    research: true,
    officialUrl: "https://www.skhynix.com/",
  },
  COHR: {
    name: "Coherent",
    cn: "Coherent",
    theme: "光通信",
    role: "光模块、激光器、数据中心光互联",
    qqq: false,
    research: true,
    officialUrl: "https://www.coherent.com/",
  },
  IREN: {
    name: "IREN",
    cn: "IREN",
    theme: "电力基建",
    role: "AI 数据中心、电力资源、算力基础设施",
    qqq: false,
    research: true,
    officialUrl: "https://iren.com/",
  },
  FORM: {
    name: "FormFactor",
    cn: "FormFactor",
    theme: "CPO封装",
    role: "晶圆级测试、探针卡、先进封装测试",
    qqq: false,
    research: true,
    officialUrl: "https://www.formfactor.com/",
  },
  KEYS: {
    name: "Keysight Technologies",
    cn: "是德科技",
    theme: "CPO封装",
    role: "高速通信测试、CPO/硅光测试",
    qqq: false,
    research: true,
    officialUrl: "https://www.keysight.com/",
  },
  ANET: {
    name: "Arista Networks",
    cn: "Arista",
    theme: "AI Agent",
    role: "AI 数据中心网络、交换机、云网络",
    qqq: false,
    research: true,
    officialUrl: "https://www.arista.com/",
  },
  CGNX: {
    name: "Cognex",
    cn: "康耐视",
    theme: "物理AI",
    role: "机器视觉、工业质检、边缘识别",
    qqq: false,
    research: true,
    officialUrl: "https://www.cognex.com/",
  },
  ROK: {
    name: "Rockwell Automation",
    cn: "罗克韦尔自动化",
    theme: "物理AI",
    role: "工业自动化、机器人控制、智能制造",
    qqq: false,
    research: true,
    officialUrl: "https://www.rockwellautomation.com/",
  },
  AME: {
    name: "AMETEK",
    cn: "AMETEK",
    theme: "物理AI",
    role: "工业仪器、传感器、自动化测量",
    qqq: false,
    research: true,
    officialUrl: "https://www.ametek.com/",
  },
  SERV: {
    name: "Serve Robotics",
    cn: "Serve Robotics",
    theme: "机器人",
    role: "配送机器人、服务机器人商业化",
    qqq: false,
    research: true,
    officialUrl: "https://www.serverobotics.com/",
  },
  ASTS: {
    name: "AST SpaceMobile",
    cn: "AST SpaceMobile",
    theme: "商业航天",
    role: "卫星通信、空天数据连接",
    qqq: false,
    research: true,
    officialUrl: "https://ast-science.com/",
  },
  MNTS: {
    name: "Momentus",
    cn: "Momentus",
    theme: "商业航天",
    role: "太空基础设施、轨道服务",
    qqq: false,
    research: true,
    officialUrl: "https://momentus.space/",
  },
  AVGO: {
    name: "Broadcom",
    cn: "博通",
    theme: "QQQ",
    role: "AI 网络芯片、ASIC、互联与基础设施软件",
    qqq: true,
    research: false,
    officialUrl: "https://www.broadcom.com/",
  },
  AMAT: {
    name: "Applied Materials",
    cn: "应用材料",
    theme: "QQQ",
    role: "半导体设备、先进制程与封装设备",
    qqq: true,
    research: false,
    officialUrl: "https://www.appliedmaterials.com/",
  },
  ASML: {
    name: "ASML",
    cn: "阿斯麦",
    theme: "QQQ",
    role: "EUV 光刻、先进制程关键设备",
    qqq: true,
    research: false,
    officialUrl: "https://www.asml.com/",
  },
  ARM: {
    name: "Arm Holdings",
    cn: "Arm",
    theme: "QQQ",
    role: "CPU/IP、端侧 AI 架构、低功耗计算",
    qqq: true,
    research: false,
    officialUrl: "https://www.arm.com/",
  },
  INTC: {
    name: "Intel",
    cn: "英特尔",
    theme: "QQQ",
    role: "CPU、晶圆制造、AI PC 与边缘计算",
    qqq: true,
    research: false,
    officialUrl: "https://www.intel.com/",
  },
  TXN: {
    name: "Texas Instruments",
    cn: "德州仪器",
    theme: "QQQ",
    role: "模拟芯片、嵌入式处理、工业与汽车电子",
    qqq: true,
    research: false,
    officialUrl: "https://www.ti.com/",
  },
  CDNS: {
    name: "Cadence Design Systems",
    cn: "Cadence",
    theme: "QQQ",
    role: "EDA、芯片设计软件、仿真验证",
    qqq: true,
    research: false,
    officialUrl: "https://www.cadence.com/",
  },
  SNPS: {
    name: "Synopsys",
    cn: "Synopsys",
    theme: "QQQ",
    role: "EDA、IP、芯片设计验证",
    qqq: true,
    research: false,
    officialUrl: "https://www.synopsys.com/",
  },
  AMZN: {
    name: "Amazon",
    cn: "亚马逊",
    theme: "QQQ",
    role: "AWS、AI 云、企业应用与数据平台",
    qqq: true,
    research: false,
    officialUrl: "https://www.amazon.com/",
  },
  GOOGL: {
    name: "Alphabet",
    cn: "谷歌",
    theme: "QQQ",
    role: "Google Cloud、搜索、多模态模型与数据平台",
    qqq: true,
    research: false,
    officialUrl: "https://abc.xyz/",
  },
  META: {
    name: "Meta Platforms",
    cn: "Meta",
    theme: "QQQ",
    role: "大模型、推荐系统、AI 广告与社交入口",
    qqq: true,
    research: false,
    officialUrl: "https://about.meta.com/",
  },
  ADBE: {
    name: "Adobe",
    cn: "Adobe",
    theme: "QQQ",
    role: "生成式内容、AI 办公、创意软件",
    qqq: true,
    research: false,
    officialUrl: "https://www.adobe.com/",
  },
  ADSK: {
    name: "Autodesk",
    cn: "Autodesk",
    theme: "QQQ",
    role: "设计软件、工业建模、生成式设计",
    qqq: true,
    research: false,
    officialUrl: "https://www.autodesk.com/",
  },
  PLTR: {
    name: "Palantir",
    cn: "Palantir",
    theme: "QQQ",
    role: "AI 决策平台、企业数据操作系统",
    qqq: true,
    research: false,
    officialUrl: "https://www.palantir.com/",
  },
  PANW: {
    name: "Palo Alto Networks",
    cn: "Palo Alto Networks",
    theme: "QQQ",
    role: "云安全、网络安全平台、AI 防御",
    qqq: true,
    research: false,
    officialUrl: "https://www.paloaltonetworks.com/",
  },
  DDOG: {
    name: "Datadog",
    cn: "Datadog",
    theme: "QQQ",
    role: "可观测性、MLOps 监控、云运维",
    qqq: true,
    research: false,
    officialUrl: "https://www.datadoghq.com/",
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
        ["NVDA", "AMD", "QCOM", "MRVL", "MU", "ALAB", "AVGO", "ARM", "ASML", "AMAT", "INTC", "TXN", "TSM", "000660.KS", "FORM", "KEYS"],
      ],
      [
        "服务器",
        "server",
        "AI 服务器把芯片、内存、网络、散热和整机集成成可部署算力。",
        "关注整机出货、液冷渗透率、ODM 订单和零部件供应瓶颈。",
        "工业 / 半导体 / 材料",
        ["NVDA", "AMD", "MRVL", "MU", "ALAB", "DELL", "ANET", "AVGO", "STX", "SNDK"],
      ],
      [
        "云计算",
        "cloud",
        "云厂商把算力资源产品化，承接模型训练、推理和企业 AI 部署需求。",
        "关注云收入增速、AI 资本开支、GPU 利用率和客户迁移趋势。",
        "互联网 / 半导体 / 公用事业",
        ["MSFT", "AMZN", "GOOGL", "NVDA", "AMD", "CRWV", "NBIS"],
      ],
      [
        "数据中心",
        "datacenter",
        "数据中心提供机柜、电力、网络、冷却和运维，是 AI 算力落地的物理空间。",
        "关注电力容量、PUE、液冷改造、土地资源和长约租赁需求。",
        "地产链 / 公用事业 / 能源 / 工业",
        ["CRWV", "NBIS", "NVDA", "MRVL", "LITE", "COHR", "ALAB", "ANET", "STX", "DELL", "IREN", "AVGO"],
      ],
      [
        "算力租赁",
        "compute",
        "把 GPU 集群按时长或任务出租，连接短期算力需求和高成本硬件供给。",
        "关注租赁价格、利用率、回本周期、客户集中度和硬件折旧。",
        "互联网 / 金融 / 半导体",
        ["CRWV", "NBIS", "NVDA", "AMD", "MSFT", "AMZN", "GOOGL", "IREN"],
      ],
      [
        "数据采集与标注",
        "data",
        "高质量数据、标注、清洗和合成数据决定模型训练质量与垂直场景可用性。",
        "关注数据合规、标注成本、私域数据壁垒和行业数据闭环。",
        "互联网 / 医药 / 工业",
        ["MSFT", "GOOGL", "META", "AMZN", "STX", "SNDK", "RKLB", "ASTS", "MNTS"],
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
        ["MSFT", "NVDA", "AMD", "GOOGL", "META", "AMZN", "PLTR"],
      ],
      [
        "算法框架",
        "framework",
        "训练框架、编译器、算子库和加速库决定硬件性能能否充分释放。",
        "关注生态占有率、硬件适配、开发者活跃度和性能提升幅度。",
        "半导体 / 互联网",
        ["NVDA", "AMD", "QCOM", "ARM", "CDNS", "SNPS"],
      ],
      [
        "AI 开发平台",
        "platform",
        "提供模型调用、应用编排、智能体开发、插件和企业集成工具。",
        "关注开发者数量、企业客户续费、插件生态和应用上线速度。",
        "互联网 / 金融 / 工业",
        ["MSFT", "NVDA", "PLTR", "ADBE", "ADSK", "CRWD"],
      ],
      [
        "MLOps",
        "mlops",
        "覆盖模型训练、部署、监控、评估、回滚和治理，让 AI 系统可持续运维。",
        "关注企业部署率、模型治理需求、安全合规和自动化运维效率。",
        "互联网 / 金融 / 医药",
        ["MSFT", "DDOG", "PLTR", "CRWD", "NVDA"],
      ],
      [
        "向量数据库",
        "vector",
        "通过向量检索和 RAG 支持知识库、搜索、推荐和企业私域问答。",
        "关注数据接入量、检索延迟、云数据库集成和企业知识库项目。",
        "互联网 / 金融 / 医药",
        ["MSFT", "GOOGL", "AMZN", "NVDA"],
      ],
      [
        "模型训练与推理平台",
        "inference",
        "负责集群调度、训练加速、推理服务、模型压缩和成本优化。",
        "关注推理量增长、单位 token 成本、模型压缩效果和平台锁定能力。",
        "互联网 / 半导体 / 公用事业",
        ["NVDA", "AMD", "MSFT", "QCOM", "MRVL", "CRWV", "NBIS", "AVGO", "ARM", "AMZN", "GOOGL"],
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
        ["MSFT", "ADBE", "GOOGL", "META"],
      ],
      [
        "AI 搜索",
        "search",
        "用生成式答案、RAG 和智能体重构搜索入口与广告分发方式。",
        "关注查询份额、广告变现、答案准确性和内容版权成本。",
        "互联网",
        ["MSFT", "GOOGL", "META", "AMZN", "NVDA"],
      ],
      [
        "AI 教育",
        "education",
        "个性化辅导、题目讲解、语言学习和教学内容生成提高教育服务效率。",
        "关注获客成本、续费率、合规政策和教学效果可验证性。",
        "互联网 / 消费",
        ["MSFT", "GOOGL", "ADBE", "NVDA"],
      ],
      [
        "AI 医疗",
        "medical",
        "覆盖辅助诊断、影像识别、药物研发、病历生成和患者管理。",
        "关注临床验证、监管审批、医院采购周期和数据合规。",
        "医药 / 互联网",
        ["ISRG", "NVDA", "MSFT", "GOOGL"],
      ],
      [
        "智能客服",
        "service",
        "用文本、语音和工单自动化降低客服成本，并提升响应速度。",
        "关注替代率、客户满意度、人工接管率和企业续费。",
        "互联网 / 金融",
        ["MSFT", "GOOGL", "AMZN", "ADBE"],
      ],
      [
        "自动驾驶",
        "auto",
        "感知、决策、仿真和车端算力共同推动辅助驾驶和无人驾驶演进。",
        "关注装车率、事故率、监管许可、车端芯片和数据闭环。",
        "工业 / 半导体 / 新能源",
        ["NVDA", "QCOM", "AMD", "ARM", "INTC"],
      ],
      [
        "工业质检",
        "inspection",
        "视觉模型和边缘推理用于缺陷检测、良率提升和生产线自动化。",
        "关注落地项目数、良率改善、设备回收期和制造业资本开支。",
        "工业 / 半导体 / 材料",
        ["NVDA", "AMD", "TER", "QCOM", "CGNX", "ROK", "AME", "FORM", "KEYS"],
      ],
      [
        "网络安全",
        "security",
        "AI 正在把终端安全、身份权限、云安全和威胁响应合并成实时防御平台。",
        "关注 ARR 增速、客户续费、企业安全预算、Agent 身份权限和 AI 攻防自动化。",
        "互联网 / 金融 / 工业",
        ["CRWD", "PANW", "MSFT", "DDOG"],
      ],
      [
        "机器人",
        "robot",
        "大模型、多模态、感知和运动控制推动服务机器人与工业机器人升级。",
        "关注出货量、BOM 成本、场景复购、控制算法和供应链成熟度。",
        "工业 / 半导体 / 材料",
        ["ISRG", "NVDA", "QCOM", "TER", "SERV", "ROK"],
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
const chainHeatByKey = new Map();
let chainRankHeat = null;
let chainRankLoading = true;
let chainHeatList = [];

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

function chainNodeKey(layerId, name) {
  return `${layerId}:${name}`;
}

function fmtChainHeat(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "暂无";
  return Number(value).toFixed(1);
}

function rankInfoForTicker(ticker) {
  if (!chainRankHeat?.rankByTicker) return null;
  return chainRankHeat.rankByTicker[String(ticker || "").trim().toUpperCase()] || null;
}

function computeNodeHeat(layer, item, originalIndex) {
  const [name, , , , , tickers = []] = item;
  const stocks = resolveStocks(tickers);
  const rankedStocks = stocks
    .map((stock) => ({ ...stock, rankInfo: rankInfoForTicker(stock.ticker) }))
    .filter((stock) => stock.rankInfo && Number.isFinite(Number(stock.rankInfo.rank)))
    .sort((left, right) => Number(left.rankInfo.rank) - Number(right.rankInfo.rank));
  if (!rankedStocks.length) {
    return {
      key: chainNodeKey(layer.id, name),
      layerId: layer.id,
      layerTitle: layer.title,
      name,
      available: false,
      heatScore: null,
      rankedCount: 0,
      totalCount: stocks.length,
      rankedStocks: [],
      originalIndex,
    };
  }
  const rankSum = rankedStocks.reduce((sum, stock) => sum + Number(stock.rankInfo.rank), 0);
  return {
    key: chainNodeKey(layer.id, name),
    layerId: layer.id,
    layerTitle: layer.title,
    name,
    available: true,
    heatScore: rankSum / rankedStocks.length,
    rankSum,
    rankedCount: rankedStocks.length,
    totalCount: stocks.length,
    rankedStocks,
    leaders: rankedStocks.slice(0, 4),
    originalIndex,
  };
}

function buildChainHeat() {
  chainHeatByKey.clear();
  chainHeatList = [];
  if (!chainRankHeat?.available) return;
  chainLayers.forEach((layer) => {
    layer.items.forEach((item, originalIndex) => {
      const heat = computeNodeHeat(layer, item, originalIndex);
      chainHeatByKey.set(heat.key, heat);
      if (heat.available) chainHeatList.push(heat);
    });
  });
  chainHeatList.sort((left, right) => (
    left.heatScore - right.heatScore
    || right.rankedCount - left.rankedCount
    || left.name.localeCompare(right.name, "zh-CN")
  ));
  chainHeatList.forEach((heat, index) => {
    heat.heatRank = index + 1;
    const cached = chainHeatByKey.get(heat.key);
    if (cached) cached.heatRank = index + 1;
  });
}

function orderedLayerItems(layer) {
  return layer.items
    .map((item, originalIndex) => {
      const [name] = item;
      return {
        item,
        originalIndex,
        heat: chainHeatByKey.get(chainNodeKey(layer.id, name)),
      };
    })
    .sort((left, right) => {
      const leftHot = left.heat?.available;
      const rightHot = right.heat?.available;
      if (leftHot && rightHot) {
        return left.heat.heatScore - right.heat.heatScore || left.originalIndex - right.originalIndex;
      }
      if (leftHot) return -1;
      if (rightHot) return 1;
      return left.originalIndex - right.originalIndex;
    })
    .map((entry) => entry.item);
}

function renderNodeHeatLine(key) {
  if (chainRankLoading) {
    return `<span class="ai-node-heatline">排名热度：读取中</span>`;
  }
  if (!chainRankHeat?.available) {
    return `<span class="ai-node-heatline muted">排名热度：暂无外部数据</span>`;
  }
  const heat = chainHeatByKey.get(key);
  if (!heat?.available) {
    return `<span class="ai-node-heatline muted">排名源覆盖：0/${escapeHtml(heat?.totalCount ?? 0)}</span>`;
  }
  const leaderText = heat.leaders
    .map((stock) => `${stock.ticker} #${stock.rankInfo.rank}`)
    .join(" / ");
  return `
    <span class="ai-node-heatline ${heat.heatRank <= 5 ? "hot" : ""}">热度 #${heat.heatRank} · 平均排名 ${fmtChainHeat(heat.heatScore)} · 覆盖 ${heat.rankedCount}/${heat.totalCount}</span>
    <span class="ai-node-rankline">${escapeHtml(leaderText)}</span>
  `;
}

function renderChainRankSummary() {
  const target = document.getElementById("chainRankSummary");
  const method = document.getElementById("chainRankMethod");
  const source = document.getElementById("chainRankSource");
  if (!target || !method || !source) return;
  if (chainRankLoading) {
    method.textContent = "正在读取美股排名源。热度 = 节点内已匹配股票 rank 之和 / 已匹配股票数量，数值越低代表热度越高。";
    source.hidden = true;
    target.innerHTML = '<div class="empty">正在生成产业链节点热度排序...</div>';
    return;
  }
  if (!chainRankHeat?.available) {
    method.textContent = chainRankHeat?.error || "外部美股排名源暂时不可用，产业链节点保持原始顺序。";
    source.hidden = true;
    target.innerHTML = '<div class="empty">暂无可用排名热度，已保留原产业链结构。</div>';
    return;
  }
  method.textContent = `数据日：${chainRankHeat.as_of_date || "暂无"}；基准：${chainRankHeat.benchmark || "QQQ"}；排名样本：${chainRankHeat.stock_count || 0} 只。节点热度按已匹配股票平均 rank 升序排列，未被排名源覆盖的股票不纳入分母。`;
  source.href = chainRankHeat.source_url || "#";
  source.hidden = !chainRankHeat.source_url;
  const hotNodes = chainHeatList.slice(0, 10);
  target.innerHTML = hotNodes.length
    ? hotNodes.map((heat) => `
      <button class="chain-rank-chip" type="button" data-node="${escapeHtml(heat.key)}">
        <span>#${heat.heatRank}</span>
        <strong>${escapeHtml(heat.name)}</strong>
        <small>${escapeHtml(heat.layerTitle)} · 平均排名 ${fmtChainHeat(heat.heatScore)} · 覆盖 ${heat.rankedCount}/${heat.totalCount}</small>
      </button>
    `).join("")
    : '<div class="empty">排名源暂未覆盖产业链节点中的股票。</div>';
}

async function loadChainRankHeat() {
  try {
    const response = await fetch("/api/us-rank-heat");
    if (!response.ok) throw new Error(`rank heat ${response.status}`);
    chainRankHeat = await response.json();
  } catch (error) {
    chainRankHeat = {
      available: false,
      error: `外部美股排名源读取失败：${error.message}`,
    };
  } finally {
    chainRankLoading = false;
    buildChainHeat();
    indexNodes();
    renderChain();
    renderChainRankSummary();
  }
}

function stockHint(tickers) {
  if (!tickers.length) return "暂无并集股票";
  const head = tickers.slice(0, 4).join(" / ");
  const suffix = tickers.length > 4 ? ` +${tickers.length - 4}` : "";
  return `${head}${suffix}`;
}

function stockBadges(stock) {
  return [
    stock.qqq ? "QQQ" : "",
    stock.research ? "自研资料库" : "",
  ].filter(Boolean);
}

function renderChain() {
  const board = document.getElementById("aiChainBoard");
  const html = chainLayers.map((layer) => {
    const items = orderedLayerItems(layer).map(([name, visual, summary, , , tickers = []]) => {
      const key = chainNodeKey(layer.id, name);
      const stocks = resolveStocks(tickers);
      const heat = chainHeatByKey.get(key);
      return `
        <button class="ai-node ${layer.id} ${heat?.available && heat.heatRank <= 5 ? "hot-node" : ""}" type="button" data-node="${escapeHtml(key)}" aria-label="查看${escapeHtml(name)}">
          <span class="ai-node-image ${escapeHtml(visual)}" aria-hidden="true"><span></span></span>
          <span class="ai-node-text">
            <strong>${escapeHtml(name)}</strong>
            <small>${escapeHtml(summary)}</small>
            <span class="ai-node-stockline">并集股票：${escapeHtml(stockHint(stocks.map((stock) => stock.ticker)))}</span>
            ${renderNodeHeatLine(key)}
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
  nodeMap.clear();
  chainLayers.forEach((layer) => {
    layer.items.forEach(([name, visual, summary, watch, related, tickers = []]) => {
      const key = chainNodeKey(layer.id, name);
      nodeMap.set(key, {
        layer,
        name,
        visual,
        summary,
        watch,
        related,
        stocks: resolveStocks(tickers),
        heat: chainHeatByKey.get(key) || null,
      });
    });
  });
}

function renderStockLinks(stocks) {
  if (!stocks.length) {
    return `<p class="stock-source-note">暂无符合并集口径的产业链股票。</p>`;
  }
  const rankedStocks = stocks
    .map((stock) => ({ ...stock, rankInfo: rankInfoForTicker(stock.ticker) }))
    .sort((left, right) => {
      const leftRank = Number(left.rankInfo?.rank ?? Number.POSITIVE_INFINITY);
      const rightRank = Number(right.rankInfo?.rank ?? Number.POSITIVE_INFINITY);
      return leftRank - rightRank || left.ticker.localeCompare(right.ticker);
    });
  return `
    <div class="stock-chip-list">
      ${rankedStocks.map((stock) => `
        <article class="chain-stock-card">
          <div class="chain-stock-main">
            <strong>${escapeHtml(stock.ticker)}</strong>
            <span>${escapeHtml(stock.cn)} · ${escapeHtml(stock.name)}</span>
            <small>${escapeHtml(stock.role)}</small>
            <div class="stock-source-badges">
              ${stockBadges(stock).map((badge) => `<em>${escapeHtml(badge)}</em>`).join("")}
              ${
                stock.rankInfo
                  ? `<em class="rank-source-badge">排名 #${escapeHtml(stock.rankInfo.rank)} · ${escapeHtml(stock.rankInfo.stock_type || stock.rankInfo.sector || "")}</em>`
                  : `<em class="rank-source-badge muted">排名源未覆盖</em>`
              }
            </div>
          </div>
          <div class="stock-action-row">
            ${
              stock.research
                ? `<a class="stock-action primary" href="${escapeHtml(stock.url)}" target="_blank" rel="noreferrer">自研网站</a>`
                : `<span class="stock-action disabled" aria-disabled="true" title="你的基本面资料库暂未建立该股票映射">自研网站</span>`
            }
            <a class="stock-action secondary" href="${escapeHtml(stock.officialUrl)}" target="_blank" rel="noreferrer">官网</a>
          </div>
        </article>
      `).join("")}
    </div>
    <p class="stock-source-note">${escapeHtml(qqqSourceNote)}</p>
  `;
}

function renderNodeHeatDetails(node) {
  if (chainRankLoading) {
    return `
      <div class="chain-dialog-section">
        <h3>排名热度</h3>
        <p>正在读取美股排名源，稍后会按节点内股票平均 rank 更新热度。</p>
      </div>
    `;
  }
  if (!chainRankHeat?.available) {
    return `
      <div class="chain-dialog-section">
        <h3>排名热度</h3>
        <p>${escapeHtml(chainRankHeat?.error || "外部美股排名源暂时不可用。")}</p>
      </div>
    `;
  }
  const heat = node.heat;
  if (!heat?.available) {
    return `
      <div class="chain-dialog-section">
        <h3>排名热度</h3>
        <p>该节点的并集股票暂未被当前美股排名源覆盖，因此不参与热度排序。</p>
      </div>
    `;
  }
  const leaders = heat.rankedStocks
    .slice(0, 8)
    .map((stock) => `<span>${escapeHtml(stock.ticker)} #${escapeHtml(stock.rankInfo.rank)}</span>`)
    .join("");
  return `
    <div class="chain-dialog-section">
      <h3>排名热度</h3>
      <p>产业链热度 #${heat.heatRank}；平均排名 ${fmtChainHeat(heat.heatScore)}；排名源覆盖 ${heat.rankedCount}/${heat.totalCount} 只节点股票。平均排名越低，说明该节点中被覆盖股票整体越靠前。</p>
      <div class="node-rank-leaders">${leaders}</div>
    </div>
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
    ${renderNodeHeatDetails(node)}
    <div class="chain-dialog-section chain-stock-section">
      <h3>并集中的相关股票</h3>
      ${renderStockLinks(node.stocks)}
    </div>
    <div class="chain-dialog-section chain-dialog-wide">
      <h3>使用方式</h3>
      <p>先看节点对应的并集股票，再根据按钮进入自研基本面页或公司官网；没有自研映射的股票，自研网站按钮会置灰。随后把这些公司与资金流排名、上尾/中部/下尾相关性和波动异常一起看。如果同一产业链节点的多只股票同时走强，说明资金可能在沿该链条扩散；如果强度偏离过大，也要同时留意回调风险。</p>
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
  renderChainRankSummary();
  loadChainRankHeat();
  document.getElementById("aiChainBoard").addEventListener("click", (event) => {
    const button = event.target.closest("[data-node]");
    if (!button) return;
    openChainDialog(button.dataset.node);
  });
  document.getElementById("chainRankSummary").addEventListener("click", (event) => {
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
