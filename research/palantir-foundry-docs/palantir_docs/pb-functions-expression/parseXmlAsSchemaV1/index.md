来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/parseXmlAsSchemaV1/

# 解析 xml 作为模式

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 解析 xml 作为模式

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

按照给定的模式定义解析 xml 字符串，忽略模式中没有的字段。

表达式类别: 文件, 结构体

## 声明参数

- 模式- 解析 xml 字符串时使用的模式定义。类型<Struct>
- Xml- 要解析的 xml 字符串。表达式<字符串>
- 非必填属性前缀- 标签属性的前缀。字面量<字符串>
- 非必填值标签- 当元素中有属性但没有子元素时使用的值标签。字面量<字符串>
输出类型:结构体

## 示例

### 示例 1: 基本情况

参数值:

- 模式: Struct<id:字符串, airport<id:字符串, miles:整型>>
- Xml:xml
- 属性前缀:null
- 值标签:null
| xml | 输出 |
| --- | --- |
| <airline><id>XB-112</id><airport><id>JFK</id><miles>2000</miles></airport></airline> | {airport: {id: JFK,miles: 2000,},id: XB-112,} |

### 示例 2: 空值情况

描述: 当输入 XML 中缺少请求的字段时，该字段变为 null。参数值:

- 模式: Struct<id:字符串, airport<id:字符串, miles:整型>>
- Xml:xml
- 属性前缀:null
- 值标签:null
| xml | 输出 |
| --- | --- |
| <airline><id>XB-112</id><airport><id>JFK</id></airport></airline> | {airport: {id: JFK,miles:null,},id: XB-112,} |

### 示例 3: 空值情况

描述: 当请求的模式过小时，只解析模式中的字段。参数值:

- 模式: Struct<id:字符串>
- Xml:xml
- 属性前缀:null
- 值标签:null
| xml | 输出 |
| --- | --- |
| <airline><id>XB-112</id><airport><id>JFK</id></airport></airline> | {id: XB-112,} |

### 示例 4: 空值情况

描述: 你可以通过在名称前添加属性前缀来读取属性。参数值:

- 模式: Struct<id:字符串, airport<_id:字符串, miles:整型>>
- Xml:xml
- 属性前缀: _
- 值标签:null
| xml | 输出 |
| --- | --- |
| <airline>    <id>XB-112</id>    <airport id="JFK"><miles>2000</miles></airport></airline> | {airport: {_id: JFK,miles: 2000,},id: XB-112,} |
