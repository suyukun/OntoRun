来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/h3CellToChildrenV1/

# H3单元到子单元

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# H3单元到子单元

> 支持于: 批处理，流处理

支持于: 批处理，流处理

获取指定分辨率和子单元粗糙度的H3索引的子单元。如果分辨率<0或>15，或者子单元分辨率低于给定H3索引的分辨率，则返回null。

表达式类别: 地理空间

## 声明参数

- 子单元分辨率- H3网格子单元分辨率在0到15之间（含）。表达式<Byte | Integer | Long | Short>
- H3索引- 一个有效的H3索引。表达式<H3索引>
输出类型:数组<H3索引>

## 示例

### 示例 1: 基本案例

参数值:

- 子单元分辨率:childrenResolution
- H3索引:h3Index
| h3Index | childrenResolution | 输出 |
| --- | --- | --- |
| 85283473fffffff | 6 | [ 862834707ffffff, 86283470fffffff, 862834717ffffff, 86283471fffffff, 862834727ffffff, 86283472fffffff, 862834737ffffff ] |
| 881F1D4887FFFFF | 9 | [ 891f1d48863ffff, 891f1d48867ffff, 891f1d4886bffff, 891f1d4886fffff, 891f1d48873ffff, 891f1d48877ffff, 891f1d4887bffff ] |
| 86be8d12fffffff | 8 | [ 88be8d1281fffff, 88be8d1283fffff, 88be8d1285fffff, 88be8d1287fffff, 88be8d1289fffff, 88be8d128bfff... |

### 示例 2: Null案例

参数值:

- 子单元分辨率:childrenResolution
- H3索引:h3Index
| h3Index | childrenResolution | 输出 |
| --- | --- | --- |
| 85283473fffffff | 4 | null |

### 示例 3: Null案例

参数值:

- 子单元分辨率:childrenResolution
- H3索引:h3Index
| h3Index | childrenResolution | 输出 |
| --- | --- | --- |
| 87283472bgggggg | 9 | null |
| 860800017ffffff | -1 | null |
| 860800017ffffff | 16 | null |
| null | 6 | null |
| 860800017ffffff | null | null |

### 示例 4: 边缘案例

参数值:

- 子单元分辨率:childrenResolution
- H3索引:h3Index
| h3Index | childrenResolution | 输出 |
| --- | --- | --- |
| 8e4e60c1c2a7fff | 15 | [ 8f4e60c1c2a7ff8, 8f4e60c1c2a7ff9, 8f4e60c1c2a7ffa, 8f4e60c1c2a7ffb, 8f4e60c1c2a7ffc, 8f4e60c1c2a7ffd, 8f4e60c1c2a7ffe ] |

### 示例 5: 边缘案例

参数值:

- 子单元分辨率:childrenResolution
- H3索引:h3Index
| h3Index | childrenResolution | 输出 |
| --- | --- | --- |
| 8029fffffffffff | 0 | [ 8029fffffffffff ] |

### 示例 6: 边缘案例

参数值:

- 子单元分辨率:childrenResolution
- H3索引:h3Index
| h3Index | childrenResolution | 输出 |
| --- | --- | --- |
| 8928308280fffff | 9 | [ 8928308280fffff ] |
