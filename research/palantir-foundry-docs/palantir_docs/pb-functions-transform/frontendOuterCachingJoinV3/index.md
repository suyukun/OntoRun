来源: https://palantir.com/docs/zh/foundry/pb-functions-transform/frontendOuterCachingJoinV3/

# 外部缓存合并

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 外部缓存合并

> 支持于: 流式处理

支持于: 流式处理

符合所有匹配条件并在缓存窗口内的左侧和右侧输入行，以及来自两个输入的不匹配行。

变换类别: 合并

## 声明的参数

- 默认缓存时间单位- 数据在逐出前缓存的默认时间单位，适用于lhs和rhs缓存。Enum<Days, Hours, Milliseconds, Minutes, Seconds, Weeks>
- 默认缓存时间值- 数据在逐出前缓存的默认时间值，适用于lhs和rhs缓存。Literal<Long>
- 合并键- 从左侧和右侧输入中用于合并的列列表。List<Tuple<Column<AnyType>, Column<AnyType>>>
- 保留左侧列- 保留的左侧列。List<Column<AnyType>>
- 左侧数据集- 在合并中使用的左侧数据集。Table
- 保留右侧列- 保留的右侧列。List<Column<AnyType>>
- 右侧数据集- 在合并中使用的右侧数据集。Table
- 非必填右侧列的前缀- 右侧列的前缀。Literal<字符串>
- 非必填rhs缓存时间覆盖- rhs数据集在逐出前缓存的时间值和单位。Tuple<Literal<Long>, Enum<Days, Hours, Milliseconds, Minutes, Seconds, Weeks>>