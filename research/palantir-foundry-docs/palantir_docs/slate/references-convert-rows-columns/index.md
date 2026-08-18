来源: https://palantir.com/docs/zh/foundry/slate/references-convert-rows-columns/

# 在行和列模式之间转换

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 在行和列模式之间转换

在JavaScript中有多种方法可以实现解决方案。这些示例突出了Slate应用程序中常见模式的通用算法。许多这些解决方案使用了内置的Lodash ↗和Moment ↗JavaScript库。

- 将行转换为列
- 将列转换为行
## 将行转换为列

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
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
57
58
59
60
61
62
63
64
65
66
67
68
69
/**
 * 将行导向的模式转换为列导向的模式（通常由查询返回）。
 * 注意：数组的第一个对象需要包含所有需要提取的键（未来的列）。
 * 如果第一个对象不包含所有键的超集，可以使用函数中的替代注释代码。
 *
 * 转换前：
 * [
 *   { foo : 1, bar : 4, baz : 7 },
 *   { bar : 5, baz : 8, foo : 2 },
 *   { foo : 3, baz : 9, bar : 6 }
 * ]
 *
 * 转换后：
 * {
 *   foo : [1, 2, 3],
 *   bar : [4, 5, 6],
 *   baz : [7, 8, 9]
 * }
 *
 */
function transformRowSchemaToColumnSchema(arr, first_object_has_all_keys=true) {
  if (_.isEmpty(arr)) {
    return [];
  }

  var orderedKeys;
  if(first_object_has_all_keys){
    // 如果第一个对象包含所有的键
    orderedKeys = _.chain(arr)
        .first()
        .keys()
        .sortBy()
        .value();
  } else {
    // 如果不是所有对象都包含所有键的替代方案：
    orderedKeys = _.uniq(_.flatMap(arr, _.keys))
  }

  // 按键排序对象
  var sortKeysBy = function(obj) {
    return _.zipObject(orderedKeys, _.map(orderedKeys, function(key) {
      return obj[key];
    }));
  };

  // 创建索引到键的映射
  var indexToKeyMapping = _.reduce(orderedKeys, function(agg, key, i) {
    agg[i] = key;
    return agg;
  }, {});

  // 将每个行对象转换为按键排序后的行对象
  var arrayOfRowObjects    = _.map(arr, sortKeysBy);
  // 将行对象转换为数组
  var arrayOfRowArrays     = _.map(arrayOfRowObjects, function(obj) { return _.values(obj) });
  // 转置行数组为列数组
  var arrayOfColumnArrays  = _.unzip(arrayOfRowArrays);
  // 将列数组转换为包含列数组的对象
  var objectOfColumnArrays = _.reduce(arrayOfColumnArrays, function(agg, columnArr, i) {
    var key = indexToKeyMapping[i];
    agg[key] = columnArr;
    return agg;
  }, {});

  return objectOfColumnArrays;
}

var data = {{f_data}}
return transformRowSchemaToColumnSchema(data)
```

## 将列变换为行

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
41
42
/**
 * 将列式结构（通常由查询返回）转换为行式结构（通常用于 {{#each}} 循环）
 *
 * 转换前:
 * {
 *   foo : [1, 2, 3],
 *   bar : [4, 5, 6],
 *   baz : [7, 8, 9]
 * }
 *
 * 转换后:
 * [
 *   { foo : 1, bar : 4, baz : 7 },
 *   { foo : 2, bar : 5, baz : 8 },
 *   { foo : 3, bar : 6, baz : 9 }
 * ]
 */

function transformColumnSchemaToRowSchema(data) {
  var keys   = _.keys(data); // 获取数据中的所有键
  var arrays = _.values(data); // 获取数据中的所有值（数组形式）

  // 如果 `data` 是直接从 SQL 查询中获取的，移除 `._response` 属性
  // delete data._response;

  var arrayOfPropertyLists = _.zip.apply(_, arrays); // 将多个数组组合成一个二维数组，每个子数组包含每个原始数组的一个元素

  var arrayOfObjects = _.map(arrayOfPropertyLists, function(list) {
    var obj = {};

    _.each(keys, function(key, i) {
      obj[key] = list[i]; // 根据键和值构建对象
    });

    return obj; // 返回构建的对象
  });

  return arrayOfObjects; // 返回行式结构的数组
}

var data = {{f_data}}
return transformColumnSchemaToRowSchema(data)
```
