来源: https://palantir.com/docs/zh/foundry/pb-functions-transform/outerCachingJoinV3/

# 外部缓存合并

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 外部缓存合并

> 支持于: 流式处理

支持于: 流式处理

将左侧和右侧数据集输入合并在一起，缓存每一侧事件时间最高的记录，以便在后续合并中使用。记录的处理时间用作决胜因素。在没有可合并值的情况下，时间结果会被乐观地发出。

变换类别: 合并

## 声明的参数

- 默认缓存时间单位- 数据在被逐出之前将被缓存的默认时间单位，适用于左侧和右侧缓存。Enum<Days, Hours, Milliseconds, Minutes, Seconds, Weeks>
- 默认缓存时间值- 数据在被逐出之前将被缓存的默认时间值，适用于左侧和右侧缓存。Literal<Long>
- 合并键- 从左侧和右侧输入中用于合并的列列表。List<Tuple<Column<AnyType>, Column<AnyType>>>
- 左侧数据集- 用于合并的左侧数据集。Table
- 右侧数据集- 用于合并的右侧数据集。Table
- 非必填右侧缓存时间覆盖- 数据从右侧数据集中被逐出之前的缓存时间值和单位。Tuple<Literal<Long>, Enum<Days, Hours, Milliseconds, Minutes, Seconds, Weeks>>