来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/cipherHashV1/

# 密码哈希

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 密码哈希

> 支持于：批处理，流处理

支持于：批处理，流处理

使用密码对表达式进行哈希。

表达式类别：其他

## 声明的参数

- 密码许可证资源标识符- 要使用的密码许可证。ResourceIdentifier
- 表达式- 要应用密码哈希的表达式。Expression<字符串>
输出类型：密码文本

## 示例

### 示例 1：基本案例

参数值：

- 密码许可证资源标识符: ri.bellaso.main.cipher-license.1-hash
- 表达式:string
| string | 输出 |
| --- | --- |
| bar | CIPHER::ri.bellaso.main.cipher-channel.1::c70a14f5cc57c940e3265045a5554d641bd549ee27a571a05cdbc75c77762eb86b1144c12f1bb7811a0bcec08b2f143989c44022e4664f615d6885ad640332cb::CIPHER |

### 示例 2：空案例

参数值：

- 密码许可证资源标识符: ri.bellaso.main.cipher-license.1-hash
- 表达式:string
| string | 输出 |
| --- | --- |
| null | null |
