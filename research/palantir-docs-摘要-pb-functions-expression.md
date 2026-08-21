# Palantir 文档精读摘要（A 栏：机制事实）

> 编制：Rose ｜ 日期：2026-08-21 ｜ 来源：Palantir Foundry 官方中文文档

## pb-functions-expression 模块
- 定位：Foundry 数据管道内置表达式函数库（301 单函数页，无概念页）。
- 函数分类：地理空间(72)/字符串(47)/数值(41)/数组(36)/日期时间(29)/聚合(22)/转换(17)/布尔/媒体(8)/数据准备(8)/二进制(7)/映射(7)/正则(5)/结构体(5)/文件(4)。
- 类型系统：参数带显式类型标签 Expression<T>/Literal<T>/Model(LLM引用)/Type<C>/Enum/List/TimeZone/Struct；泛型+界限；输出可为联合类型或错误结构 Struct<ok,error>。
- 确定性：显式非确定函数 uuidV1/uniformRandomV1/normalRandomV1/currentDateV1/currentTimestampV1/firstV1/lastV1；随机函数加种子但不保证完全确定性（分布式行序）；**官方建议建 ID 用 sha256 不用 uuid**。
- 行级/聚合/行展开：行级标量逐行；聚合按组/分区（sum/distinctCount/collectArray/rowNumber/rank/lag/lead/pivot→Map）；行展开用 explode 类。
- 约 44 个函数仅批处理（窗口排序/近似聚合/媒体LLM/分组几何）。
- 来源：research/palantir_foundry_docs/palantir_docs/pb-functions-expression/（301 文件全读）
