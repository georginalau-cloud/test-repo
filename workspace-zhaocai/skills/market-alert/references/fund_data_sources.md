# 基金数据信息

## 基金持仓查询

### 天天基金网（EastMoney）
- **个股持仓明细**: `https://fundf10.eastmoney.com/FundArchivesDatas.aspx?type=jjcc&code={FUND_CODE}&topline=10&year={YEAR}&month={MONTH}`
  - 自动抓取脚本: `scripts/fetch_fund_holdings.py`
  - 输出文件: `references/fund_holdings_realtime.json`
  - 例: `https://fundf10.eastmoney.com/FundArchivesDatas.aspx?type=jjcc&code=006751&topline=10&year=2026&month=3`
  - 返回: Q1/Q2/Q3/Q4 季报前10大重仓股、占净值比例、持股数量、持仓市值
- **基金档案**: `http://fund.eastmoney.com/{FUND_CODE}.html`

### 10jqka（同花顺）
- **基金主页**: `https://basic.10jqka.com.cn/{FUND_CODE}/index.html`

## 持仓数据字段说明

天天基金网季报字段:
- `占净值比例` = 该股票市值 / 基金净资产（%）
- `持股数（万股）` = 股票数量（万股）
- `持仓市值（万元）` = 持仓市值（万元）

计算用户穿透占用资金:
```
用户持有份额 × 基金净值 = 用户持有市值（元）
用户持有市值 × (持仓占比% / 100) = 用户在该股票上的资金（元）
```
