来源: https://palantir.com/docs/zh/foundry/slate/references-helpers/

# Handlebar 辅助函数

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Handlebar 辅助函数

辅助函数是在Handlebars模板中可以调用的预定义函数。辅助函数具有名称、参数和返回值。例如，模板{{add 5 var1}}调用add辅助函数，作用于一个整数（5）和一个名为var1的变量。如果var1被设为 7，那么模板的计算结果为 12。

辅助函数分为以下几类：

- 内置辅助函数 - 来自 Handlebars 库
- 核心辅助函数 - 可用于查询和微件中
- 微件辅助函数 - 仅在微件中可访问
- Foundry 辅助函数 - 仅在 Foundry 查询中可访问
- SQL 辅助函数 - 仅在 SQL 查询中可访问
辅助函数不能用于函数编辑器中。

## 内置辅助函数

以下是来自 Handlebars 库的可用辅助函数。请参阅Handlebars 文档 ↗以了解每个辅助函数：

- if ↗
- unless ↗
- each ↗
## 核心辅助函数

以下核心辅助函数可用于查询和微件中：

- toString
- toNumber
- concat
- substring
- contains
- jsonParse
- jsonStringify
- add
- subtract
- multiply
- divide
- max
- min
- eq
- ne
- lt
- le
- gt
- ge
- encodeURI
- encodeURIComponent
- getSelectedDisplayValue
- getSelectedDisplayValues
- lookup
- and
- or
- not
### toString

toString 辅助函数使用JavaScript String() ↗函数将任何给定值转换为字符串。

#### 示例

- 对字符串使用 toString{{toString 'hello'}}渲染为 "hello"
- {{toString 'hello'}}渲染为 "hello"
- 对数字使用 toString{{toString 1}}渲染为 "1"
- {{toString 1}}渲染为 "1"
- 对字符串数组使用 toString{{toString variable}}在上下文为{ variable: ["hello", "world"] }时渲染为 "hello,world"
- {{toString variable}}在上下文为{ variable: ["hello", "world"] }时渲染为 "hello,world"
- 对数字数组使用 toString{{toString variable}}在上下文为{ variable: [1, 2, 3] }时渲染为 "1,2,3"
- {{toString variable}}在上下文为{ variable: [1, 2, 3] }时渲染为 "1,2,3"
- 对对象使用 toString{{toString variable}}在上下文为{ variable: {"hello": "world"} }时渲染为 "[Object Object]"
- {{toString variable}}在上下文为{ variable: {"hello": "world"} }时渲染为 "[Object Object]"
### toNumber

toNumber 辅助函数使用JavaScript Number() ↗函数将任何给定值转换为数字。如果该值无法转换为数字，则返回 NaN。

#### 示例

- 对数字使用 toNumber{{toNumber 1}}渲染为 1
- {{toNumber 1}}渲染为 1
- 对表示数字的字符串使用 toNumber{{toNumber '2'}}渲染为 2
- {{toNumber '2'}}渲染为 2
- 对不表示数字的字符串使用 toNumber{{toNumber 'hello'}}渲染为 NaN
- {{toNumber 'hello'}}渲染为 NaN
- 对数组使用 toNumber{{toNumber variable}}在上下文为{ variable: [1, 2, 3] }时渲染为 NaN
- {{toNumber variable}}在上下文为{ variable: [1, 2, 3] }时渲染为 NaN
- 对对象使用 toNumber{{toNumber variable}}在上下文为{ variable: {"hello": "world"} }时渲染为 NaN
- {{toNumber variable}}在上下文为{ variable: {"hello": "world"} }时渲染为 NaN
### concat

concat 辅助函数接收任意数量的参数，通过首先使用 JavaScript String() 函数将每个参数转换为字符串，然后将它们连接在一起。

#### 示例

- 对两个数字使用 concat{{concat 1 2}}渲染为 "12"
- {{concat 1 2}}渲染为 "12"
- 对两个字符串和一个数字使用 concat{{concat 'hello' 'world' 2}}渲染为 "helloworld2"
- {{concat 'hello' 'world' 2}}渲染为 "helloworld2"
- 对两个字符串数组使用 concat{{concat array1 array2}}在上下文为{ array1: ["hello", "world"], array2: ["again", "and again"] }时渲染为 "helloworldagainand again"
- {{concat array1 array2}}在上下文为{ array1: ["hello", "world"], array2: ["again", "and again"] }时渲染为 "helloworldagainand again"
- 对三个数字和一个对象使用 concat{{concat 1 2 3 variable}}在上下文为{ variable: {"hello": "world"} }时渲染为 "123[Object Object]"
- {{concat 1 2 3 variable}}在上下文为{ variable: {"hello": "world"} }时渲染为 "123[Object Object]"
### substring

substring 辅助函数接受一个输入字符串（value），以及起始位置和结束位置（非必填），然后传递给 JavaScript substring() 函数。这使您能够获取输入字符串的子字符串。

#### 示例

- 对字符串使用 substring{{substring 'foo' 0 1}}渲染为 "f"
- {{substring 'foo' 0 1}}渲染为 "f"
- 如果输入字符串长度小于结束位置，将返回输入字符串{{substring 'foo' 0 6}}渲染为 "foo"
- {{substring 'foo' 0 6}}渲染为 "foo"
- 如果未提供结束索引{{substring 'foo' 1}}渲染为 "oo"
- {{substring 'foo' 1}}渲染为 "oo"
### contains

contains 辅助函数接受一个数组或字符串（value）和一个要搜索的值（searchValue），如果该值在数组中，则返回 true，否则返回 false。它通过调用value.indexOf(searchvalue) !== -1来实现。

#### 示例

- 对数组使用 contains{{contains variable 3}}在上下文为{ variable: [1, 2, 3] }时渲染为 true
- {{contains variable 3}}在上下文为{ variable: [1, 2, 3] }时渲染为 true
- 对字符串使用 contains{{contains variable "hello"}}在上下文为{ variable: "hello world" }时渲染为 true
- {{contains variable "hello"}}在上下文为{ variable: "hello world" }时渲染为 true
### jsonParse

jsonParse 辅助函数接受一个 JSON 字符串作为输入，并使用 JavaScript 的JSON.parse ↗函数解析它。

#### 示例

- 对 JSON 字符串化的字符串使用 jsonParse{{jsonParse '\"foo\"'}}渲染为 "foo"
- {{jsonParse '\"foo\"'}}渲染为 "foo"
- 对 JSON 字符串化的数组使用 jsonParse{{jsonParse varA}}在上下文为"[\"hello\",\"world\"]"时渲染为["hello", "world"]
- {{jsonParse varA}}在上下文为"[\"hello\",\"world\"]"时渲染为["hello", "world"]
- 对 JSON 字符串化的对象使用 jsonParse{{jsonParse varA}}在上下文为"{\"varA\":{\"hello\":\"world\",\"foo\":[\"bar\",\"baz\"]}}"时渲染为{ varA: {"hello": "world", "foo": ["bar", "baz"]} }
- {{jsonParse varA}}在上下文为"{\"varA\":{\"hello\":\"world\",\"foo\":[\"bar\",\"baz\"]}}"时渲染为{ varA: {"hello": "world", "foo": ["bar", "baz"]} }
- 对数字使用 jsonParse{{jsonParse 123}}在控制台抛出错误 "jsonParse: Error: value must be a string"
- {{jsonParse 123}}在控制台抛出错误 "jsonParse: Error: value must be a string"
- 对无效 JSON 字符串使用 jsonParse{{jsonParse varA}}在上下文为"[\"hello\","时在控制台抛出错误 "jsonParse: SyntaxError: Unable to parse JSON string"
- {{jsonParse varA}}在上下文为"[\"hello\","时在控制台抛出错误 "jsonParse: SyntaxError: Unable to parse JSON string"
### jsonStringify

jsonStringify 辅助函数接受任何对象作为输入，并返回该对象转换为 JSON 的结果（传递给 JavaScript 的JSON.stringify ↗函数）。

#### 示例

- 对字符串使用 jsonStringify{{jsonStringify 'foo'}}渲染为"foo"（双引号包含在渲染文本中）
- {{jsonStringify 'foo'}}渲染为"foo"（双引号包含在渲染文本中）
- 对对象使用 jsonStringify{{jsonStringify varA}}在上下文为{ varA: {"hello": "world", "foo": ["bar", "baz"]} }时渲染为{"hello":"world","foo":["bar","baz"]}（同样，双引号包含在渲染文本中）
### add

add 辅助函数用于将两个数字相加。

#### 示例

- 对两个数字使用 add{{add 20 5}}渲染为 25
- {{add 20 5}}渲染为 25
- 对非数字值使用 add{{add 10 'abc'}}在控制台抛出错误 "value must be a number"
- {{add 10 'abc'}}在控制台抛出错误 "value must be a number"
### subtract

subtract 辅助函数用于将第二个数字从第一个数字中减去。

#### 示例

- 对两个数字使用 subtract{{subtract 20 5}}渲染为 15
- {{subtract 20 5}}渲染为 15
- 对非数字值使用 subtract{{subtract 10 'abc'}}在控制台抛出错误 "value must be a number"
- {{subtract 10 'abc'}}在控制台抛出错误 "value must be a number"
### multiply

multiply 辅助函数用于将两个数字相乘。

#### 示例

- 对两个数字使用 multiply{{multiply 20 5}}渲染为 100
- {{multiply 20 5}}渲染为 100
- 对非数字值使用 multiply{{multiply 10 'abc'}}在控制台抛出错误 "value must be a number"
- {{multiply 10 'abc'}}在控制台抛出错误 "value must be a number"
### divide

divide 辅助函数用于将第一个数字除以第二个数字。

#### 示例

- 对两个数字使用 divide{{divide 20 5}}渲染为 4
- {{divide 20 5}}渲染为 4
- 对非数字值使用 divide{{divide 10 'abc'}}在控制台抛出错误 "value must be a number"
- {{divide 10 'abc'}}在控制台抛出错误 "value must be a number"
### max

max 辅助函数用于查找给定数字或数字数组中的最大值。

#### 示例

- 对数字数组使用 max{{max variable}}在上下文为{ variable: [1, 2, 3] }时渲染为 3
- {{max variable}}在上下文为{ variable: [1, 2, 3] }时渲染为 3
- 对数字数组和两个数字使用 max{{max variable 12 15}}在上下文为{ variable: [1, 2, 3] }时渲染为 15
- {{max variable 12 15}}在上下文为{ variable: [1, 2, 3] }时渲染为 15
- 对字符串使用 max{{max 'hello' 123}}在控制台抛出错误 "value must be a number or a number array"
- {{max 'hello' 123}}在控制台抛出错误 "value must be a number or a number array"
- 对无效数组使用 max{{max variable}}在上下文为{ variable: ["hello", "world"] }时在控制台抛出错误 "value must be a number or a number array"
- {{max variable}}在上下文为{ variable: ["hello", "world"] }时在控制台抛出错误 "value must be a number or a number array"
### min

min 辅助函数用于查找给定数字或数字数组中的最小值。

#### 示例

- 对数字数组使用 min{{min variable}}在上下文为{ variable: [1, 2, 3] }时渲染为 1
- {{min variable}}在上下文为{ variable: [1, 2, 3] }时渲染为 1
- 对数字数组和两个数字使用 min{{min variable 6 10}}在上下文为{ variable: [1, 2, 3] }时渲染为 1
- {{min variable 6 10}}在上下文为{ variable: [1, 2, 3] }时渲染为 1
- 对字符串使用 min{{min 'hello' 123}}在控制台抛出错误 "value must be a number or a number array"
- {{min 'hello' 123}}在控制台抛出错误 "value must be a number or a number array"
- 对无效数组使用 min{{min variable  }}在上下文为{ variable: ["hello", "world"] }时在控制台抛出错误 "value must be a number or a number array"
- {{min variable  }}在上下文为{ variable: ["hello", "world"] }时在控制台抛出错误 "value must be a number or a number array"
### eq

eq 辅助函数比较两个数字或字符串，并检查它们是否相等

#### 示例

- 对两个数字使用 eq{{eq 1 1}}渲染为 true
对两个数字使用 eq

- {{eq 1 1}}渲染为 true
- 对非数字或字符串的值，或类型不同的值使用 eq{{eq [1, 2] 5}}在控制台抛出错误 "type mismatch"
对非数字或字符串的值，或类型不同的值使用 eq

- {{eq [1, 2] 5}}在控制台抛出错误 "type mismatch"
- 在 if 块中使用 eq{{#if (eq name 'Steven')}}
  Your name is Steven.
{{else}}
  Your name is not Steven.
{{/if}}在上下文为{ name: "Steven" }时渲染为 "Your name is Steven."
在 if 块中使用 eq

```
{{#if (eq name 'Steven')}}
  Your name is Steven.
{{else}}
  Your name is not Steven.
{{/if}}
```

在上下文为{ name: "Steven" }时渲染为 "Your name is Steven."

### ne

ne 辅助函数比较两个数字或字符串，并检查它们是否不同

#### 示例

- 对两个数字使用 ne{{ne 1 1}}渲染为 false
- {{ne 1 1}}渲染为 false
- 对非数字或字符串的值，或类型不同的值使用 ne{{ne [1, 2] 5}}在控制台抛出错误 "type mismatch"
- {{ne [1, 2] 5}}在控制台抛出错误 "type mismatch"
### lt

lt 辅助函数比较两个数字或字符串，并检查第一个是否小于第二个。

#### 示例

- 对两个数字使用 lt{{lt 1 2}}渲染为 true
- {{lt 1 2}}渲染为 true
- 对非数字或字符串的值，或类型不同的值使用 lt{{lt [1, 2] 5}}在控制台抛出错误 "type mismatch"
- {{lt [1, 2] 5}}在控制台抛出错误 "type mismatch"
### le

le 辅助函数比较两个数字或字符串，并检查第一个是否小于或等于第二个。

#### 示例

- 对两个数字使用 le{{le 1 1}}渲染为 true
- {{le 1 1}}渲染为 true
- 对非数字或字符串的值，或类型不同的值使用 le{{le [1, 2] 5}}在控制台抛出错误 "type mismatch"
- {{le [1, 2] 5}}在控制台抛出错误 "type mismatch"
### gt

gt 辅助函数比较两个数字或字符串，并检查第一个是否大于第二个。

#### 示例

- 对两个数字使用 gt{{gt 2 1}}渲染为 true
- {{gt 2 1}}渲染为 true
- 对非数字或字符串的值，或类型不同的值使用 gt{{gt [1, 2] 5}}在控制台抛出错误 "type mismatch"
- {{gt [1, 2] 5}}在控制台抛出错误 "type mismatch"
### ge

ge 辅助函数比较两个数字或字符串，并检查第一个是否大于或等于第二个。

#### 示例

- 对两个数字使用 ge{{ge 1 1}}渲染为 true
- {{ge 1 1}}渲染为 true
- 对非数字或字符串的值，或类型不同的值使用 ge{{ge [1, 2] 5}}在控制台抛出错误 "type mismatch"
- {{ge [1, 2] 5}}在控制台抛出错误 "type mismatch"
### encodeURI

encodeURI 辅助函数使用JavaScript encodeURI() ↗函数编码任何给定字符串。

#### 示例

- 对字符串使用 encodeURI{{encodeURI 'hello world?'}}渲染为 "hello%20world?"
- {{encodeURI 'hello world?'}}渲染为 "hello%20world?"
- 对非字符串值使用 encodeURI{{encodeURI variable}}在上下文为{ variable: [1, 2, 3] }时在控制台抛出错误 "value must be a string"
- {{encodeURI variable}}在上下文为{ variable: [1, 2, 3] }时在控制台抛出错误 "value must be a string"
### encodeURIComponent

encodeURIComponent 辅助函数使用JavaScript encodeURIComponent() ↗函数编码任何给定字符串。

#### 示例

- 对字符串使用 encodeURIComponent{{encodeURIComponent 'hello world?'}}渲染为 "hello%20world%3F"
- {{encodeURIComponent 'hello world?'}}渲染为 "hello%20world%3F"
- 对非字符串值使用 encodeURI{{encodeURIComponent variable}}在上下文为{ variable: [1, 2, 3] }时在控制台抛出错误 "value must be a string"
- {{encodeURIComponent variable}}在上下文为{ variable: [1, 2, 3] }时在控制台抛出错误 "value must be a string"
### getSelectedDisplayValue

getSelectedDisplayValue 辅助函数从给定的值和 selectedValue 中获取 displayValues 的 selectedDisplayValue。

#### 示例

- 使用 getSelectedDisplayValue 和 values, displayValues 以及 selectedValue{{getSelectedDisplayValue values displayValues selectedValue}}在上下文为{ values: [1, 2, 3], displayValues: ["a", "b", "c"], selectedValue: 2 }返回["b"]
- {{getSelectedDisplayValue values displayValues selectedValue}}在上下文为{ values: [1, 2, 3], displayValues: ["a", "b", "c"], selectedValue: 2 }返回["b"]
- 当 values 或 displayValues 不是数组时使用 getSelectedDisplayValue{{getSelectedDisplayValue values displayValues selectedValue}}在上下文为{ values: "hello", displayValues: ["a", "b", "c"], selectedValue: 2 }时在控制台抛出错误 "values must be an array"
- {{getSelectedDisplayValue values displayValues selectedValue}}在上下文为{ values: "hello", displayValues: ["a", "b", "c"], selectedValue: 2 }时在控制台抛出错误 "values must be an array"
- 当 selectedValue 不在 values 中时使用 getSelectedDisplayValue{{getSelectedDisplayValue values displayValues selectedValue}}在上下文为{ values: [1,2,3], displayValues: ["a", "b", "c"], selectedValue: 4 }时在控制台抛出错误 "selectedValue '4' is not in values"
- {{getSelectedDisplayValue values displayValues selectedValue}}在上下文为{ values: [1,2,3], displayValues: ["a", "b", "c"], selectedValue: 4 }时在控制台抛出错误 "selectedValue '4' is not in values"
### getSelectedDisplayValues

getSelectedDisplayValues 辅助函数从给定的值和 selectedValues 中获取 displayValues 的 selectedDisplayValues。

#### 示例

- 使用 getSelectedDisplayValues 和 values, displayValues 以及 selectedValues{{getSelectedDisplayValues values displayValues selectedValues}}在上下文为{ values: [1, 2, 3], displayValues: ["a", "b", "c"], selectedValues: [2, 3] }返回["b", "c"]
- {{getSelectedDisplayValues values displayValues selectedValues}}在上下文为{ values: [1, 2, 3], displayValues: ["a", "b", "c"], selectedValues: [2, 3] }返回["b", "c"]
- 当 values, displayValues 或 selectedValues 不是数组时使用 getSelectedDisplayValues{{getSelectedDisplayValues values displayValues selectedValues}}在上下文为{ values: "hello", displayValues: ["a", "b", "c"], selectedValues: 2 }时在控制台抛出错误 "values must be an array"
- {{getSelectedDisplayValues values displayValues selectedValues}}在上下文为{ values: "hello", displayValues: ["a", "b", "c"], selectedValues: 2 }时在控制台抛出错误 "values must be an array"
- 当某些 selectedValue 不在 values 中时使用 getSelectedDisplayValues{{getSelectedDisplayValues values displayValues selectedValues}}在上下文为{ values: [1,2,3], displayValues: ["a", "b", "c"], selectedValues: [4] }时在控制台抛出错误 "selectedValue '4' is not in values"
- {{getSelectedDisplayValues values displayValues selectedValues}}在上下文为{ values: [1,2,3], displayValues: ["a", "b", "c"], selectedValues: [4] }时在控制台抛出错误 "selectedValue '4' is not in values"
### lookup

lookup 辅助函数使用内置Handlebars lookup ↗的变体，并可以按照 Handlebars 文档中描述的使用。此外，Slate 的 lookup 变体可以描述长属性链，如下面的示例所示。

#### 示例

- {{lookup a "b" "c"}}在上下文为{ a: { b: { c: "test" } } }时将返回 "test"
### and

and辅助函数对提供的布尔参数执行 AND (&&) 逻辑比较。它至少需要两个参数。

#### 示例

- {{and var1 var2}}在上下文为{ var1: "true", var2: "false" }时渲染为 "false"
### or

or辅助函数对提供的布尔参数执行 OR (||) 逻辑比较。它至少需要两个参数。

#### 示例

- {{or var1 var2}}在上下文为{ var1: "true", var2: "false" }时渲染为 "true"
### not

not辅助函数对提供的布尔参数执行 NOT (!) 逻辑比较。它只能应用于单个参数。

#### 示例

- {{not var}}在上下文为{ var : "true" }渲染为 "false"
## 微件辅助函数

以下微件辅助函数可用于微件中：

- formatNumber
- formatDate
### formatNumber

formatNumber 辅助函数使用Numeral.js ↗库将任何给定数字格式化为字符串。注意，该值必须是数字，格式必须是字符串。

#### 示例

- 对数字使用 formatNumber{{formatNumber 1400 '0,0'}}渲染为 "1,400"有关格式化数字的更多示例，请查看 Numeral.js 库。
- {{formatNumber 1400 '0,0'}}渲染为 "1,400"有关格式化数字的更多示例，请查看 Numeral.js 库。
- 有关格式化数字的更多示例，请查看 Numeral.js 库。
- 对非数字值使用 formatNumber{{formatNumber 'abc' '0,0'}}在控制台抛出错误 "value must be a number"
- {{formatNumber 'abc' '0,0'}}在控制台抛出错误 "value must be a number"
- 使用无效格式（非字符串格式）使用 formatNumber{{formatNumber 1400 variable}}在上下文为{ variable: ["hello": "world"] }时在控制台抛出错误 "format must be a string"
- {{formatNumber 1400 variable}}在上下文为{ variable: ["hello": "world"] }时在控制台抛出错误 "format must be a string"
### formatDate

formatDate 辅助函数使用Moment.js ↗库将任何给定日期格式化为字符串。注意，该值必须是日期，格式必须是字符串。

#### 示例

- 对字符串使用 formatDate{{formatDate '2014-1-2' 'MM/DD/YYYY'}}渲染为 "01/02/2014"有关格式化日期的更多示例，请查看 Moment.js 库。
- {{formatDate '2014-1-2' 'MM/DD/YYYY'}}渲染为 "01/02/2014"有关格式化日期的更多示例，请查看 Moment.js 库。
- 有关格式化日期的更多示例，请查看 Moment.js 库。
- 对数字使用 formatDate{{formatDate 1237705200000 'YYYY-MM-DD'}}渲染为 "2009-03-22"有关格式化日期的更多示例，请查看 Moment.js 库。
- {{formatDate 1237705200000 'YYYY-MM-DD'}}渲染为 "2009-03-22"有关格式化日期的更多示例，请查看 Moment.js 库。
- 有关格式化日期的更多示例，请查看 Moment.js 库。
- 对无效日期字符串使用 formatDate{{formatDate 'some string' 'YYYY-MM-DD'}}在控制台抛出错误 "value must be a valid date"
- {{formatDate 'some string' 'YYYY-MM-DD'}}在控制台抛出错误 "value must be a valid date"
- 使用无效格式（非字符串格式）使用 formatDate{{formatDate '2014-1-2' variable}}在上下文为{ variable: ["hello": "world"] }时在控制台抛出错误 "format must be a string"
- {{formatDate '2014-1-2' variable}}在上下文为{ variable: ["hello": "world"] }时在控制台抛出错误 "format must be a string"
## Foundry 辅助函数

以下辅助函数可用于 HttpJson Foundry 查询中。

- joinParams
### joinParams

joinParams 辅助函数接受一个参数数组，并使用,连接单引号的参数。

#### 示例

- 使用字符串数组 joinParams"SELECT * FROM `table1` WHERE name IN ({{joinParams names}})"在上下文为{ names: ["Bill", "John J.", "Sam's", "Jay"] }渲染为"SELECT * FROM `table1` WHERE name IN ('Bill', 'John J.', 'Sam\'s', 'Jay')"
```
"SELECT * FROM `table1` WHERE name IN ({{joinParams names}})"
```

```
"SELECT * FROM `table1` WHERE name IN ('Bill', 'John J.', 'Sam\'s', 'Jay')"
```

- 使用字符串 joinParams"SELECT * FROM table1 WHERE name IN ({{joinParams name}});"在上下文为{ name: "Bill" }抛出错误 "parameters must be an array in joinParams helper"
```
"SELECT * FROM table1 WHERE name IN ({{joinParams name}});"
```

## SQL 辅助函数

以下 SQL 辅助函数可用于 SQL 查询中。注意，尽管 HttpJson Foundry 查询使用 Spark SQL 语法，但不应在这些查询中使用这些辅助函数。

- alias
- schema
- table
- column
- param
### alias

alias 辅助函数接受别名列或表名。列和表辅助函数会根据信息架构检查值。但是，临时列或表名不在架构中。alias 辅助函数为用户提供了一种注册临时列或表名的方法。当名称不是常量值时，会抛出错误。

#### 示例

- 使用 alias 注册别名列名"SELECT id as {{alias 'alias_column_name'}} FROM table1 ORDER BY {{column aliasColumnName}};"在上下文为{ aliasColumnName: "alias_column_name" }渲染为"SELECT id as alias_column_name FROM table1 ORDER BY alias_column_name;"
使用 alias 注册别名列名

```
"SELECT id as {{alias 'alias_column_name'}} FROM table1 ORDER BY {{column aliasColumnName}};"
```

在上下文为{ aliasColumnName: "alias_column_name" }渲染为

```
"SELECT id as alias_column_name FROM table1 ORDER BY alias_column_name;"
```

- 使用 alias 注册区分大小写的别名列名"SELECT id as "{{alias 'Alias Column Name'}}" FROM table1 ORDER BY "{{column aliasColumnName}}";"在上下文为{ aliasColumnName: "Alias Column Name" }渲染为"SELECT id as "Alias Column Name" FROM table1 ORDER BY "Alias Column Name";"
使用 alias 注册区分大小写的别名列名

```
"SELECT id as "{{alias 'Alias Column Name'}}" FROM table1 ORDER BY "{{column aliasColumnName}}";"
```

在上下文为{ aliasColumnName: "Alias Column Name" }渲染为

```
"SELECT id as "Alias Column Name" FROM table1 ORDER BY "Alias Column Name";"
```

- 使用 alias 注册别名表名"SELECT id as "{{alias 'Alias Column Name'}}" FROM table1 ORDER BY "{{column aliasColumnName}}";"在上下文为{ aliasColumnName: "Alias Column Name" }渲染为"SELECT id as "Alias Column Name" FROM table1 ORDER BY "Alias Column Name";"
使用 alias 注册别名表名

```
"SELECT id as "{{alias 'Alias Column Name'}}" FROM table1 ORDER BY "{{column aliasColumnName}}";"
```

在上下文为{ aliasColumnName: "Alias Column Name" }渲染为

```
"SELECT id as "Alias Column Name" FROM table1 ORDER BY "Alias Column Name";"
```

- 使用非常量值 alias:"SELECT id as {{alias aliasColumnName}} FROM table1 ORDER BY {{table aliasColumnName}};"在上下文为{ aliasColumnName: "alias_column_name" }抛出错误 "Only constant parameters are not allowed..."
使用非常量值 alias:

```
"SELECT id as {{alias aliasColumnName}} FROM table1 ORDER BY {{table aliasColumnName}};"
```

在上下文为{ aliasColumnName: "alias_column_name" }抛出错误 "Only constant parameters are not allowed..."

### schema

schema 辅助函数接受一个架构名称和一个白名单名称列表。它确保架构名称在白名单名称列表中，并根据数据源的信息表检查架构名称。当架构名称不存在于白名单名称列表或信息表中时，会抛出错误。

#### 示例

- 使用有效架构名称的 schema"SELECT * FROM {{schema schemaName 'schema1' 'schema2'}}.table1;"在上下文为{ schemaName: "schema1" }渲染为"SELECT * FROM schema1.table1;"
```
"SELECT * FROM {{schema schemaName 'schema1' 'schema2'}}.table1;"
```

```
"SELECT * FROM schema1.table1;"
```

- 使用不在白名单名称列表中的架构名称的 schema"SELECT * FROM {{schema schemaName 'schema1' 'schema2'}}.table1;"在上下文为{ schemaName: "schemaNameNotInList" }渲染为"SELECT FROM schemaNameNotInList.table1"并在执行时抛出错误 "schema name must be in the list of the whitelist names."
```
"SELECT * FROM {{schema schemaName 'schema1' 'schema2'}}.table1;"
```

```
"SELECT FROM schemaNameNotInList.table1"
```

- 使用带有白名单名称列表中引用的架构名称的 schema"SELECT * FROM {{schema schemaName 'schema1' 'schema2' templatizedName}}.table1;"在上下文为{ schemaName: "schema1", templatizedName: "anotherSchemaName" }渲染为"SELECT * FROM schema1.table1;"并在执行时抛出错误 "References ['templatizedName'] cannot be dynamic for security reasons."
```
"SELECT * FROM {{schema schemaName 'schema1' 'schema2' templatizedName}}.table1;"
```

```
"SELECT * FROM schema1.table1;"
```

- 使用无效架构名称的 schema"SELECT * FROM {{schema schemaName 'invalidSchema1'}}.table1;"在上下文为{ schemaName: "invalidSchema1" }渲染为"SELECT * FROM invalidSchema1.table1;"并在执行时抛出错误 "Invalid schema name 'invalidSchema1.'"
```
"SELECT * FROM {{schema schemaName 'invalidSchema1'}}.table1;"
```

```
"SELECT * FROM invalidSchema1.table1;"
```

### table

table 辅助函数接受一个表名和一个白名单名称列表。它确保表名在白名单名称列表中，并根据数据源的信息表检查表名。当表名不存在于白名单名称列表或信息表中时，会抛出错误。

#### 示例

- 使用有效表名的 table"SELECT * FROM {{table tableName 'table1' 'table2'}};"在上下文为{ tableName: "table1" }渲染为"SELECT * FROM table1;"
```
"SELECT * FROM {{table tableName 'table1' 'table2'}};"
```

```
"SELECT * FROM table1;"
```

- 使用不在白名单名称列表中的表名的 table"SELECT * FROM {{table tableName 'table1' 'table2'}};"在上下文为{ tableName: "tableNameNotInList" }渲染为"SELECT * FROM tableNameNotInList;"并在执行时抛出错误 "table name must be in the list of the whitelist names."
```
"SELECT * FROM {{table tableName 'table1' 'table2'}};"
```

```
"SELECT * FROM tableNameNotInList;"
```

- 使用带有白名单名称列表中引用的表名的 table"SELECT * FROM {{table tableName 'table1' 'table2' templatizedName}};"在上下文为{ tableName: "table1", templatizedName: "anotherTableName" }渲染为"SELECT * FROM table1;"并在执行时抛出错误 "References ['templatizedName'] cannot be dynamic for security reasons."
```
"SELECT * FROM {{table tableName 'table1' 'table2' templatizedName}};"
```

```
"SELECT * FROM table1;"
```

- 使用无效表名的 table"SELECT * FROM {{table tableName 'invalidTable1'}};"在上下文为{ tableName: "invalidTable1" }渲染为"SELECT * FROM invalidTable1;"并在执行时抛出错误 "Invalid table name 'invalidTable1'."
```
"SELECT * FROM {{table tableName 'invalidTable1'}};"
```

```
"SELECT * FROM invalidTable1;"
```

### column

column 辅助函数接受一个列名或列名列表，并根据数据源的信息表进行检查。当列名不存在于信息表中时，会抛出错误。

#### 示例

- 使用有效列名的 column"SELECT {{column columnName}} FROM table1;"在上下文为{ columnName: "column1" }渲染为"SELECT column1 FROM table1;"
```
"SELECT {{column columnName}} FROM table1;"
```

```
"SELECT column1 FROM table1;"
```

- 使用有效区分大小写的列名的 column"SELECT "{{column columnName}}" FROM table1;"在上下文为{ columnName: "Column 1" }渲染为 "SELECT "Column 1" FROM table1;"
```
"SELECT "{{column columnName}}" FROM table1;"
```

- 使用有效列名列表的 column"SELECT {{column columnNames}} FROM table1;"在上下文为{ columnNames: ["column1", "column2"] }渲染为"SELECT column1, column2 FROM table1;"
```
"SELECT {{column columnNames}} FROM table1;"
```

```
"SELECT column1, column2 FROM table1;"
```

- 使用无效列名的 column"SELECT {{column columnName}} FROM table1;"在上下文为{ columnName: "invalidColumn1" }渲染为"SELECT invalidColumn1 FROM table1;"并抛出错误 "Invalid column name 'invalidColumn1'."
```
"SELECT {{column columnName}} FROM table1;"
```

```
"SELECT invalidColumn1 FROM table1;"
```

### param

param 辅助函数接受一个参数或参数列表。在常规模式下，它将参数存储在列表中并返回问号。在预览模式下，它返回参数。注意：预览模式用于预览渲染的查询和调试。

#### 示例

- 在常规模式下对数字使用 param"SELECT * FROM table1 WHERE id = {{param parameter1}};"在上下文为{ parameter1: 1234 }渲染为"SELECT * FROM table1 WHERE id = ?;"参数列表为[1234]
```
"SELECT * FROM table1 WHERE id = {{param parameter1}};"
```

```
"SELECT * FROM table1 WHERE id = ?;"
```

- 在常规模式下对字符串列表使用 param"SELECT * FROM table1 WHERE text IN ({{param parameter1}});"在上下文为{ parameter1: ["some", "text"] }渲染为"SELECT * FROM table1 WHERE text IN (?, ?);"参数列表为["some", "text"]
```
"SELECT * FROM table1 WHERE text IN ({{param parameter1}});"
```

```
"SELECT * FROM table1 WHERE text IN (?, ?);"
```

- 在常规模式下使用 toString 辅助函数对数字使用 param"SELECT * FROM table1 WHERE text = {{param (toString parameter1)}};"在上下文为{ parameter1: 1234 }渲染为"SELECT * FROM table1 WHERE text = ?;"参数列表为["1234"]
```
"SELECT * FROM table1 WHERE text = {{param (toString parameter1)}};"
```

```
"SELECT * FROM table1 WHERE text = ?;"
```

- 在常规模式下使用 toNumber 辅助函数对字符串使用 param"SELECT * FROM table1 WHERE text = {{param (toNumber parameter1)}};"在上下文为{ parameter1: "1234" }渲染为"SELECT * FROM table1 WHERE text = ?;"参数列表为[1234]
```
"SELECT * FROM table1 WHERE text = {{param (toNumber parameter1)}};"
```

```
"SELECT * FROM table1 WHERE text = ?;"
```

- 在常规模式下使用 concat 辅助函数对 LIKE 操作使用 param"SELECT * FROM table1 WHERE text LIKE {{param (concat '%' parameter1 '%')}};"在上下文为{ parameter1: "some text" }渲染为"SELECT * FROM table1 WHERE text = ?;" 参数列表为 `["%some text%"]`
```
"SELECT * FROM table1 WHERE text LIKE {{param (concat '%' parameter1 '%')}};"
```

```
"SELECT * FROM table1 WHERE text = ?;" 参数列表为 `["%some text%"]`
```

- 在预览模式下对数字使用 param"SELECT * FROM table1 WHERE id = {{param parameter1}};"在上下文为{ parameter1: 1234 }渲染为"SELECT * FROM table1 WHERE id = 1234;"
```
"SELECT * FROM table1 WHERE id = {{param parameter1}};"
```

```
"SELECT * FROM table1 WHERE id = 1234;"
```

- 在预览模式下对字符串列表使用 param"SELECT * FROM table1 WHERE text IN ({{param parameter1}});"在上下文为{ parameter1: ["some", "text"] }渲染为"SELECT * FROM table1 WHERE text IN ('some', 'text');"
```
"SELECT * FROM table1 WHERE text IN ({{param parameter1}});"
```

```
"SELECT * FROM table1 WHERE text IN ('some', 'text');"
```

- 使用未定义参数的 param"SELECT * FROM table1 WHERE id = {{param parameter1}};"在上下文为{ }抛出错误 "Error: parameter value cannot be null in param helper"
```
"SELECT * FROM table1 WHERE id = {{param parameter1}};"
```

- 使用包含 null 的数组的 param"SELECT * FROM table1 WHERE text IN ({{param parameter1}});"在上下文为{ parameter: ["some", null] }抛出错误 "Error: parameter array cannot have null value in param helper"。
```
"SELECT * FROM table1 WHERE text IN ({{param parameter1}});"
```
