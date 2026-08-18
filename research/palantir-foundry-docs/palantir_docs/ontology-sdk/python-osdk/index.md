来源: https://palantir.com/docs/zh/foundry/ontology-sdk/python-osdk/

# Python Ontology SDK

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Python Ontology SDK

此页面提供基于示例餐馆Object的Python OSDK通用文档。您可以在开发者控制台中生成特定于您的Ontology的文档。

| 属性 | API 名称 | 类型 |
| --- | --- | --- |
| 餐馆 ID (主键) | restaurantId | 字符串 |
| 餐馆名称 (标题) | restaurantName | 字符串 |
| 地址 | address | 字符串 |
| 电子邮件 | eMail | 字符串 |
| 评论数 | numberOfReviews | Integer |
| 电话号码 | phoneNumber | 字符串 |
| 评论摘要 | reviewSummary | 字符串 |

## 加载单个餐馆

参数：

- primaryKeystring: 您想要获取的示例餐馆的主键
示例查询：

```
Copied!1
2
# 获取名为 ExampleRestaurant 的对象，其主键为 primaryKey
result = client.ontology.objects.ExampleRestaurant.get("primaryKey")
```

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
{
    "__rid": "ri.phonograph2-objects.main.object.00000000-0000-0000-0000-000000000000",  // 资源ID，唯一标识数据对象
    "__primaryKey": "Restaurant Id",  // 主键标识字段为餐馆ID
    "eMail": "E Mail",  // 餐馆的电子邮件地址
    "restaurantId": "Restaurant Id",  // 餐馆的ID
    "address": "Address",  // 餐馆的地址
    "reviewSummary": "Review Summary",  // 评论摘要
    "phoneNumber": "Phone Number",  // 餐馆的电话号码
    "numberOfReviews": 123,  // 评论数量
    "restaurantName": "Restaurant Name",  // 餐馆的名称
}
```

## 加载示例餐厅的页面

加载请求页面大小的对象列表，如果存在，则在给定的页面词元之后加载。

请注意，此端点利用了用于对象类型的底层对象同步技术。如果示例餐厅由 Object Storage v2 支持，则没有请求限制。如果由 Phonograph 支持，则限制为 10,000 个结果——当请求超过 10,000 个示例餐厅时，将抛出ObjectsExceededLimit出错。

参数：

- pageSizeinteger（非必填）：请求页面的大小，最大为 10,000。如果未提供，将加载最多 10,000 个示例餐厅。初始页面的pageSize用于后续页面。
- pageToken字符串（非必填）：如果提供，将请求一个大小小于或等于首次请求页面的pageSize的页面。
示例查询：

```
Copied!1
2
3
4
5
6
result = client.ontology.objects.ExampleRestaurant.page(page_size=30, page_token=None)
# 获取第一页的数据，page_size=30 表示每页包含30个对象，page_token=None 表示从第一页开始。
page_token = result.next_page_token
# 获取下一页的令牌，可以用于请求下一页的数据。
data = result.data
# 获取当前页的数据。
```

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
{
    "nextPageToken": "v1.000000000000000000000000000000000000000000000000000000000000000000000000",
    // 用于标识下一页的数据令牌

    "data": [
        {
            "__rid": "ri.phonograph2-objects.main.object.00000000-0000-0000-0000-000000000000",
            // 资源ID，用于唯一标识对象

            "__primaryKey": "Restaurant Id",
            // 主键字段，标识餐厅的唯一ID

            "eMail": "E Mail",
            // 餐厅的电子邮件地址

            "restaurantId": "Restaurant Id",
            // 餐厅的ID，可能与主键相同

            "address": "Address",
            // 餐厅的地址

            "reviewSummary": "Review Summary",
            // 餐厅的评论总结

            "phoneNumber": "Phone Number",
            // 餐厅的联系电话

            "numberOfReviews": 123,
            // 餐厅的评论数量

            "restaurantName": "Restaurant Name"
            // 餐厅的名称
        },
        // ... Rest of page
        // 其余页面的数据
    ]
}
```

## 加载所有示例餐厅

加载所有示例餐厅。根据语言的不同，结果可能是包含所有行的列表或用于遍历所有行的迭代器。

请注意，此端点利用了用于对象类型的底层对象同步技术。如果示例餐厅由对象存储V2支持，则没有请求限制。如果由Phonograph支持，则有10,000个结果的限制——当请求超过10,000个示例餐厅时，将抛出一个ObjectsExceededLimit出错。

示例查询：

```
Copied!1
2
3
objects_iterator = client.ontology.objects.ExampleRestaurant.iterate()
# 将对象迭代器转换为列表，获取所有 ExampleRestaurant 对象的实例
objects = list(objects_iterator)
```

示例API响应：

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
{
    "data": [
        {
            "__rid": "ri.phonograph2-objects.main.object.00000000-0000-0000-0000-000000000000", // 记录唯一标识符
            "__primaryKey": "Restaurant Id", // 主键，餐厅ID
            "eMail": "E Mail", // 电子邮件
            "restaurantId": "Restaurant Id", // 餐厅ID
            "address": "Address", // 地址
            "reviewSummary": "Review Summary", // 评论摘要
            "phoneNumber": "Phone Number", // 电话号码
            "numberOfReviews": 123, // 评论数量
            "restaurantName": "Restaurant Name", // 餐厅名称
        },
        // ... Rest of data
    ]
}
```

## 加载排序结果

通过为特定属性指定排序方向来加载示例餐厅的有序列表。通过API调用时，排序标准通过fields数组指定。通过SDK调用时，您可以将多个orderBy调用链接在一起。字符串的排序顺序是区分大小写的，这意味着数字会在大写字母之前，大写字母会在小写字母之前。例如，Cat 会在 bat 之前。

参数：

- field字符串：您希望排序的属性。使用SDK时，通过sortBy接口为您提供。
- directionasc|desc：您希望的排序方向，可以是升序或降序。使用SDK时，通过sortBy接口上的asc()和desc()函数提供。
示例查询：

```
Copied!1
2
3
4
from ontology_sdk.ontology.objects import ExampleRestaurant

# 查询非空的餐馆名称，并按餐馆名称升序排序
client.ontology.objects.ExampleRestaurant.where(~ExampleRestaurant.object_type.restaurant_name.is_null()).order_by(ExampleRestaurant.object_type.restaurant_name.asc()).iterate()
```

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
{
    "nextPageToken": "v1.000000000000000000000000000000000000000000000000000000000000000000000000", // 用于获取下一页数据的令牌
    "data": [
        {
            "__rid": "ri.phonograph2-objects.main.object.00000000-0000-0000-0000-000000000000", // 资源标识符
            "__primaryKey": "Object A", // 主键，标识对象的唯一性
            "restaurantName": "A", // 餐馆名称
            // ...其余属性
        },
        {
            "__rid": "ri.phonograph2-objects.main.object.00000000-0000-0000-0000-000000000000", // 资源标识符
            "__primaryKey": "Object B", // 主键，标识对象的唯一性
            "restaurantName": "B", // 餐馆名称
            // ...其余属性
        },
        // ...页面的其他数据
    ]
}
```

## 筛选

您可以执行的筛选类型取决于给定对象类型的属性类型。这些筛选也可以通过布尔表达式组合在一起以构建更复杂的筛选。

请注意，此端点利用了用于对象类型的底层对象同步技术。如果 Example Restaurant 由 Object Storage v2 支持，则没有请求限制。如果由 Phonograph 支持，则结果限制为 10,000 个——当请求超过 10,000 个 Example Restaurant 时，将抛出一个ObjectsExceededLimit出错。

参数：

- whereSearchQuery(非必填): 筛选特定属性。可能的操作取决于属性的类型。
- orderByOrderByQuery(非必填): 基于特定属性对结果排序。如果使用 SDK，可以将.where调用与orderBy调用链接以实现相同的结果。
- pageSizeinteger(非必填): 请求的页面大小最多为 10,000。如果未提供，将加载最多 10,000 个 Example Restaurant。初始页面的pageSize将用于后续页面。如果使用 SDK，将.where调用与.page方法链接。
- pageToken字符串(非必填): 如果提供，将请求一个大小小于或等于首次请求页面的pageSize的页面。如果使用 SDK，将.where调用与.page方法链接。
示例查询：

```
Copied!1
2
3
4
from ontology_sdk.ontology.objects import ExampleRestaurant

# 使用 where 方法筛选出 restaurant_name 为空的 ExampleRestaurant 对象，并进行迭代
page = client.ontology.objects.ExampleRestaurant.where(ExampleRestaurant.object_type.restaurant_name.is_null()).iterate()
```

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
{
    "nextPageToken": "v1.000000000000000000000000000000000000000000000000000000000000000000000000",
    "data": [
        {
            "__rid": "ri.phonograph2-objects.main.object.00000000-0000-0000-0000-000000000000",
            "__primaryKey": "Restaurant Id", // 餐厅ID
            "restaurantName": null,
            // ... 其他属性
        },
        // ... 其他页面内容
    ]
}
```

### 搜索筛选的类型 (SearchQuery)

#### 起始

仅适用于字符串属性。搜索餐厅名称以给定字符串开头的示例餐厅（不区分大小写）。

参数：

- 字段string：要使用的属性名称（例如，restaurantName）。
- 值string：用于与餐厅名称进行前缀匹配的值。例如，“foo”将匹配“foobar”但不匹配“barfoo”。
示例查询：

```
Copied!1
2
3
4
from ontology_sdk.ontology.objects import ExampleRestaurant

# 查找餐馆名称以'foo'开头的ExampleRestaurant对象集
ExampleRestaurantObjectSet = client.ontology.objects.ExampleRestaurant.where(ExampleRestaurant.object_type.restaurant_name.starts_with(['foo']))
```

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
{
    "nextPageToken": "v1.000000000000000000000000000000000000000000000000000000000000000000000000",
    "data": [{
        "__rid": "ri.phonograph2-objects.main.object.00000000-0000-0000-0000-000000000000",
        "__primaryKey": "Restaurant Id", // 餐馆ID
        "restaurantName": "foobar", // 餐馆名称
        // ... 其他属性
    }]
}
```

#### 包含任意词语

仅适用于字符串属性。返回示例餐馆，其中restaurantName包含提供的值中以空格分隔的任何词语（不区分大小写，顺序不限）。

参数：

- field字符串：要使用的属性名称（例如restaurantName）。
- value字符串：要匹配的空格分隔词组。例如，“foo bar”将匹配“bar baz”，但不匹配“baz qux”。
- fuzzyboolean：允许在搜索查询中进行近似匹配。
示例查询：

```
Copied!1
2
3
4
5
6
from ontology_sdk.ontology.objects import ExampleRestaurant

# 创建一个查询集合，过滤条件是餐厅名称包含任意一个指定的术语，例如 'foo bar'
ExampleRestaurantObjectSet = client.ontology.objects.ExampleRestaurant.where(
    ExampleRestaurant.object_type.restaurant_name.contains_any_term(['foo bar'])
)
```

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
{
    "nextPageToken": "v1.000000000000000000000000000000000000000000000000000000000000000000000000",
    "data": [
        {
            "__rid": "ri.phonograph2-objects.main.object.00000000-0000-0000-0000-000000000000",
            "__primaryKey": "Restaurant Id",  // 餐厅ID
            "restaurantName": "foo bar baz",  // 餐厅名称
            // ... 其他属性
        },
        {
            "__rid": "ri.phonograph2-objects.main.object.00000000-0000-0000-0000-000000000001",
            "restaurantName": "bar baz",  // 餐厅名称
            // ... 其他属性
        },
    ]
}
```

#### 包含所有术语

仅适用于字符串属性。返回示例餐厅，其中restaurantName包含提供的值中以空格分隔的所有单词（不区分大小写），顺序不限。

参数：

- 字段string: 要使用的属性名称（例如，restaurantName）。
- 值string: 要匹配的以空格分隔的单词集。例如，“foo bar”将匹配“hello foo baz bar”，但不匹配“foo qux”。
- 模糊boolean: 允许在搜索查询中进行近似匹配。
示例查询：

```
Copied!1
2
3
4
5
6
7
from ontology_sdk.ontology.objects import ExampleRestaurant

# 使用 ExampleRestaurant 类从本体中获取餐馆对象集合
ExampleRestaurantObjectSet = client.ontology.objects.ExampleRestaurant.where(
    # 查询餐馆名称包含所有指定术语的餐馆对象，这里术语为 'foo' 和 'bar'
    ExampleRestaurant.object_type.restaurant_name.contains_all_terms(['foo bar'])
)
```

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
{
    "nextPageToken": "v1.000000000000000000000000000000000000000000000000000000000000000000000000",
    "data": [{
        "__rid": "ri.phonograph2-objects.main.object.00000000-0000-0000-0000-000000000000",
        "__primaryKey": "Restaurant Id", // 餐厅ID
        "restaurantName": "hello foo baz bar", // 餐厅名称
        // ... Rest of properties
    }]
}
```

#### 包含所有术语按顺序

仅适用于字符串属性。返回示例餐馆，其中restaurantName包含所提供顺序中的所有术语（不区分大小写），但它们必须彼此相邻。

参数：

- 字段string：要使用的属性名称（例如，restaurantName）。
- 值string：用空格分隔的单词集合以进行匹配。例如，“foo bar”将匹配“hello foo bar baz”，但不匹配“bar foo qux”。
- 模糊boolean：允许在搜索查询中进行近似匹配
示例查询：

```
Copied!1
2
3
4
5
from ontology_sdk.ontology.objects import ExampleRestaurant

# 使用ExampleRestaurant对象集来查询符合条件的餐馆
# 这里的条件是餐馆名称包含所有按顺序的术语'foo bar'
ExampleRestaurantObjectSet = client.ontology.objects.ExampleRestaurant.where(ExampleRestaurant.object_type.restaurant_name.contains_all_terms_in_order(['foo bar']))
```

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
{
    "nextPageToken": "v1.000000000000000000000000000000000000000000000000000000000000000000000000",
    "data": [{
        "__rid": "ri.phonograph2-objects.main.object.00000000-0000-0000-0000-000000000000",
        "__primaryKey": "Restaurant Id", // 主键，表示餐厅的唯一标识符
        "restaurantName": "foo bar baz", // 餐厅名称
        // ... Rest of properties // 其他属性
    }]
}
```

#### 范围比较

仅适用于数值、字符串和日期时间属性。返回示例餐馆，其中ExampleRestaurant.object_type.restaurantName小于某个值。

参数:

- 字段字符串: 要使用的属性名称 (例如 restaurantName)。
- 值字符串: 要与餐馆名称比较的值
比较类型:

- 小于<
- 大于>
- 小于或等于<=
- 大于或等于>=
示例查询:

```
Copied!1
2
3
4
5
6
from ontology_sdk.ontology.objects import ExampleRestaurant

# 使用客户端的ontology对象来筛选餐馆
ExampleRestaurantObjectSet = client.ontology.objects.ExampleRestaurant.where(
    ExampleRestaurant.object_type.restaurant_name < "Restaurant Name"  # 筛选餐馆名称小于"Restaurant Name"的记录
)
```

#### 等于

仅适用于布尔、日期时间、数值和字符串属性。搜索餐厅名称等于给定值的示例餐厅。

参数：

- fieldstring: 要使用的属性名称（例如，restaurantName）。
- valuestring: 用于与餐厅名称进行等值检查的值。
示例查询：

```
Copied!1
2
3
4
from ontology_sdk.ontology.objects import ExampleRestaurant

# 查询名为 "Restaurant Name" 的餐馆对象集
ExampleRestaurantObjectSet = client.ontology.objects.ExampleRestaurant.where(ExampleRestaurant.object_type.restaurant_name == "Restaurant Name")
```

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
{
    "nextPageToken": "v1.000000000000000000000000000000000000000000000000000000000000000000000000",
    "data": [{
        "__rid": "ri.phonograph2-objects.main.object.00000000-0000-0000-0000-000000000000",
        "__primaryKey": "Restaurant Id", // 餐厅的唯一标识符
        "restaurantName": "Restaurant Name", // 餐厅名称
        // ... 其他属性
    }]
}
```

#### 空值检查

仅适用于数组、布尔值、日期时间、数值和字符串属性。根据restaurantName是否存在搜索示例餐厅。

参数：

- fieldstring：要使用的属性名称（例如restaurantName）。
- valueboolean：餐厅名称是否存在。注意，对于TypeScript SDK，您需要使用非筛选来检查字段是否非空。
示例查询：

```
Copied!1
2
3
4
5
from ontology_sdk.ontology.objects import ExampleRestaurant

# 使用 ExampleRestaurant 类来获取餐厅对象集合
# 过滤条件是餐厅名称为空的对象
ExampleRestaurantObjectSet = client.ontology.objects.ExampleRestaurant.where(ExampleRestaurant.object_type.restaurant_name.is_null())
```

#### 非筛选

返回不满足查询条件的示例餐馆。可以进一步与其他布尔筛选操作组合。

参数：

- valueSearchQuery：要反转的搜索查询。
示例查询：

```
Copied!1
2
3
4
from ontology_sdk.ontology.objects import ExampleRestaurant

# 使用 `where` 方法筛选出所有 `restaurantId` 不为空的 ExampleRestaurant 对象
ExampleRestaurantObjectSet = client.ontology.objects.ExampleRestaurant.where(~ExampleRestaurant.object_type.restaurantId.is_null())
```

#### 并且筛选

返回满足所有查询条件的示例餐厅。这可以进一步与其他布尔筛选操作结合。

参数：

- 值SearchQuery[]：要合并在一起的搜索查询集。
示例查询：

```
Copied!1
2
3
4
5
6
from ontology_sdk.ontology.objects import ExampleRestaurant

# 创建一个ExampleRestaurant对象集，过滤条件为restaurantId不为空且等于指定的<primaryKey>
ExampleRestaurantObjectSet = client.ontology.objects.ExampleRestaurant.where(
    ~ExampleRestaurant.object_type.restaurantId.is_null() & (ExampleRestaurant.object_type.restaurantId == '<primaryKey>')
)
```

#### 或筛选

返回满足任意指定查询条件的示例餐厅。可以进一步与其他布尔筛选操作组合。

参数：

- valueSearchQuery[]: 要一起进行或操作的搜索查询集合。
示例查询：

```
Copied!1
2
3
4
5
6
7
from ontology_sdk.ontology.objects import ExampleRestaurant

# 使用 ExampleRestaurant 类来创建一个对象集
# 过滤条件是 restaurantId 为空或者等于 '<primaryKey>'
ExampleRestaurantObjectSet = client.ontology.objects.ExampleRestaurant.where(
    ExampleRestaurant.object_type.restaurantId.is_null() | (ExampleRestaurant.object_type.restaurantId == '<primaryKey>')
)
```

### 聚合

对示例餐厅进行聚合。

参数：

- aggregationAggregation[](非必填): 要执行的聚合函数集。使用SDK，可以通过.where将聚合计算与进一步的搜索链接在一起。
- groupByGroupBy[](非必填): 为聚合结果创建的一组分组
- whereSearchQuery(非必填): 对特定属性进行筛选。可能的操作取决于属性的类型。
示例查询：

```
Copied!1
2
3
4
5
6
7
8
from ontology_sdk.ontology.objects import ExampleRestaurant

# 计算ExampleRestaurant中restaurant_name不为null的餐厅数量
numExampleRestaurant = client.ontology.objects.ExampleRestaurant
    .where(~ExampleRestaurant.object_type.restaurant_name).is_null())  # 过滤掉restaurant_name为null的记录
    .group_by(ExampleRestaurant.object_type.restaurant_name).exact())  # 根据restaurant_name分组
    .count()  # 统计每个组的记录数
    .compute()  # 计算结果
```

```
// 这是一个JSON格式的数据，包含了餐厅的统计信息
{
    excludedItems: 0, // 被排除的项数
    data: [{ // 数据数组
        group: {
            "restaurantName": "Restaurant Name" // 餐厅名称
        },
        metrics: [
            {
                name: "count", // 统计项名称
                value: 100 // 统计值
            }
        ]
    }]
}
```

### 聚合类型（Aggregation）

#### 近似不同

计算restaurantName的近似不同值的数量。

参数：

- field字符串: 要使用的属性名称（例如restaurantName）。
- name字符串（非必填）: 计算计数的别名。默认情况下，这是 "distinctCount"
示例查询：

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
from ontology_sdk.ontology.objects import ExampleRestaurant

# 使用 approximate_distinct 方法计算 ExampleRestaurant 的 restaurant_name 字段的近似不同值的数量
numExampleRestaurant = client.ontology.objects.ExampleRestaurant
    .approximate_distinct(ExampleRestaurant.object_type.restaurant_name)
    .compute()

# 以下代码与上面的代码等效，但使用 metric_name 作为名称，而不是默认的 "distinctCount"
numExampleRestaurant = client.ontology.objects.ExampleRestaurant
    .aggregate(
        {"metric_name": ExampleRestaurant.object_type.restaurant_name.approximate_distinct()}
    )
    .compute()
```

```
// 该JSON对象包含两个主要属性：excludedItems和data。
// excludedItems表示被排除的项目数量。
// data是一个数组，其中每个元素代表一个数据组。

{
    excludedItems: 0, // 被排除的项目数为0
    data: [{
        group: {}, // group对象，目前为空，可以用于存储组的相关信息。
        metrics: [
            {
                name: "distinctCount", // 度量名称为"distinctCount"，表示不同项的计数。
                value: 100 // distinctCount的值为100。
            }
        ]
    }]
}
```

#### 计数

计算示例餐厅的总计数。

参数：

- name字符串（非必填）：计算计数的别名。默认情况下，这是count。
示例查询：

```
Copied!1
2
3
4
numExampleRestaurant = client.ontology.objects.ExampleRestaurant
    .count()
    .compute()
    # 获取 ExampleRestaurant 对象的数量，并计算结果
```

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
{
    excludedItems: 0, // 被排除的项目数量
    data: [{
        group: {}, // 分组信息，当前为空
        metrics: [
            {
                name: "count", // 度量名称：计数
                value: 100 // 度量值：100
            }
        ]
    }]
}
```

#### 数值聚合

仅适用于数值属性。计算示例餐厅的数值属性的最大值、最小值、总和或平均值。

参数：

- 字段字符串: 要使用的属性名称（例如 numberOfReviews）。
- 名称字符串（非必填）：计算值的别名。默认情况下，这是“avg”
聚合类型：

- 平均值:avg()
- 最大值:max()
- 最小值:min()
- 总和:sum()
示例查询：

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
from ontology_sdk.ontology.objects import ExampleRestaurant

# 计算 ExampleRestaurant 中 number_of_reviews 字段的平均值
avgExampleRestaurant = client.ontology.objects.ExampleRestaurant
    .avg(ExampleRestaurant.object_type.number_of_reviews)
    .compute()

# 这与上面的代码等效，但使用 metric_name 作为名称而不是默认的 "avg"
avgExampleRestaurant = client.ontology.objects.ExampleRestaurant
    .aggregate(
        {"metric_name": ExampleRestaurant.object_type.number_of_reviews.avg()}
    )
    .compute()
```

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
{
    excludedItems: 0, // 排除项的数量为0
    data: [{
        group: {}, // 组信息，目前为空对象
        metrics: [
            {
                name: "avg", // 度量名称，这里是平均值
                value: 100  // 度量的值，平均值为100
            }
        ]
    }]
}
```

### 分组类型 (GroupBy)

#### 精确分组

通过restaurantName的确切值对示例餐厅进行分组。

参数：

- 字段字符串: 使用的属性名称（例如，restaurantName）。
- maxGroupCount整数（非必填）：要创建的restaurantName分组的最大数量。
示例查询：

```
Copied!1
2
3
4
5
6
7
from ontology_sdk.ontology.objects import ExampleRestaurant

# 使用 ExampleRestaurant 对象进行分组，按餐馆名称进行精确分组，并计算每个组的数量。
numExampleRestaurant = client.ontology.objects.ExampleRestaurant
    .group_by(ExampleRestaurant.object_type.restaurant_name.exact())  # 按餐馆名称精确分组
    .count()  # 计算每个分组的数量
    .compute()  # 执行计算操作
```
