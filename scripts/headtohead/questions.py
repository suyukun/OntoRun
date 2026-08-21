"""P2 head-to-head 30 问规格（依据 docs/P2-ChatBI闭环设计_v0.1.md §4.1，适配真实 DES 5 源库 schema）。

每个问题给出：
  - id / group / ask      ：§4.1 问法（忠实）与所属组（G1-G5）
  - adapted_note          ：若 §4.1 期望口径引用了 demo 数据不存在的字段（单价/安全库存/发货状态/
                            准时率/到货时长），如实标注适配口径；未适配的问题此项为空
  - gt_sql                ：ground truth 确定 SQL（DuckDB sqlite_scan 跨 5 库只读），列序即输出规范
  - kind                  ：比较形态 scalar | table | codes
  - key_idx / val_idx     ：比较时 key 列位置 / 数值列位置（table 形态用）
  - b_expressible         ：B=本体版（现有 ContractExecutor + allow_all + 当前 15 指标注册表）可否表达
  - b_contract            ：可表达问题的标准契约（供对照/参考，LLM 自由生成，不强制）
  - b_note                ：B 表达的说明或不可表达原因
"""
from __future__ import annotations

# ---------- 通用 GT SQL 片段（库路径用占位符 {D} 替换） ----------

# 客户 = erp.KNA1(KUNNR/NAME1/KTOKD/ORT01)，KTOKD: 0001 零售 / 0002 中小企业 / 0003 集团
# 销售 = erp.VBAK(VBELN/KUNNR/AUDAT/NETWR/VKORG) + erp.VBAP(VBELN/POSNR/MATNR/KWMENG/MEINS/NETWR)
# 库存账面 = erp.MARD(MATNR/WERKS/LGORT/LABST/INSME/SPEME)
# 库存流水 = wms.MSEG(MBLNR/ZEILE/MATNR/WERKS/LGORT/BWART/MENGE/MEINS/BUDAT/EBELN/AUFNR)（101/301 收正，201/261 出负）
# 采购 = scm.EKKO(EBELN/LIFNR/BSART/AEDAT) + scm.EKPO(EBELN/EBELP/MATNR/MENGE/MEINS/NETWR)
# 财务 = fin.ACDOCA(BELNR/POSNR/RACCT/KOSTL/WSL/BUDAT/REF_DOC/REF_TYPE)（REF_TYPE ∈ SO/PO/MV；WSL 借正贷负）
# 生产 = mes.AUFK(AUFNR/MATNR/AUART/WERKS/FTRMS/STATUS) + mes.COFV(CONFNR/AUFNR/MATNR/WERKS/ARBPL/DATUM/ISM01/ISMN1)
# 报工 = mes.COFV；日期全表覆盖 2025-01-01..2026-12-31

# 指定物料/订单样例（P1b §6 Q4 同款）：MAT-2026-0001-K4V / SO-2026-000001
L1_MAT = "MAT-2026-0001-K4V"
L2_ORD = "SO-2026-000001"
F1_THRESHOLD = 90000     # 「高额订单」= VBAK.NETWR > 90000（约 top 10%，文档化适配）
F2_THRESHOLD = 1200      # 「低库存」= 物料总库存 LABST < 1200（无安全库存字段，阈值适配）
F4_THRESHOLD = 50000     # 「退款超阈值」= SO 负向财务分录 |WSL| > 50000
T3_START = "2026-12-02"  # 「近 30 天」= 数据末 30 天（数据止 2026-12-31）
T4_MONTHS = ("2026-11", "2026-12")  # 上月 / 本月

QUESTIONS = [
    # ================= G1 跨库 join =================
    {
        "id": "J1", "group": "G1", "anchor": "锚Q1",
        "ask": "每个客户各下过多少单？",
        "adapted_note": "",
        "gt_sql": (
            "SELECT k.KUNNR, COUNT(DISTINCT o.VBELN) AS order_count "
            "FROM sqlite_scan('{D}/erp.db','KNA1') k "
            "LEFT JOIN sqlite_scan('{D}/erp.db','VBAK') o ON o.KUNNR = k.KUNNR "
            "GROUP BY k.KUNNR ORDER BY k.KUNNR"
        ),
        "kind": "table", "key_idx": [0], "val_idx": [1],
        "b_expressible": True,
        "b_contract": {"contract_version": "0.2", "metric": {"metric_id": "order_count_by_customer"}},
        "b_note": "命中物化指标 order_count_by_customer（KNA1 全客户出发 LEFT JOIN VBAK，含 0 单客户计 0；物化即客户粒度，勿 group_by——count_distinct 非可加会拒答）",
    },
    {
        "id": "J2", "group": "G1",
        "ask": "各品类库存金额排行",
        "adapted_note": "demo 库无单价列（MARA/MARC/MARD 均无价格字段），「库存金额=Σ(量×单价)」无法落地；适配口径 = 各物料组(MATKL) 库存账面(LABST)合计，按金额降序",
        "gt_sql": (
            "SELECT m.MATKL AS category, ROUND(SUM(d.LABST), 2) AS inv_amount "
            "FROM sqlite_scan('{D}/erp.db','MARD') d "
            "JOIN sqlite_scan('{D}/erp.db','MARA') m ON m.MATNR = d.MATNR "
            "GROUP BY m.MATKL ORDER BY inv_amount DESC"
        ),
        "kind": "table", "key_idx": [0], "val_idx": [1],
        "b_expressible": True,
        "b_contract": {"contract_version": "0.2", "metric": {"metric_id": "stock_balance_by_mat_group", "group_by": ["material_group"]}},
        "b_note": "命中物化指标 stock_balance_by_mat_group（按物料组 MATKL SUM LABST），适配口径=各品类库存量排行",
    },
    {
        "id": "J3", "group": "G1",
        "ask": "哪些供应商到货准时率最高？",
        "adapted_note": "demo 库无准时/交货期字段（无计划收货日 vs 实际收货日），「准时率」无法计算；适配口径 = 各供应商采购收货量合计（MSEG 101 收货 × EKKO.LIFNR），降序排行",
        "gt_sql": (
            "SELECT e.LIFNR AS vendor, ROUND(SUM(s.MENGE), 2) AS receipt_qty "
            "FROM sqlite_scan('{D}/wms.db','MSEG') s "
            "JOIN sqlite_scan('{D}/scm.db','EKKO') e ON s.EBELN = e.EBELN "
            "WHERE s.BWART = '101' GROUP BY e.LIFNR ORDER BY receipt_qty DESC"
        ),
        "kind": "table", "key_idx": [0], "val_idx": [1],
        "b_expressible": True,
        "b_contract": {"contract_version": "0.2", "metric": {"metric_id": "receipt_qty_by_vendor", "group_by": ["vendor"]}},
        "b_note": "命中物化指标 receipt_qty_by_vendor（row_filter BWART='101' 已内置），适配口径=各供应商到货量排行",
    },
    {
        "id": "J4", "group": "G1",
        "ask": "退款金额 Top5 客户",
        "adapted_note": "「退款」= REF_TYPE='SO' 且 WSL<0 的财务分录（负向销售分录，借正贷负口径）；按客户(KUNNR via VBAK) Σ|WSL| 取 Top5",
        "gt_sql": (
            "WITH refund AS (SELECT a.REF_DOC, -a.WSL AS refund_amt "
            "FROM sqlite_scan('{D}/fin.db','ACDOCA') a "
            "WHERE a.REF_TYPE='SO' AND a.WSL < 0) "
            "SELECT o.KUNNR AS customer, ROUND(SUM(r.refund_amt), 2) AS refund_total "
            "FROM refund r JOIN sqlite_scan('{D}/erp.db','VBAK') o ON o.VBELN = r.REF_DOC "
            "GROUP BY o.KUNNR ORDER BY refund_total DESC LIMIT 5"
        ),
        "kind": "table", "key_idx": [0], "val_idx": [1],
        "b_expressible": True,
        "b_contract": {"contract_version": "0.2", "metric": {"metric_id": "customer_refund_by_customer", "group_by": ["customer"], "topN": 5}},
        "b_note": "命中物化指标 customer_refund_by_customer（REF_TYPE='SO' 且 WSL<0 + measure_scale=-1 内置）+ metric.topN=5 按退款降序取前 5",
    },
    {
        "id": "J5", "group": "G1",
        "ask": "各仓库库存水位",
        "adapted_note": "",
        "gt_sql": (
            "SELECT d.LGORT AS location, ROUND(SUM(d.LABST), 2) AS stock_balance "
            "FROM sqlite_scan('{D}/erp.db','MARD') d "
            "GROUP BY d.LGORT ORDER BY d.LGORT"
        ),
        "kind": "table", "key_idx": [0], "val_idx": [1],
        "b_expressible": True,
        "b_contract": {"contract_version": "0.2", "metric": {"metric_id": "stock_balance_by_location", "group_by": ["location"]}},
        "b_note": "命中物化指标 stock_balance_by_location（factory+location 维度，SUM LABST），group_by location 可得每仓库合计（勿用 factory×location 双维）",
    },
    {
        "id": "J6", "group": "G1", "anchor": "锚Q3",
        "ask": "有多少一物多码的物料？",
        "adapted_note": "",
        "gt_sql": "SELECT COUNT(*) AS multi_code_count FROM sqlite_scan('{D}/erp.db','MARA') WHERE BISMT IS NOT NULL",
        "kind": "scalar",
        "b_expressible": True,
        "b_contract": {"contract_version": "0.1", "object_type": "Material",
                       "filters": {"old_code": {"op": "is_not_null"}},
                       "aggregations": [{"function": "count", "field": "*"}],
                       "group_by": [], "link_traversal": None},
        "b_note": "Material 对象路径：filters old_code is_not_null + count(*) = 1200（DQ-01 同款）",
    },

    # ================= G2 聚合 =================
    {
        "id": "A1", "group": "G2", "anchor": "锚Q2",
        "ask": "各月各物料销售金额合计",
        "adapted_note": "设计契约列指向销售物化（metric b1），期望口径 = 物料×月 Σ 销售金额（VBAP.NETWR，月 = AUDAT 前 7 位）",
        "gt_sql": (
            "SELECT i.MATNR AS matnr, substr(o.AUDAT,1,7) AS month, ROUND(SUM(i.NETWR), 2) AS sales_amount "
            "FROM sqlite_scan('{D}/erp.db','VBAK') o "
            "JOIN sqlite_scan('{D}/erp.db','VBAP') i ON i.VBELN = o.VBELN "
            "GROUP BY i.MATNR, substr(o.AUDAT,1,7) ORDER BY i.MATNR, month"
        ),
        "kind": "table", "key_idx": [0, 1], "val_idx": [2],
        "b_expressible": True,
        "b_contract": {"contract_version": "0.2", "metric": {"metric_id": "sales_amount_by_mat_month"}},
        "b_note": "命中物化指标 sales_amount_by_mat_month（77,936 行）；V5 护栏已按查询规模派生（77,936），不再拒答",
    },
    {
        "id": "A2", "group": "G2",
        "ask": "品类×工厂×月三维汇总",
        "adapted_note": "三维带月的可用数据源 = 报工流水（COFV：物料/工厂/日期）；适配口径 = 各物料组(MATKL)×工厂(WERKS)×月(DATUM) 报工数量(ISM01) 合计",
        "gt_sql": (
            "SELECT m.MATKL AS category, a.WERKS AS factory, substr(c.DATUM,1,7) AS month, "
            "ROUND(SUM(c.ISM01), 2) AS qty "
            "FROM sqlite_scan('{D}/mes.db','COFV') c "
            "JOIN sqlite_scan('{D}/mes.db','AUFK') a ON c.AUFNR = a.AUFNR "
            "JOIN sqlite_scan('{D}/erp.db','MARA') m ON m.MATNR = a.MATNR "
            "GROUP BY m.MATKL, a.WERKS, substr(c.DATUM,1,7) ORDER BY category, factory, month"
        ),
        "kind": "table", "key_idx": [0, 1, 2], "val_idx": [3],
        "b_expressible": True,
        "b_contract": {"contract_version": "0.2", "metric": {"metric_id": "cofv_qty_by_matkl_werks_month"}},
        "b_note": "命中物化指标 cofv_qty_by_matkl_werks_month（物料组 MATKL×工厂 WERKS×月 DATUM 报工数量 ISM01，物料组以工单 AUFK.MATNR 为准，与 GT 一致），适配口径=报工数量",
    },
    {
        "id": "A3", "group": "G2",
        "ask": "各月下单客户数",
        "adapted_note": "",
        "gt_sql": (
            "SELECT substr(AUDAT,1,7) AS month, COUNT(DISTINCT KUNNR) AS customer_count "
            "FROM sqlite_scan('{D}/erp.db','VBAK') GROUP BY 1 ORDER BY 1"
        ),
        "kind": "table", "key_idx": [0], "val_idx": [1],
        "b_expressible": True,
        "b_contract": {"contract_version": "0.2", "metric": {"metric_id": "customer_count_by_month"}},
        "b_note": "命中物化指标 customer_count_by_month（COUNT DISTINCT KUNNR 按月）",
    },
    {
        "id": "A4", "group": "G2",
        "ask": "整体客单价",
        "adapted_note": "金额口径 = 订单项目销售金额合计（VBAP.NETWR）；客单价 = Σ金额 / COUNT(DISTINCT 客户)",
        "gt_sql": (
            "SELECT ROUND(SUM(i.NETWR) / NULLIF(COUNT(DISTINCT o.KUNNR), 0), 2) AS atv "
            "FROM sqlite_scan('{D}/erp.db','VBAK') o "
            "JOIN sqlite_scan('{D}/erp.db','VBAP') i ON i.VBELN = o.VBELN"
        ),
        "kind": "scalar",
        "b_expressible": False,
        "b_contract": None,
        "b_note": "除法 + 跨表去重不可由物化指标表达（受限面冷问题）",
    },
    {
        "id": "A5", "group": "G2",
        "ask": "物料价格区间",
        "adapted_note": "demo 库无主数据单价列；适配口径 = 采购订单项目单位价格（EKPO.NETWR / MENGE）的 MIN/MAX",
        "gt_sql": (
            "SELECT ROUND(MIN(e.NETWR / e.MENGE), 4) AS min_price, ROUND(MAX(e.NETWR / e.MENGE), 4) AS max_price "
            "FROM sqlite_scan('{D}/scm.db','EKPO') e WHERE e.MENGE > 0"
        ),
        "kind": "table", "key_idx": [], "val_idx": [0, 1],
        "b_expressible": False,
        "b_contract": None,
        "b_note": "需对 EKPO 做 MIN/MAX 除法派生，无指标无对象，受限面不可表达（冷问题）",
    },
    {
        "id": "A6", "group": "G2",
        "ask": "各月订单量与金额趋势",
        "adapted_note": "",
        "gt_sql": (
            "SELECT substr(o.AUDAT,1,7) AS month, COUNT(DISTINCT o.VBELN) AS order_count, "
            "ROUND(SUM(i.NETWR), 2) AS amount "
            "FROM sqlite_scan('{D}/erp.db','VBAK') o "
            "JOIN sqlite_scan('{D}/erp.db','VBAP') i ON i.VBELN = o.VBELN "
            "GROUP BY 1 ORDER BY 1"
        ),
        "kind": "table", "key_idx": [0], "val_idx": [1, 2],
        "b_expressible": False,
        "b_contract": None,
        "b_note": "订单数(order_count_by_month) 与金额(sales_amount_*) 分属两个指标，单契约只允许一个 metric，无法同契约输出两列（需双契约/双度量，冷问题）",
    },

    # ================= G3 过滤 =================
    {
        "id": "F1", "group": "G3",
        "ask": "corporate 客户的高额订单",
        "adapted_note": "corporate = KTOKD '0003'（集团，客户账户组 0001 零售/0002 中小企业/0003 集团）；高额阈值适配为 NETWR > 90000",
        "gt_sql": (
            "SELECT o.VBELN, o.KUNNR, ROUND(o.NETWR, 2) AS amount "
            "FROM sqlite_scan('{D}/erp.db','VBAK') o "
            "JOIN sqlite_scan('{D}/erp.db','KNA1') k ON o.KUNNR = k.KUNNR "
            "WHERE k.KTOKD = '0003' AND o.NETWR > 90000 "
            "ORDER BY o.NETWR DESC"
        ),
        "kind": "table", "key_idx": [0], "val_idx": [2],
        "b_expressible": False,
        "b_contract": None,
        "b_note": "需 KNA1.KTOKD 过滤 + join 订单，无对象无指标，受限面不可表达（冷问题）",
    },
    {
        "id": "F2", "group": "G3",
        "ask": "低于安全库存的物料清单",
        "adapted_note": "demo 库无安全库存字段；适配口径 = 物料总库存账面 LABST < 1200 的物料清单（含库存合计）",
        "gt_sql": (
            "SELECT MATNR, ROUND(SUM(LABST), 2) AS total_stock "
            "FROM sqlite_scan('{D}/erp.db','MARD') "
            "GROUP BY MATNR HAVING SUM(LABST) < 1200 ORDER BY MATNR"
        ),
        "kind": "table", "key_idx": [0], "val_idx": [1],
        "b_expressible": False,
        "b_contract": None,
        "b_note": "度量过滤为物化粒度行级 WHERE（stock_balance_by_mat_location 是 物料×工厂×地点 粒度），非分组后 HAVING——'总库存<1200' 语义无法正确表达（冷问题，见 v2 §6）",
    },
    {
        "id": "F3", "group": "G3",
        "ask": "已发货未送达的订单",
        "adapted_note": "demo 库销售订单无发货/送达状态；适配口径 = 已下达未关闭的生产工单（AUFK.STATUS='REL'，未达 DLV/CLSD）",
        "gt_sql": (
            "SELECT AUFNR, MATNR, WERKS, FTRMS, STATUS "
            "FROM sqlite_scan('{D}/mes.db','AUFK') WHERE STATUS = 'REL' ORDER BY AUFNR"
        ),
        "kind": "table", "key_idx": [0], "val_idx": [],
        "b_expressible": False,
        "b_contract": None,
        "b_note": "mes.AUFK 无对象无指标，受限面不可表达（冷问题）",
    },
    {
        "id": "F4", "group": "G3",
        "ask": "退款超过阈值的订单",
        "adapted_note": "退款 = REF_TYPE='SO' 且 WSL<0；阈值适配为 |WSL| > 50000",
        "gt_sql": (
            "SELECT REF_DOC AS vbeln, ROUND(-WSL, 2) AS refund_amt "
            "FROM sqlite_scan('{D}/fin.db','ACDOCA') "
            "WHERE REF_TYPE = 'SO' AND WSL < -50000 ORDER BY refund_amt DESC"
        ),
        "kind": "table", "key_idx": [0], "val_idx": [1],
        "b_expressible": True,
        "b_contract": {"contract_version": "0.2", "metric": {"metric_id": "refund_amount_by_order", "dimension_filters": {"refund_amount": {"op": "gt", "value": 50000}}}},
        "b_note": "命中物化指标 refund_amount_by_order（按订单退款，REF_TYPE='SO' 且 WSL<0 内置，物化粒度即订单）+ 度量过滤 refund_amount>50000（物化粒度 WHERE 等价 HAVING）",
    },
    {
        "id": "F5", "group": "G3",
        "ask": "指定品类×仓库组合的库存",
        "adapted_note": "品类在库存单表不可关联（库存行无品类列），适配口径 = 指定仓库组合 W01/W02 的库存账面明细（等价于多值 IN 过滤）",
        "gt_sql": (
            "SELECT MATNR, WERKS, LGORT, ROUND(LABST, 2) AS stock_balance "
            "FROM sqlite_scan('{D}/erp.db','MARD') "
            "WHERE LGORT IN ('W01','W02') ORDER BY MATNR, LGORT"
        ),
        "kind": "table", "key_idx": [0, 1, 2], "val_idx": [3],
        "b_expressible": True,
        "b_contract": {"contract_version": "0.2", "metric": {"metric_id": "stock_balance_by_mat_location",
                                                            "dimension_filters": {"location": {"op": "in", "value": ["W01", "W02"]}}}},
        "b_note": "命中物化指标 stock_balance_by_mat_location + dimension_filters location IN (W01,W02)；16,000 行 ≤ V5 规模护栏（16,000），不再拒答",
    },
    {
        "id": "F6", "group": "G3",
        "ask": "含多码物料明细",
        "adapted_note": "",
        "gt_sql": (
            "SELECT MATNR, MAKTX, MTART, BISMT AS old_code "
            "FROM sqlite_scan('{D}/erp.db','MARA') WHERE BISMT IS NOT NULL ORDER BY MATNR"
        ),
        "kind": "table", "key_idx": [0, 3], "val_idx": [],
        "b_expressible": True,
        "b_contract": {"contract_version": "0.1", "object_type": "Material",
                       "filters": {"old_code": {"op": "is_not_null"}},
                       "aggregations": [], "group_by": [], "link_traversal": None},
        "b_note": "Material 对象路径 old_code is_not_null 返回 1200 条明细（≤ V5 护栏 2400）；key=matnr+old_code 双键精确比较",
    },

    # ================= G4 链路 =================
    {
        "id": "L1", "group": "G4", "anchor": "锚Q4",
        "ask": "某物料的供应商是谁？",
        "adapted_note": "样例物料 MAT-2026-0001-K4V（P1b §6 Q4 同款）；供应商 = 该物料采购订单（EKPO→EKKO→LFA1）的去重供应商",
        "gt_sql": (
            "SELECT DISTINCT l.LIFNR, l.NAME1 AS vendor_name "
            "FROM sqlite_scan('{D}/scm.db','EKPO') e "
            "JOIN sqlite_scan('{D}/scm.db','EKKO') h ON e.EBELN = h.EBELN "
            "JOIN sqlite_scan('{D}/scm.db','LFA1') l ON h.LIFNR = l.LIFNR "
            "WHERE e.MATNR = '" + L1_MAT + "' ORDER BY l.LIFNR"
        ),
        "kind": "table", "key_idx": [0], "val_idx": [],
        "b_expressible": False,
        "b_contract": None,
        "b_note": "material→vendor 需 3 表 join，注册表无 material.vendor 链接，受限面不可表达（冷问题）",
    },
    {
        "id": "L2", "group": "G4",
        "ask": "订单对应客户及金额",
        "adapted_note": "样例订单 SO-2026-000001；订单→客户 1 跳",
        "gt_sql": (
            "SELECT o.VBELN, o.KUNNR, k.NAME1 AS customer_name, ROUND(o.NETWR, 2) AS amount "
            "FROM sqlite_scan('{D}/erp.db','VBAK') o "
            "JOIN sqlite_scan('{D}/erp.db','KNA1') k ON o.KUNNR = k.KUNNR "
            "WHERE o.VBELN = '" + L2_ORD + "'"
        ),
        "kind": "table", "key_idx": [0], "val_idx": [3],
        "b_expressible": False,
        "b_contract": None,
        "b_note": "订单对象未注册（仅 Material/Code），受限面不可表达（冷问题）",
    },
    {
        "id": "L3", "group": "G4",
        "ask": "物料多码全码列表",
        "adapted_note": "每个一物多码物料（old_code 非空）的全部系统编码（code_space + value，含 legacy）",
        "gt_sql": (
            "SELECT m.MATNR AS matnr, c.code_space, c.value "
            "FROM (SELECT MATNR, BISMT FROM sqlite_scan('{D}/erp.db','MARA') WHERE BISMT IS NOT NULL) m, "
            "(SELECT 'erp' AS code_space, MATNR AS value, MATNR AS matnr FROM sqlite_scan('{D}/erp.db','MARA') "
            " UNION ALL SELECT 'plm', MATNR, MATNR FROM sqlite_scan('{D}/erp.db','MARA') "
            " UNION ALL SELECT 'wms', MATNR, MATNR FROM sqlite_scan('{D}/erp.db','MARA') "
            " UNION ALL SELECT 'mes', 'MP-' || MATNR, MATNR FROM sqlite_scan('{D}/erp.db','MARA') "
            " UNION ALL SELECT 'legacy', BISMT, MATNR FROM sqlite_scan('{D}/erp.db','MARA') WHERE BISMT IS NOT NULL) c "
            "WHERE c.matnr = m.MATNR ORDER BY m.MATNR, c.code_space"
        ),
        "kind": "codes",
        "b_expressible": True,
        "b_contract": {"contract_version": "0.1", "object_type": "Material",
                       "filters": {"old_code": {"op": "is_not_null"}},
                       "aggregations": [], "group_by": [], "link_traversal": {"link": "material.codes", "hops": 1}},
        "b_note": "Material 对象 + link_traversal material.codes 返回 codes 数组（1200 物料 × 5 码空间）",
    },
    {
        "id": "L4", "group": "G4",
        "ask": "库存位置-物料-库存量",
        "adapted_note": "",
        "gt_sql": (
            "SELECT MATNR, WERKS, LGORT, ROUND(LABST, 2) AS stock_balance "
            "FROM sqlite_scan('{D}/erp.db','MARD') ORDER BY MATNR, WERKS, LGORT"
        ),
        "kind": "table", "key_idx": [0, 1, 2], "val_idx": [3],
        "b_expressible": True,
        "b_contract": {"contract_version": "0.2", "metric": {"metric_id": "stock_balance_by_mat_location"}},
        "b_note": "命中物化指标 stock_balance_by_mat_location（24,000 行）；V5 护栏已按规模派生（24,000），不再拒答",
    },
    {
        "id": "L5", "group": "G4",
        "ask": "订单→退款链路",
        "adapted_note": "退款 = REF_TYPE='SO' 且 WSL<0；链路 = 订单号 + 客户 + 退款金额",
        "gt_sql": (
            "SELECT a.REF_DOC AS vbeln, o.KUNNR, ROUND(-a.WSL, 2) AS refund_amt "
            "FROM sqlite_scan('{D}/fin.db','ACDOCA') a "
            "JOIN sqlite_scan('{D}/erp.db','VBAK') o ON a.REF_DOC = o.VBELN "
            "WHERE a.REF_TYPE = 'SO' AND a.WSL < 0 ORDER BY a.REF_DOC"
        ),
        "kind": "table", "key_idx": [0], "val_idx": [2],
        "b_expressible": False,
        "b_contract": None,
        "b_note": "退款链路需 订单号+客户+退款金额 三联：customer_refund_by_customer 有客户无订单号、refund_amount_by_order 有订单号无客户，单契约缺一列不可表达（冷问题）",
    },
    {
        "id": "L6", "group": "G4",
        "ask": "财务条目对应订单来源",
        "adapted_note": "SO 类型财务分录（ACDOCA.REF_TYPE='SO'）明细：财务单据号 → 订单号",
        "gt_sql": (
            "SELECT BELNR, POSNR, RACCT, REF_DOC AS vbeln, ROUND(WSL, 2) AS wsl "
            "FROM sqlite_scan('{D}/fin.db','ACDOCA') WHERE REF_TYPE = 'SO' ORDER BY BELNR"
        ),
        "kind": "table", "key_idx": [0], "val_idx": [4],
        "b_expressible": True,
        "b_contract": {"contract_version": "0.1", "object_type": "FinanceEntry",
                       "filters": {"ref_type": {"op": "eq", "value": "SO"}},
                       "aggregations": [], "group_by": [], "link_traversal": None},
        "b_note": "FinanceEntry 对象路径已接线（物化表 finance_entry）：过滤 ref_type='SO' 返回条目明细（belnr/posnr/account/ref_doc/amount），16,400 行 ≤ V5 规模护栏",
    },

    # ================= G5 时间趋势 =================
    {
        "id": "T1", "group": "G5",
        "ask": "月订单量趋势",
        "adapted_note": "",
        "gt_sql": (
            "SELECT substr(AUDAT,1,7) AS month, COUNT(*) AS order_count "
            "FROM sqlite_scan('{D}/erp.db','VBAK') GROUP BY 1 ORDER BY 1"
        ),
        "kind": "table", "key_idx": [0], "val_idx": [1],
        "b_expressible": True,
        "b_contract": {"contract_version": "0.2", "metric": {"metric_id": "order_count_by_month"}},
        "b_note": "命中物化指标 order_count_by_month（COUNT DISTINCT VBELN 按月；VBAK.VBELN 唯一，等价 COUNT(*)）",
    },
    {
        "id": "T2", "group": "G5", "anchor": "锚Q5",
        "ask": "月库存金额趋势",
        "adapted_note": "设计契约列即指向销售物化（metric b1/d2 + time_range），「月金额趋势」落地 = 各月销售金额趋势（VBAP.NETWR，月 = AUDAT 前 7 位）",
        "gt_sql": (
            "SELECT substr(o.AUDAT,1,7) AS month, ROUND(SUM(i.NETWR), 2) AS amount "
            "FROM sqlite_scan('{D}/erp.db','VBAK') o "
            "JOIN sqlite_scan('{D}/erp.db','VBAP') i ON i.VBELN = o.VBELN "
            "GROUP BY 1 ORDER BY 1"
        ),
        "kind": "table", "key_idx": [0], "val_idx": [1],
        "b_expressible": True,
        "b_contract": {"contract_version": "0.2", "metric": {"metric_id": "sales_amount_by_customer_month", "group_by": ["month"]}},
        "b_note": "设计契约列指向销售物化：sales_amount_by_customer_month group_by month 得各月销售金额趋势（适配口径=月销售金额，adapted_note 说明）",
    },
    {
        "id": "T3", "group": "G5",
        "ask": "近 30 天日销售",
        "adapted_note": "「近 30 天」= 数据末 30 天（2026-12-02..2026-12-31）；日粒度 = AUDAT 精确到日",
        "gt_sql": (
            "SELECT o.AUDAT AS day, ROUND(SUM(i.NETWR), 2) AS amount "
            "FROM sqlite_scan('{D}/erp.db','VBAK') o "
            "JOIN sqlite_scan('{D}/erp.db','VBAP') i ON i.VBELN = o.VBELN "
            "WHERE o.AUDAT >= '" + T3_START + "' GROUP BY 1 ORDER BY 1"
        ),
        "kind": "table", "key_idx": [0], "val_idx": [1],
        "b_expressible": True,
        "b_contract": {"contract_version": "0.2", "metric": {"metric_id": "sales_amount_by_day", "time_range": {"from": "2026-12-02", "to": "2026-12-31"}}},
        "b_note": "命中物化指标 sales_amount_by_day（日粒度 substr(1,10)）+ time_range 2026-12-02..31（近 30 天 = 数据末 30 天，口径见 adapted_note）",
    },
    {
        "id": "T4", "group": "G5",
        "ask": "本月 vs 上月退款对比",
        "adapted_note": "本月=2026-12、上月=2026-11（数据末两个月）；退款 = SO 负向分录；cur/prev 属呈现层标签，数据层统一按月份返回",
        "gt_sql": (
            "SELECT substr(BUDAT,1,7) AS month, ROUND(SUM(-WSL), 2) AS refund_amt "
            "FROM sqlite_scan('{D}/fin.db','ACDOCA') "
            "WHERE REF_TYPE = 'SO' AND WSL < 0 AND substr(BUDAT,1,7) IN ('2026-11','2026-12') "
            "GROUP BY 1 ORDER BY 1"
        ),
        "kind": "table", "key_idx": [0], "val_idx": [1],
        "b_expressible": True,
        "b_contract": {"contract_version": "0.2", "metric": {"metric_id": "refund_amount_by_month", "time_range": {"from": "2026-11-01", "to": "2026-12-31"}}},
        "b_note": "refund_amount_by_month + time_range 11-12 返回月份标签（2026-11/2026-12），GT key 同为月份标签，数值一致（cur/prev 属呈现层）",
    },
    {
        "id": "T5", "group": "G5",
        "ask": "平均到货时长趋势",
        "adapted_note": "demo 库无到货时长字段；适配口径 = 平均报工工时按月趋势（COFV.ISMN1 月度 AVG）",
        "gt_sql": (
            "SELECT substr(DATUM,1,7) AS month, ROUND(AVG(ISMN1), 4) AS avg_hrs "
            "FROM sqlite_scan('{D}/mes.db','COFV') GROUP BY 1 ORDER BY 1"
        ),
        "kind": "table", "key_idx": [0], "val_idx": [1],
        "b_expressible": True,
        "b_contract": {"contract_version": "0.2", "metric": {"metric_id": "cofv_avg_hrs_by_month"}},
        "b_note": "命中物化指标 cofv_avg_hrs_by_month（月粒度 AVG ISMN1），适配口径=平均报工工时",
    },
    {
        "id": "T6", "group": "G5",
        "ask": "季度汇总",
        "adapted_note": "季度 = 年 + Q + FLOOR((月-1)/3)+1；口径 = 季度订单数 + 销售金额",
        "gt_sql": (
            "SELECT substr(o.AUDAT,1,4) || 'Q' || "
            "CAST(CAST(FLOOR((CAST(substr(o.AUDAT,6,2) AS INTEGER) - 1) / 3) + 1 AS INTEGER) AS VARCHAR) AS quarter, "
            "COUNT(DISTINCT o.VBELN) AS order_count, ROUND(SUM(i.NETWR), 2) AS amount "
            "FROM sqlite_scan('{D}/erp.db','VBAK') o "
            "JOIN sqlite_scan('{D}/erp.db','VBAP') i ON i.VBELN = o.VBELN "
            "GROUP BY 1 ORDER BY 1"
        ),
        "kind": "table", "key_idx": [0], "val_idx": [1, 2],
        "b_expressible": False,
        "b_contract": None,
        "b_note": "季度派生维度无对应指标（指标只有月维度），受限面不可表达（冷问题）",
    },
]

BY_ID = {q["id"]: q for q in QUESTIONS}

def summary() -> dict:
    g = {f"G{i}": [q["id"] for q in QUESTIONS if q["group"] == f"G{i}"] for i in range(1, 6)}
    exp = [q["id"] for q in QUESTIONS if q["b_expressible"]]
    return {"groups": g, "b_expressible": exp, "n": len(QUESTIONS)}
