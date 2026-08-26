# S3 M1b DES 金融化设计（v1）

> 目标：DES 从"制造业专用"升级为"企业模拟引擎"，支持金融风控场景。
> 复用：Faker/Mimesis（通用字段）、pyDMNrules（规则引擎）、S2 确定性基建（seed/manifest/配置驱动）。
> 借鉴：TOGAF/DDD/BPMN/DMN/SynEval（方法论模板）。自研：企业调研编排器（薄壳）。

## 一、目录结构（新增金融模板层）
```
data/des/
├── des_industry_template.yaml        # 现有制造业模板（保持）
├── des_risk_industry_template.yaml   # 新增：金融风控行业模板（54 表注册表）
├── des_metrics.yaml                  # 现有指标（扩展金融指标）
└── enterprises/
    ├── hc_precision/                 # 现有制造业（保留）
    └── ap_anping/                    # 新增：安平金控
        ├── des_enterprise.yaml       # 企业覆盖层（继承 risk 模板）
        ├── profile.json              # STEP1 画像（已产出 docs/ 版，转 JSON）
        ├── domains.json              # STEP2 业务域
        ├── flows.json                # STEP3 流程+状态机
        ├── rules.json                # STEP4 DMN 规则集
        ├── schema.yaml               # 54 表结构（脱敏后）
        ├── {system}.db               # 生成数据（SQLite）
        ├── manifest.json             # 校验
        └── quality_report.json       # STEP6 质量门禁
```

## 二、行业模板层（des_risk_industry_template.yaml）
54 表注册表按域分 6 个系统：
| 系统 | 库 | 覆盖域 |
|---|---|---|
| customer | customer.db | 客户/集团/关系/名单/资产/投资 |
| risk | risk.db | 预警信号/处置/指标/排名/押品 |
| concentration | concentration.db | 集中度限额/调整/预警 |
| approval | approval.db | 审批单/节点/任务/待办/日志 |
| project | project.db | 风险项目/共债/衍生/背离 |
| base | base.db | 机构/用户/字典/参数 |

每表注册：kind(master/transaction)、row_count、pk、depends_on、fk、injection。

## 三、行分布设计（核心表密度 ≥3-5 万行）
| 表 | 行数 | 说明 |
|---|---|---|
| ap_customer | 50000 | 核心主数据 |
| ap_group_customer | 8000 | 集团客户 |
| ap_warning_signal | 80000 | **核心事实表** |
| ap_disposal | 40000 | 处置 |
| ap_approve_order | 20000 | 审批单 |
| ap_dim_metric | 50000 | 指标 |
| ap_risk_project | 5000 | 风险项目 |
| ap_collateral | 20000 | 押品 |
| ...（其余维度表 1k-5k） | | |
| Σ | ~30 万 | 总门禁 |

## 四、金融专用生成函数（真实感来源，注册进 DES）
| 函数 | 用途 |
|---|---|
| anping_cust_no() | 客户号编码 CUST-{YYYY}-{seq} |
| warn_level_decide() | 预警等级判定（调 DMN 规则 1） |
| five_category_assign() | 五级分类（调 DMN 规则 2） |
| concentration_calc() | 集中度计算（调 DMN 规则 3） |
| exposure_sim() | 跨板块敞口模拟（客户→多子公司敞口） |
| collateral_val() | 押品估值（含贬值注入） |
| approve_flow() | 审批链状态推进（按 NODE_SEQ） |
| codebt_link() | 共债关联注入 |

## 五、确定性保证
- 固定 seed（ap_anping seed=20260827）
- 调研段（STEP1-4）冻结后进 STEP5
- manifest：行数/sha256/外键完整性（复用 S2 逻辑）

## 六、质量门禁（STEP6）
- rows-per-object 健康：核心表 ≥3-5 万行，无空对象
- 规则命中率：DMN 规则全命中（如预警等级分布合理、五级分类分布合理）
- 外键完整性：100%
- 字段语义一致性：抽样比对 schema 注释

## 七、实现拆分（派活给编码子代理）
1. 读脱敏 JSON → 生成 schema.yaml（54 表字段/类型/枚举/外键）
2. 写 des_risk_industry_template.yaml（表注册表 + 行分布）
3. 写 ap_anping/des_enterprise.yaml（企业覆盖层）
4. 写金融专用生成函数模块（src/des/generators/risk_*.py）
5. 集成 pyDMNrules 规则引擎（DMN 规则 → 生成校验）
6. manifest + 质量门禁
7. 一条命令生成 + README

## 八、依赖（需 Jack 确认可加）
- Faker / Mimesis（通用字段）
- pyDMNrules（规则引擎）—— 或 bkflow-dmn（更新维护）
> 遵循"先问：加依赖"边界，派活前 Jack 确认。
