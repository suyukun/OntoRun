来源: https://palantir.com/docs/zh/foundry/workshop/widgets-iframe/

# Iframe

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Iframe

iframe微件允许在Workshop中嵌入外部全页应用，为搭建者提供了一种将自定义视图添加到其模块的方法。

请注意，由于iframe需要额外的内存和处理资源，您的Workshop模块的稳定性和性能可能会受到影响。我们不建议在屏幕上嵌入多个iframe微件。

## 配置选项

iframe微件支持WebURL或Slate作为输入。在下面的部分中了解更多关于Slate输入选项的信息。

### URL

输入应用程序的URL作为静态字符串或字符串变量。

您需要配置内容安全策略（CSP）以在您的Foundry环境中iframe外部资源。如果您使用的是外部于Foundry环境的URL并向Foundry API发出请求，您还必须配置跨域资源共享（CORS）。

### Slate

Slate配置选项允许您将Slate应用嵌入到您的Workshop模块中。可以使用参数使嵌入的Slate应用程序和Workshop模块相互交互。

下面的部分提供了如何使用iframe微件嵌入Slate应用程序的详细信息。

#### Slate来源

Slate来源定义了在您的模块中引用嵌入Slate的方法。您可以选择使用Compass引用或永久链接作为您的Slate来源。

- Compass引用：允许您使用Foundry资源选择器选择要嵌入的Slate应用程序。
- 永久链接：允许您输入Slate应用程序的永久链接或RID以选择嵌入。您可以在您的URL中找到Slate RID：/workspace/slate/documents/\<slate-permalink>/latest。
#### URL参数

URL参数附加到您的Slate URL，并用于在Slate中设置变量。更改URL参数将导致整个页面重新加载，因此我们建议仅将URL参数用于不常需修改的变量。要在Slate中引用URL参数，请设置一个与URL参数同名的变量，并使用handlebars引用它：{{username}}。

示例：根据用户名和ID在加载时更改嵌入Slate应用程序的外观。

#### 输入参数

输入参数从Workshop模块传递到嵌入的Slate应用程序。输入参数由其键和其值类型定义。可以将静态字符串、字符串变量、数字和对象集传递到嵌入的Slate应用程序。

在您的Slate应用程序中，可以通过使用事件面板中的Slate.getMessage事件以及下面的代码示例作为参考，从您的Workshop模块中检索信息。parameter_key必须与您在Workshop中iframe微件中定义的键匹配。

```
Copied!1
2
3
4
5
// 获取事件负载对象
const payload = {{slEventValue}}

// 返回指定参数键对应的值
return payload["<parameter_key>"]
```

示例：设置一个Workshop筛选以调整嵌入式Slate应用程序中的视图。

```
Copied!1
2
const payload = {{slEventValue}} // 从事件中获取的有效载荷
return payload["flight-alerts"] // 返回有效载荷中的航班警报信息
```

#### 输出参数

输出参数从Slate嵌入传递到Workshop模块。输出参数由其键和其值类型定义。对象集、对象集筛选和字符串变量可以传递到Workshop模块。在您的Workshop模块中，可以通过将Workshop变量指派给参数来检索来自Slate应用程序的信息。在您的Slate应用程序中，您需要使用Slate.sendMessage事件和下面的代码片段启动信息传输。代码中的参数键必须与您在Workshop微件中定义的键匹配。

```
Copied!1
2
3
4
5
return {
    type: "WORKSHOP//SET_OUTPUT_VALUE", // 动作类型，用于设置输出值
    outputParameterKey: "<parameter_key>", // 输出参数的键名
    value: {{<data_to_be_sent>}} // 要发送的数据
}
```

某些 JavaScript 原语在将值存储到字符串变量时会被映射到适当的 Workshop 类型。undefined将被映射为undefined（实际上将变量重置为其默认值），而null将清除字符串变量的值。

示例：使用嵌入的 Slate 应用中的选择状态以更改 Workshop 中的筛选集状态。

```
// 返回一个对象，该对象用于设置工作坊的输出值
return {
    type: "WORKSHOP//SET_OUTPUT_VALUE", // 表示操作类型，用于设置输出值
    outputParameterKey: "selected-objects", // 输出参数的键，指定要设置的输出对象
    value: {{f_selection}} // 输出值，通常是一个变量或表达式
}
```

#### 可触发事件

您可以从Slate触发任何Workshop事件。可触发事件由其键和事件类型定义。您可以触发打开覆盖层、重置变量等事件。

在您的Workshop模块中，定义您要触发的event_key和事件。在您的Slate应用程序中，使用事件面板中的Slate.sendMessage事件以及以下代码片段作为参考。event_key必须与iframe微件中定义的键相匹配。

```
Copied!1
2
3
4
return {
    type: "WORKSHOP//TRIGGER_WORKSHOP_EVENT",
    eventKey: "<event_key>", // 事件的唯一标识符，用于触发特定的工作坊事件
}
```

示例：使用Slate中的按钮点击在Workshop中切换一个可折叠部分。
