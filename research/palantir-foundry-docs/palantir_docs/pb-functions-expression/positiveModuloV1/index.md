来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/positiveModuloV1/

# 正数模

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 正数模

> 支持于: 批处理

支持于: 批处理

返回表达式的正模。

表达式类别: 数值

## 声明的参数

- 分母-无描述Expression<T2>
- 分子-无描述Expression<T1>
类型变量界限：T1 接受 Byte | Integer | Long | Short**T2 接受 Byte | Integer | Long | Short

输出类型：T1

## 示例

### 示例 1: 基本情况

参数值：

- 分母: 3
- 分子: 10
输出：1

### 示例 2: 空值情况

参数值：

- 分母:null
- 分子: 10
输出：null

### 示例 3: 空值情况

参数值：

- 分母: 3
- 分子:null
输出：null
