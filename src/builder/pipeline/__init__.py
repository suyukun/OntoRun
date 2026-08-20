"""转换管道子包。

DAG 执行器 + E1 三路径处理步骤：
- 节点类型：connector → storage → transform → output（蓝图 §6）；
- 步骤原语：schema_infer / cleanse / flatten / parse_xml / doc_to_md / md_to_struct；
- DAG schema 落地 P2（节点：id/kind/config/next[]，前后端共用，补丁 C4）。

P0 仅子包骨架；P2 实现 DAG 执行 + E1 步骤。
"""
