来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/arraySliceV1/

# 切片数组

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 切片数组

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

返回从第一个位置到第二个位置的数组切片。第一个位置必须为1或更高。如果第二个位置超过数组长度，将返回数组的其余部分。

表达式类别: 数组

## 声明的参数

- 表达式- 要切片的数组。Expression<Array<T>>
- 切片起始- 数组索引从1开始，如果起始值为负数则从末尾开始。如果该值为零，表达式将抛出出错。Expression<Integer>
- 切片长度- 切片的长度。如果切片长度超过数组末尾，将返回数组的其余部分。Expression<Integer>
类型变量边界：T 接受 AnyType

输出类型：Array<T>

## 示例

### 示例 1: 基本案例

参数值:

- 表达式:array
- 切片起始:sliceBegins
- 切片长度:sliceLength
| array | sliceBegins | sliceLength | 输出 |
| --- | --- | --- | --- |
| [ hello, world, out, there ] | 1 | 2 | [ hello, world ] |
| [ hello, world, out, there ] | 2 | 2 | [ world, out ] |
| [ hello, world, out, there ] | 1 | 0 | [  ] |
| [ hello, world, out, there ] | 2 | 10 | [ world, out, there ] |
| [ hello, world, out, there ] | -1 | 2 | [ there ] |

### 示例 2: 空案例

参数值:

- 表达式:array
- 切片起始:sliceBegins
- 切片长度:sliceLength
| array | sliceBegins | sliceLength | 输出 |
| --- | --- | --- | --- |
| [ hello, world, out, there ] | 0 | 1 | null |
| [ hello, world, out, there ] | 0 | 0 | null |
| [ hello, world, out, there ] | 1 | -1 | null |
| [  ] | 1 | 2 | [  ] |
| [null,null] | 1 | 1 | [null] |
