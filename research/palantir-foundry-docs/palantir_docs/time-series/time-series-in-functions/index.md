来源: https://palantir.com/docs/zh/foundry/time-series/time-series-in-functions/

# 函数中的时间序列

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 函数中的时间序列

函数支持对时间序列属性的操作。在本页面中，我们将介绍如何在函数中设置和使用时间序列属性。

## 初始设置

要在函数中使用时间序列，您需要先将时间序列存储在Ontology中。您可以按照这里的步骤开始。

一旦您的时间序列存储在Ontology中，我们需要为我们的时间序列函数创建代码库。在这个代码库中，我们首先导入Ontology类型，以便引用存储在这些Ontology类型中的时间序列。

现在您可以在函数中使用时间序列了。

## 在函数中使用时间序列

要在函数中访问时间序列，首先在您的代码库中创建一个Object支持的函数。这些函数可以直接访问Ontology中的时间序列属性。当您编写好函数后，有两种方式来运行您的新函数。您可以选择在实时预览中测试您的函数或发布您的函数并在整个平台的其他应用中开始使用它。

以下是一些常见操作的快速示例，帮助您入门。

### 获取第一个或最后一个点

在处理时间序列属性时，检查第一个或最后一个点是很有用的。由于函数没有内置的时间序列点类型，您可以返回值或时间戳。例如，以下函数用于读取机器上的最新温度：

```
// 该函数用于获取机器的最新温度数据
@Function()
public async getLatestTemperature(machine: MachineRoot): Promise<Double | undefined> {
    // 获取机器温度数据的最新点
    const latest = await machine.temperatureId?.getLastPointV2();
    // 返回最新温度值
    return latest?.value;
}
```

您可以通过以下函数获取首次温度读数：

```
Copied!1
2
3
4
5
6
@Function()
public async getEarliestTemperature(machine: MachineRoot): Promise<Double | undefined> {
    // 获取机器的最早温度数据点的值
    const earliest = await machine.temperatureId?.getFirstPointV2();
    return earliest?.value; // 返回最早温度数据点的值，如果不存在则返回undefined
}
```

### 对一系列数据进行聚合

一个有用的聚合是计算一定范围内点的平均值。请考虑以下获取示例机器平均温度的函数。

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
    @Function()
    public async getAverageTemperature(machine: MachineRoot): Promise<Double | undefined> {
        // 获取指定机器的平均温度
        const aggregation = await machine.temperatureId?.aggregate()
            .overEntireRange()  // 在整个范围内进行聚合
            .mean()  // 计算平均值
            .compute();  // 执行计算
        return aggregation?.mean!;  // 返回计算得到的平均值
    }
```

### 求导

在上述示例的基础上，您还可以通过使用以下计算函数来获取同一机器上温度的平均更改：

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
    @Function()
    public async getAverageTemperature(machine: MachineRoot): Promise<Double | undefined> {
        // 获取指定机器的平均温度
        const aggregation = await machine.temperatureId?.derivative()
            .aggregate() // 进行聚合操作
            .overEntireRange() // 在整个范围内
            .mean() // 计算平均值
            .compute(); // 执行计算
        return aggregation?.mean; // 返回计算的平均值
    }
```

### 指定时间范围

您可以对时间序列应用导数之外的其他变换。以下是如何将时间戳参数应用为时间序列范围的示例。

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
    @Function()
    public async getAverageTemperatureOverRange(
        machine: MachineRoot,
        start: Timestamp,
        end: Timestamp): Promise<Double | undefined>
    {
        // 获取指定时间范围内的平均温度
        const latest = await machine.temperatureId?.timeRange({min: start, max: end})
            .aggregate() // 聚合数据
            .overEntireRange() // 在整个范围内
            .mean() // 计算平均值
            .compute(); // 计算结果
        return latest?.mean; // 返回平均温度
    }
```
