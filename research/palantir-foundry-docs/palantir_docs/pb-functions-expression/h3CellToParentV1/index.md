来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/h3CellToParentV1/

# H3单元到父级

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# H3单元到父级

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

获取指定分辨率的H3索引的父级，指定父级粗度。对于分辨率<0或>15或高于给定索引的分辨率返回null。

表达式类别: 地理空间

## 声明的参数

- H3索引- 一个有效的H3索引。Expression<H3 Index>
- 父级分辨率- H3网格父级分辨率在0到15之间（包括0和15）。Expression<Byte | Integer | Long | Short>
输出类型:H3 Index

## 示例

### 示例1: 基本情况

参数值:

- H3索引:h3Index
- 父级分辨率:parentResolution
| h3Index | parentResolution | 输出 |
| --- | --- | --- |
| 881f1d4887fffff | 7 | 871f1d488ffffff |
| 860800017ffffff | 3 | 830800fffffffff |

### 示例2: Null情况

参数值:

- H3索引:h3Index
- 父级分辨率:parentResolution
| h3Index | parentResolution | 输出 |
| --- | --- | --- |
| 87283472bgggggg | 9 | null |
| 860800017ffffff | -1 | null |
| 860800017ffffff | 16 | null |
| null | 6 | null |
| 860800017ffffff | null | null |

### 示例3: 边缘情况

参数值:

- H3索引:h3Index
- 父级分辨率: 15
| h3Index | 输出 |
| --- | --- |
| 8f2000000000000 | 8f2000000000000 |

### 示例4: 边缘情况

参数值:

- H3索引:h3Index
- 父级分辨率: 0
| h3Index | 输出 |
| --- | --- |
| 860800017ffffff | 8009fffffffffff |
