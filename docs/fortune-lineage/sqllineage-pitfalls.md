# sqllineage 1.5.9 已知坑位与 fallback 调研（DWS 表级血缘）

> 调研日期：2026-09-10 · 对象：reata/sqllineage 1.5.9（PyPI 当前最新，2026-09-05 发布）
> 结论方式：官方文档/GitHub issues 检索 + 本机 uv 临时环境实测（sqllineage==1.5.9 / sqlglot 30.18.0，未动项目环境）
> 用途：财富广场 ETL（DWS/PG 系方言，delete+insert 双写、${data_ds} 占位符、union all 嵌套、行内中文注释）全量解析兜底依据。

## 1. 占位符变量（${var}）：官方态度 = 必须预处理，工具不管

**结论：sqllineage 无任何变量替换机制（v1.5.9 CLI 无 variable/substitution 选项），官方明确「不打算支持，调用方自己替换成 runnable SQL 再喂」——${data_ds} 出现在表名或未加引号处会直接 InvalidSyntaxException，必须预处理替换；仅在引号内字符串字面量中出现时恰好能通过（不可依赖）。**

- 官方原话（#463，maintainer reata）：*"For the moment, we don't have plans to support variables substitution. So you should take care of the variables and call sqllineage with runnable sql."*
  来源：https://github.com/reata/sqllineage/issues/463
- 旁证：#548 请求接入 sqlfluff templater 配置，2024-04 关闭，v1.5.9 CLI（version/e/f/v/l/g/p/d/ds/silent_mode/sqlalchemy_url）无任何 templater/variable 入口。
  来源：https://github.com/reata/sqllineage/issues/548
- 本机实测：`create table a_${data_ds} as ...` → InvalidSyntaxException（unparsable）；`ds = '${data_ds}'`（引号内）→ 正常解析出正确边。
- sqlglot 同理：裸 ${var} 会 ParseError，预处理是所有解析器的共同前置步骤（正则替换 \`\$\{([A-Za-z0-9_.]+)\}\s*→ 固定安全值\s* 即可）。

## 2. dialect：传 dialect="postgres"，DWS 最稳

**结论：默认 dialect="ansi" 对方言语法最弱，官方强烈建议显式传 dialect；DWS 是 PostgreSQL 系，选 `dialect="postgres"`（sqlfluff 方言族，实测本批脚本全部解析通过），Redshift/SparkSQL 等同族方言仅作个别脚本解析失败时的备选，不作为默认。**

- 官方 README（Dialect-Awareness Lineage 节）：*"By default, sqllineage use ansi dialect... To get the most out of sqllineage, we strongly encourage you to pass the dialect."*
  来源：https://github.com/reata/sqllineage/blob/v1.5.9/README.md
- 可用 dialect 清单继承自 sqlfluff（postgres/redshift/bigquery/hive/sparksql/tsql 等）：
  来源：https://docs.sqlfluff.com/en/stable/reference/dialects.html
- DWS 兼容 PG 语法（华为官方定位 PostgreSQL 9.2.4 内核系），postgres 方言为第一选择。
- 本机实测：postgres dialect 下 delete+insert、union all、多层 CTE+子查询、行内中文注释全部解析正确。
- 注意（1.5.9 已修的 PG 坑）：PG 带引号点号标识符曾抛 SQLLineageException（#787，1.5.9 修复）；实测 `dw."t.a"` 现在能解析但目标名输出为 `dw.t.a`，引号语义有损，与元数据对账时注意。

## 3. delete+insert 同脚本双写：表级可靠，DELETE 本身静默零输出

**结论：表级血缘以 INSERT INTO 为准，DELETE 语句不产生任何边（既不算 source 也不算 target、不报错），所以「delete+insert 双写」方向正确无假边——真正的坑是 DELETE-only 清理脚本会静默产出空血缘（漏边），以及同表先读后写会被归入 Intermediate Tables。**

- 已知问题（**仍然 open**）：#327 "Does not detect DELETE/Drops"——DELETE/DROP 语句 source/target 双空。
  来源：https://github.com/reata/sqllineage/issues/327
- 本机实测（1.5.9）：`delete from dw.t_fact_order ...; insert into dw.t_fact_order select ... union all ...` → source=[ods 两表]、target=[dw.t_fact_order]、无假边；`delete from dw.t_tmp ...` 单独跑 → source/target 全空、无任何告警。
- 旁注：同表先读后写（如 `insert into t select ... from t` 聚合）会出现在 Intermediate Tables（README 官方示例），消费边时按「中间表」处理。
- 列级附加坑（表级不受影响，做列级时注意）：#577 同脚本先 UPDATE 再读该表，列级元数据被 mask。
  来源：https://github.com/reata/sqllineage/issues/577

## 4. union all / 嵌套子查询 / 多层 CTE：长尾缺陷存在，头部场景 1.5.9 已验证正确

**结论：嵌套 UNION（UNION 内嵌 UNION ALL 分支）曾确认丢源表（#696）、UNION-in-CTE 曾报错（#376）、标量子查询/CASE ELSE 分支里丢源表（#795）——前两个及 #795 均已在 ≤1.5.9 修复且本机实测通过，但该类「分支丢失/静默漏边」是 sqllineage 的高发缺陷模式，POC 必须把嵌套 union/CTE 用例锁进回归集。**

- #696 Incorrect Lineage Detection for Nested UNION（maintainer 确认 bug，2025-10-12 修复关闭；1.5.9 发布于 2026-09-05，含该修复；本机实测三源表全部识别）：
  来源：https://github.com/reata/sqllineage/issues/696
- #376 UNION within CTE causes error（2023 年旧案，已修复，说明此类结构历史上出过事）：
  来源：https://github.com/reata/sqllineage/issues/376
- #795 source table missing when subquery is used in scalar projection or CASE ELSE branch（1.5.9 release notes Bugfix 节）：
  来源：https://github.com/reata/sqllineage/releases/tag/v1.5.9
- 行内中文注释：实测无干扰（`-- 订单编号` 等注释不影响解析），无需预处理。

## 5. fallback 阶梯：sqllineage 错边/漏边时怎么降级

**可靠性排序：预处理后的 sqllineage(dialect=postgres) ＞ sqlglot 最小提取器 ＞ 正则兜底（正则仅审计用，不做血缘源）。**

### 阶梯 0（前置，无条件）：预处理
- 替换 ${var} → 安全占位值；按分号切语句、记录语句序号（错边定位到语句级）；剥离/规范化注释非必须（实测中文注释无害）。

### 阶梯 1（主路径）：sqllineage
- `LineageRunner(sql, dialect="postgres")`；捕获 InvalidSyntaxException/SQLLineageException → 该脚本降级阶梯 2。

### 阶梯 2（降级）：sqlglot 手写最小提取（~35 行，本机实测通过）
- 适用：sqllineage 解析失败或结果存疑的脚本；同样要求先替换 ${var}（裸占位符 sqlglot 也 ParseError）。
- 已验证形态（sqlglot 30.18.0，read="postgres"，union all / 多层 CTE / 嵌套子查询 / delete+insert 均正确）：

```python
import sqlglot
from sqlglot import exp

def extract_tables(sql: str, read: str = "postgres"):
    """返回 (sources, targets)；解析失败返回 (None, None) 交由上层降级。"""
    try:
        stmts = sqlglot.parse(sql, read=read)
    except sqlglot.errors.ParseError:
        return None, None
    src, dst = set(), set()
    for st in stmts:
        if st is None:
            continue
        ctes = {c.alias_or_name for c in st.find_all(exp.CTE)}
        if isinstance(st, exp.Insert):                      # INSERT INTO t ... → t 是目标
            tbl = st.this.this if isinstance(st.this, exp.Schema) else st.this
            if isinstance(tbl, exp.Table):
                dst.add(tbl.name)
        elif isinstance(st, exp.Create) and isinstance(st.this, (exp.Table, exp.Schema)):
            tbl = st.this.this if isinstance(st.this, exp.Schema) else st.this
            if isinstance(tbl, exp.Table):
                dst.add(tbl.name)
        for t in st.find_all(exp.Table):                    # 其余 Table 节点 → 源（剔除 CTE 别名）
            if t.name and t.name not in ctes:
                src.add(t.name)
    return sorted(src - dst), sorted(dst)
```
- 边界（如实说明）：CTE 互相引用靠别名集合剔除，递归 CTE / 极端嵌套未逐一验证；INSERT 的 ${DS} 分区子句等 DWS 专有语法可能 ParseError——此提取器是「比 sqllineage 更笨但可控」的降级，不是等价替代；两边结果不一致的脚本标记人工复核，别自动二选一。

### 阶梯 3（最后兜底）：正则
- 适用边界：仅限结构规整脚本（顶层 `INSERT INTO <表> SELECT ... FROM <表列表>`，无 CTE、无别名重复、无嵌套 union、注释已剥离）；对 CTE/别名/子查询必然误报漏报，且 SQL 关键词出现在注释/字符串里会造假表名。
- 定位：只做「覆盖率审计与统计」（如统计全库脚本里 INSERT 目标表个数），**永远不作为血缘边的数据源**。

## 实测记录（1.5.9 本机冒烟，2026-09-10）

| # | 用例 | dialect=postgres 结果 |
|---|------|----------------------|
| 1 | delete+insert 双写 + union all + 文件头中文注释 | ✅ 边正确，无假边 |
| 2 | 同 ds 过滤的 delete+insert | ✅ 边正确 |
| 3 | 嵌套 union（#696 复现样例） | ✅ 三源表全识别（已修复） |
| 4 | 多层 CTE + 嵌套子查询 + using join | ✅ 边正确 |
| 5 | delete-only | ⚠️ 静默空输出（#327 open） |
| 6 | `dw."t.a"` 带引号点号标识符 | ⚠️ 可解析但引号语义有损（#787 修复后残留） |
| 7 | ${data_ds} 在引号内字符串 | ✅ 恰好能过（不可依赖） |
| 8 | ${data_ds} 在表名 | ❌ InvalidSyntaxException → 必须预处理 |
| 9 | 行内中文注释（select 列后） | ✅ 无干扰 |

## 来源清单
- 官方文档（1.5.9）：https://sqllineage.readthedocs.io/en/latest/
- README（dialect 建议）：https://github.com/reata/sqllineage/blob/v1.5.9/README.md
- Issue #463（变量不支持，官方原话）：https://github.com/reata/sqllineage/issues/463
- Issue #548（sqlfluff templater 请求，未落地）：https://github.com/reata/sqllineage/issues/548
- Issue #327（DELETE/DROP 不产出血缘，open）：https://github.com/reata/sqllineage/issues/327
- Issue #696（嵌套 UNION 丢源表，已修）：https://github.com/reata/sqllineage/issues/696
- Issue #376（UNION-in-CTE 报错，已修）：https://github.com/reata/sqllineage/issues/376
- Issue #577（同脚本 UPDATE mask 列级元数据）：https://github.com/reata/sqllineage/issues/577
- v1.5.9 release notes（含 #787/#795 修复）：https://github.com/reata/sqllineage/releases/tag/v1.5.9
- sqlfluff 方言清单：https://docs.sqlfluff.com/en/stable/reference/dialects.html
