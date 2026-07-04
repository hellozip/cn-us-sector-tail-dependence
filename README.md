# China-US Sector Tail Dependence

这个项目用于研究中美主要板块在近七年中的相关性和下尾共振关系。它不预测哪个板块会上涨，而是回答一个更适合组合管理的问题：

> 当一个板块进入极端下跌区间时，另一个板块是否也容易同时下跌？

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

- Pearson correlation
- Spearman rank correlation
- Empirical lower-tail dependence
- Co-crash lift versus independence
- Cross-market same-sector comparison
- Empirical C-Vine ordering based on lower-tail dependence

核心下尾指标：

```text
lower_tail_dependence = P(U_i <= alpha, U_j <= alpha) / alpha
```

其中 `U_i` 和 `U_j` 是收益率经过经验分布排名后的 Copula 变量，`alpha` 默认是 `5%`。该指标越高，说明两个板块在极端下跌日共同下跌的经验概率越高。

`co_crash_lift_vs_independence` 衡量共同下跌概率相对独立情形放大了多少倍：

```text
co_crash_lift = P(U_i <= alpha, U_j <= alpha) / alpha^2
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

- `report.html`: 可直接打开的 HTML 报告
- `lower_tail_dependence.svg`: 下尾相关性热力图
- `co_crash_lift.svg`: 共同暴跌放大倍数热力图
- `pearson_correlation.svg`: Pearson 相关性热力图
- `spearman_correlation.svg`: Spearman 相关性热力图
- `pair_metrics_alpha_0.05.csv`: 所有板块两两指标
- `matched_sector_metrics_alpha_0.05.csv`: 中美同板块对照
- `cvine_empirical_order.csv`: 基于下尾相关性的经验 C-Vine 节点排序

## Included Snapshot

本仓库包含一次已生成的分析快照：

```text
reports/2026-07-04/report.html
```

该快照使用 `2019-07-04` 至 `2026-07-04` 的近七年数据，保留报告、热力图和派生指标 CSV；原始价格和收益率数据不放入仓库，可通过脚本重新抓取。

这次快照中的初步现象：

- 美股内部顺周期板块下尾共振较强，金融、工业、材料之间的共同下跌风险尤其突出。
- 中美同板块之间的下尾相关性整体低于美股内部板块相关性。
- 中美同板块里，新能源、能源、半导体、互联网的下尾相关性相对更高。
- 公用事业的中美下尾共振较低，但中国侧 `CN_UTILITIES` 历史较短，需要谨慎解读。

## Install

项目尽量少依赖复杂金融包，第一版只需要：

```powershell
pip install -r requirements.txt
```

当前实现不需要 `yfinance`、`scipy` 或 `arch`。Yahoo 数据通过官方 chart API 抓取，热力图用项目内置 SVG 生成器输出。

## Notes For Investment Use

这个项目适合做组合风险研究：

- 哪些中美板块在极端下跌时容易一起跌
- 哪些跨市场板块可能提供更好的尾部分散
- 哪些板块更像下尾风险中心节点
- 当前持仓是否集中暴露在同一个尾部风险簇

它不适合直接当成买卖信号。低相关不等于一定会上涨，高下尾相关也不等于不能持有；它只说明这些资产在极端行情中的组合风险关系。

## Next Extensions

- Add rolling lower-tail dependence windows
- Add GARCH standardized residuals
- Add POT-GPD tail fitting
- Add parameterized C-Vine Copula fitting
- Add Mean-CVaR portfolio optimization
