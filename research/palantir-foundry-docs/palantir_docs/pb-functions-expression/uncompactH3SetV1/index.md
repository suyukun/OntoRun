来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/uncompactH3SetV1/

# 解压一组 H3 索引

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 解压一组 H3 索引

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

将 H3 索引解压到指定的分辨率。所有输入索引的分辨率必须小于或等于请求的分辨率，否则此变换将返回 null。如果任何输入索引无效，此变换将返回 null。输出索引按升序排序。

表达式类别: 地理空间

## 声明的参数

- H3 集- H3 单元格集。Expression<Array<H3 Index>>
- 分辨率- H3 网格分辨率，介于 0 到 15（含）之间。Expression<Byte | Integer | Long | Short>
输出类型:Array<H3 Index>

## 示例

### 示例 1: 基本情况

参数值:

- H3 集:h3_set
- 分辨率:resolution
| h3_set | resolution | 输出 |
| --- | --- | --- |
| [ 86754e64fffffff, 87754a914ffffff, 87754a916ffffff, 87754a930ffffff, 87754a932ffffff, 87754a933ffff... | 7 | [ 87754a914ffffff, 87754a916ffffff, 87754a930ffffff, 87754a932ffffff, 87754a933ffffff, 87754a934ffff... |

### 示例 2: Null 情况

参数值:

- H3 集:h3_set
- 分辨率:resolution
| h3_set | resolution | 输出 |
| --- | --- | --- |
| null | 7 | null |
| [ 86754e64fffffff, 87754a914ffffff, 87754a916ffffff, 87754a930ffffff, 87754a932ffffff, 87754a933ffff... | null | null |
| null | null | null |

### 示例 3: 边界情况

参数值:

- H3 集:h3_set
- 分辨率:resolution
| h3_set | resolution | 输出 |
| --- | --- | --- |
| [ 87754e648ffffff, 87754e648ffffff ] | 7 | [ 87754e648ffffff ] |

### 示例 4: 边界情况

参数值:

- H3 集:h3_set
- 分辨率:resolution
| h3_set | resolution | 输出 |
| --- | --- | --- |
| [ 87754e648ffffff ] | 7 | [ 87754e648ffffff ] |

### 示例 5: 边界情况

参数值:

- H3 集:h3_set
- 分辨率:resolution
| h3_set | resolution | 输出 |
| --- | --- | --- |
| [ 87754e648ffffff ] | 6 | null |

### 示例 6: 边界情况

参数值:

- H3 集:h3_set
- 分辨率:resolution
| h3_set | resolution | 输出 |
| --- | --- | --- |
| [ Invalid h3 index ] | 7 | null |
