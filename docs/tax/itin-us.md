# 美国 ITIN（个人纳税人识别号）

整理自 IRS 官方页面，时间 2026-10。

## ITIN 是什么

美国国税局签发的**报税用识别号**，格式 `9XX-7X-XXXX`（第 4、5 位为 70–88、90–92、94–99）。

**它不是**：社保号（SSN）、移民身份、工作许可、身份证明文件。

## 前提硬门槛：必须证明「联邦纳税目的」

IRS Topic No. 857 原文：

> **"An ITIN does not get issued solely for opening bank/investment accounts, e-commerce or starting a business."**
> （ITIN 不会仅因开银行/投资账户、做电商或创业而签发。）

具体要求：

1. W-7 申请包**必须附有效美国联邦所得税申报表**（1040 / 1040-NR / 1040X），除非符合 IRS 规定的 5 类 Exception；
2. IRS 另外堵了漏洞：**"通常，所有填报数据均为零的报税表不会显示联邦纳税目的。"**

**结论：没有真实美国收入/申报义务，申请会被退回。**

## 官方明文「不会」带来的四件事

- 不带来社保福利
- 不符合 EITC（劳动所得税抵免）资格
- **不提供或更改移民身份**
- **不授权在美合法工作**
- **不在联邦税务系统之外用作身份证明**

补充限制：

- **不能**用 ITIN 办州驾照（IRS 曾就此向各州 DMV 发通函）
- **不能**作 I-9 工作资格证明
- **不能**同时持有 ITIN 和 SSN —— 拿到 SSN 后须停用 ITIN 并**书面通知 IRS** 合并记录

## 申请成本与流程

| 项 | 说明 |
| --- | --- |
| IRS 费用 | **IRS 本身不收 ITIN 申请费** |
| 文件形式 | 只接受**原件**或**发证机关认证的副本**；**公证副本不被接受**（`Notarized copies are not acceptable`） |
| 护照 | 唯一可单独使用的文件 |
| 寄原件风险 | 回寄走**普通国际信函、无追踪号** |
| 大陆替代路径 | 美国使领馆做认证副本（约 **50 美元/份**）；或 IRS 授权的 **CAA**（市价约 **260–400 美元**） |
| 周期 | 官方 7 周；报税季（1/15–4/30）或海外申请 **9–11 周** |

## 过期规则

连续 **3 个纳税年度**未在美国联邦税表上使用，即在第三个年度后 **12 月 31 日过期**。续用需重走 W-7。

## 有 ITIN 之后的申报义务

若有**美国来源收入**（股息 / 利息 / 房租 / 自由职业 / 平台分成），产生 **1040-NR** 申报义务。

同时，中国税务居民需就**全球所得**在中国申报。已在美国扣缴的税可经中美税收协定机制抵免。**两边都不报是双重风险。**

## 最容易出事的地方：境外银行 CRS / FATCA 自证表

**持有 ITIN ≠ 美国税收居民。** 这是最容易被搞混的一点。

- 汇丰 / 恒生中国 CRS 声明原文：**「如客户国籍为中国，且为中国税收居民，则纳税人识别号码为中国居民身份证号码。」**
- Citi、National Bank 等机构的表格里，**ITIN 归在「I am a citizen or resident of the United States for tax purposes」栏**

**后果**：中国税收居民该填身份证号；若误把 ITIN 填进税号栏、或勾错「美国税收居民」，账户信息会被**交换给美国 IRS**。

补充：FATCA 法定的 **US indicia** 清单（美财政部 Annex I）**不包含美国 TIN** —— 单有 ITIN 不构成美国身份标记。

## 隐私口径的变化

IRC §6103 传统上禁止非税务目的披露。但 **2025-04-07** DHS 与财政部签署协议，IRS 会向 ICE 共享纳税人信息以协助**非税务刑事**调查。目前限「已有最终遣返令」人员，诉讼仍在进行、协议仍有效。

对普通中国居民相关性极低。

## 场景对照

| 目的 | 可行 |
| --- | --- |
| 美国无收入，想先备着 | ❌ 会被退回 |
| 有美国收入 | ✅ 但 F-1 学生若可打工应**先申请 SSN**，只有 SSA 出具拒绝信才转办 ITIN |
| 想开美国银行账户 / 办卡 | ❌ IRS 明文禁止此理由 |
| 美股/基金收款主张协定预扣优惠 | ⚠️ 多数场景 W-8BEN 填**中国税号**即可，先问券商 |
| 美国电商 / 自由职业平台收款 | ⚠️ 先确认平台要的是 US TIN 还是外国 TIN |
| 被多扣美国预扣税要退税 | ✅ 经典用途，可停止 backup withholding（避免被扣 **24%**） |

## 参考

- `https://www.irs.gov/individuals/individual-taxpayer-identification-number`
- `https://www.irs.gov/forms-pubs/about-form-w-7`
- `https://www.irs.gov/individuals/itin-expiration-frequently-asked-questions`
- `https://www.irs.gov/tin/itin/how-to-renew-an-itin`
- `https://www.irs.gov/zh-hans/tin/itin/itin-application-frequently-asked-questions`
