来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/isArrayUniqueV1/

# 数组元素是唯一的

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 数组元素是唯一的

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

如果数组的元素是唯一的，则返回 true，否则返回 false。如果数组为空，则返回值为 false。

表达式类别: 数组, 布尔值

## 声明的参数

- Expression- 可能包含重复元素的数组。Expression<Array<ComparableType>>
输出类型:Boolean

## 示例

### 示例 1: 基本情况

参数值:

- Expression:part_ids
| part_ids | 输出 |
| --- | --- |
| [ ABC-123, DCE-123, EFG-123 ] | true |
| [ ABC-123, ABC-123, EFG-123 ] | false |

### 示例 2: 基本情况

参数值:

- Expression:part_ids
| part_ids | 输出 |
| --- | --- |
| [  ] | true |

### 示例 3: 空值情况

参数值:

- Expression:part_ids
| part_ids | 输出 |
| --- | --- |
| [ ABC-123,null] | true |
| [ ABC-123,null, ABC-123 ] | false |
| [null,null] | false |

### 示例 4: 空值情况

参数值:

- Expression:part_ids
| part_ids | 输出 |
| --- | --- |
| null | false |
| [ ABC-123, EFG-123 ] | true |

### 示例 5: 边缘情况

参数值:

- Expression:part_ids
| part_ids | 输出 |
| --- | --- |
| [ [ ABC-123, EFG-123 ], [ ABC-123, EFG-123 ] ] | false |
| [ [ ABC-123, EFG-123 ], [ ABC-123, XYZ-123 ] ] | true |
| [ [ ABC-123, EFG-123 ], [ EFG-123, ABC-123 ] ] | true |

### 示例 6: 边缘情况

参数值:

- Expression:address
| address | 输出 |
| --- | --- |
| [ {city: New York,street: Broadway,}, {city: New York,street: Broadway,} ] | false |
| [ {city: New York,street: Broadway,}, {city: Los Angeles,street: Hoover Street,} ] | true |
