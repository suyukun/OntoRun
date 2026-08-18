"""数据连接器子包（重写蓝图 v0.3 §3 / §6 路径 A/B/C）。

MVP 范围：本地文件接入（CSV/Excel/JSON/MD/PDF/DOCX），上传后落 datasets 表（蓝图 §4）
+ 文件本体存到 data/builder_samples/。SQL/REST 连接器列发布期 TODO。

- 路径 A 结构化：csv/excel → schema 推断 + 清洗；
- 路径 B 半结构化：json/xml → 拍平/解析；
- 路径 C 非结构化：md/pdf/docx → 转 md → md_to_struct（markitdown 可用性见 §11 预案）。

P0 仅子包骨架与上传入表 stub；P2 实现具体解析。
"""
