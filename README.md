# China-US Sector Dependence

这个项目用于研究中美主要板块在近七年中的相关性结构。它不预测哪个板块会上涨，而是把相关性拆成三段分别分析：

- 下尾相关性：两个板块是否容易在极端下跌时一起跌。
- 上尾相关性：两个板块是否容易在极端上涨时一起涨。
- 中间部分相关性：剔除两端极端行情后，两个板块在常态市场中的联动程度。

当前默认流程会先使用 `GARCH(1,1)` 消除条件波动率，再对标准化残差做相关性和经验 Copula 分析：

```text
raw price
-> log return
-> GARCH(1,1) conditional volatility
-> standardized residual = (return - mean) / sigma_t
-> lower / upper / middle dependence analysis
-> latest regime and possible flow candidates
```

默认板块池去掉“消费”，保留“互联网”，共 10 个板块：

- Internet
- Semiconductor
- New Energy
- Healthcare
- Financials
- Real Estate Chain
- Energy
- Materials
- Industrials
- Utilities

## Method

项目默认使用 Yahoo Finance 日度复权价格，计算对数收益率，并输出：

- GARCH(1,1)-standardized residuals
- GARCH parameter table
- Pearson correlation
- Spearman rank correlation
- Empirical lower-tail dependence
- Empirical upper-tail dependence
- Middle-market Pearson/Spearman correlation
- Co-crash lift versus independence
- Co-rally lift versus independence
- Cross-market same-sector comparison
- Empirical C-Vine ordering based on lower-tail dependence
- Latest sector regime classification
- Potential flow candidates inferred from latest data and historical dependence
- Downside contagion watchlist

核心定义：

```text
lower_tail_dependence = P(U_i <= alpha, U_j <= alpha) / alpha
upper_tail_dependence = P(U_i >= 1 - alpha, U_j >= 1 - alpha) / alpha
middle_correlation = Corr(R_i, R_j | alpha < U_i < 1-alpha and alpha < U_j < 1-alpha)
```

其中 `U_i` 和 `U_j` 是收益率经过经验分布排名后的 Copula 变量，`alpha` 默认是 `5%`。

放大倍数指标：

```text
lower_co_crash_lift = P(U_i <= alpha, U_j <= alpha) / alpha^2
upper_co_rally_lift = P(U_i >= 1-alpha, U_j >= 1-alpha) / alpha^2
```

## Default Asset Proxies

| Market | Sector | Ticker | Proxy |
|---|---|---:|---|
| US | Internet | FDN | First Trust Dow Jones Internet Index Fund |
| US | Semiconductor | SMH | VanEck Semiconductor ETF |
| US | New Energy | QCLN | First Trust Nasdaq Clean Edge Green Energy Index Fund |
| US | Healthcare | XLV | Health Care Select Sector SPDR Fund |
| US | Financials | XLF | Financial Select Sector SPDR Fund |
| US | Real Estate Chain | XHB | SPDR S&P Homebuilders ETF |
| US | Energy | XLE | Energy Select Sector SPDR Fund |
| US | Materials | XLB | Materials Select Sector SPDR Fund |
| US | Industrials | XLI | Industrial Select Sector SPDR Fund |
| US | Utilities | XLU | Utilities Select Sector SPDR Fund |
| CN | Internet | 513050.SS | E Fund CSI Overseas China Internet 50 ETF Index Fund |
| CN | Semiconductor | 512760.SS | Guotai CES Semiconductor Industry ETF |
| CN | New Energy | 515030.SS | ChinaAMC CSI New Energy Automobile ETF |
| CN | Healthcare | 512010.SS | E Fund CSI 300 Health Care Index Fund |
| CN | Financials | 510230.SS | Guotai SSE 180 Financial Index ETF |
| CN | Real Estate Chain | 512200.SS | China Southern CSI All Share Real Estate ETF |
| CN | Energy | 159945.SZ | GF CSI All Share Energy Index ETF |
| CN | Materials | 512400.SS | China Southern CSI SWS Nonferrous ETF |
| CN | Industrials | 512660.SS | Guotai CSI National Defense ETF |
| CN | Utilities | 159611.SZ | CSI All Share Power and Power Grid ETF |

中国侧的部分 ETF 是代理标的，不等于完整行业指数。例如 `CN_INDUSTRIALS` 使用国防/高端制造代理，`CN_UTILITIES` 使用电力电网代理，`CN_REAL_ESTATE_CHAIN` 当前使用地产 ETF 作为地产链核心代理。你可以直接修改 [config/sector_assets.csv](config/sector_assets.csv) 替换成自己更认可的指数或 ETF。

## Quick Start

```powershell
python scripts/run_analysis.py --start 2019-07-04 --end 2026-07-04 --alpha 0.05
```

输出目录：

```text
outputs/latest/
```

关键输出：

- `report.html`: 可直接打开的 HTML 报告。
- `volumes.csv`: Yahoo 图表接口返回的成交量序列。
- `turnover_amount.csv`: 收盘价乘以成交量得到的成交额代理序列。
- `garch_params.csv`: 每个板块的 GARCH(1,1) 参数。
- `standardized_residuals.csv`: GARCH 标准化残差，相关性分析默认使用这个矩阵。
- `latest_regime_alpha_0.05.csv`: 最新交易日每个板块的标准化残差、历史分位数和区间状态。
- `flow_candidates_alpha_0.05.csv`: 基于最新强势板块和历史相关性的潜在流向候选。
- `risk_contagion_candidates_alpha_0.05.csv`: 基于最新弱势板块和历史下尾相关性的风险传导候选。
- `fund_flow_amount.csv`: 可选外部输入，真实净流入/净流出金额；项目不会用 Yahoo 成交量或涨跌幅伪造该数据。
- `sector_total_size.csv`: 可选外部输入，板块总规模、ETF AUM 或行业总市值口径，用作真实资金流占比分母。
- `fund_flow_sources.csv`: 可选外部输入，逐板块注明资金流金额来源、总规模来源、币种和口径说明。
- `lower_tail_dependence.svg`: 下尾相关性热力图。
- `upper_tail_dependence.svg`: 上尾相关性热力图。
- `middle_pearson_correlation.svg`: 中间部分 Pearson 相关性热力图。
- `middle_spearman_correlation.svg`: 中间部分 Spearman 相关性热力图。
- `lower_co_crash_lift.svg`: 共同暴跌相对独立情形的放大倍数。
- `upper_co_rally_lift.svg`: 共同上涨相对独立情形的放大倍数。
- `pearson_correlation.svg`: 全样本 Pearson 相关性热力图。
- `spearman_correlation.svg`: 全样本 Spearman 相关性热力图。
- `pair_metrics_alpha_0.05.csv`: 所有板块两两指标。
- `matched_sector_metrics_alpha_0.05.csv`: 中美同板块对照。
- `cvine_empirical_order.csv`: 基于下尾相关性的经验 C-Vine 节点排序。

## Web Dashboard

项目包含一个可部署到 Render 的前端看板，用来查看最新板块状态、真实板块资金流入流出综述、潜在流向、风险传导、GARCH 参数和相关性热力图。资金流综述只读取外部接入的真实资金流数据：`fund_flow_amount.csv` 提供真实净流入/净流出金额，`sector_total_size.csv` 提供该板块总规模，流入流出占比为“真实净流入/净流出金额 / 该板块总规模”，并对比上一交易日排名生成上升/下降箭头。若未配置这些文件，页面会明确显示未配置真实来源，不会用“收益率 × 成交额”替代真实资金流。页面也提供可点击的“机会提示”“风险提示”和“波动异常”弹窗：机会提示关注下一步可能承接资金扩散的板块，风险提示同时覆盖下尾传导风险和短线过热回调风险，波动异常基于 GARCH 条件波动率的历史分位数识别当前显著偏离自身常态波动的板块。

真实资金流输入支持两种格式。宽表格式：

```csv
date,US_SEMICONDUCTOR,CN_SEMICONDUCTOR
2026-07-02,-585876190,120000000
```

长表格式：

```csv
date,id,flow_amount
2026-07-02,US_SEMICONDUCTOR,-585876190
```

`sector_total_size.csv` 同样支持宽表，或长表字段 `date,id,total_size`。`fund_flow_sources.csv` 建议字段：

```csv
id,flow_source,total_size_source,currency,notes
US_SEMICONDUCTOR,数据商/ETF净申赎/券商资金流口径,ETF AUM或行业总市值来源,USD,说明统计口径和更新时间
```

中国侧真实资金流可用东方财富公开板块资金流向抓取：

```powershell
python scripts/fetch_real_fund_flows.py
```

该脚本会读取 [config/eastmoney_flow_map.csv](config/eastmoney_flow_map.csv) 中的东方财富 BK 板块代码，直接请求东方财富公开网页接口，并生成：

- `fund_flow_amount.csv`: `f62` 主力净流入，作为真实净流入/净流出金额。
- `sector_total_size.csv`: `f20` 总市值，作为该板块总规模分母。
- `fund_flow_sources.csv`: 逐板块记录字段来源、公开页面 URL、币种、BK 代码/ETF 代码和代理口径说明。
- `eastmoney_sector_boards.csv`: 本次抓到的原始板块字段留档。
- `us_etf_snapshots.csv`: 美国代理 ETF 的 StockAnalysis AUM、份额、价格和数据日期快照。

`fund_flow_amount.csv` 和 `sector_total_size.csv` 会按 `date,id` 追加并去重：同一天重复抓取会覆盖同一日期的最新值，新交易日会保留历史记录。页面的排名变化不是按自然日“昨天”比较，而是按每个板块自己的上一个有效资金流交易日比较，适配周末、节假日和中美交易日不一致的情况。网页点击“刷新分析”时也会自动尝试运行该脚本；首页读取 `/api/dashboard` 时还会判断资金流日期是否早于今天，若过期则启动后台资金流刷新，不阻塞页面打开。工具栏的“刷新资金流”按钮会调用独立接口，只更新板块资金流，不重新跑 GARCH/Copula 分析。

美国侧公开来源调研后采用 StockAnalysis ETF 页面作为可自动接入的数据源。ETFDB 和 ETF.com 页面存在直接 fund flow 展示，但当前自动请求经常被 Cloudflare 阻断，不适合作为稳定抓取源；Yahoo Finance 图表/行情字段不提供可直接等同于 ETF 净申购/净赎回的免费标准字段；Nasdaq API 可取部分 ETF AUM 信息，但不提供净流入字段。StockAnalysis 页面可稳定取得 ETF AUM、Shares Outstanding、价格和数据日期，因此项目会先写入 `us_etf_snapshots.csv`，并在同一 ETF 存在上一个有效交易日快照后生成美国侧资金流估计：

- 优先公式：`(本期份额 - 上期份额) × 本期价格`。
- 备用公式：`本期 AUM - 上期 AUM × (本期价格 / 上期价格)`。

这类美国侧金额在来源中标注为“ETF 净申赎估计”，不是 ETFDB/ETF.com 披露口径的官方 fund flow。第一次运行通常只会记录快照，不会生成美国侧资金流金额；等下一次有效交易日快照写入后，才会出现可比较的美国侧流入/流出估计。

本地运行：

```powershell
python app.py
```

然后打开：

```text
http://127.0.0.1:8000
```

看板接口：

- `GET /api/dashboard`: 读取当前 `outputs/latest/`，如果没有本地输出则回退到 `reports/` 中最新快照。
- `POST /api/fund-flow-refresh`: 只运行 `scripts/fetch_real_fund_flows.py`，按真实资金流来源更新 `fund_flow_amount.csv`、`sector_total_size.csv`、`fund_flow_sources.csv` 和美国 ETF 快照。
- `POST /api/refresh`: 按页面上的起止日期和 tail alpha 重新抓取数据、估计 GARCH，并刷新 `outputs/latest/`。
- `GET /report-assets/report.html`: 打开脚本生成的完整 HTML 报告。

Render 部署：

1. 把仓库推送到 GitHub。
2. 在 Render 新建 `Blueprint` 或 `Web Service`，选择本仓库。
3. 如果使用 Blueprint，Render 会读取 [render.yaml](render.yaml)。
4. 如果手动建 Web Service，使用：

```text
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 900
```

Render 免费实例的磁盘不是长期持久化存储，因此页面刷新后的 `outputs/latest/` 主要用于当前实例查看；仓库内的 `reports/2026-07-04/` 快照会作为稳定兜底数据。

## Included Snapshot

本仓库包含一次已生成的分析快照：

```text
reports/2026-07-04/report.html
```

该快照使用 `2019-07-04` 至 `2026-07-04` 的近七年数据，保留报告、热力图和派生指标 CSV；原始价格和收益率数据不放入仓库，可通过脚本重新抓取。

## Install

项目尽量少依赖复杂金融包，当前版本只需要：

```powershell
pip install -r requirements.txt
```

当前实现不需要 `yfinance`、`scipy` 或 `arch`。Yahoo 数据通过 chart API 抓取，热力图用项目内置 SVG 生成器输出。

GARCH(1,1) 使用项目内置的正态 QMLE 估计器，不依赖外部 `arch` 包。它的目标是先剥离条件波动率，再做相关性结构分析。

## Notes For Investment Use

这个项目适合做组合风险研究：

- 今天哪个板块进入 GARCH 标准化后的上尾/下尾状态。
- 哪些中美板块在极端下跌时容易一起跌。
- 哪些中美板块在极端上涨时一起涨。
- 哪些板块在常态行情中相关性高，但在尾部行情中不同步。
- 哪些板块平时看似分散，但在极端行情中会突然共振。
- 当前持仓是否集中暴露在同一个尾部风险簇。
- 如果今天某个板块成为上尾强势板块，历史上哪些板块更容易跟随。

它不适合直接当成买卖信号。低相关不等于一定会上涨，高尾部相关也不等于不能持有；它只说明这些资产在不同市场状态中的组合风险关系。

## Next Extensions

- Add rolling lower/middle/upper dependence windows.
- Add POT-GPD tail fitting.
- Add parameterized C-Vine Copula fitting.
- Add Mean-CVaR portfolio optimization.
