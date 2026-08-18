来源: https://palantir.com/docs/zh/foundry/notepad/widgets-functions/

# 函数

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 函数

此微件仅适用于文档模板。

对象上的函数微件允许您使用TypeScript函数来计算在从模板生成文档时插入的值。

您可以将函数与在生成时传递的输入参数连接。对象上的函数部分也可以嵌套在生成器部分中，例如部分生成器或表行生成器；这使您能够为对象集中的每个对象计算单独的值。我们建议在生成器中配置批处理函数。

## 批处理函数

批处理函数是接受对象集作为参数并为对象集中每个对象返回结果的函数。用户可以为嵌套在生成器部分内的对象上的函数部分配置批处理函数。

以下是配置了批处理函数的对象上的函数部分的示例：

使用批处理函数显著减少了从模板生成文档所需的时间。这是因为执行函数的开销：非批处理函数必须为对象集中每个对象执行一次，而批处理函数仅需为整个对象集执行一次。

在使用批处理函数配置对象上的函数部分时，必须使用Object set from generator配置对象集参数。此模板输入指的是为周围生成器部分配置的对象集。

批处理函数可能除了对象集参数之外还有其他参数。

经验丰富的Foundry用户可能熟悉函数支持的属性。批处理函数类似于函数支持的属性。

### 编写批处理函数

批处理函数将对象集作为参数并返回一个FunctionsMap，该映射将对象集中每个对象映射到相应的结果。有关更多详细信息，请参阅接受的函数输入和输出部分。

例如，考虑一个未批处理的函数，该函数接受一个航班警报对象，并根据其延迟计算警报的紧急程度：

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
@Function()
public getAlertUrgency(flightAlert: FlightAlertWorkshopTutorial): string {
    const hoursDelayed = flightAlert.timeOfDelayHours
    if (hoursDelayed! > 4) {
        return "High"; // 如果延误时间超过4小时，紧急程度为高
    }
    else if (hoursDelayed! > 2) {
        return "Medium"; // 如果延误时间超过2小时且不超过4小时，紧急程度为中
    }
    else {
        return "Low"; // 如果延误时间不超过2小时，紧急程度为低
    }
}
```

此函数的批处理版本接收一个FlightAlertWorkshopTutorial对象集，并返回一个FunctionsMap<FlightAlertWorkshopTutorial, 字符串>。返回的FunctionsMap包含FlightAlertWorkshopTutorial对象与其紧急程度的映射。

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
@Function()
public flightAlertCalculateUrgency(flightAlerts: ObjectSet<FlightAlertWorkshopTutorial>):
    FunctionsMap<FlightAlertWorkshopTutorial, string> {
    const map = new FunctionsMap<FlightAlertWorkshopTutorial, string>();
    // 对所有的航班警报进行遍历
    flightAlerts.all().forEach(flightAlert => {
        const hoursDelayed = flightAlert.timeOfDelayHours
        // 如果延迟超过4小时，设置紧急程度为高
        if (hoursDelayed! > 4) {
            map.set(flightAlert, "High")
        }
        // 如果延迟超过2小时但不超过4小时，设置紧急程度为中
        else if (hoursDelayed! > 2) {
            map.set(flightAlert, "Medium")
        }
        // 如果延迟不超过2小时，设置紧急程度为低
        else {
            map.set(flightAlert, "Low")
        }
    });
    return map; // 返回紧急程度映射
}
```

## 接受的函数输入和输出

### 非批处理函数的必需输出

非批处理函数必须返回以下类型之一才能在Notepad模板中使用：

- 布尔值
- 日期
- 双精度
- 浮点
- 整数
- 长整数
- 字符串
### 批处理函数的必需输入和输出

有效的批处理函数必须至少有一个类型为ObjectSet<K>的参数，并且必须有一个返回值类型为FunctionsMap<K, V>。类型V必须是以下接受的类型之一：

- 布尔值
- 日期
- 双精度
- 浮点
- 整数
- 长整数
- 字符串
以集合或列表作为参数的函数目前不符合有效批处理函数的资格。

## 微件属性

- 批处理/非批处理：允许用户选择是否配置批处理或非批处理函数。仅当函数微件嵌套在生成器部分中时才显示。
- 函数：要运行的函数。如果上面选择了批处理选项，则仅提供批处理函数。
- 函数版本：要运行的函数版本。
- 函数输入：传入函数的值。可用的参数由所选函数定义。
- 函数结果：函数执行后生成的输出。结果可以解析为各种格式，如纯文本或Markdown。
## 模板配置

- 函数输入：根据所选函数，可以通过参数将不同的预期输入值模板化。
嵌入的对象上的函数部分也可以通过这种方式连接到生成器部分。
