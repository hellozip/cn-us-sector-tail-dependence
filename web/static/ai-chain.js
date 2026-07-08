const FUNDAMENTAL_PAGE_URL = "https://hellozip.github.io/us-stock-fundamental-dashboard/static/index.html";

const qqqSourceNote =
  "股票筛选口径：严格并集 = Nasdaq-100/QQQ 中的产业链相关股票 ∪ 你的基本面资料库中已覆盖的产业链相关股票。Nasdaq 成分数据时间为 Jul 6, 2026 11:24 AM；QQQ 实际持仓会随基金披露变化。";

const cnSourceNote =
  "A股筛选口径：沿用同一套 AI 产业链节点，每个节点维护 5 只代表性 A 股，仅用于产业链观察和横向比较，不构成买卖建议。";

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

const cnStockCatalog = {
  "688981.SH": { name: "SMIC", cn: "中芯国际", role: "晶圆代工、先进制程与国产半导体制造底座", market: "A股", exchange: "科创板", officialUrl: "https://www.smics.com/" },
  "688256.SH": { name: "Cambricon", cn: "寒武纪", role: "AI 训练与推理芯片、智能计算加速卡", market: "A股", exchange: "科创板", officialUrl: "https://www.cambricon.com/" },
  "688041.SH": { name: "Hygon", cn: "海光信息", role: "CPU、DCU 与国产算力芯片平台", market: "A股", exchange: "科创板", officialUrl: "https://www.hygon.cn/" },
  "002371.SZ": { name: "NAURA", cn: "北方华创", role: "半导体设备、刻蚀与薄膜沉积设备", market: "A股", exchange: "深交所", officialUrl: "https://www.naura.com/" },
  "603501.SH": { name: "Will Semiconductor", cn: "韦尔股份", role: "图像传感器、车载与边缘 AI 感知芯片", market: "A股", exchange: "上交所", officialUrl: "https://www.willsemi.com/" },
  "603019.SH": { name: "Sugon", cn: "中科曙光", role: "AI 服务器、高性能计算与算力基础设施", market: "A股", exchange: "上交所", officialUrl: "https://www.sugon.com/" },
  "000977.SZ": { name: "Inspur Information", cn: "浪潮信息", role: "AI 服务器、整机交付与数据中心基础设施", market: "A股", exchange: "深交所", officialUrl: "https://www.inspur.com/" },
  "601138.SH": { name: "Foxconn Industrial Internet", cn: "工业富联", role: "AI 服务器制造、云计算硬件与智能制造", market: "A股", exchange: "上交所", officialUrl: "https://www.fii-foxconn.com/" },
  "000938.SZ": { name: "Unisplendour", cn: "紫光股份", role: "云网络、服务器、交换机与企业基础设施", market: "A股", exchange: "深交所", officialUrl: "https://www.unisplendour.com/" },
  "002261.SZ": { name: "Talkweb", cn: "拓维信息", role: "国产算力、教育信息化与 AI 应用平台", market: "A股", exchange: "深交所", officialUrl: "https://www.talkweb.com.cn/" },
  "688111.SH": { name: "Kingsoft Office", cn: "金山办公", role: "AI 办公、文档协作与企业知识管理", market: "A股", exchange: "科创板", officialUrl: "https://www.wps.cn/" },
  "600588.SH": { name: "Yonyou", cn: "用友网络", role: "企业云服务、ERP 与 AI 开发平台", market: "A股", exchange: "上交所", officialUrl: "https://www.yonyou.com/" },
  "600845.SH": { name: "Baosight Software", cn: "宝信软件", role: "工业软件、云服务、数据中心与 MLOps 运维", market: "A股", exchange: "上交所", officialUrl: "https://www.baosight.com/" },
  "300454.SZ": { name: "Sangfor", cn: "深信服", role: "云计算、网络安全、企业 IT 基础设施", market: "A股", exchange: "创业板", officialUrl: "https://www.sangfor.com.cn/" },
  "603881.SH": { name: "Athub", cn: "数据港", role: "IDC 数据中心、机柜与云基础设施", market: "A股", exchange: "上交所", officialUrl: "https://www.athub.com/" },
  "300383.SZ": { name: "Sinnet", cn: "光环新网", role: "IDC、云计算服务与数据中心运营", market: "A股", exchange: "创业板", officialUrl: "https://www.sinnet.com.cn/" },
  "300738.SZ": { name: "Ofidc", cn: "奥飞数据", role: "数据中心、云计算与算力基础设施服务", market: "A股", exchange: "创业板", officialUrl: "https://www.ofidc.com/" },
  "300442.SZ": { name: "Range Intelligent", cn: "润泽科技", role: "大型数据中心、算力基础设施与机柜资源", market: "A股", exchange: "创业板", officialUrl: "https://www.rzidc.com/" },
  "002335.SZ": { name: "Kehua Data", cn: "科华数据", role: "数据中心电源、储能与算力基础设施", market: "A股", exchange: "深交所", officialUrl: "https://www.kehua.com/" },
  "300846.SZ": { name: "CapitalOnline", cn: "首都在线", role: "云服务、GPU 算力租赁与海外云资源", market: "A股", exchange: "创业板", officialUrl: "https://www.capitalonline.net/" },
  "688787.SH": { name: "Speechocean", cn: "海天瑞声", role: "训练数据、语音数据与数据标注服务", market: "A股", exchange: "科创板", officialUrl: "https://www.speechocean.com/" },
  "300229.SZ": { name: "TRS", cn: "拓尔思", role: "语义智能、数据中台、大模型与智能搜索", market: "A股", exchange: "创业板", officialUrl: "https://www.trs.com.cn/" },
  "002230.SZ": { name: "iFLYTEK", cn: "科大讯飞", role: "语音 AI、大模型、教育与行业应用平台", market: "A股", exchange: "深交所", officialUrl: "https://www.iflytek.com/" },
  "300678.SZ": { name: "CASIC", cn: "中科信息", role: "数据智能、行业 AI 与信息化解决方案", market: "A股", exchange: "创业板", officialUrl: "https://www.casinfo.com.cn/" },
  "300766.SZ": { name: "Daily Interactive", cn: "每日互动", role: "数据智能、用户画像、数据采集与分析", market: "A股", exchange: "创业板", officialUrl: "https://www.getui.com/" },
  "300418.SZ": { name: "Kunlun Tech", cn: "昆仑万维", role: "大模型、AI 搜索、AIGC 与互联网应用", market: "A股", exchange: "创业板", officialUrl: "https://www.kunlun.com/" },
  "601360.SH": { name: "360 Security", cn: "三六零", role: "AI 搜索、大模型、浏览器入口与网络安全", market: "A股", exchange: "上交所", officialUrl: "https://www.360.cn/" },
  "688327.SH": { name: "Cloudwalk", cn: "云从科技", role: "计算机视觉、大模型与行业智能平台", market: "A股", exchange: "科创板", officialUrl: "https://www.cloudwalk.com/" },
  "300496.SZ": { name: "ThunderSoft", cn: "中科创达", role: "端侧 AI、智能汽车操作系统与边缘算法", market: "A股", exchange: "创业板", officialUrl: "https://www.thundersoft.com/" },
  "688088.SH": { name: "ArcSoft", cn: "虹软科技", role: "视觉算法、影像 AI 与智能终端算法", market: "A股", exchange: "科创板", officialUrl: "https://www.arcsoft.com.cn/" },
  "300378.SZ": { name: "Digiwin", cn: "鼎捷数智", role: "工业软件、企业 AI 开发平台与数字化管理", market: "A股", exchange: "创业板", officialUrl: "https://www.digiwin.com/" },
  "300624.SZ": { name: "Wondershare", cn: "万兴科技", role: "AI 创意软件、视频生成与办公效率工具", market: "A股", exchange: "创业板", officialUrl: "https://www.wondershare.cn/" },
  "300687.SZ": { name: "SIE Consulting", cn: "赛意信息", role: "企业数字化、工业软件与模型运维场景", market: "A股", exchange: "创业板", officialUrl: "https://www.chinasie.com/" },
  "300166.SZ": { name: "BONC", cn: "东方国信", role: "大数据平台、数据治理与行业智能分析", market: "A股", exchange: "创业板", officialUrl: "https://www.bonc.com.cn/" },
  "688031.SH": { name: "Transwarp", cn: "星环科技", role: "大数据平台、分布式数据库与向量检索底座", market: "A股", exchange: "科创板", officialUrl: "https://www.transwarp.cn/" },
  "688692.SH": { name: "Dameng", cn: "达梦数据", role: "国产数据库、企业数据底座与知识库基础设施", market: "A股", exchange: "科创板", officialUrl: "https://www.dameng.com/" },
  "002368.SZ": { name: "Taiji", cn: "太极股份", role: "政企数据平台、系统集成与知识库建设", market: "A股", exchange: "深交所", officialUrl: "https://www.taiji.com.cn/" },
  "603636.SH": { name: "Linewell", cn: "南威软件", role: "政务数据平台、知识库与数字政府应用", market: "A股", exchange: "上交所", officialUrl: "https://www.linewell.com/" },
  "688095.SH": { name: "Foxit", cn: "福昕软件", role: "PDF 文档软件、AI 办公与企业文档处理", market: "A股", exchange: "科创板", officialUrl: "https://www.foxitsoftware.cn/" },
  "603039.SH": { name: "Weaver", cn: "泛微网络", role: "协同办公、OA 与企业流程智能化", market: "A股", exchange: "上交所", officialUrl: "https://www.weaver.com.cn/" },
  "300364.SZ": { name: "COL", cn: "中文在线", role: "数字内容、AI 搜索与生成式内容应用", market: "A股", exchange: "创业板", officialUrl: "https://www.col.com/" },
  "300559.SZ": { name: "Jiafa Education", cn: "佳发教育", role: "智慧教育、考试信息化与教育 AI 场景", market: "A股", exchange: "创业板", officialUrl: "https://www.jf-r.com/" },
  "002841.SZ": { name: "CVTE", cn: "视源股份", role: "教育交互屏、会议平板与端侧智能硬件", market: "A股", exchange: "深交所", officialUrl: "https://www.cvte.com/" },
  "002955.SZ": { name: "HiteVision", cn: "鸿合科技", role: "智慧教育硬件、交互显示与课堂数字化", market: "A股", exchange: "深交所", officialUrl: "https://www.honghe-tech.com/" },
  "300253.SZ": { name: "Winning Health", cn: "卫宁健康", role: "医疗信息化、医院数据平台与 AI 医疗应用", market: "A股", exchange: "创业板", officialUrl: "https://www.winning.com.cn/" },
  "300451.SZ": { name: "B-Soft", cn: "创业慧康", role: "医疗 IT、电子病历与智慧医院平台", market: "A股", exchange: "创业板", officialUrl: "https://www.bsoft.com.cn/" },
  "603108.SH": { name: "Runda Medical", cn: "润达医疗", role: "检验数据、医疗服务网络与 AI 医疗场景", market: "A股", exchange: "上交所", officialUrl: "https://www.rundamedical.com/" },
  "300168.SZ": { name: "Wonders Information", cn: "万达信息", role: "医疗医保信息化与城市数据平台", market: "A股", exchange: "创业板", officialUrl: "https://www.wondersgroup.com/" },
  "002123.SZ": { name: "Montnets", cn: "梦网科技", role: "企业通信、智能客服与消息平台", market: "A股", exchange: "深交所", officialUrl: "https://www.montnets.com/" },
  "300002.SZ": { name: "Ultrapower", cn: "神州泰岳", role: "ICT 运维、智能客服与企业服务软件", market: "A股", exchange: "创业板", officialUrl: "https://www.ultrapower.com.cn/" },
  "300634.SZ": { name: "Richinfo", cn: "彩讯股份", role: "协同办公、智能客服与企业通信服务", market: "A股", exchange: "创业板", officialUrl: "https://www.richinfo.cn/" },
  "002920.SZ": { name: "Desay SV", cn: "德赛西威", role: "智能座舱、自动驾驶域控与车载 AI", market: "A股", exchange: "深交所", officialUrl: "https://www.desaysv.com/" },
  "002405.SZ": { name: "NavInfo", cn: "四维图新", role: "高精地图、自动驾驶数据与车载软件", market: "A股", exchange: "深交所", officialUrl: "https://www.navinfo.com/" },
  "600699.SH": { name: "Joyson Electronics", cn: "均胜电子", role: "汽车电子、智能驾驶与安全系统", market: "A股", exchange: "上交所", officialUrl: "https://www.joyson.cn/" },
  "002906.SZ": { name: "Foryou", cn: "华阳集团", role: "智能座舱、HUD 与车载电子", market: "A股", exchange: "深交所", officialUrl: "https://www.foryougroup.com/" },
  "688400.SH": { name: "Luster", cn: "凌云光", role: "机器视觉、工业质检与光学成像系统", market: "A股", exchange: "科创板", officialUrl: "https://www.lusterinc.com/" },
  "688686.SH": { name: "OPT", cn: "奥普特", role: "机器视觉核心部件、工业质检与自动化检测", market: "A股", exchange: "科创板", officialUrl: "https://www.optmv.com/" },
  "300802.SZ": { name: "Jutze", cn: "矩子科技", role: "AOI 检测、机器视觉与电子制造质检", market: "A股", exchange: "创业板", officialUrl: "https://www.jutze.com.cn/" },
  "688003.SH": { name: "TZTEK", cn: "天准科技", role: "机器视觉装备、精密测量与工业检测", market: "A股", exchange: "科创板", officialUrl: "https://www.tztek.com/" },
  "300567.SZ": { name: "Wuhan Jingce", cn: "精测电子", role: "显示与半导体检测设备、工业质检", market: "A股", exchange: "创业板", officialUrl: "https://www.wuhanjingce.com/" },
  "688561.SH": { name: "QAX", cn: "奇安信", role: "政企网络安全、终端安全与威胁响应", market: "A股", exchange: "科创板", officialUrl: "https://www.qianxin.com/" },
  "002439.SZ": { name: "Venustech", cn: "启明星辰", role: "网络安全、态势感知与政企安全运营", market: "A股", exchange: "深交所", officialUrl: "https://www.venustech.com.cn/" },
  "300369.SZ": { name: "NSFOCUS", cn: "绿盟科技", role: "云安全、网络攻防与安全服务", market: "A股", exchange: "创业板", officialUrl: "https://www.nsfocus.com.cn/" },
  "002747.SZ": { name: "Estun", cn: "埃斯顿", role: "工业机器人、伺服系统与智能制造", market: "A股", exchange: "深交所", officialUrl: "https://www.estun.com/" },
  "300124.SZ": { name: "Inovance", cn: "汇川技术", role: "工控自动化、伺服系统与工业机器人核心部件", market: "A股", exchange: "创业板", officialUrl: "https://www.inovance.com/" },
  "300024.SZ": { name: "Siasun", cn: "机器人", role: "工业机器人、移动机器人与智能制造装备", market: "A股", exchange: "创业板", officialUrl: "https://www.siasun.com/" },
  "300607.SZ": { name: "Topstar", cn: "拓斯达", role: "工业机器人、注塑自动化与智能制造", market: "A股", exchange: "创业板", officialUrl: "https://www.topstarltd.com/" },
  "688017.SH": { name: "Leaderdrive", cn: "绿的谐波", role: "机器人精密减速器、谐波传动核心部件", market: "A股", exchange: "科创板", officialUrl: "https://www.leaderdrive.com/" },
};

const cnChainStocksByVisual = {
  chip: ["688981.SH", "688256.SH", "688041.SH", "002371.SZ", "603501.SH"],
  server: ["603019.SH", "000977.SZ", "601138.SH", "000938.SZ", "002261.SZ"],
  cloud: ["688111.SH", "600588.SH", "600845.SH", "000938.SZ", "300454.SZ"],
  datacenter: ["603881.SH", "300383.SZ", "300738.SZ", "300442.SZ", "002335.SZ"],
  compute: ["603019.SH", "000977.SZ", "300442.SZ", "300846.SZ", "002261.SZ"],
  data: ["688787.SH", "300229.SZ", "002230.SZ", "300678.SZ", "300766.SZ"],
  model: ["002230.SZ", "300418.SZ", "601360.SH", "300229.SZ", "688327.SH"],
  framework: ["688256.SH", "688041.SH", "002230.SZ", "300496.SZ", "688088.SH"],
  platform: ["002230.SZ", "688111.SH", "600588.SH", "300378.SZ", "300624.SZ"],
  mlops: ["600845.SH", "600588.SH", "300687.SZ", "300166.SZ", "300229.SZ"],
  vector: ["688031.SH", "300229.SZ", "688692.SH", "002368.SZ", "603636.SH"],
  inference: ["688256.SH", "688041.SH", "603019.SH", "002230.SZ", "000977.SZ"],
  office: ["688111.SH", "688095.SH", "300624.SZ", "002230.SZ", "603039.SH"],
  search: ["601360.SH", "300418.SZ", "300229.SZ", "300766.SZ", "300364.SZ"],
  education: ["002230.SZ", "300559.SZ", "002841.SZ", "002261.SZ", "002955.SZ"],
  medical: ["002230.SZ", "300253.SZ", "300451.SZ", "603108.SH", "300168.SZ"],
  service: ["002230.SZ", "002123.SZ", "300002.SZ", "300229.SZ", "300634.SZ"],
  auto: ["002920.SZ", "300496.SZ", "002405.SZ", "600699.SH", "002906.SZ"],
  inspection: ["688400.SH", "688686.SH", "300802.SZ", "688003.SH", "300567.SZ"],
  security: ["601360.SH", "688561.SH", "300454.SZ", "002439.SZ", "300369.SZ"],
  robot: ["002747.SZ", "300124.SZ", "300024.SZ", "300607.SZ", "688017.SH"],
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
let currentMarket = "us";

function fundamentalUrl(ticker) {
  const params = new URLSearchParams({
    ticker,
    q: ticker,
    source: "ai-chain",
  });
  return `${FUNDAMENTAL_PAGE_URL}?${params.toString()}#companies`;
}

function activeCatalog(market = currentMarket) {
  return market === "cn" ? cnStockCatalog : stockCatalog;
}

function activeSourceNote() {
  return currentMarket === "cn" ? cnSourceNote : qqqSourceNote;
}

function resolveStocks(tickers, market = currentMarket) {
  const seen = new Set();
  const catalog = activeCatalog(market);
  return tickers
    .filter((ticker) => catalog[ticker] && !seen.has(ticker) && seen.add(ticker))
    .map((ticker) => ({ ticker, ...catalog[ticker], url: market === "us" ? fundamentalUrl(ticker) : "" }));
}

function resolveNodeStocks(item, market = currentMarket) {
  const [, visual, , , , tickers = []] = item;
  if (market === "cn") {
    return resolveStocks(cnChainStocksByVisual[visual] || [], "cn");
  }
  return resolveStocks(tickers, "us");
}

function chainNodeKey(layerId, name) {
  return `${layerId}:${name}`;
}

function fmtChainHeat(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "暂无";
  return Number(value).toFixed(1);
}

function rankInfoForTicker(ticker) {
  if (currentMarket !== "us") return null;
  if (!chainRankHeat?.rankByTicker) return null;
  return chainRankHeat.rankByTicker[String(ticker || "").trim().toUpperCase()] || null;
}

function computeNodeHeat(layer, item, originalIndex) {
  const [name] = item;
  const stocks = resolveNodeStocks(item);
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
  if (currentMarket !== "us" || !chainRankHeat?.available) return;
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
  if (currentMarket === "cn") {
    const heat = chainHeatByKey.get(key);
    return `<span class="ai-node-heatline cn">A股代表股：${escapeHtml(heat?.totalCount ?? 5)}只</span>`;
  }
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
  const eyebrow = document.getElementById("chainRankEyebrow");
  const title = document.getElementById("chainRankTitle");
  if (!target || !method || !source) return;
  if (currentMarket === "cn") {
    if (eyebrow) eyebrow.textContent = "A股代表池";
    if (title) title.textContent = "同一产业链节点下的A股代表股票";
    method.textContent = "A股模式沿用美股图谱相同的上游基础层、中游技术/平台层、下游应用层划分；每个节点选取5只代表性A股，按人工维护的代表性顺序展示，不使用美股排名源排序。";
    source.hidden = true;
    const nodes = chainLayers.flatMap((layer) => layer.items.map((item) => {
      const [name] = item;
      const key = chainNodeKey(layer.id, name);
      const stocks = resolveNodeStocks(item, "cn");
      return { key, layerTitle: layer.title, name, stocks };
    }));
    target.innerHTML = nodes.map((node) => `
      <button class="chain-rank-chip cn" type="button" data-node="${escapeHtml(node.key)}">
        <span>${node.stocks.length}</span>
        <strong>${escapeHtml(node.name)}</strong>
        <small>${escapeHtml(node.layerTitle)} · ${escapeHtml(stockHint(node.stocks.map((stock) => stock.ticker)))}</small>
      </button>
    `).join("");
    return;
  }
  if (eyebrow) eyebrow.textContent = "排名热度";
  if (title) title.textContent = "按对应股票平均排名重排产业链节点";
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
  if (stock.market === "A股") {
    return ["A股", stock.exchange || ""].filter(Boolean);
  }
  return [
    stock.qqq ? "QQQ" : "",
    stock.research ? "自研资料库" : "",
  ].filter(Boolean);
}

function renderChain() {
  const board = document.getElementById("aiChainBoard");
  const html = chainLayers.map((layer) => {
    const items = orderedLayerItems(layer).map((item) => {
      const [name, visual, summary] = item;
      const key = chainNodeKey(layer.id, name);
      const stocks = resolveNodeStocks(item);
      const heat = chainHeatByKey.get(key);
      const stockLineLabel = currentMarket === "cn" ? "A股代表股" : "并集股票";
      return `
        <button class="ai-node ${layer.id} ${heat?.available && heat.heatRank <= 5 ? "hot-node" : ""}" type="button" data-node="${escapeHtml(key)}" aria-label="查看${escapeHtml(name)}">
          <span class="ai-node-image ${escapeHtml(visual)}" aria-hidden="true"><span></span></span>
          <span class="ai-node-text">
            <strong>${escapeHtml(name)}</strong>
            <small>${escapeHtml(summary)}</small>
            <span class="ai-node-stockline">${stockLineLabel}：${escapeHtml(stockHint(stocks.map((stock) => stock.ticker)))}</span>
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
    layer.items.forEach((item) => {
      const [name, visual, summary, watch, related] = item;
      const key = chainNodeKey(layer.id, name);
      nodeMap.set(key, {
        layer,
        name,
        visual,
        summary,
        watch,
        related,
        stocks: resolveNodeStocks(item),
        heat: chainHeatByKey.get(key) || null,
      });
    });
  });
}

function renderStockLinks(stocks) {
  if (!stocks.length) {
    return `<p class="stock-source-note">暂无符合并集口径的产业链股票。</p>`;
  }
  const rankedStocks = stocks.map((stock) => ({ ...stock, rankInfo: rankInfoForTicker(stock.ticker) }));
  if (currentMarket === "us") {
    rankedStocks.sort((left, right) => {
      const leftRank = Number(left.rankInfo?.rank ?? Number.POSITIVE_INFINITY);
      const rightRank = Number(right.rankInfo?.rank ?? Number.POSITIVE_INFINITY);
      return leftRank - rightRank || left.ticker.localeCompare(right.ticker);
    });
  }
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
                currentMarket === "us"
                  ? stock.rankInfo
                    ? `<em class="rank-source-badge">排名 #${escapeHtml(stock.rankInfo.rank)} · ${escapeHtml(stock.rankInfo.stock_type || stock.rankInfo.sector || "")}</em>`
                    : `<em class="rank-source-badge muted">排名源未覆盖</em>`
                  : ""
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
    <p class="stock-source-note">${escapeHtml(activeSourceNote())}</p>
  `;
}

function renderNodeHeatDetails(node) {
  if (currentMarket === "cn") {
    const leaders = node.stocks
      .slice(0, 5)
      .map((stock) => `<span>${escapeHtml(stock.ticker)} ${escapeHtml(stock.cn)}</span>`)
      .join("");
    return `
      <div class="chain-dialog-section">
        <h3>A股代表池</h3>
        <p>该节点沿用同一产业链划分，选取5只A股代表公司，用于观察国内产业链映射和横向对比；排序为人工维护的代表性顺序，不是买卖建议。</p>
        <div class="node-rank-leaders">${leaders}</div>
      </div>
    `;
  }
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
  const stockSectionTitle = currentMarket === "cn" ? "A股代表股票" : "并集中的相关股票";
  const usageText = currentMarket === "cn"
    ? "先看节点对应的A股代表公司，再通过官网按钮查看公司信息；A股暂未接入本项目自研基本面映射时，自研网站按钮会置灰。后续可以把这些公司继续接入资金流、相关性和波动异常指标，用于观察国内AI产业链扩散方向。"
    : "先看节点对应的并集股票，再根据按钮进入自研基本面页或公司官网；没有自研映射的股票，自研网站按钮会置灰。随后把这些公司与资金流排名、上尾/中部/下尾相关性和波动异常一起看。如果同一产业链节点的多只股票同时走强，说明资金可能在沿该链条扩散；如果强度偏离过大，也要同时留意回调风险。";
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
      <h3>${stockSectionTitle}</h3>
      ${renderStockLinks(node.stocks)}
    </div>
    <div class="chain-dialog-section chain-dialog-wide">
      <h3>使用方式</h3>
      <p>${usageText}</p>
    </div>
  `;
  document.getElementById("chainDialog").hidden = false;
  document.body.classList.add("modal-open");
}

function closeChainDialog() {
  document.getElementById("chainDialog").hidden = true;
  document.body.classList.remove("modal-open");
}

function updateMarketButtons() {
  document.querySelectorAll("[data-market]").forEach((button) => {
    button.classList.toggle("active", button.dataset.market === currentMarket);
  });
}

function setMarket(market) {
  currentMarket = market === "cn" ? "cn" : "us";
  updateMarketButtons();
  if (currentMarket === "us" && !chainRankHeat) {
    chainRankLoading = true;
  } else {
    chainRankLoading = false;
  }
  buildChainHeat();
  indexNodes();
  renderChain();
  renderChainRankSummary();
  if (currentMarket === "us" && !chainRankHeat) {
    loadChainRankHeat();
  }
}

document.addEventListener("DOMContentLoaded", () => {
  setMarket("us");
  document.getElementById("aiChainBoard").addEventListener("click", (event) => {
    const button = event.target.closest("[data-node]");
    if (!button) return;
    openChainDialog(button.dataset.node);
  });
  document.querySelector(".chain-market-toggle").addEventListener("click", (event) => {
    const button = event.target.closest("[data-market]");
    if (!button) return;
    setMarket(button.dataset.market);
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
