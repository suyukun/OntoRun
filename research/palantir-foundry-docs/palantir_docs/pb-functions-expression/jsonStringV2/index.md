来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/jsonStringV2/

# 转换数据为JSON

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 转换数据为JSON

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

将输入变换为json字符串。

表达式类别: 文件, 字符串

## 声明的参数

- 输入- 要变换的输入。表达式<数组<AnyType> | 映射<AnyType, AnyType> | 结构体>
输出类型:字符串

## 示例

### 示例 1: 基本情况

参数值:

- 输入:array
| array | 输出 |
| --- | --- |
| [ hello, world ] | ["hello","world"] |

### 示例 2: 基本情况

参数值:

- 输入:struct
| struct | 输出 |
| --- | --- |
| {airline: {id: NA,},} | {"airline":{"id":"NA"}} |

### 示例 3: 基本情况

参数值:

- 输入:struct_0
| struct_0 | 输出 |
| --- | --- |
| {date: 2021-01-01,dec32: 1.12,dec33: 0.120,**dec... | {"dec32":1.12,"dec33":0.120,"dec64":10.0000,"timestamp":"2021-01-01T01:01:01.000Z","date":"2021-01-01","struct_1":{"airline":{"id":"NA"}}} |

### 示例 4: 基本情况

参数值:

- 输入:array
| array | 输出 |
| --- | --- |
| [ 1.00, 2.10, 36.00 ] | [1.00,2.10,36.00] |

### 示例 5: 基本情况

参数值:

- 输入:map
| map | 输出 |
| --- | --- |
| {a -> 1,b -> 2,} | {"a":"1","b":"2"} |

### 示例 6: 基本情况

参数值:

- 输入:array
| array | 输出 |
| --- | --- |
| [ {airline: {id: NA,},},null] | [{"airline":{"id":"NA"}},null] |

### 示例 7: 基本情况

参数值:

- 输入:map
| map | 输出 |
| --- | --- |
| {a -> {airline: {id: NA,},},} | {"a":{"airline":{"id":"NA"}}} |

### 示例 8: 基本情况

参数值:

- 输入:struct_0
| struct_0 | 输出 |
| --- | --- |
| {array_1: [null,null,null],struct_1: {double:null,string:null,},} | {"struct_1":{"string","double"},"array_1":[null,null,null]} |
| {array_1:null,struct_1:null,} | {"struct_1","array_1"} |
