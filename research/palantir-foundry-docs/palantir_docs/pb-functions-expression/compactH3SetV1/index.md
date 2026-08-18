来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/compactH3SetV1/

# 压缩一组H3索引

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 压缩一组H3索引

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

如果可能，将H3索引压缩为混合分辨率的子集。运行逆操作uncompact可确保生成与压缩前相同的一组索引，如果输入索引的分辨率都是相同的。如果任何输入索引无效，此变换将返回null。输出索引按升序排序。

表达式类别: 地理空间

## 声明的参数

- H3索引- 一组H3单元。Expression<Array<H3 Index>>
输出类型:Array<H3 Index>

## 示例

### 示例1: 基本情况

参数值:

- H3索引:h3_set
| h3_set | 输出 |
| --- | --- |
| [ 87754a914ffffff, 87754a916ffffff, 87754a930ffffff, 87754a932ffffff, 87754a933ffffff, 87754a934ffff... | [ 86754e64fffffff, 87754a914ffffff, 87754a916ffffff, 87754a930ffffff, 87754a932ffffff, 87754a933ffff... |

### 示例2: Null情况

参数值:

- H3索引:h3_set
| h3_set | 输出 |
| --- | --- |
| null | null |

### 示例3: 边缘情况

参数值:

- H3索引:h3_set
| h3_set | 输出 |
| --- | --- |
| [ 86754e64fffffff, 86754e64fffffff ] | [ 86754e64fffffff ] |

### 示例4: 边缘情况

参数值:

- H3索引:h3_set
| h3_set | 输出 |
| --- | --- |
| [ Invalid h3 index ] | null |
