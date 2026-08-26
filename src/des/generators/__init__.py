"""DES 行业专用生成函数包。

- risk_generators：金融风控行业专用生成函数（编码/DMN 规则/金融专用函数/生成上下文工具/共享业务池）。
- risk_table_generators：脊柱 12 张核心表的行生成器；risk_table_specs：54 表注册表（RISK_TABLE_SPECS）。
- risk_table_generators_customer / risk / approval / base：M1b 全量补全 42 张新表的行生成器。
- risk_ddl：金融 DDL（脊柱 12 + M1b 全量 42 = 54，脱敏后字段，docs/S3-M1a-字段脱敏映射-全量42表.json）。
- risk_ddl_ext / risk_ddl_ext2：M1b 42 张新表 DDL（由 scripts/s3_m1b_scaffold_risk_ext.py 生成）。
"""
