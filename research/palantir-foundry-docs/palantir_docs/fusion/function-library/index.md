来源: https://palantir.com/docs/zh/foundry/fusion/function-library/

# 函数库

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 函数库

## 核心函数

这些函数是Fusion的默认方法。

#### abs(value: number): number

计算一个数的绝对值（即没有符号的数）。

例如：abs(-2)将返回值2。

参数

- value:NUMBER
#### acos(value: number): number

返回一个数的反余弦值。反余弦是余弦为该数的角度。返回的角度以弧度表示，范围在0到Π之间。

例如：acos(1)将返回值0。

参数

- value:NUMBER
#### all_token_match(value: any): same_as_first_argument

返回一个带有修饰符的value，允许以词元化的方式执行搜索和查找，其中所有术语出现在结果中的某处。

参数

- value:ANY
#### any_token_match(value: any): same_as_first_argument

返回一个带有修饰符的value，允许以词元化的方式执行搜索和查找，其中至少有一个术语出现在结果中的某处。

参数

- value:ANY
#### array([arg: any, ...]): string

创建一个包含所有输入属性的数组。生成的数组将用[方括号]包围。所有属性将列在一个单元格中。

例如：array('John', 'Mary', 'Richard')结果是数组 [ John, Mary, Richard ]

注意：如果属性是字符串，它们需要用'单引号'括起来。

参数

- arg:ANY
#### array_concat([array: array, ...]): array

将所有输入数组连接成一个单一数组。

例如：假设你在单元格A1中有数组[1,2,3]，在单元格A2中有数组[4,5,6]。Array_concat(A1,A2)将返回新数组 [1,2,3,4,5,6]。

参数

- array:ARRAY
#### array_contains(array: array, value: any): boolean

检查array是否包含value。如果数组包含该值，函数返回true。

例如：如果数组 [ John, Mary, Richard ] 在单元格E7中，实施array_contains(E7, 'Richard')将检查数组中是否有值 'Richard'。在这种情况下，函数将返回True。如果输入array_contains(E7, 'Louise')，函数将返回False。

参数

- array:ARRAY
- value:ANY
#### array_difference(array: array, [differenceArrays: array, ...]): array

返回第一个数组中在其他任何数组中都不存在的所有唯一元素，顺序没有保证。

例如：给定数组[ John, Mary, Richard, Richard ]在单元格E7中，数组[ John, Mary, Bob]在单元格E8中，array_difference(E7, E8)将返回[ Richard ]。

参数

- array:ARRAY
- differenceArrays:ARRAY
#### array_distinct([value: any, ...]): array

返回一个仅包含输入参数的不同值的数组。

例如：array_distinct(array(3, 2, 1), 4, array(1, 2))将返回数组 array(3, 1, 4, 2)。

注意：值的顺序不保留。此外，附加到值的任何标签（例如模糊或精确）都将被删除。

参数

- value:ANY
#### array_flatten([arg: any, ...]): string

创建一个包含所有输入属性的数组。生成的数组将用[方括号]包围。所有属性将列在一个单元格中。此函数类似于array，但会折叠单元格范围和数组，按从左到右、逐行的方式取值。范围内的空值和错误将被忽略。

例如：array_flatten('John', A1:B2)其中A1 = array('Zoe', 'Charles')，A2 = 'Mary'和B2 = 'Richard'，结果为数组 [ John, Zoe, Charles, Mary, Richard ]。注意单元格A1中的数组被展平到输出中，并且空单元格B1被跳过。

注意：如果属性是字符串，它们需要用'单引号'括起来。

参数

- arg:ANY
#### array_get_at_index(array: array, index: number): any

返回指定array中位置index（从1开始）的元素。

例如：如果数组 [ John, Mary, Richard ] 在单元格E7中，并且我们想验证第3个位置的属性，我们可以使用array_get_at_index(E7, 3)。这将返回Richard，数组中的第三个属性。

参数

- array:ARRAY
- index:NUMBER
#### array_get_first(array: array): any

获取array的第一个元素。

参数

- array:ARRAY
#### array_get_last(array: array): any

获取array的最后一个元素。

参数

- array:ARRAY
#### array_intersection(array: array, [intersectionArrays: array, ...]): array

返回在所有给定数组中存在的所有唯一元素，顺序没有保证。

例如：给定数组[ John, Mary, Mary, Richard ]在单元格E7中，数组[ John, Mary, John, Bob]在单元格E8中，array_intersection(E7, E8)将返回[ John, Mary ]。

参数

- array:ARRAY
- intersectionArrays:ARRAY
#### array_length(array: array): number

返回给定数组的长度。

例如：如果数组 [ John, Mary, Richard ] 在单元格E7中，并且我们想确定数组的长度，我们可以写：array_length(E7)。函数将返回值3，因为数组中有三个属性。

参数

- array:ARRAY
#### array_slice(array: array, start_index: number, [end_index: number]): array

从array中截取从start_index（包含）到end_index（包含）的部分，并返回一个数组。

例如：如果数组[ John, Mary, Richard ]在单元格E7中，array_slice(E7, 1, 2)将返回[ John, Mary ]。如果start_index为零或大于数组长度，则返回空数组。比如：array_slice(E7, 5, 2)→[]。如果start_index为负数，则用作从数组末尾的偏移量。比如：array_slice(E7, -2, 2)→[ Mary ]。如果end_index为零或大于数组长度，则提取直到数组末尾的子数组。比如：array_slice(E7, 2, 5)→[ Mary, Richard ]。如果end_index为负数，则用作从数组末尾的偏移量。比如：array_slice(E7, 1, -2)→[ John, Mary ]。

参数

- array:ARRAY
- start_index:NUMBER
- end_index:NUMBER
#### array_sort(array: array, [sort_direction: any]): array

返回按升序排序的给定数组。您可以指定FALSE或'DESC'作为第二个参数以降序排序。

例如：如果数组 [ 3, 4, 1 ] 在单元格E7中，并且我们想对数组进行排序，我们可以写：array_sort(E7, 'DESC')。函数将返回数组 [ 4, 3, 1 ]。

参数

- array:ARRAY
- sort_direction:ANY
#### array_zip([array: array, ...]): array

创建一个分组元素的数组，其中第一个包含给定数组的第一个元素，第二个包含给定数组的第二个元素，依此类推。生成的数组的长度将等于最短输入数组的长度。

例如：如果你在单元格A1中有数组['a', 'b', 'c']和数组[1, 2, 3]在单元格A2中。array_zip(A1, A2)将返回新数组[ [ 'a', '1' ], [ 'b', '2' ], [ 'c', '3' ] ]。

参数

- array:ARRAY
#### asin(value: number): number

返回一个数的反正弦值。反正弦是正弦为该数的角度。返回的角度以弧度表示，范围在-Π/2到Π/2之间。

例如：asin(-1)将返回值-Π/2。

参数

- value:NUMBER
#### atan(value: number): number

返回一个数的反正切值。反正切是正切为该数的角度。返回的角度以弧度表示，范围在-Π/2到Π/2之间。

例如：atan(0)将返回值0。

参数

- value:NUMBER
#### atan2(x_num: number, y_num: number): number

返回指定x和y坐标的反正切值或反正切。反正切是从x轴到包含原点(0, 0)和坐标点(x_num, y_num)的线的角度。角度以弧度表示，范围在-Π到Π之间，不包括-Π。

例如：atan2(1,1)将返回值0.785398163。

参数

- x_num:NUMBER
- y_num:NUMBER
#### avg([range: range, ...]): number

计算指定range的数值平均值。此范围可以作为一组值或一组值的范围输入。

例如：avg(5, 7, 11)将返回7.66。

参数

- range:RANGE
#### binary([value: any, ...]): binary

从数字创建一个二进制对象。每个数字将被视为无符号字节(0-255)。高位将被忽略。

例如：binary(0, 0, 127)。

参数

- value:ANY
#### branch(dataset_path: string, branch_name: string): same_as_first_argument

返回带有branch_name标记的dataset_path。应用于查找中的第一个参数以指定要在搜索中使用的分支。

注意：如果您找不到新索引的数据集，请刷新页面或导航到查找和使用数据，选择索引数据集，然后选择刷新按钮。

参数

- dataset_path:STRING
- branch_name:STRING
#### case_toggle(value: string): string

将大写字母更改为小写字母，反之亦然。数字保持不变。

参数

- value:STRING
#### cbrt(value: number): number

计算给定value的立方根。

例如：cbrt(8)将返回2。

参数

- value:NUMBER
#### ceil(value: number): number

通过向上舍入到没有小数的最接近数字来计算给定value的上限。

例如：Ceil(5.2)将返回6。

参数

- value:NUMBER
#### checkbox([checked: boolean], [label: string]): boolean

渲染一个复选框，如果选中则返回true，否则返回false，并带有一个可选的标签。如果未提供已选参数，则默认为false和未选中。

参数

- checked:BOOLEAN
- label:STRING
#### coalesce([arg: any, ...]): any

返回第一个不是null的属性。或者，如果所有属性都是null，将返回null。

例如：假设我们有一个包含姓名和null值混合的A列。如果我们使用coalesce(columnA)，函数将返回第一个可用的姓名。

参数

- arg:ANY
#### color(cell_value: any, [text_color: string], [background_color: string]): any

渲染具有指定文本和背景颜色的单元格。

参数

- cell_value:ANY
- text_color:STRING
- background_color:STRING
#### concat([arg: string, ...]): string

将多个输入字符串属性连接到一个字符串属性中。

例如：假设名字John在单元格A2中，姓氏Smith在单元格B2中。使用concat函数，我们可以在C2中输入concat(A2, ' ', B2)来获取字符串'John Smith'。

所有集合类型的参数会被递归展平。例如，concat(array(1, 2), array(array(3, 4, 5)), 6)将返回字符串'123456'。

- arg:STRING
#### concat_ws(separator: string, [arg: string, ...]): string

将多个输入字符串属性连接成一个带有separator的单一字符串属性。所有集合类型的参数将被递归展平。

例如：假设名字John在单元格A2中，姓氏Smith在单元格B2中。使用concat_ws函数，我们可以在C2中输入concat_ws('_',A2, B2)得到结果'John_Smith'。

所有集合类型的参数像在concat函数中一样递归展平。

参数

- separator:STRING
- arg:STRING
#### cos(value: number): number

计算给定value的余弦值。

例如：cos(190)将返回0.066。

参数

- value:NUMBER
#### count([range: range, ...]): number

返回组中的项目数。

例如：假设我们想知道特定列中的对象数量。我们可以选择count函数，突出显示该列，并检索一个值。

参数

- range:RANGE
#### count_distinct([range: range, ...]): number

返回组中的不同项目数。

例如：count_distinct(columnA)将返回该列中的不同对象数。此函数也可以应用于数组，并将返回该数组中的不同对象数。

参数

- range:RANGE
#### count_numeric([value: any, ...]): number

计算组中的数值项目数。

例如：假设你有100行包含各种名称和数字。要仅确定该列中数值项目的数量，使用count_numeric(A1:A100)来获取值。

参数

- value:ANY
#### countif(range: range, criteria: any): number

返回在范围range中等于指定criteria的项目数。

例如：假设A列包含一个动物列表，你想知道在前100行中'Dog'出现的次数。使用countif(A1:A100, 'Dog')来获得唯一计数。

参数

- range:RANGE
- criteria:ANY
#### countifs([range: range, criteria: any, ...]): number

返回在范围range中等于所有range、criteria对的criteria的项目数。

例如：countifs(A1:A100, 'Red', B1:B100, 2)将返回在A列中包含值Red且在B列中包含数字2的所有值的计数。

参数

- range:RANGE
- criteria:ANY
#### date(year: number, month: number, day: number): date_time

以格式yyyy-MM-dd创建一个具有定义year、month、day的日期。

对于年份< 1900的日期（例如 '97'），年份将被解释为1900的偏移量（例如 '1997'）。

参数

- year:NUMBER
- month:NUMBER
- day:NUMBER
#### date_add(dateOrDaysLeft: any, dateOrDaysRight: any): date_time

返回dateOrDaysLeft加上dateOfDaysRight的日期或时间戳。每个参数可以是天数或天数的分数或日期。日期必须为格式yyyy-MM-dd。

例如：假设我们想知道2021-05-06后40天的日期。此日期位于单元格D2中。使用date_add(D2, 40)来得到2021-06-15。再例如：如果我想要2021-05-06加上半天的时间戳。此日期位于单元格D2中。使用date_add(D2, 0.5)来得到2021-05-06 12:00。

参数

- dateOrDaysLeft:ANY
- dateOrDaysRight:ANY
#### date_diff(start: date_time, end: date_time): number

返回从start到end的天数。日期必须为格式yyyy-MM-dd。

例如：假设我们想知道2021-01-15和2021-06-15之间的天数。这些单元格分别位于B2和B5。使用date_diff (B2, B5)来得到-151天的差异。

参数

- start:DATE_TIME
- end:DATE_TIME
#### date_format(date: date_time, format: string): string

将日期/时间戳date转换为由format中的字符串指定的格式的字符串。格式可以是字符串yyyy-MM-dd的变体。

例如：将日期2021-05-06重新格式化为05-06-21使用date_format('2021-05-06', 'MM-dd-yy')。

参数

- date:DATE_TIME
- format:STRING
#### date_sub(dateOrDaysLeft: any, dateOfDaysRight: any): date_time

返回dateOrDaysLeft减去dateOfDaysRight的日期或时间戳。每个参数可以是天数或天数的分数或日期。日期必须为格式yyyy-MM-dd。

例如：假设我们想知道2021-05-06前40天的日期。此日期位于单元格D2中。使用date_sub(D2, 40)来得到2021-03-27。再例如：如果我想要2021-05-06减去半天的时间戳。此日期位于单元格D2中。使用date_sub(D2, 0.5)来得到2021-05-05 12:00。例如：如果我想知道两个日期之间的天数差异，其中一个日期在单元格D1中，另一个在单元格D2中。使用date_sub(D1, D2)。

参数

- dateOrDaysLeft:ANY
- dateOfDaysRight:ANY
#### datepicker([selectedDateTime: date_time], [timePrecision: string]): date_time

返回一个带有选定日期的日期选择器。日期必须为格式yyyy-MM-dd，可选HH:mm（时间信息）。时间精度必须为'NONE'、'MINUTE'或'SECOND'之一。

参数

- selectedDateTime:DATE_TIME
- timePrecision:STRING
#### day_of_month(date: date_time): number

从给定的日期/时间戳/字符串中提取月份的日期为整数。

例如：假设日期2021-06-18位于单元格B2中。day_of_month(B2)将返回18。

参数

- date:DATE_TIME
#### day_of_year(date: date_time): number

从给定的日期/时间戳/字符串中计算年份的日期为整数。

例如：假设日期2021-06-18位于单元格B2中。day_of_year(B2)将返回169。

参数

- date:DATE_TIME
#### document_metadata(key: string): string

访问文档元数据。要实现，请传入您需要的元数据字段的key。

支持的键：

- creator返回文档的创建者（如果已知）。
- document_identifier返回文档的内部标识符（例如，在submit_to_region_with_key函数中使用）
例如：document_metadata('creator')将返回文档创建者的用户名。

参数

- key:STRING
#### dropdown(values: array, [selected_value: string], [allow_invalid: boolean], [placeholder_text: string]): any

渲染一个带有可从提供的values数组中选择的值的下拉菜单。values必须是唯一的，因为每个值在下拉菜单中转换为字符串标签。

例如，=dropdown(array('red', 'blue', 'green'))将创建一个带有值'red', 'blue', 'green'的下拉菜单。

当提供selected_value时，它指定下拉菜单的默认字符串标签。selected_value是非必填的，可以设置为null，这将使下拉菜单的选择默认为未选择状态。如果selected_value被设置且选择的标签在values数组中不再找到（例如如果底层数据更改），结果将是一个空单元格。

当allow_invalid设置为true时，它将覆盖此行为，并仍然输出先前保存的选择。此结果只能是字符串，并且仅在尝试从一组字符串值中保留先前选择时推荐。

placeholder_text允许您在未选择值时在下拉菜单中显示文本（它可以用作提示或说明）

参数

- values:ARRAY
- selected_value:STRING
- allow_invalid:BOOLEAN
- placeholder_text:STRING
#### empty_cell(): any

返回一个空结果。当与if或iferror函数结合使用时非常有用（例如if(not isnull(A1), A1, empty_cell())）

#### eq(value: any): same_as_first_argument

将当前value标记为等于（==）比较。

应用于查找函数中的参数以更改搜索行为。

参数

- value:ANY
#### exact(value: any): same_as_first_argument

返回一个带有修饰符的value，以使搜索和查找精确匹配value。

参数

- value:ANY
#### exp(value: number): number

返回e的value次幂。常数e等于2.718，自然对数的底数。

例如：exp(2)返回7.389。这是自然对数e的2次幂的结果。

参数

- value:NUMBER
#### experimental_add_tags(value: any, tags: array): same_as_first_argument [EXPERIMENTAL]

将tags添加到value并返回新的标记值。

参数

- value:ANY
- tags:ARRAY
#### experimental_copy_and_sync_button(label: string, folder: string, name: string, [exports: array], [onCompleteMessage: string], [onFailureMessage: string], [redirectToHomeAfterCompletion: boolean]): same_as_first_argument [EXPERIMENTAL]

渲染一个按钮，带有标签label，当点击时，将复制电子表格到folder，名称为name。

导出将使用以下模式进行复制：‘$name- Export$sheetName'。导出可以通过在exports中传入所需导出的工作表名称来约束。如果任何导出缺失，复制将失败。完成和失败消息可以分别传入onCompleteMessage和onFailureMessage。如果redirectToHomeAfterCompletion设置为true，用户将在完成后被重定向到他们的主页文件夹。

参数

- label:STRING
- folder:STRING
- name:STRING
- exports:ARRAY
- onCompleteMessage:STRING
- onFailureMessage:STRING
- redirectToHomeAfterCompletion:BOOLEAN
#### experimental_error([value: string, ...]): any [EXPERIMENTAL]

输出一个错误。

参数

- value:STRING
#### experimental_get_tags(value: any): array [EXPERIMENTAL]

返回与value关联的标签数组。

参数

- value:ANY
#### experimental_io_blocking_function([extra_delay: number]): string [EXPERIMENTAL]

测试方法，阻塞I/O直到超时。可以选择性地在超时后给予额外的延迟，以模拟表现不佳的I/O函数。

参数

- extra_delay:NUMBER
#### experimental_range(width: number, [value: any, ...]): range [EXPERIMENTAL]

输出一个范围。

参数

- width:NUMBER
- value:ANY
#### experimental_remove_tags(value: any, [tags: array]): same_as_first_argument [EXPERIMENTAL]

从value中移除数组tags中的标签，或者如果没有tags参数，则从value中移除所有标签。

参数

- value:ANY
- tags:ARRAY
#### factorial(value: number): number

计算给定value的阶乘。

例如：factorial(3)将返回6。

参数

- value:NUMBER
#### find(search_for: string, text_to_search: string, [starting_index: number]): number

返回字符串text_to_search中第一个search_for实例的索引。您可以选择提供一个starting_index进行搜索。

例如：假设你在单元格A1中有短语'The grey cat chased the grey mouse'。为了确定'grey'的第一个实例的索引，实现find('grey', A1)来获得索引5。

参数

- search_for:STRING
- text_to_search:STRING
- starting_index:NUMBER
#### floor(value: number): number

通过向下舍入到没有小数的最接近数字来计算给定value的下限。

例如：floor(3.2)将舍入为3。而，floor (-4.5)将舍入为-5。

参数

- value:NUMBER
#### format_number(value: number, decimalPlaces: number): number

将数值单元格value格式化为类似 #,###.## 的格式，并四舍五入到由decimalPlaces指定的小数位数。该函数将结果返回为字符串。

例如：假设你在A列中有一个4位数字的列，并且你想包含千位分隔符以及2个小数位。使用format_number(A1, 2)来将第一个数字重新格式化为 #,###.00。向下拖动框以应用于A列的其余部分。

参数

- value:NUMBER
- decimalPlaces:NUMBER
#### format_string([format: string, ...]): number

以printf风格格式化arg并使用format将结果返回为字符串属性。

参数

- format:STRING
#### fuzzy(value: any, [distance: number]): same_as_first_argument

返回一个带有修饰符的value，允许以模糊方式执行搜索和查找，其中搜索的值在distance编辑范围内。仅支持0、1和2的编辑距离，默认为2。

距离对应于Levenshtein距离，一种从一个字符串到另一个字符串所需的单字符编辑次数的度量。

参数

- value:ANY
- distance:NUMBER
#### get_object_rid(object_or_property: any): string

返回给定对象或对象属性的对象RID。

参数

- object_or_property:ANY
#### get_object_type_id(object_or_property: any): string

返回给定对象或对象属性的对象类型ID。

参数

- object_or_property:ANY
#### get_property(object: object, key: string): object

返回对象的给定属性。

参数

- object:OBJECT
- key:STRING
#### gt(value: any): same_as_first_argument

将当前value标记为大于（>）比较。

应用于查找函数中的参数以更改搜索行为。

参数

- value:ANY
#### gte(value: any): same_as_first_argument

将当前value标记为大于或等于（>=）比较。

应用于查找函数中的参数以更改搜索行为。

参数

- value:ANY
#### hlookup(value: any, range: range, row: number): any

在range的第一行中查找value并获取row（从1开始）。

例如：假设A列是一个颜色列表。hlookup(A1,A1:A100,5)将返回该列中第5行的颜色。

参数

- value:ANY
- range:RANGE
- row:NUMBER
#### hour(date: date_time): number

从给定的日期/时间戳/字符串中提取小时为整数。此函数将忽略字符串中的日期和分钟。

例如：假设你在单元格A2中有时间戳2021-02-15 08:30:15。hour(A2)将返回8。

参数

- date:DATE_TIME
#### if(condition: boolean, value_if_true: any, value_if_false: any): any

如果condition评估为true，返回在value_if_true中指定的值。如果condition评估为false，返回在value_if_false中指定的值。

例如：假设我们实现函数if(A1 >=5, 'True', 'False')。如果A1等于6，函数将返回True。如果A1等于4，函数将返回False。

参数

- condition:BOOLEAN
- value_if_true:ANY
- value_if_false:ANY
#### iferror(value: any, value_if_error: any): any

如果没有检测到错误，则返回value。否则，抛出由value_if_error指定的错误。此函数为管理错误消息提供了一个更优雅的解决方案。

例如：假设你在单元格C3中有简单公式A1/B2。如果B2为空白，你希望公式抛出错误'在B2中输入一个值。'实现iferror(A1/B2, '在B2中输入一个值。')。

参数

- value:ANY
- value_if_error:ANY
#### index(range: range, row_offset: number, column_offset: number): any

返回range中的一个单元格的内容，由row_offset和column_offset指定。row_offset指定要从中提取数据的行，而column_offset指定要从中提取数据的列。

例如：index(A1:C6, 2, 3)意味着你想从范围A1中提取第2行，第3列的数据。

注意：如果行偏移量设置为0，将选择由column_offset指定的整个列。如果列偏移量为0，将选择由row_offset指定的整行。如果两者都为零，将选择整个单元格范围。

参数

- range:RANGE
- row_offset:NUMBER
- column_offset:NUMBER
#### internal_region_result(region_id: string): any [EXPERIMENTAL]

内部函数。

参数

- region_id:STRING
#### isNull(value: any): boolean

如果属性为空或空单元格，则返回true。否则，函数返回false。

例如：假设A列包含整数和空值的混合。使用isnull(A1)来确定列中的第一个值是否为true（即空值）或整数。向下拖动此公式以应用于列的其余部分。

参数

- value:ANY
#### last_day(date: date_time): number

给定一个date属性，函数返回指定月份的最后一天，格式为yyyy-MM-dd。注意：日期必须作为字符串输入。

例如：假设当前日期为2021-02-01，你想计算该月的最后日期。使用last_day('2021-02-01')得到2021-02-28。注意：一月份的日期将始终返回31，而二月份的日期将返回28或29，具体取决于年份。

参数

- date:DATE_TIME
#### left(text: string, [num_chars: number]): string

返回字符串text开头的num_chars个字符。

例如：如果字符串'John Smith'在单元格A2中，right(A2, 3)将返回ith。

参数

- text:STRING
- num_chars:NUMBER
#### length(value: any): number

根据字符数计算给定字符串或二进制属性的长度。

例如：length('John Smith')将返回10。

参数

- value:ANY
#### ln(value: number): number

计算给定值的自然对数。如果值为0或以下，函数将返回出错。

例如：ln(7)将返回1.9459。

参数

- value:NUMBER
#### log(value: number, base: number): number

计算value的以base为底的对数。

例如：log(8,2)将返回3。

参数

- value:NUMBER
- base:NUMBER
#### lookup(dataset_path: string, result_column: string, [column: string, value: string, ...]): any

返回在dataset_path中与在column、value对中定义的筛选匹配的result_column的值。

例如：lookup('/Users/me/myData', 'my_column', 'first_name', 'John', 'last_name', 'Doe')将在数据集'/Users/me/myData'中搜索first_name = 'John' 和last_name = 'Doe'的行，并在列'my_column'中获取值。

注意：

- Value可以使用exact或fuzzy函数包装，以指定匹配是否应精确或模糊。Dataset_path可以使用branch函数包装，以指定数据集的分支进行查找。
- 如果您找不到新索引的数据集，请刷新页面或导航到查找和使用数据，选择索引数据集，然后选择刷新按钮。
参数

- dataset_path:STRING
- result_column:STRING
- column:STRING
- value:STRING
#### lookup_array(dataset_path: string, result_column: string, [column: string, value: string, ...]): any

返回在dataset_path中与在column、value对中定义的筛选匹配的result_column的值，作为基于全局排序的数组。结果使用column、value对定义的后续参数进行筛选。

例如：lookup('/Users/me/myData', 'my_column', 'first_name', 'John', 'last_name', 'Doe')将在数据集'/Users/me/myData'中搜索first_name = 'John' 和last_name = 'Doe'的行，并在列'my_column'中获取值。

注意：

- Value可以使用exact或fuzzy函数包装，以指定匹配是否应精确或模糊。
- 如果您找不到新索引的数据集，请刷新页面或导航到查找和使用数据，选择索引数据集，然后选择刷新按钮。
参数

- dataset_path:STRING
- result_column:STRING
- column:STRING
- value:STRING
#### lookup_distinct(dataset_path: 字符串, result_column: 字符串, [column: 字符串, value: 字符串, ...]): any

返回dataset_path中result_column的不同值，这些值与column、value对中定义的筛选条件匹配。

例如：lookup_distinct('/Users/me/myData', 'my_column', 'first_name', 'John')将在数据集 '/Users/me/myData' 中搜索 'first_name' 等于 'John' 的行。该函数将抓取与筛选条件匹配的 'my_column' 的不同值。

注意：

- Value可以使用exact或fuzzy函数包装，以指定匹配是否应为精确或模糊。Dataset_path可以使用branch函数包装，以指定要查找的数据集分支。
- 如果无法找到新索引的数据集，请刷新页面或导航至查找并使用数据，选择索引数据集，然后选择刷新按钮。
参数

- dataset_path:字符串
- result_column:字符串
- column:字符串
- value:字符串
#### lookup_dropdown(dataset_path: 字符串, result_column: 字符串, [selected_value: 字符串], [column: 字符串, value: 字符串, ...]): any

返回一个下拉菜单，包含来自dataset_path中result_column的建议值，selected_value是当前值。selected_value可以设置为 null，这将使下拉菜单的选择默认为未选择状态。

例如：lookup_dropdown('/Users/me/myData', 'my_column', NULL, 'first_name', 'John')将返回一个来自 '/Users/me/myData' 的下拉菜单选项，其中 'first_name' 等于 'John' 的行。函数将抓取与筛选条件匹配的 'my_column' 的不同值。

注意：如果无法找到新索引的数据集，请刷新页面或导航至查找并使用数据，选择索引数据集，然后选择刷新按钮。

参数

- dataset_path:字符串
- result_column:字符串
- selected_value:字符串
- column:字符串
- value:字符串
#### lookup_schema(datasource_path: 字符串, [branch: 字符串]): array

返回由datasource_path指定的数据源的列名。您可以选择性地为您的搜索提供一个数据源分支。

注意：

- 列名将作为数组返回。
- 如果无法找到新索引的数据集，请刷新页面或导航至查找并使用数据，选择索引数据集，然后选择刷新按钮。
参数

- datasource_path:字符串
- branch:字符串
#### [已弃用] lookup_set(dataset_path: 字符串, result_column: 字符串, [column: 字符串, value: 字符串, ...]): any

返回dataset_path中result_column的匹配值作为无序集合。结果使用column、value对中定义的后续参数进行筛选。

例如：lookup('/Users/me/myData', 'my_column', 'first_name', 'John', 'last_name', 'Doe') 将在 '/Users/me/myData' 的数据集中搜索 'first_name' 等于 'John' 且 'last_name' 等于 'Doe' 的行，并抓取匹配行中 my_column 的值。

注意：

- Value可以使用exact或fuzzy函数包装，以指定匹配是否应为精确或模糊。
- 如果无法找到新索引的数据集，请刷新页面或导航至查找并使用数据，选择索引数据集，然后选择刷新按钮。
参数

- dataset_path:字符串
- result_column:字符串
- column:字符串
- value:字符串
#### lookup_sorted(dataset_path: 字符串, result_column: 字符串, sort_column: 字符串, sort_direction: 字符串, [column: 字符串, value: 字符串, ...]): any

返回dataset_path中result_column列的值，按指定的sort_column和sort_direction排序。'result_column' 中的数据可以使用column、value对中定义的后续参数进行筛选。

注意：

- sort_column、result_column和column必须是数据集dataset_path中的列名。此外，sort_direction可以是 'ASC' 或 'DESC'，分别表示升序和降序。
- Value可以使用exact或fuzzy函数包装，以指定匹配是否应为精确或模糊。
- 如果无法找到新索引的数据集，请刷新页面或导航至查找并使用数据，选择索引数据集，然后选择刷新按钮。
参数

- dataset_path:字符串
- result_column:字符串
- sort_column:字符串
- sort_direction:字符串
- column:字符串
- value:字符串
#### lower(value: 字符串): 字符串

将value指定的字符串转换为小写。

例如：假设字符串 'JANE DOE' 在 B2 中。lower(B2)将返回 'jane doe'。

参数

- value:字符串
#### lpad(value: 字符串, length: 数字, pad: 字符串): 字符串

将value中的字符串属性左填充至length长度，并使用pad中指定的字符串。

例如：假设您想用字符串 'NY-' 左填充 A 列中的电话号码字符串。每个填充的电话号码将有 13 个字符。要实现此功能，请使用lpad(A1, 13, 'NY-')并得到 NY-##########。

参数

- value:字符串
- length:数字
- pad:字符串
#### lt(value: any): same_as_first_argument

将当前value标记为小于 (<) 比较。

应用于查找函数中的参数以更改搜索行为。

参数

- value:ANY
#### lte(value: any): same_as_first_argument

将当前value标记为小于或等于 (<=) 比较。

应用于查找函数中的参数以更改搜索行为。

参数

- value:ANY
#### ltrim(value: 字符串): 字符串

从value中的字符串左端修剪空格。

例如：如果字符串 'John Smith' 在单元格 A2 中，并且有 4 个前导空格，ltrim(A2)将去除这些空格。

参数

- value:字符串
#### match(item: any, range: range, criteria: 数字): same_as_first_argument

通过指定的criteria在range中搜索一个项。该函数返回该项在范围内的相对位置（从 1 开始）。

criteria的可能代码如下：

- 1找到小于或等于item的最大值。range定义的范围中的值必须按升序排列。
- 0找到与item完全相等的第一个值。range定义的范围中的值可以是任何顺序。
- -1找到大于或等于item的最小值。range定义的范围中的值必须按降序排列。
例如：如果范围A1:A3包含值 5、25 和 38，则公式match(25,A1:A3,0)返回数字 2，因为 25 是范围中的第二个项。

参数

- item:ANY
- range:RANGE
- criteria:数字
#### max([value: any, ...]): any

返回一组数字、日期或时间戳中的最大值。

例如：max(1,5,23)将返回 23。或者，max(A1:A100)将返回该范围内的最大值。max(date(2021, 2, 2), date(2021, 2, 1))将返回日期 date(2021, 2, 2)。max(parse_timestamp('2021-02-02 00:00:01', 'yyyy-MM-dd HH:mm:ss'), parse_timestamp('2021-02-02 00:00:02', 'yyyy-MM-dd HH:mm:ss'))将返回时间戳 '2021-02-02 00:00:02'。

参数

- value:ANY
#### md5(value: any): 字符串

计算一个字符串的 MD5 摘要，并将值作为 32 个字符的十六进制字符串返回。

例如：假设您在单元格 A2 中有字符串 'John Smith'。md5(A2)将返回 6117323d2cabbc17d44c2b44587f682c。

参数

- value:ANY
#### mean([value: 数字, ...]): 数字

返回一组数值的平均值。

例如：mean(5,8,12)将返回 8.33。

参数

- value:数字
#### median([value: 数字, ...]): 数字

返回一组数值的中位数。

例如：median(10, 11, 19, 20, 21)将返回 19。或者，median(A1:A100)将返回该范围内的中位数。

参数

- value:数字
#### min([value: any, ...]): any

返回一组数字、日期或时间戳中的最小值。

例如：min(5,8,12)将返回 5。或者，min(A1:A100)将返回该范围内的最小值。min(date(2021, 2, 2), date(2021, 2, 1))将返回日期 date(2021, 2, 1)。min(parse_timestamp('2021-02-02 00:00:01', 'yyyy-MM-dd HH:mm:ss'), parse_timestamp('2021-02-02 00:00:02', 'yyyy-MM-dd HH:mm:ss'))将返回时间戳 '2021-02-02 00:00:01'

参数

- value:ANY
#### minute(date: date_time): 数字

提取date的分钟作为整数。

例如：假设您在单元格 A2 中有时间戳2021-02-15 08:30:15。minute(A2)将返回 30。

参数

- date:DATE_TIME
#### month(date: date_time): 数字

提取date的月份作为整数。

例如：假设您在单元格 A2 中有时间戳2021-02-15 08:30:15。month(A2)将返回 2。

参数

- date:DATE_TIME
#### months_between(start: date_time, end: date_time): 数字

返回start和end日期之间的月份数。

例如：months_between('2020-02-15', '2022-01-15')将返回 23。

参数

- start:DATE_TIME
- end:DATE_TIME
#### multidropdown(values: array, [selected_value: array], [allow_invalid: boolean], [placeholder_text: 字符串]): any

呈现一个下拉菜单，允许从提供的values数组中选择值。与 dropdown 函数不同，multidropdown 允许用户一次选择多个值。这些values必须是唯一的，因为每个值将转换为字符串等效标签。

当提供selected_value时，它指定下拉菜单的默认字符串标签。selected_value是非必填的，可以设置为 null，这将使下拉菜单的选择默认为未选择状态。

注意：如果设置了selected_value且所选标签在values数组中不再找到（例如基础数据发生变化），结果将是一个空单元格。

将allow_invalid设置为 true 将覆盖此行为，并仍然输出先前保存的选择。此结果目前只能是字符串，只有在尝试从字符串值集中保留先前选择时才推荐使用此模式。

placeholder_text允许在未选择值时在下拉菜单中显示文本（这可以用作提示或说明）。

参数

- values:ARRAY
- selected_value:ARRAY
- allow_invalid:BOOLEAN
- placeholder_text:字符串
#### neq(value: any): same_as_first_argument

将当前value标记为不等于 (!=) 比较。

应用于查找函数中的参数以更改搜索行为。

参数

- value:ANY
#### net_workdays(start_date: date_time, end_date: date_time, [holidays: any]): 数字

返回 start_date 和 end_date 之间的整天工作日数。工作日不包括周末。目前，此函数不支持将假期作为参数。

例如：net_workdays('2021-01-01','2021-02-01') 将返回 23，因为这是一月期间的工作日数量，忽略假期。

参数

- start_date:DATE_TIME
- end_date:DATE_TIME
- holidays:ANY
#### object(objectRid: 字符串): Object [实验性]

加载具有给定对象 RID 的对象。

参数

- objectRid:字符串
#### object_dropdown(object_set: array, [selected_object_rid: 字符串], [placeholder_text: 字符串]): Object [实验性]

返回一个下拉菜单，包含来自对象集的建议值，selected_object_rid是来自对象集的当前选定对象的 RID。

参数

- object_set:ARRAY
- selected_object_rid:字符串
- placeholder_text:字符串
#### object_set(objectSetRid: 字符串, [paramKey: 字符串, paramValue: any, ...]): array [实验性]

加载具有给定对象集 RID 的对象集。

参数

- objectSetRid:字符串
- paramKey:字符串
- paramValue:ANY
#### parse_date(date_string: 字符串, [formats: 字符串, ...]): date

将字符串解析为日期。如果指定了多种格式，它们将按顺序尝试，直到一个成功为止。

例如：parse_date('25/01/2022', 'dd/MM/yyyy')将返回 2022 年 1 月 25 日的日期。

有关格式化和解析日期的模式的详细信息，请参阅Java DateTimeFormatter 文档 ↗。

参数

- date_string:字符串
- formats:字符串
#### parse_timestamp(timestamp_string: 字符串, [formats: 字符串, ...]): date_time

将字符串解析为时间戳。如果指定了多种格式，它们将按顺序尝试，直到一个成功为止。

例如：parse_timestamp('25/01/2022 12:03', 'dd/MM/yyyy HH:mm')将返回 2022 年 1 月 25 日中午 3 分钟的日期。

参数

- timestamp_string:字符串
- formats:字符串
#### percentile(array: array, pp: 数字): 数字

返回数组中有pp个值小于它的数。

- array: 未必排序的正数/负数数组。
- pp: 百分位数，必须在 0 和 1 之间（包含）。pp=0将返回数组的最小值，pp=0.5返回中位数，pp=1返回最大值。
- 示例：=percentile(array(7.25, 5.3, 8, 10), 0.25)返回 6.7625，即数组值中 25% 小于它的值。=percentile(array(12, 20, 10, 25, 28, 30, 34, 60), 0)返回 10，即数组中的最小值。=percentile(A2:A9, A13)也可以与范围和单元格引用一起使用。=percentile(array_flatten(A2:A9), A13)
- =percentile(array(7.25, 5.3, 8, 10), 0.25)返回 6.7625，即数组值中 25% 小于它的值。
- =percentile(array(12, 20, 10, 25, 28, 30, 34, 60), 0)返回 10，即数组中的最小值。
- =percentile(A2:A9, A13)也可以与范围和单元格引用一起使用。
- =percentile(array_flatten(A2:A9), A13)
参数

- array:ARRAY
- pp:数字
#### pow(value: 数字, power: 数字): 数字

返回value的power次幂的结果。

例如：pow(5, 2)将返回 25。

参数

- value:数字
- power:数字
#### product([value: any, ...]): 数字

返回表达式中所有数值的乘积。

例如：product(6*2)将返回 12。

参数

- value:ANY
#### quarter(date: date_time): 数字

提取日期的年度季度作为整数。

例如：假设日期 2021-08-15 在单元格 A1 中。Quarter(A1)将返回 3，因为该日期在年度的第三季度。

参数

- date:DATE_TIME
#### query_params([key: 字符串, value: 字符串, ...]): 字符串

将key、value对编码为 URL 查询参数中安全使用的格式。

例如：=query_params('k1', 'this is long', 'k2', 'v+2')将返回k1=this%20is%20long&k2=v%2B2

参数

- key:字符串
- value:字符串
#### rank(number: 数字, collection: array, sortOrder: 数字): 数字

返回指定数字在按sortOrder排序的数字集合中的排名。排名将是数字相对于集合中其他值的值。

如果sortOrder等于 0，集合中的数字排名将按降序表示。

如果sortOrder等于非零数字，排名将按升序表示。

注意：集合中的所有非数字值将被忽略。

例如：假设您在单元格 A1、A2、A3 和 A4 中分别有值 94、79 和 83、96。Rank(94, A1:A4, 1)将返回 2，因为 94 是该值集合中第二高的排名值。如果我们想确定该列中其他数字的排名，应将集合的表达式更改为 A$1$4。这样，范围将不会改变。

参数

- number:数字
- collection:ARRAY
- sortOrder:数字
#### regexp_replace(value: 字符串, search: 字符串, replace: 字符串): 字符串

将value中所有与search匹配的子字符串替换为replace。

例如：假设 A 列是动物列表，某些单元格包含字符串 'The'，例如 'The Dog'。如果我们想将每个 'The' 替换为字符串 'One'，只需实现regexp_replace(A1, 'The', 'One')。新单元格将显示 'One Dog' 而不是 'The Dog'。只需拖动单元格的角落即可应用于 A 列的其余部分。

参数

- value:字符串
- search:字符串
- replace:字符串
#### reverse(value: 字符串): 字符串

反转value并将其作为新字符串返回。

例如：Reverse('John Smith')将返回 htimS nhoJ。

参数

- value:字符串
#### right(text: 字符串, [num_chars: 数字]): 字符串

从字符串text的末尾返回num_chars指定的字符数。

例如：如果字符串 'John Smith' 在单元格 A2 中，left(A2, 3)将返回Joh。

参数

- text:字符串
- num_chars:数字
#### round(value: 数字, decimalPlaces: 数字): 数字

将value四舍五入到decimalPlaces指定的小数位数。

例如：Round(4.56, 1)将返回 4.6。Round(4.56, 0)将返回 5。

参数

- value:数字
- decimalPlaces:数字
#### rpad(value: 字符串, length: 数字, pad: 字符串): 字符串

将value中的字符串属性右填充至指定的length，并使用pad中的字符串。

例如：假设您想用字符串 '-NY' 右填充 A 列中的电话号码字符串。每个新号码将有 13 个字符。要实现此功能，请使用rpad(A1, 13, '-NY')以获得 ##########-NY。

参数

- value:字符串
- length:数字
- pad:字符串
#### rtrim(value: 字符串): 字符串

从value指定的字符串右端修剪空格。

例如：如果单元格 A2 中的字符串 'John Smith' 有 4 个尾随空格，rtrim(A2)将去除这些空格。

参数

- value:字符串
#### second(date: date_time): 数字

提取date中的秒作为整数。

例如：假设您在单元格 A2 中有时间戳2021-02-15 08:30:15。second(A2)将返回 15。

参数

- date:DATE_TIME
#### [已弃用] set_get_any(set: any): any

从给定集合中检索一个随机元素。

参数

- set:ANY
#### [已弃用] set_to_array(set: any): array

将给定集合转换为数组，按升序排序。

例如：假设我们在 A1 中有一组名称。set_to_array(A1)将这些名称转换为数组。

参数

- set:ANY
#### sha1(value: any): 字符串

计算属性的 SHA-1 摘要，并将值作为 40 个字符的十六进制字符串返回。

例如：sha1('The cow jumped over the moon.') 将返回 6e2780eb20fdaf78f6c8335d0b17526c7ef12a79。

参数

- value:ANY
#### sin(value: 数字): 数字

计算value的正弦值。

例如：sin(140)将返回 0.98。

参数

- value:数字
#### split(text: 字符串, delimiter: 字符串): array

使用指定的delimiter分割text，并将片段输出为一行。注意：空片段将被忽略。

例如：假设您在单元格 A1 中有字符串 'Jane | 24 | F'。要将其分割为片段数组，可以使用split(A1, '|')来获得 '[ Jane , 24 , F ]'。

参数

- text:字符串
- delimiter:字符串
#### split_regex(text: 字符串, delimiter: 字符串): array

使用指定的delimiter的正则表达式语法分割text，并将片段输出为一行。注意：空片段将被忽略。

例如：假设您在单元格 A1 中有字符串 '123ABCDE456FGHIJKL789MNOPQ012'。要将其分割为非数字片段（即在任何数字上分割），可以使用=split_regex(A1, '\d+')来获得 '[ ABCDE, FGHIJKL, MNOPQ ]'。

参数

- text:字符串
- delimiter:字符串
#### sqrt(value: 数字): 数字

计算value的平方根。

例如：sqrt(16)将返回 4。

参数

- value:数字
#### stddev([value: 数字, ...]): 数字

返回一组表达式的样本标准偏差。

例如：假设您在单元格 A1、A2 和 A3 中分别有值 23、45、32。stddev(A1:A3)将返回 11.06。

参数

- value:数字
#### stddev_p([value: any, ...]): 数字

返回一组表达式的偏差标准偏差，假设其参数是整个总体。如果它们仅代表总体的一个样本，请改用STDDEV。

参数

- value:ANY
#### submit_to_region_with_key(button_label: 字符串, document_identifier: 字符串, region_name: 字符串, should_submit: any, key_column: 字符串, key_value: any, [column: 字符串, value: any, ...]): 字符串

创建一个按钮，当点击时，将数据提交到具有指定键的区域。

例如：=submit_to_region_with_key('Submit!', 'ri.fusion.main.document...', 'submit_table', TRUE, 'key_column', A2:A10, 'value_column', B2:B10)将 A2和 B2:10 提交到指定工作表中表 'submit_table' 的 'key_column' 和 'value_column' 列中。

注意：您可以在参数中包含任意数量的key column、value对以出现在接收电子表格中。但是，您必须列出所有希望出现的参数，并按它们将提交的确切顺序列出。

参数

- button_label:字符串指定您希望按钮上显示的字符串。
- document_identifier:字符串插入您的提交将被写入的数据集的 RID。RID 可以在文档的 URL 中识别，类似于 ri.fusion.main...
- region_name:字符串指定您要写入的表区域的名称。如果您尚未指定此表区域，请转到接收电子表格，使用 'create table region' 微件，并为您的表命名一个直观的名称。
- should_submit:ANY对应于您的提交表中包含布尔值（即 true/false）的特定列。如果should_submit为 true，则数据将被提交。
- key_column:字符串指定您希望提交值的列标题。key_column中的每个值必须是唯一的。
- key_value:ANY表示要提交到指定key_column的特定单元格或单元格范围。
- column:字符串
- value:ANY
#### submit_to_region_with_key_and_timestamp(button_label: 字符串, document_identifier: 字符串, region_name: 字符串, should_submit: any, timestamp_column: 字符串, key_column: 字符串, key_value: any, [column: 字符串, value: any, ...]): 字符串

创建一个按钮，当点击时，将数据提交到具有指定键的区域。

例如：=submit_to_region_with_key_and_timestamp('Submit!', 'ri.fusion.main.document...', 'submit_table', TRUE, 'time', 'key_column', A2:A10, 'value_column', B2:B10)将 A2和 B2:10 提交到指定工作表中表 'submit_table' 的 'key_column' 和 'value_column' 列中。当前时间戳将提交到 'time' 列。

注意：您可以在参数中包含任意数量的key column、value对以出现在接收电子表格中。但是，您必须列出所有希望出现的参数，并按它们将提交的确切顺序列出。

参数

- button_label:字符串指定您希望按钮上显示的字符串。
- document_identifier:字符串插入您的提交将被写入的数据集的 RID。RID 可以在文档的 URL 中识别，类似于 ri.fusion.main...
- region_name:字符串指定您要写入的表区域的名称。如果您尚未指定此表区域，请转到接收电子表格，使用 'create table region' 微件，并为您的表命名一个直观的名称。
- should_submit:ANY对应于您的提交表中包含布尔值（即 true/false）的特定列。如果should_submit为 true，则数据将被提交。
- timestamp_column:字符串指定您希望提交当前时间戳的列标题。
- key_column:字符串指定您希望提交值的列标题。key_column中的每个值必须是唯一的。
- key_value:ANY表示要提交到指定key_column的特定单元格或单元格范围。
- column:字符串
- value:ANY
#### submit_to_region_with_key_and_timestamp_lazy(button_label: 字符串, document_identifier: 字符串, region_name: 字符串, should_submit: any, timestamp_column: 字符串, key_column: 字符串, key_value: any, [column: 字符串, value: any, ...]): 字符串

行为与submit_to_region_with_key完全相同，只是它在点击时计算要提交的值，并缓存目标区域信息。如果您要提交大的范围，或者预计会快速连续多次提交到同一区域，请使用此选项。

创建一个按钮，当点击时，将数据提交到具有指定键的区域。

例如：=submit_to_region_with_key_and_timestamp_lazy('Submit!', 'ri.fusion.main.document...', 'submit_table', TRUE, 'time', 'key_column', A2:A10, 'value_column', B2:B10)将 A2和 B2:10 提交到指定工作表中表 'submit_table' 的 'key_column' 和 'value_column' 列中。当前时间戳将提交到 'time' 列。

注意：您可以在参数中包含任意数量的key column、value对以出现在接收电子表格中。但是，您必须列出所有希望出现的参数，并按它们将提交的确切顺序列出。

参数

- button_label:字符串指定您希望按钮上显示的字符串。
- document_identifier:字符串插入您的提交将被写入的数据集的 RID。RID 可以在文档的 URL 中识别，类似于 ri.fusion.main...
- region_name:字符串指定您要写入的表区域的名称。如果您尚未指定此表区域，请转到接收电子表格，使用 'create table region' 微件，并为您的表命名一个直观的名称。
- should_submit:ANY对应于您的提交表中包含布尔值（即 true/false）的特定列。如果should_submit为 true，则数据将被提交。
- timestamp_column:字符串指定您希望提交当前时间戳的列标题。
- key_column:字符串指定您希望提交值的列标题。key_column中的每个值必须是唯一的。
- key_value:ANY表示要提交到指定key_column的特定单元格或单元格范围。
- column:字符串
- value:ANY
#### submit_to_region_with_key_lazy(button_label: 字符串, document_identifier: 字符串, region_name: 字符串, should_submit: any, key_column: 字符串, key_value: any, [column: 字符串, value: any, ...]): 字符串

行为与submit_to_region_with_key完全相同，只是它在点击时计算要提交的值，并缓存目标区域信息。如果您要提交大的范围，或者预计会快速连续多次提交到同一区域，请使用此选项。

创建一个按钮，当点击时，将数据提交到具有指定键的区域。

例如：=submit_to_region_with_key_lazy('Submit!', 'ri.fusion.main.document...', 'submit_table', TRUE, 'time', 'key_column', A2:A10, 'value_column', B2:B10)将 A2和 B2:10 提交到指定工作表中表 'submit_table' 的 'key_column' 和 'value_column' 列中。

注意：您可以在参数中包含任意数量的key column、value对以出现在接收电子表格中。但是，您必须列出所有希望出现的参数，并按它们将提交的确切顺序列出。

参数

- button_label:字符串指定您希望按钮上显示的字符串。
- document_identifier:字符串插入您的提交将被写入的数据集的 RID。RID 可以在文档的 URL 中识别，类似于 ri.fusion.main...
- region_name:字符串指定您要写入的表区域的名称。如果您尚未指定此表区域，请转到接收电子表格，使用 'create table region' 微件，并为您的表命名一个直观的名称。
- should_submit:ANY对应于您的提交表中包含布尔值（即 true/false）的特定列。如果should_submit为 true，则数据将被提交。
- key_column:字符串指定您希望提交值的列标题。key_column中的每个值必须是唯一的。
- key_value:ANY表示要提交到指定key_column的特定单元格或单元格范围。
- column:字符串
- value:ANY
#### substring(value: 数字, index: 数字, length: 数字): 字符串

从value中提取从index（从 1 开始）开始的子字符串，直到长度为length。

例如：假设您在单元格 A1 中有短语 'cow jumped over the moon'，并且想提取子字符串 'cow'。子字符串从索引 1 开始，长度为 3。使用substring(A1, 1, 3)提取字符串 'cow'。

参数

- value:数字
- index:数字
- length:数字
#### subtotal(function_code: 数字, [range: range, ...]): 数字

计算function_code指定的聚合（下文列出）在后续参数中指定的范围上的结果。如果range中有其他小计（或嵌套小计），这些嵌套小计将被忽略以避免重复计算。

function_code的可能代码如下：

- 1 或 101: AVG
- 2 或 102: COUNT_NUMERIC
- 3 或 103: COUNT
- 4 或 104: MAX
- 5 或 105: MIN
- 6 或 106: PRODUCT
- 7 或 107: STDDEV
- 8 或 108: STDDEV_P
- 9 或 109: SUM
- 10 或 110: VARIANCE
- 11 或 111: VARIANCE_P
参数

- function_code:数字
- range:RANGE
#### sum([value: 数字, ...]): 数字

返回一组表达式的和。

例如：sum(23,45,32)将返回 100。

参数

- value:数字
#### sum_distinct([value: 数字, ...]): 数字

返回表达式中不同数值的和（即将忽略所有重复值）。

例如：sum_distinct(23,45,32,45)将返回 100。该函数将忽略第二个 45，因为它不计算重复数字。

参数

- value:数字
#### sum_product([value: any, ...]): 数字

将给定value中的对应组件相乘，并返回这些乘积的和。每个value必须具有相同的维度，所有非数值参数将被视为零。

例如：sum_product(A1:A3, B1:B3)将返回 A1B1 + A2B2 + A3*B3 的和。

参数

- value:ANY
#### sumif(criteria_range: range, condition: any, sum_range: range): number

返回sum_range中所有criteria_range等于condition的值的总和。

注意：criteria_range和sum_range的范围大小必须匹配。

例如：假设A1行包含一个名字列表，C1行包含相应的年龄。如果您想汇总A1中名为'John'的所有人的年龄，请使用sumif(A1:A50, 'John', C1:C50)来获得总和。

参数

- criteria_range:RANGE
- condition:ANY
- sum_range:RANGE
#### sumifs(sum_range: range, [criteria_range: range, condition: any, ...]): number

返回sum_range中所有符合后续条件的值的总和。

例如：sumifs(A1:B5, C1:D5, 10, H4:I8, 'John')返回A1中所有单元格的总和，其中C1中的对应单元格等于10，且H4中的对应单元格等于'John'。

注意：criteria_range和sum_range的范围大小必须匹配。

参数

- sum_range:RANGE
- criteria_range:RANGE
- condition:ANY
#### tan(value: number): number

计算value的正切值。

例如：tan(45)将返回1.6197。

参数

- value:NUMBER
#### timestamp(year: number, month: number, day: number, hour: number, minute: number, second: number): date_time

以格式yyyy-MM-dd HH:mm创建一个带有定义year、month、day、hour、minute、second的时间戳。
对于年份小于1900的时间戳（例如'97'），年份将被解释为从1900年的偏移量（例如'1997'）。

参数

- year:NUMBER
- month:NUMBER
- day:NUMBER
- hour:NUMBER
- minute:NUMBER
- second:NUMBER
#### to_unix_timestamp(date: string, [pattern: string]): number

将带有一个非必填pattern（即日期格式）的时间戳date转换为其UNIX纪元，即自1970年1月1日00:00:00 GMT以来的毫秒数。日期可以是日期、时间戳或字符串。如果提供字符串，可以包含用于解析的模式。

例如：假设您有字符串2021-02-15。日期的pattern是yyyy-MM-dd。要转换此时间戳，请使用to_unix_timestamp('2021-02-15', 'yyyy-MM-dd')。

参数

- date:STRING
- pattern:STRING
#### tooltip(cell_value: any, tooltip_content: string, [open_delay: number]): any

渲染一个带有悬停时出现的工具提示的单元格。

tooltip_content参数可以格式化为一个markdown字符串。open_delay参数可以被用于在悬停时更改工具提示出现的延迟。

参数

- cell_value:ANY
- tooltip_content:STRING
- open_delay:NUMBER
#### trim(value: string): string

去除value两端的空格。

例如：假设您在单元格A1中有字符串'John Smith'，并且两端各有4个空格。trim(A1)将创建一个没有空格的新字符串。

参数

- value:STRING
#### upper(value: string): string

将整个字符串转换为大写。

例如：假设您在单元格A1中有名称John Smith。Upper(A1)将返回JOHN SMITH。

参数

- value:STRING
#### url(url: string, [label: string]): any

渲染一个带有非必填label的url超链接。

例如：url('myblog.com', 'My Blog')将创建一个带有标签'My Blog'的超链接。

参数

- url:STRING
- label:STRING
#### url_encode(input: any): string

将input编码为可安全用于URL路径和参数。

例如：=url(concat('http://example.com/test?param=', url_encode(A5)))

参数

- input:ANY
#### variance([value: number, ...]): number

返回一组值的无偏差方差。

例如：variance(23, 45, 32)将返回122.33。

参数

- value:NUMBER
#### variance_p([value: any, ...]): number

返回一组值的有偏差方差，假设value项构成整个总体。

注意：如果它们仅代表总体的样本，请使用VARIANCE。

参数

- value:ANY
#### vlookup(value: any, range: range, column: number): any

在range的第一列中查找value并获取column（从1开始）。

例如：假设A列是一个水果名称列表，C列是价格列表。vlookup(A3,A1:C6,3)将获取单元格A3中的水果名称，并返回指定范围内第3列中的相应价格。

参数

- value:ANY
- range:RANGE
- column:NUMBER
#### week_of_year(date: date_time): number

计算date的周数作为整数。

例如：Week_of_year('2021-06-18')将返回24。

参数

- date:DATE_TIME
#### workday(start_date: date_time, value: number, [holidays: any]): date

返回表示工作日的日期，该日期是指示的工作日数之前或之后的日期（起始日期）。工作日不包括周末和假日。

例如：workday('2010-01-01',10)将返回2010-01-15，因为忽略了周末。另一个例子：workday('2010-01-01',10, '2010-01-05')返回2010-01-18，因为忽略了周末加上一个假日。

参数

- start_date:DATE_TIME
- value:NUMBER
- holidays:ANY
#### year(date: date_time): number

提取date的年份作为整数。

例如：假设您在单元格A2中有时间戳2022-02-15 08:30:15。Year(A2)将返回2022。

参数

- date:DATE_TIME
## 操作函数

Fusion的默认操作库方法。

#### compute_on_trigger(actionCell: any): any [实验性]

在触发时惰性计算作为参数传入的actionCell引用中的操作。

这不会被视为该单元格的依赖关系，从而在某些情况下避免循环依赖。

参数

- actionCell:ANY
#### copy_range(source: any, target: range, [copy_result: boolean]): string

当触发时，将内容从一个范围复制到另一个范围的操作。

参数

- source:ANY要从中复制的单元格范围。如果想清空目标，可以为NULL
- target:RANGE
- copy_result:BOOLEAN如果为true，则复制计算的单元格值。如果为false或未提供，则复制单元格公式。
#### dropdown(values: array, [selected_value: string], [actionBeforeChange: any], [allow_invalid: boolean], [placeholder_text: string]): any [实验性]

渲染一个下拉菜单，值可以从提供的values数组中选择。values必须是唯一的，因为每个值在下拉菜单中都转换为一个字符串标签。

此函数不能嵌套在action.serial或action.parallel中。

例如：=action.dropdown(array('red', 'blue', 'green'))将创建一个下拉菜单，值为'red'，'blue'，'green'。

当提供actionBeforeChange时，它指定将在保存和被其他公式考虑之前执行的操作。

当提供selected_value时，它指定下拉菜单的默认字符串标签。selected_value是非必填的，可以设置为null，这将默认下拉菜单的选择为未选择状态。如果selected_value已设置且所选标签不再在values数组中找到（例如如果底层数据更改），结果将是一个空单元格。

当allow_invalid设置为true时，它将覆盖此行为，并仍然输出先前保存的选择。此结果只能是字符串，并且仅在尝试从一组字符串值中保留先前选择时才推荐使用。

placeholder_text允许在未选择值时在下拉菜单中显示文本（这可以用作提示或说明）

参数

- values:ARRAY
- selected_value:STRING
- actionBeforeChange:ANY
- allow_invalid:BOOLEAN
- placeholder_text:STRING
#### fail(): any

一个无操作的失败操作。可以在串行中结合使用以进行短路。

#### label(type: string, label: string, [icon: string], [intent: string]): string

渲染一个标签。类型可以是：'button'、'link'或'tag'。

例如：action.label('button', 'Submit', 'tick', 'success')将渲染一个带有勾号和单词'Submit'的绿色按钮。

参数

- type:STRING
- label:STRING
- icon:STRING可以在Blueprint 文档 ↗中查看图标列表。
- intent:STRINGintent定义标签的颜色：'primary'为蓝色，'success'为绿色，'warning'为橙色，'danger'为红色。可以在Blueprint 文档 ↗中查看意图及其输出的完整列表。
#### open_markdown_panel(panel_title: string, markdown_content: string): string

打开一个带有提供标题和markdown字符串的上下文侧面板。

如果使用CSS样式进行markdown，可以使用.fusion-markdown-panel类进行范围限定。

参数

- panel_title:STRING
- markdown_content:STRING
#### open_url(url: string, [redirect: boolean]): string

打开一个URL，默认为在新标签页中打开，如果想重定向现有电子表格页面，请将redirect参数设置为true。

参数

- url:STRING
- redirect:BOOLEAN
#### parallel([action: any, ...]): string

给定一组操作，一次触发所有操作。

- action:ANY
#### plugin(action_name: string, [arg: any, ...]): any

运行部署到该服务器的自定义操作。请联系您的Palantir代表以获取可用操作的列表。

参数

- action_name:STRING
- arg:ANY
#### serial(action: any, actionOnSuccess: any, [actionOnFailure: any]): string

定义仅在上一个操作成功（或失败）时发生的操作。

参数

- action:ANY
- actionOnSuccess:ANY
- actionOnFailure:ANY
#### submit_options([key: string, value: any, ...]): options [实验性]

为action.submit_to_region_with_options(...)配置键值选项。

可用选项：

- submitEmptyCells: 空或null单元格将覆盖此列目标表中存在的数据
- succeedWhenNoRows: 更改操作行为以便在shouldSubmit为false或所有行均为false时成功，而不是失败并显示通知
参数

- key:STRING
- value:ANY
#### submit_to_region(document_identifier: string, region_name: string, should_submit: any, timestamp_column: string, key_column: string, key_value: any, [column: string, value: any, ...]): string

创建一个按钮以指定键提交数据到区域。

例如：=action.submit_to_region('ri.fusion.main.document...', 'submit_table', TRUE, 'time', 'first_column', A1:A10, 'second_column', B1:B10)将A1和B1:10分别提交到表'submit_table'的'first_column'和'second_column'列中，在指定的表格中。当前时间戳将提交到'time'列。

参数

- document_identifier:STRING插入您的提交将写入的数据集的RID。RID可以在文档的URL中识别，看起来像ri.fusion.main...。document_metadata('document_identifier')可以用于引用当前表格的RID。
document_identifier:STRING插入您的提交将写入的数据集的RID。RID可以在文档的URL中识别，看起来像ri.fusion.main...。document_metadata('document_identifier')可以用于引用当前表格的RID。

- region_name:STRING指定您要写入的表格区域的名称。如果您尚未指定此表格区域，请转到接收电子表格，使用'create table region'微件，并给表格一个直观的名称。
region_name:STRING指定您要写入的表格区域的名称。如果您尚未指定此表格区域，请转到接收电子表格，使用'create table region'微件，并给表格一个直观的名称。

- should_submit:ANY对应于提交表格中的特定列，该列包含布尔值（即true/false）。如果should_submit为true，则数据将提交。
should_submit:ANY对应于提交表格中的特定列，该列包含布尔值（即true/false）。如果should_submit为true，则数据将提交。

- timestamp_column:STRING指定您希望提交当前时间戳的列头。使用null如果不需要时间戳。
timestamp_column:STRING指定您希望提交当前时间戳的列头。使用null如果不需要时间戳。

- key_column:STRING指定您希望提交值的列头。
key_column:STRING指定您希望提交值的列头。

- key_value:ANY表示要提交到指定key_column的特定单元格或单元格范围。
key_value:ANY表示要提交到指定key_column的特定单元格或单元格范围。

- column:STRING
column:STRING

- value:ANY
value:ANY

#### submit_to_region_with_options(document_identifier: string, region_name: string, submit_options: options, should_submit: any, timestamp_column: string, key_column: string, key_value: any, [column: string, value: any, ...]): string [实验性]

创建一个按钮以指定键提交数据到区域。

例如：=action.submit_to_region_with_options('ri.fusion.main.document...', 'submit_table', TRUE, 'time', 'first_column', A1:A10, 'second_column', B1:B10)将A1和B1:10分别提交到表'submit_table'的'first_column'和'second_column'列中，在指定的表格中。当前时间戳将提交到'time'列。

参数

- document_identifier:STRING插入您的提交将写入的数据集的RID。RID可以在文档的URL中识别，看起来像ri.fusion.main...。document_metadata('document_identifier')可以用于引用当前表格的RID。
- region_name:STRING指定您要写入的表格区域的名称。如果您尚未指定此表格区域，请转到接收电子表格，使用'create table region'微件，并给表格一个直观的名称。
- submit_options:OPTIONS指定用于提交操作的可配置选项，使用action.submit_options(...)，submit_options函数文档中的可能值
- should_submit:ANY对应于提交表格中的特定列，该列包含布尔值（即true/false）。如果should_submit为true，则数据将提交。
- timestamp_column:STRING指定您希望提交当前时间戳的列头。使用null如果不需要时间戳。
- key_column:STRING指定您希望提交值的列头。
- key_value:ANY表示要提交到指定key_column的特定单元格或单元格范围。
- column:STRING
- value:ANY
#### success(): any

一个无操作的成功操作。可以在串行中结合使用以进行短路。

#### toast(message: string, [intent: string], [dismissButton: string]): string

触发一个通知。叮！

如果定义了dismissButton，通知将停留直到用户点击关闭按钮。如果通知被action_serial函数包裹，随后的操作将被触发。

参数

- message:STRING
- intent:STRING
- dismissButton:STRING
#### trigger(label: any, action: any): string

给定一个标签和一个操作，当点击标签时触发操作。

使用action_label函数配置标签。

参数

- label:ANY
- action:ANY
#### validate_table(table_range: range, [condition: any, ...]): string

给定一个范围和一组条件，验证所有条件是否满足。

参数

- table_range:RANGE
- condition:ANY
## 验证函数

Fusion的默认验证库方法。

#### column_enum(column_name: string, allowed_values: array): string

给定一个列名和一组允许的值，验证该列中所有非空值是否在允许的列表中。

参数

- column_name:STRING
- allowed_values:ARRAY
#### column_not_null([column_name: string, ...]): string

给定一组列名，验证它们在非空行中不为空。即这些列只能在整行为空时为空。

参数

- column_name:STRING
#### column_numeric([column_name: string, ...]): string

给定一组列名，验证每列仅包含数值。

参数

- column_name:STRING
#### column_regex(column_name: string, regex: string): string

给定一个列名和一个正则表达式字符串，验证该列中所有值是否匹配给定的正则表达式。

参数

- column_name:STRING
- regex:STRING
#### table_headers([column_name: string, ...]): string

给定一组列名，验证它们在定义的表中是否存在。

参数

- column_name:STRING
#### table_key([column_name: string, ...]): string

给定一组列名，验证它们的组合在表中是否唯一。例如：给定一个范围，其中第一行包含这两个列名：Name和Age：如果有两条记录：[Bob, 20]和[Bobby, 20]，那么table_key('Name', 'Age')应该成功。然而，如果两条记录是：[Bob, 20]和[Bob, 20]，那么table_key('Name', 'Age')应该失败。

参数

- column_name:STRING
## 图表函数

用于绘制数据的方法。

#### bar(x_values: any, y_values: any, [options: any, ...]): barplot

在柱状图上绘制一系列xy值。

可用选项：

- drawLabels: boolean
- orientation: "horizontal" | "vertical"
参数

- x_values:ANY
- y_values:ANY
- options:ANY
#### chart([Plots-or-options: any, ...]): chart

在图表上绘制多个系列，具有可配置选项。

可用选项：

- showAxes: boolean
- showLegend: boolean
- showResetZoomButton: boolean
- showToolbar: boolean
- tooltip: false | "closest" | "aggregate"
- yAxisInset: boolean
- rangeSelection: "select" | "visual" | false
- height: number (px)
- width: number (px)
- Plots-or-options:ANY
#### line(x_values: any, y_values: any, [options: any, ...]): lineplot

在折线图上绘制一系列xy值。
可用选项：

- dataMarkers: boolean
- color: string
参数

- x_values:ANY
- y_values:ANY
- options:ANY
#### options([key: string, value: any, ...]): options

可配置键值选项图表。

参数

- key:STRING
- value:ANY
## 时间序列函数

与时间序列交互的方法。

#### count(timeSeries: any): number

返回系列中的点数。

参数

- timeSeries:ANY
#### derivative(timeSeries: any): any

对时间序列求导数（关于秒）。

参数

- timeSeries:ANY
#### difference(timeSeries: any): number

返回系列中第一个值与最后一个值之间的差异。

参数

- timeSeries:ANY
#### first_timestamp(timeSeries: any): time

返回时间序列中第一个点的时间戳。

参数

- timeSeries:ANY
#### first_value(timeSeries: any): any

返回时间序列中第一个点的值。

参数

- timeSeries:ANY
#### integral(timeSeries: any, method: string): any

对于子系列中的每个点，输出到该点为止的系列下的总面积。

支持三种不同的积分方法：linear，使用梯形规则进行积分近似，lhs/lhr分别使用左和右黎曼和。

参数

- timeSeries:ANY
- method:STRING
#### last(timeSeries: any, timeAmount: number, timeUnit: string): any

筛选时间序列以保留指定持续时间的最后部分。

支持的单位：

- hours/h
- minutes/m
- seconds/s
- microseconds/us
- nanoseconds/ns
参数

- timeSeries:ANY
- timeAmount:NUMBER
- timeUnit:STRING
#### last_timestamp(timeSeries: any): time

返回时间序列中最后一个点的时间戳。

参数

- timeSeries:ANY
#### last_value(timeSeries: any): any

返回时间序列中最后一个点的值。

参数

- timeSeries:ANY
#### max(timeSeries: any): number

返回整个时间序列的最大值。

参数

- timeSeries:ANY
#### mean(timeSeries: any): number

返回整个时间序列的平均值。

参数

- timeSeries:ANY
#### min(timeSeries: any): number

返回整个时间序列的最小值。

参数

- timeSeries:ANY
#### scale(timeSeries: any, scale: number): any

取每个滴答并将值乘以指定的因子。

也就是说，对于包含滴答(t, v)的源时间序列，经过x缩放后，结果缩放时间序列将有滴答(t, v * x)。

参数

- timeSeries:ANY
- scale:NUMBER
#### shift(timeSeries: any, shift: number): any

取时间序列的每个点并按指定量偏移值。

也就是说，对于包含滴答(t, v)的源时间序列，经过x偏移后，结果值偏移时间序列将有滴答(t, v + x)。

参数

- timeSeries:ANY
- shift:NUMBER
#### stddev(timeSeries: any): number

返回整个时间序列的标准偏差。

参数

- timeSeries:ANY
#### time_range(timeSeries: any, startTime: any, endTime: any): any

选择时间序列的特定时间范围。

参数

- timeSeries:ANY
- startTime:ANY
- endTime:ANY
#### timeseries(seriesId: string): any

返回给定ID的时间序列。

参数

- seriesId:STRING