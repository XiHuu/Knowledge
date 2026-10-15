# 马来西亚 TIN（e-Daftar 填报指南）

针对**外国人**申请马来西亚纳税人识别号（Nombor Pengenalan Cukai）的实操要点。整理时间 2026-10。

## 唯一渠道：e-Daftar

**2024-01-01 起，个人 TIN 只能通过 MyTax 门户的 e-Daftar 在线申请**，到分局柜台也会被要求回到线上办。

- 门户：`https://mytax.hasil.gov.my`
- 入口：`https://mytax.hasil.gov.my/ezHasil?data=e-Daftar`
- LHDN **不收取** TIN 注册费

外国人另有 **e-Daftar e-KYC** 路径：MyTax 手机 App，用**带 NFC 芯片的护照**配**活体自拍**做人脸比对。

> 注意：马来西亚公民与永久居民（18 岁以上）由 JPN 数据**自动注册**，不在此流程内。外国人必须自己申请。

## 文件类型：IG

| 类别 | File Type | 支持文件 |
| --- | --- | --- |
| 非公民 / 非居民 / 外国个人 | **IG** | 有效护照复印件；或 social visit pass / UNHCR card / IMM13 pass / 原籍国身份证件 |
| 临时居民（MyKAS） | IG | MyKAS 卡副本 |

若在马来西亚做生意，另需 SSM 营业执照或盖章的合伙/合资协议。

## Part A 字段填写（外国人）

| 字段 | 填法 |
| --- | --- |
| **Type of Reference Number** | `Passport Number` |
| **Passport Country** | 外国人**必须填** |
| **Source Income** | 无生意往来 → `NON-BUSINESS ACTIVITIES` |
| **Name** | ⚠️ **名在前、姓在后**。例：张三 → `SAN ZHANG` |
| **Citizen / Country of Residence** | 如实填（这是居住地数据字段，不是税务居民声明） |
| **Reason TIN Registration** | 无特定理由 → `OTHERS` |
| **Taxpayer category** | `NORMAL` |
| 婚姻状况 | 选单身 → Part D 会提示无需填写，直接 Next |

带 `*` 的为必填；`Residential Address` 必填，Postcode 选完后 City / State 自动带出。

## ⚠️ Honorific 字段的陷阱

该下拉框是**马来语称谓**，且**混着一堆马来西亚封衔**。

### 该选的

| 情况 | 选 | 等价英文 |
| --- | --- | --- |
| 男性 | **ENCIK** | Mr |
| 女性（未婚） | **CIK** | Ms / Miss |
| 女性（已婚） | **PUAN** | Madam / Mrs |

### 千万别选的（那是勋衔，不是称呼）

| 不要选 | 是什么 |
| --- | --- |
| **DATO' / DATUK / DATIN** | 州 / 联邦勋衔，必须有授勋 |
| **TAN SRI / PUAN SRI** | 联邦高级勋衔 |
| **TUN / TOH PUAN** | 马来西亚最高勋衔 |
| **DATUK SERI / DATO' SERI** | 高级勋衔 |
| **HJ / HJH**（Haji / Hajjah） | 只给已完成麦加朝觐的穆斯林 |
| **DR / PROF** | 只有真持有学位 / 教职才能选 |

这类官方申报表格底下都有「所填信息真实无误」的声明条款，而这些勋衔在马来西亚**可公开核验**。**选 ENCIK / CIK / PUAN 永远是对的。**

> 遇到 action / 表单行为与预期不符时，认准官方来源；中文中介文章常互相抄错。

## 税号 ≠ 税务居民

**这是最容易误解的一点。**

- 外国人申请到的 TIN，官方分类原文是 **"Non-citizen or non-resident / foreign individual"** —— 本身就是**非居民**类目下发的
- 马来西亚的税务居民判定依据 **Income Tax Act 1967 第 7(1)(a) 条**：**在基准年内在马来西亚实际停留 ≥182 天**
- 不满足 182 天 → 法律上是**非居民**，非居民对马来西亚来源所得适用 30% 固定税率（自 YA2020 起），居民适用累进税率

**拿到 TIN 不改变居住事实。** 在银行 CRS 自证表上勾选「在该国是税务居民」并签字，与实际身份不符会构成虚假自证 —— 而自证表上明确要求所填信息真实准确。

## 拿到 TIN 之后

TIN 是后续所有交互的引用号：ByrHASiL 缴款、BE / B / M / MT 报税表申报、联系 HASiL 客服。

**首次登录 MyTax 会显示 "Digital Certificate does not exist"**，需另行激活数字证书：

- **e-CP55D**：网页端
- **e-KYC**：MyTax 手机 App 人脸识别

两者自 2023-09-01 起均为强制电子服务。

## 联系方式

- HASiL 客服：`03-8911 1000`（本地）/ `603-8911 1000`（海外）
- 办公时间：周一至周五 09:00–17:00

## 参考

- `https://www.hasil.gov.my/en/individu/pendaftaran/`
- `https://www.hasil.gov.my/en/e-perkhidmatan/`
- `https://mytax.hasil.gov.my/assets/pdf/e-Daftar.pdf`
- `https://www.oecd.org/content/dam/oecd/en/topics/policy-issue-focus/aeoi/malaysia-tin.pdf`
