# Palantir 文档精读摘要（A 栏：机制事实）

> 编制：Rose ｜ 日期：2026-08-21 ｜ 来源：Palantir Foundry 官方中文文档（AIP 机器翻译）

## sap 模块
- **集成方式**：Connector 2.0 = SAP 认证 ABAP 附加组件（SAR 包），装在 SAP NetWeaver 应用层，经 HTTPS 把 S/4HANA/ECC/BW/SLT 数据接入；**无直接数据库访问**，一切经应用层与标准 SAP 安全。
- **支持对象**：ERP 表/视图、BW InfoProvider、BEx 查询、SLT、CDS 视图、函数/BAPI、表数据模型、ALV 报告。
- **表结构对接**：ABAP→Foundry 类型映射固定（CHAR/NUMC→String、DATS→Date、CURR/QUAN→Decimal、FLTP→Double、TIMS→String）；透明/池/簇表均可提取；日期格式 YYYYMMDD。
- **增量/CDC**：六种增量类型（单字段/多字段/变更文档表 CDHDR/CDPOS/双表合并/请求/BW 提取器/SLT 触发器）；比较一律"≥"避免漏数据→会重复须去重。
- **SLT CDC**：数据库触发器→ODQ 队列；首次全量加载并建触发器，之后仅取变更。
- **权限**：四类角色；行级筛选在数据离 SAP 前应用（SAP 侧预筛选强制叠加）；列级用删除列/掩码/哈希/加密（AES、MD5/SHA1/SHA256）。
- **写回**：Foundry Webhook 调 SAP 函数/BAPI 写回；OAuth 2.0 授权码流实现命名用户归属。
- **来源**：research/palantir_foundry_docs/palantir_docs/sap/（33 文件全读）
