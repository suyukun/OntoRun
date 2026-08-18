来源: https://palantir.com/docs/zh/foundry/workshop/widgets-chart/

# Chart XY

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Chart XY

如果 Chart XY 微件无法实现所需的功能或格式，请考虑使用Vega Chart微件。

Chart XY微件用于将 Objects 可视化为交互式图表。模块搭建者配置 Chart XY 微件可以：

- 显示柱状图、折线图和散点图数据。
- 选择可视化的属性，这些属性如何聚合（例如，计数、总和、平均值），以及这些属性是否/如何分段。
- 使用 Function 支持的层显示更高级的聚合类型和图表。
- 为图表标题、坐标轴、图例和数字格式设置显示选项。
- 启用图表上的选择和下游筛选。
下面的截图显示了三个配置的 Chart XY 微件显示Flight Alerts数据的示例：

## 配置选项

在下图中，蓝色箭头左侧可以看到一个新添加（但尚未配置）的 Chart XY 微件及其初始配置面板。蓝色箭头右侧可以看到一个单独的Layer配置面板，其中已填充Flight Alerts的支持对象集：

### 图层配置选项

配置图层是向 Chart XY 微件添加数据的必要步骤。图层的配置选项如下：

- 标题为配置面板中的当前图层设置标题。注意：该标题对模块用户不可见，但旨在帮助搭建者组织和管理使用多个图层的复杂Chart XY配置。
- 为配置面板中的当前图层设置标题。
- 注意：该标题对模块用户不可见，但旨在帮助搭建者组织和管理使用多个图层的复杂Chart XY配置。
- 数据输入控制该图层的输入数据。对象集选项允许使用 Workshop 对象集变量作为输入。Function 聚合选项允许使用返回 2D 聚合或 3D 聚合的函数作为输入。注意：Function 聚合层将仅具有以下图层配置选项的子集。时间序列集选项允许使用 Workshop 时间序列集变量作为输入。有关时间序列集变量的更多信息，请参见变量。这会配置一个时间序列图表，在 X 轴上显示时间范围，在 Y 轴上显示变量的时间序列值。
- 控制该图层的输入数据。
- 对象集选项允许使用 Workshop 对象集变量作为输入。
- Function 聚合选项允许使用返回 2D 聚合或 3D 聚合的函数作为输入。注意：Function 聚合层将仅具有以下图层配置选项的子集。
- 注意：Function 聚合层将仅具有以下图层配置选项的子集。
- 时间序列集选项允许使用 Workshop 时间序列集变量作为输入。有关时间序列集变量的更多信息，请参见变量。这会配置一个时间序列图表，在 X 轴上显示时间范围，在 Y 轴上显示变量的时间序列值。
- 图层类型选择显示的图表类型。目前的选项包括柱状图、折线图和散点图。如果数据输入是时间序列集，则仅支持折线图选项。有关时间序列集变量的更多信息，请参见变量。
- 选择显示的图表类型。目前的选项包括柱状图、折线图和散点图。如果数据输入是时间序列集，则仅支持折线图选项。有关时间序列集变量的更多信息，请参见变量。
- 区域选项为折线图提供三种可视化选项："Line"（显示简单的折线图），"Area"（绘制折线图并在每条折线下方阴影），和"Stacked"（类似于 "Area" 选项，但将分段图表值堆叠在一起）。区域选项仅适用于折线图。
- 为折线图提供三种可视化选项："Line"（显示简单的折线图），"Area"（绘制折线图并在每条折线下方阴影），和"Stacked"（类似于 "Area" 选项，但将分段图表值堆叠在一起）。
- "Line"（显示简单的折线图），
- "Area"（绘制折线图并在每条折线下方阴影），和
- "Stacked"（类似于 "Area" 选项，但将分段图表值堆叠在一起）。
- 区域选项仅适用于折线图。
- 标签切换图表上值标签的显示。此选项当前适用于柱状图和折线图。
- 切换图表上值标签的显示。
- 此选项当前适用于柱状图和折线图。
- X 轴属性确定在图表上绘制的属性类型。
- 确定在图表上绘制的属性类型。
- 柱状/折线/图表系列使用单个/多个系列允许为选定的X 轴属性绘制一个或多个图表系列。例如，如果选择 "Alert Type" 作为X 轴属性，多个系列将允许绘制每个 "Alert Type" 的计数以及每个 "Alert Type" 的 "# of Hours Delayed" 总和。系列聚合确定用于在图表上绘制每个值的聚合方法。默认情况下，设置为 "计数"。其他选项包括："平均值"、"最小值"、"最大值"、"总和" 和 "大致唯一计数"。按分段非必填。启用每个绘制值按次要属性类型分段。例如，如果选择 "Alert Type" 作为X 轴属性，然后选择 "Aircraft Type" 作为柱状图上的按分段选项，每个柱状图将显示按每个 "Aircraft Type" 分段的每个 "Alert Type" 的对象计数。显示空值/缺失值仅适用于折线图。控制在折线图上如何显示空值或缺失值。选项包括 "Gap"（将缺失值显示为绘制线中的空缺），"Ignored"（忽略缺失值，并将绘制线连接前一个和下一个可用值），或 "Zeroes"（将缺失值视为等于值 "0"）。显示覆盖非必填。覆盖当前系列的图例显示名称。对于分段图表，覆盖单个分段的图例显示名称。分段覆盖仅适用于柱状图。修改每个柱状图值的显示方式。选项包括："Stacked"、"Percentage" 和 "Grouped"。
- 使用单个/多个系列允许为选定的X 轴属性绘制一个或多个图表系列。例如，如果选择 "Alert Type" 作为X 轴属性，多个系列将允许绘制每个 "Alert Type" 的计数以及每个 "Alert Type" 的 "# of Hours Delayed" 总和。
- 允许为选定的X 轴属性绘制一个或多个图表系列。
- 例如，如果选择 "Alert Type" 作为X 轴属性，多个系列将允许绘制每个 "Alert Type" 的计数以及每个 "Alert Type" 的 "# of Hours Delayed" 总和。
- 系列聚合确定用于在图表上绘制每个值的聚合方法。默认情况下，设置为 "计数"。其他选项包括："平均值"、"最小值"、"最大值"、"总和" 和 "大致唯一计数"。
- 确定用于在图表上绘制每个值的聚合方法。
- 默认情况下，设置为 "计数"。
- 其他选项包括："平均值"、"最小值"、"最大值"、"总和" 和 "大致唯一计数"。
- 按分段非必填。启用每个绘制值按次要属性类型分段。例如，如果选择 "Alert Type" 作为X 轴属性，然后选择 "Aircraft Type" 作为柱状图上的按分段选项，每个柱状图将显示按每个 "Aircraft Type" 分段的每个 "Alert Type" 的对象计数。
- 非必填。
- 启用每个绘制值按次要属性类型分段。
- 例如，如果选择 "Alert Type" 作为X 轴属性，然后选择 "Aircraft Type" 作为柱状图上的按分段选项，每个柱状图将显示按每个 "Aircraft Type" 分段的每个 "Alert Type" 的对象计数。
- 显示空值/缺失值仅适用于折线图。控制在折线图上如何显示空值或缺失值。选项包括 "Gap"（将缺失值显示为绘制线中的空缺），"Ignored"（忽略缺失值，并将绘制线连接前一个和下一个可用值），或 "Zeroes"（将缺失值视为等于值 "0"）。
- 仅适用于折线图。
- 控制在折线图上如何显示空值或缺失值。
- 选项包括 "Gap"（将缺失值显示为绘制线中的空缺），"Ignored"（忽略缺失值，并将绘制线连接前一个和下一个可用值），或 "Zeroes"（将缺失值视为等于值 "0"）。
- 显示覆盖非必填。覆盖当前系列的图例显示名称。对于分段图表，覆盖单个分段的图例显示名称。
- 非必填。
- 覆盖当前系列的图例显示名称。
- 对于分段图表，覆盖单个分段的图例显示名称。
- 分段覆盖仅适用于柱状图。修改每个柱状图值的显示方式。选项包括："Stacked"、"Percentage" 和 "Grouped"。
- 仅适用于柱状图。
- 修改每个柱状图值的显示方式。
- 选项包括："Stacked"、"Percentage" 和 "Grouped"。
- 选择作为筛选非必填，且仅适用于对象集支持的图表。设置时，允许通过输出对象集筛选变量对该图层进行选择和下游微件筛选。
- 非必填，且仅适用于对象集支持的图表。
- 设置时，允许通过输出对象集筛选变量对该图层进行选择和下游微件筛选。
- 删除图层允许删除当前图层。
- 允许删除当前图层。
- 场景与场景比较启用此切换以选择要比较数据的场景数组变量。这将使用图表的 "按分段" 轴将表中的数据与数组中的场景值进行比较。如果启用此选项，则无法按其他属性分段。有关场景的更多信息，请参见场景文档。
- 与场景比较启用此切换以选择要比较数据的场景数组变量。这将使用图表的 "按分段" 轴将表中的数据与数组中的场景值进行比较。如果启用此选项，则无法按其他属性分段。
- 启用此切换以选择要比较数据的场景数组变量。这将使用图表的 "按分段" 轴将表中的数据与数组中的场景值进行比较。
- 如果启用此选项，则无法按其他属性分段。
- 有关场景的更多信息，请参见场景文档。
### 图表范围的配置选项

除了上述图层的配置选项外，主要的 Chart XY 配置面板还包含许多图表范围的配置选项：

- 分类轴显示标题启用后，显示分类轴的标题，并允许覆盖该标题。默认情况下，该标题将显示图表系列中绘制的属性类型。启用数字格式启用后，为分类轴键中显示的数字值提供配置选项。配置选项包括数字分组，显示的最小/最大小数位数，科学记数法等。排序依据控制每个图表值的显示排序逻辑。默认情况下，按字母顺序从 A 到 Z 对分类键进行排序。
- 显示标题启用后，显示分类轴的标题，并允许覆盖该标题。默认情况下，该标题将显示图表系列中绘制的属性类型。
- 启用后，显示分类轴的标题，并允许覆盖该标题。
- 默认情况下，该标题将显示图表系列中绘制的属性类型。
- 启用数字格式启用后，为分类轴键中显示的数字值提供配置选项。配置选项包括数字分组，显示的最小/最大小数位数，科学记数法等。
- 启用后，为分类轴键中显示的数字值提供配置选项。
- 配置选项包括数字分组，显示的最小/最大小数位数，科学记数法等。
- 排序依据控制每个图表值的显示排序逻辑。默认情况下，按字母顺序从 A 到 Z 对分类键进行排序。
- 控制每个图表值的显示排序逻辑。
- 默认情况下，按字母顺序从 A 到 Z 对分类键进行排序。
- 值轴使用多个值轴仅在配置了多个图表系列时可用，并允许按系列配置值轴。当图表上的不同系列具有大不相同的值范围时，这可能会很有帮助。显示标题启用后，显示值轴的标题，并允许覆盖该标题。默认情况下，该标题将显示图表系列中使用的聚合类型。启用数字格式启用后，为值轴中显示的数字值提供配置选项。配置选项包括数字分组，显示的最小/最大小数位数，科学记数法等。比例类型允许将值轴比例设置为 "线性"（默认）或 "对数"。最小边界默认情况下，根据显示的图表值设置为 "自动计算最小边界"。如果切换为 "最小值"，模块搭建者可以控制值轴上的最小值显示。最大边界默认情况下，根据显示的图表值设置为 "自动计算最大边界"。如果切换为 "最大值"，模块搭建者可以控制值轴上的最大值显示。
- 使用多个值轴仅在配置了多个图表系列时可用，并允许按系列配置值轴。当图表上的不同系列具有大不相同的值范围时，这可能会很有帮助。
- 仅在配置了多个图表系列时可用，并允许按系列配置值轴。当图表上的不同系列具有大不相同的值范围时，这可能会很有帮助。
- 显示标题启用后，显示值轴的标题，并允许覆盖该标题。默认情况下，该标题将显示图表系列中使用的聚合类型。
- 启用后，显示值轴的标题，并允许覆盖该标题。
- 默认情况下，该标题将显示图表系列中使用的聚合类型。
- 启用数字格式启用后，为值轴中显示的数字值提供配置选项。配置选项包括数字分组，显示的最小/最大小数位数，科学记数法等。
- 启用后，为值轴中显示的数字值提供配置选项。
- 配置选项包括数字分组，显示的最小/最大小数位数，科学记数法等。
- 比例类型允许将值轴比例设置为 "线性"（默认）或 "对数"。
- 允许将值轴比例设置为 "线性"（默认）或 "对数"。
- 最小边界默认情况下，根据显示的图表值设置为 "自动计算最小边界"。如果切换为 "最小值"，模块搭建者可以控制值轴上的最小值显示。
- 默认情况下，根据显示的图表值设置为 "自动计算最小边界"。
- 如果切换为 "最小值"，模块搭建者可以控制值轴上的最小值显示。
- 最大边界默认情况下，根据显示的图表值设置为 "自动计算最大边界"。如果切换为 "最大值"，模块搭建者可以控制值轴上的最大值显示。
- 默认情况下，根据显示的图表值设置为 "自动计算最大边界"。
- 如果切换为 "最大值"，模块搭建者可以控制值轴上的最大值显示。
- 图例显示图例切换图表系列标题和系列颜色的图例显示。定位选项启用 "显示图例" 时，控制图例在图表中的定位。
- 显示图例切换图表系列标题和系列颜色的图例显示。
- 切换图表系列标题和系列颜色的图例显示。
- 定位选项启用 "显示图例" 时，控制图例在图表中的定位。
- 启用 "显示图例" 时，控制图例在图表中的定位。
- 柱状图方向水平/垂直切换控制图表的方向。对于柱状图，默认是 "水平"。对于折线图或散点图，仅允许 "垂直"。
- 水平/垂直切换控制图表的方向。对于柱状图，默认是 "水平"。对于折线图或散点图，仅允许 "垂直"。
- 控制图表的方向。
- 对于柱状图，默认是 "水平"。
- 对于折线图或散点图，仅允许 "垂直"。
## Function 聚合（Function 支持的图层）

配置 Function 支持的图层需要编写一个函数，该函数返回TwoDimensionalAggregation或ThreeDimensionalAggregation。

下面是一个完整示例，该示例返回TwoDimensionalAggregation以便将一个时间序列除以另一个时间序列进行图表展示：

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
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
import { Function, TwoDimensionalAggregation, ThreeDimensionalAggregation,
         IRange, Timestamp } from "@foundry/functions-api";
import { ObjectSet, MyObjectType } from "@foundry/ontology-api"

// 定义一个类，用于时间序列的聚合操作
export class TimeseriesAggregations {

    @Function()
    // 定义一个异步函数，计算对象集合中的每个对象在总和中的百分比
    public async percentOfTotal(objects:ObjectSet<MyObjectType>):
                                Promise<TwoDimensionalAggregation<IRange<Timestamp>>> {
        // 按天对对象进行分组，并计算每组的值之和，得到分子
        const numerators = await objects.groupBy(e => e.date.byDays())
                                        .sum(e => e.value);
        // 按天对对象进行分组，并计算每组的总和，得到分母
        const denominators = await objects.groupBy(e => e.date.byDays())
                                          .sum(e => e.total);

        // 调用divide方法计算百分比
        return this.divide(numerators, denominators);
    }

    // 私有方法，用于计算百分比
    private divide(numerators:TwoDimensionalAggregation<IRange<Timestamp>>,
                              denominators: TwoDimensionalAggregation<IRange<Timestamp>>):
                              TwoDimensionalAggregation<IRange<Timestamp>> {

        // 计算每个时间段的百分比
        const percentage = numerators.buckets.map((bucket, i) => {
           const numerator = bucket.value;
           const denominator = denominators.buckets[i].value;
            if (denominator == 0) { // 如果分母为0，避免除以0错误
                return { key: bucket.key, value: 0 };
            }
            return { key: bucket.key, value: numerator / denominator }
        });

        return { buckets: percentage };
    }
}
```

以下是一个完整的示例，它返回一个ThreeDimensionalAggregation，将为segmentBy()返回的每个值绘制一个单独的系列：

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
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
import { Function, TwoDimensionalAggregation, ThreeDimensionalAggregation,
         IRange, Timestamp } from "@foundry/functions-api";
import { ObjectSet, MyObjectType } from "@foundry/ontology-api"

export class TimeseriesAggregations {

    @Function()
    public async percentOfTotalSegmented(objects:ObjectSet<MyObjectType>):
                                         Promise<ThreeDimensionalAggregation<IRange<Timestamp>, string>> {
        // 计算分子：对对象按日期分组，再按groupId进行细分，最后计算value的和
        const numerators = await objects.groupBy(e => e.date.byDays())
                                        .segmentBy(e => e.groupId.topValues())
                                        .sum(e => e.value);
        // 计算分母：与分子类似，只不过这里计算的是total的和
        const denominators = await objects.groupBy(e => e.date.byDays())
                                          .segmentBy(e => e.groupId.topValues())
                                          .sum(e => e.total);

        // 调用divideThreeDimensional方法计算百分比
        return this.divideThreeDimensional(numerators, denominators);
    }

    private divideThreeDimensional(numerators:ThreeDimensionalAggregation<IRange<Timestamp>, string>,
                             denominators: ThreeDimensionalAggregation<IRange<Timestamp>, string>):
                             ThreeDimensionalAggregation<IRange<Timestamp>, string> {

        var percentage = numerators.buckets; // 拷贝分子数据
        for (let i = 0; i < numerators.buckets.length; i++) {
            for (let j = 0; j < numerators.buckets[i].value.length; j++) {
                // 计算每个分段的百分比：分子/分母
                percentage[i].value[j].value = numerators.buckets[i].value[j].value /
                                               denominators.buckets[i].value[j].value;
            }
        }

        // 返回计算出的百分比结果
        return { buckets: percentage };
    }
}
```

有关更多示例，请参阅对象集聚合和创建自定义聚合的函数文档。
