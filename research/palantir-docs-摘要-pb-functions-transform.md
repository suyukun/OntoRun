# Palantir 文档精读摘要（A 栏：机制事实）

> 编制：Rose ｜ 日期：2026-08-21 ｜ 来源：Palantir Foundry 官方中文文档

## pb-functions-transform 模块
- 定位：Pipeline Builder 变换函数库（80 函数页）；**不涉及 Python/Java 代码执行**，全声明式内置函数。
- 函数分类：聚合（aggregate/window/pivot/unpivot/topRow/rollUp/fpGrowth）、合并（joinV2 7 种 + complex* 系列 + unionByName 宽窄策略 + mappingJoin/leftLookupJoin）、地理空间（geoDistance/Intersection/Knn）、文件解析（CSV/JSON/Excel/Shapefile/XML）、数组/结构/日期/媒体/ML。
- 类型系统：Table/Files/Media 输入；Column<AnyType>/Set/List/Tuple；Literal 编译期字面量；Enum；Type<Struct>；Expression<AnyType> 嵌套；ColumnPredicate 按条件筛列；Window/Trigger 流式参数。
- 确定性/幂等：pivotV1 要求提供全部透视值→schema 静态预知；computeExpressionIfAbsentV1 按 key 缓存只算一次；keyByV3 不重排数据；timeBounded* 基于事件时间+水印。
- 限制：geoKnn 邻居数据集须整体入内存；parseShapefileV1 需 .shp/.shx/.dbf 三件套；kmeansV1 k 越多越慢。
- 来源：research/palantir_foundry_docs/palantir_docs/pb-functions-transform/（80 文件全读）
