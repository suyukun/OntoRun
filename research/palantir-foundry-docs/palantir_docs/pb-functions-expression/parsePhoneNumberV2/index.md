来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/parsePhoneNumberV2/

# 解析电话号码

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 解析电话号码

> 支持于：批处理，流处理

支持于：批处理，流处理

解析和规范化电话号码。

表达式类别: 字符串

## 声明的参数

- Expression- 要解析的电话号码。Expression<字符串>
- Format- 所需的电话号码格式。Enum<E164, E164_DIGITS_ONLY, INTERNATIONAL, NATIONAL, RFC3966>
- 非必填Region- 电话号码所属的地区。注意：当未指定地区时，将在没有地区的情况下进行解析，这可能导致结果不准确或根本没有结果。在您有多种号码且无法指派单一地区的情况下，这可能会很有用。Enum<阿富汗, 阿尔巴尼亚, 阿尔及利亚, 美属萨摩亚, 安道尔, 安哥拉, 安圭拉, 安提瓜和巴布达, 阿根廷, 亚美尼亚, 等...>
输出类型:电话号码

## 示例

### 示例 1: 基本案例

描述: 应返回仅包含数字的E164格式解析后的号码。参数值:

- Expression: +1 415 5552671
- Format:E164_DIGITS_ONLY
- Region:US
输出:14155552671

### 示例 2: 基本案例

描述: 应返回E164格式解析后的号码。参数值:

- Expression: +1 415 5552671
- Format:E164
- Region:US
输出:+14155552671

### 示例 3: 基本案例

描述: 应返回国际格式解析后的号码。参数值:

- Expression: +1 415 5552671
- Format:INTERNATIONAL
- Region:US
输出:+1 415-555-2671

### 示例 4: 基本案例

描述: 应返回国家格式解析后的号码。参数值:

- Expression: +1 415 5552671
- Format:NATIONAL
- Region:US
输出:(415) 555-2671

### 示例 5: 基本案例

描述: 应返回RFC3966格式解析后的号码。参数值:

- Expression: +1 415 5552671
- Format:RFC3966
- Region:US
输出:tel:+1-415-555-2671

### 示例 6: 基本案例

描述: 返回格式化的美国电话号码参数值:

- Expression:phoneNumber
- Format:E164
- Region:US
| phoneNumber | 输出 |
| --- | --- |
| (234) 235-5678 | +12342355678 |
| +1 415 5552671 | +14155552671 |
| (415) 5552671 | +14155552671 |
| Whatsapp@14155552671 | +14155552671 |

### 示例 7: 空值案例

描述: 当电话号码无法解析时返回null参数值:

- Expression:phoneNumber
- Format:E164
- Region:null
| phoneNumber | 输出 |
| --- | --- |
| null | null |
| 9991-COMPANY | null |
| empty string | null |

### 示例 8: 边缘案例

描述: 尝试仅基于号码本身解析号码。未指定地区参数值:

- Expression:phoneNumber
- Format:E164
- Region:null
| phoneNumber | 输出 |
| --- | --- |
| (234) 235-5678 | null |
| +1 415 5551111 | +14155551111 |
| 1 415 555 1111 | null |
| +1 411 1111111 | null |
| +34 91 23 45678 | +34912345678 |
| Whatsapp@34912345678 | null |
