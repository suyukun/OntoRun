来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/valueFromMapV1/

# 从映射中获取值

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 从映射中获取值

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

使用键从映射中获取值。

表达式类别: 映射

## 声明的参数

- 键- 键表达式。Expression<K>
- 映射- 映射表达式。Expression<Map<K, V>>
类型变量界限:K 接受 ComparableType**V 接受 AnyType

输出类型:V

## 示例

### 示例 1: 基本情况

参数值:

- 键: [ 1 ]
- 映射: {[ 1 ] -> Foo,}
输出:Foo

### 示例 2: 基本情况

参数值:

- 键: Bar
- 映射: {Bar -> 2,Foo -> 1,}
输出:2

### 示例 3: 基本情况

参数值:

- 键: 1
- 映射: {1 -> 10,2 -> 20,}
输出:10

### 示例 4: 基本情况

参数值:

- 键: Foo
- 映射: {Bar -> World,Foo -> Hello,}
输出:Hello

### 示例 5: 基本情况

参数值:

- 键: Foo
- 映射: {Bar -> World,}
输出:null

### 示例 6: 基本情况

参数值:

- 键: [ [ 1 ], [ 1 ] ]
- 映射: {[ [ 1 ], [ 1 ] ] -> Foo,}
输出:Foo

### 示例 7: 空值情况

参数值:

- 键:key
- 映射:map
| map | key | 输出 |
| --- | --- | --- |
| null | null | null |
| {Foo -> Hello,} | null | null |
| null | Foo | null |
