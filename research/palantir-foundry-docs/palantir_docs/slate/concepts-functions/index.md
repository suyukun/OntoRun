来源: https://palantir.com/docs/zh/foundry/slate/concepts-functions/

# 定义和运行 Slate 函数

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 定义和运行 Slate 函数

Slate 函数仅在 Slate 中可用，并且与 Foundry 函数不同；Foundry 函数在整个平台上可访问。您可以使用 Slate 平台编辑器在 Slate 中访问 Foundry 函数。有关更多信息，请参考函数文档。

函数编辑器允许您在 Handlebars 可访问的项目上定义和运行 JavaScript 函数，例如查询结果、全局变量和微件属性。

函数无法访问 DOM 或 Slate空间，并且不会保存任何状态。它们只能用于数据变换。

函数通常用于轻量级的数据处理任务，例如字符串解析。函数支持异步语法（包括async、await关键字和 promise）。

## 每个文档级别的函数库

用户可以编写带有参数的可重用 JavaScript 函数。这将有助于代码的重构，并减少在函数中复制和粘贴代码。您还可以使用重新运行所有函数按钮重新运行和更新依赖于函数库的所有函数。

## 默认可用的 JavaScript 库

为了增强函数的使用，Slate 默认附带以下外部 JavaScript 库：Lodash ↗、Math.js ↗、Moment ↗、Numeral ↗、和es6-shim ↗。在编写函数时可以随意使用这些库。

除非所有用户都被要求使用支持这些功能的浏览器，否则不要使用 ES6 语法功能。

## 示例

### 示例 1：添加两个微件属性

此函数添加两个下拉微件的值，并在文本微件中显示结果。

打开函数编辑器并添加一个名为addNumbers的函数。添加以下 JavaScript：

```
Copied!1
2
// 返回左侧选择的值与右侧选择的值之和
return {{lhs.selectedValue}} + {{rhs.selectedValue}};
```

然后，在文本微件中，通过在Handlebars中引用函数的名称{{addNumbers}}来显示返回值。

函数编辑器不接受任何形式的帮助程序。

### 示例 2: 解析查询结果

此函数解析查询结果中的每个元素。假设有一个名为asteroids的查询，它返回以下JSON：

```
Copied!1
2
3
4
5
{
  "id": [6, 7, 8],  // 小行星的编号
  "name": ["Hebe", "Iris", "Flora"],  // 小行星的名字
  "diameter": [185.18, 199.83, 135.89]  // 小行星的直径，单位为公里
}
```

以下函数返回一个结果，该结果结合了名称和ID，并添加了一个新的周长属性。

```
Copied!1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
var asteroids = {{asteroids}}; // 小行星数据的占位符
var formattedNames = []; // 格式化后的小行星名称数组
var circumference = []; // 小行星周长数组

// 遍历每个小行星的名称
for (var i = 0; i < asteroids.name.length; i++) {
  // 格式化名称并添加到formattedNames数组中
  formattedNames.push(formatName(
    asteroids.name[i], asteroids.designation[i]));
  // 计算周长并添加到circumference数组中
  circumference.push(asteroids.diameter[i] * 3.14);
}

// 返回包含格式化名称、直径和周长的对象
return {
  name: formattedNames,
  diameter: asteroids.diameter,
  circumference: circumference
};

// 辅助函数：格式化小行星名称
function formatName(name, designation) {
  return name + " (" + designation + ")"; // 将名称与编号组合成格式化字符串
}
```

生成的JSON如下所示：

```
Copied!1
2
3
4
5
{
  "name": ["Hebe (6)", "Iris (7)", "Flora (8)"],  // 小行星的名称以及编号
  "diameter": [185.18, 199.83, 135.89],  // 小行星的直径（单位：公里）
  "circumference": [581.4652,627.4662,426.6946]  // 小行星的周长（单位：公里）
}
```

### 示例3：使用设置超时和承诺创建暂停

此函数创建一个五秒间隔的setTimeout来暂停 Slate 函数五秒钟，然后再执行。

```
Copied!1
2
3
4
5
return new Promise(resolve => {
  setTimeout(() => {
    resolve(); // 5秒后执行resolve，表示Promise完成
  }, 5000);
});
```

此函数在暂停五秒钟后返回undefined。
