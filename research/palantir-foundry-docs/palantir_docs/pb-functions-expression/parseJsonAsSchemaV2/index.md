来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/parseJsonAsSchemaV2/

# 解析 json 为结构体

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 解析 json 为结构体

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

根据给定的模式定义解析 json 字符串，忽略模式中没有的任何字段。

表达式类别: 数据准备, 文件, 流行, 结构体

## 声明的参数

- Json- 使用模式解析的 Json。Expression<字符串>
- Schema- 解析 json 字符串时使用的模式定义。Type<Array<AnyType> | Map<String, String> | Struct>
输出类型:Array<AnyType> | Map<String, String> | Struct

## 示例

### 示例 1: 基本情况

参数值:

- Json:json
- Schema: Struct<airline:字符串, airport<id:字符串, miles>>
| json | 输出 |
| --- | --- |
| {"airline": "XB-112","airport": {"id": "JFK","miles": 2000}} | {airline: XB-112,airport: {id: JFK,miles: 2000,},} |

### 示例 2: 空情况

描述: 当请求的字段在输入 JSON 中缺失时，该字段变为 null。参数值:

- Json:json
- Schema: Struct<airline:字符串, airport<id:字符串, miles>>
| json | 输出 |
| --- | --- |
| {"airline": "XB-112","airport": {"id": "JFK"}} | {airline: XB-112,airport: {id: JFK,miles:null,},} |

### 示例 3: 空情况

描述: 当请求的字段在输入 JSON 中为 null 时，该字段变为 null。参数值:

- Json:json
- Schema: Struct<airline:字符串, airport<id:字符串, miles>>
| json | 输出 |
| --- | --- |
| {"airline": "XB-112","airport": {"id": "JFK","miles": null}} | {airline: XB-112,airport: {id: JFK,miles:null,},} |

### 示例 4: 空情况

描述: 测试结构体字段为数组。参数值:

- Json:json
- Schema: Struct<airline:字符串, airport<id:字符串, countries<字符串>>>
| json | 输出 |
| --- | --- |
| {"airline": "XB-112","airport": {"id": "JFK","countries": ["USA", "Canada"]}} | {airline: XB-112,airport: {countries: [ USA, Canada ],id: JFK,},} |

### 示例 5: 空情况

描述: 测试结构体字段为空字符串。参数值:

- Json:json
- Schema: Struct<airline:字符串, airport<id:字符串, countries<字符串>>>
| json | 输出 |
| --- | --- |
| {"airline": "XB-112","airport": {"id": "","countries": ["USA", "Canada"]}} | {airline: XB-112,airport: {countries: [ USA, Canada ],id:empty string,},} |

### 示例 6: 空情况

描述: 测试结构体字段为带有 null 元素的数组。参数值:

- Json:json
- Schema: Struct<airline:字符串, airport<id:字符串, countries<字符串>>>
| json | 输出 |
| --- | --- |
| {"airline": "XB-112","airport": {"id": "JFK","countries": ["USA", null]}} | {airline: XB-112,airport: {countries: [ USA,null],id: JFK,},} |

### 示例 7: 空情况

描述: 测试结构体字段为 null 字符串。参数值:

- Json:json
- Schema: Struct<airline:字符串, airport<id:字符串, countries<字符串>>>
| json | 输出 |
| --- | --- |
| {"airline": "XB-112","airport": {"id": null,"countries": ["USA", "Canada"]}} | {airline: XB-112,airport: {countries: [ USA, Canada ],id:null,},} |

### 示例 8: 空情况

描述: 测试具有一个字段为 map 的结构体。参数值:

- Json:json
- Schema: Struct<airline:字符串, airport<id:字符串, countries<String, Integer>>>
| json | 输出 |
| --- | --- |
| {"airline": "XB-112","airport": {"id": "JFK","countries": {"USA": 4}}} | {airline: XB-112,airport: {countries: {USA -> 4,},id: JFK,},} |

### 示例 9: 空情况

描述: 解析具有双精度字段的结构体。参数值:

- Json:json
- Schema: Struct<airline:字符串, airport<id:字符串, miles>>
| json | 输出 |
| --- | --- |
| {"airline": "XB-112","airport": {"id": "JFK","miles": 4.2}} | {airline: XB-112,airport: {id: JFK,miles: 4.2,},} |

### 示例 10: 空情况

描述: 解析为双精度的整数应返回双精度。参数值:

- Json:json
- Schema: Struct<airline:字符串, airport<id:字符串, miles>>
| json | 输出 |
| --- | --- |
| {"airline": "XB-112","airport": {"id": "JFK","miles": 4}} | {airline: XB-112,airport: {id: JFK,miles: 4.0,},} |

### 示例 11: 空情况

描述: 当 map 中有 null 值时，结果结构体将具有 null 值。参数值:

- Json:json
- Schema: Struct<airline:字符串, airport<id:字符串, countries<String, Integer>>>
| json | 输出 |
| --- | --- |
| {"airline": "XB-112","airport": {"id": "JFK","countries": {"USA": null}}} | {airline: XB-112,airport: {countries: {USA ->null,},id: JFK,},} |
