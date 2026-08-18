来源: https://palantir.com/docs/zh/foundry/carbon/code-reference/

# YAML 配置参考

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# YAML 配置参考

Carbon 工作区可以直接在 YAML 中编辑，也可以使用图形用户界面编辑。本页包含如何配置 Carbon 工作区不同部分的 YAML 示例，以 Claims Portal 为例。Claims Portal 示例的完整 YAML 可以在YAML 代码示例中找到。

## 元数据和常规配置

### 工作区的名称和描述

```
Copied!1
2
3
displayMetadata:
  title: Claim Portal  # 索赔门户
  description: Everything related to claim management  # 与索赔管理相关的所有内容
```

### 设置自定义图标

#### 蓝图图标

```
Copied!1
2
3
4
5
6
7
        icon:
          type: blueprintIcon
          blueprintIcon:
            iconName: music  # 图标名称为“music”
            color:
              type: custom
              custom: '#FF66A1'  # 自定义颜色，十六进制代码为#FF66A1
```

#### Palantir 应用程序图标

```
Copied!1
2
3
4
5
6
7
        icon:
          type: applicationIcon  # 图标类型为应用程序图标
          applicationIcon:
            iconName: contour-app  # 图标名称为 contour-app
            color:
              type: custom  # 颜色类型为自定义
              custom: '#FF66A1'  # 自定义颜色代码为 #FF66A1
```

### 设置可发现的模块

```
Copied!1
2
3
discoverableModules:
  - ri.workshop.main.module.25b772f5-a095-48c6-a889-a960eeb93ce1  # 可被发现的模块之一，唯一标识符为UUID格式
  - ri.workshop.main.module.6e10d8bb-90a4-47d2-86e3-3f10bfca0a1e  # 另一个可被发现的模块，UUID格式标识符
```

## Carbon 菜单栏

### 锚定模块

#### 锚定模块：工作坊示例

```
Copied!1
2
3
4
5
6
configuration:
  moduleShortcuts:
    primary:
      - title: Alert Inbox  # 警报收件箱
        moduleRid: ri.workshop.main.module.a1838b32-448d-43f6-beff-3c9e40a34929
        parameterValues: {}
```

#### 锚定模块：Object View 示例

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
configuration:
  moduleShortcuts:
    primary:
      - title: Order BF645S
        description: null  # 描述为空
        icon:
          type: blueprintIcon
          blueprintIcon:
            iconName: eye-open  # 图标名称为“eye-open”
            color:
              type: custom
              custom: '#FFC940'  # 图标颜色为自定义的黄色（#FFC940）
        moduleRid: ri.carbon..core-module.object-view  # 模块的资源标识符
        parameterValues:
          objectRid:
            type: object
            object:
              objectRid: ri.phonograph2-objects.main.object.ab863bd7-c82c-482f-9218-9ba1df79bd3c  # 对象的资源标识符
```

该YAML配置定义了一个模块快捷方式，主要包括一个名为“Order BF645S”的项目。图标是一个自定义颜色的“eye-open”图标，并关联到特定的模块和对象资源标识符。

#### 锚定模块：Object Explorer 示例

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
configuration:
  moduleShortcuts:
    primary:
      - title: Cancelled Orders  # 标题：取消的订单
        description: null  # 描述：空
        icon:
          type: blueprintIcon  # 图标类型：蓝图图标
          blueprintIcon:
            iconName: clipboard  # 图标名称：剪贴板
            color:
              type: custom  # 颜色类型：自定义
              custom: '#2EE6D6'  # 自定义颜色：#2EE6D6
        moduleRid: ri.carbon..core-module.exploration  # 模块标识符
        parameterValues:
          objectSetRid:
            type: string  # 类型：字符串
            string:
              string: ri.object-set.main.versioned-object-set.36824ec3-3746-4d74-9e96-5094b8c8630e  # 对象集标识符
```

这个 YAML 配置片段定义了一个模块快捷方式，主要用于“取消的订单”。它包含一个自定义颜色的剪贴板图标，并且关联了特定的对象集标识符。

#### 锚定模块：搜索示例

```
Copied!1
2
3
4
5
6
configuration:
  moduleShortcuts:
    primary:
      - title: Search  # 搜索
        moduleRid: ri.carbon..core-module.search  # 模块资源ID
        parameterValues: {}  # 参数值
```

### 多标签模块

#### 多标签模块：工作坊示例

```
Copied!1
2
3
4
5
6
configuration:
  moduleShortcuts:
    secondary:
      - title: Alert Inbox # 标题：警报收件箱
        moduleRid: ri.workshop.main.module.a1838b32-448d-43f6-beff-3c9e40a34929 # 模块唯一标识符
        parameterValues: {}  # 参数值为空，表示没有额外参数
```

#### 多标签模块：Object视图示例

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
configuration:
  moduleShortcuts:
    secondary:
      - title: Order BF645S  # 标题：Order BF645S
        description: null  # 描述：空
        icon:
          type: blueprintIcon  # 图标类型：蓝图图标
          blueprintIcon:
            iconName: eye-open  # 图标名称：eye-open
            color:
              type: custom  # 颜色类型：自定义
              custom: '#FFC940'  # 自定义颜色：#FFC940
        moduleRid: ri.carbon..core-module.object-view  # 模块RID：ri.carbon..core-module.object-view
        parameterValues:
          objectRid:
            type: object  # 类型：对象
            object:
              objectRid: ri.phonograph2-objects.main.object.ab863bd7-c82c-482f-9218-9ba1df79bd3c  # 对象RID：ri.phonograph2-objects.main.object.ab863bd7-c82c-482f-9218-9ba1df79bd3c
```

#### 多标签模块：Object Explorer 示例

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
configuration:
  moduleShortcuts:
    secondary:
      - title: Cancelled Orders # 取消订单
        description: null
        icon:
          type: blueprintIcon
          blueprintIcon:
            iconName: clipboard # 图标名称：剪贴板
            color:
              type: custom
              custom: '#2EE6D6' # 自定义颜色
        moduleRid: ri.carbon..core-module.exploration # 模块资源ID
        parameterValues:
          objectSetRid:
            type: string
            string:
              string: ri.object-set.main.versioned-object-set.36824ec3-3746-4d74-9e96-5094b8c8630e # 对象集资源ID
```

以上是一个 YAML 配置文件的代码片段，主要用于设置模块快捷方式。它包括模块的标题、图标和参数值等信息。

#### 多标签模块：搜索示例

```
Copied!1
2
3
4
5
6
configuration:
  moduleShortcuts:
    secondary:
      - title: Search
        moduleRid: ri.carbon..core-module.search
        parameterValues: {}  # 参数值设为空，表示没有特别参数需要传递给搜索模块
```

在上面的代码中，moduleRid是模块的唯一标识符。parameterValues是传递给模块的参数，此处为空表示没有参数。

## 首页

### 自定义标志 - 非必填

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
configuration:
  homePage:
      logo:
      source:
        type: compassResource  # 指定资源的类型为 compassResource
        compassResource:
          resourceRid: ri.blobster.main.image.50505d65-4001-4f55-8fda-669f52347745  # 资源的唯一标识符
      maxWidth: 60  # 图标的最大宽度
      maxHeight: 60  # 图标的最大高度
```

### 设置部分标题和描述

#### 添加标题和描述 - 非必填

```
Copied!1
2
3
4
5
6
7
8
configuration:
  homePage:
    columns:
      - sections:
          - title: Triaging apps  # 分类应用
            description: All the apps you need to triage claims  # 所有用于分类索赔的应用
            displayAs: null
            contents:
```

### 更改部分项目的显示类型

#### 将部分项目显示为列表 - 非必填

请注意，列表是默认选项。

```
Copied!1
2
3
4
5
6
configuration:
  homePage:
    columns:
      - sections:
          - displayAs: LIST  # 显示方式设置为列表
            contents:  # 内容部分
```

#### 将部分项目显示为卡片 - 非必填

```
Copied!1
2
3
4
5
6
configuration:
  homePage:
    columns:
      - sections:
          - displayAs: CARD  # 以卡片形式显示
            contents:  # 内容部分
```

### 默认部分显示所有模块

```
Copied!1
2
3
4
5
6
7
configuration:
  homePage:
    columns:
      - sections:
          - contents:
              type: modules # 定义内容的类型为模块
              modules: {}   # 模块的具体内容，目前为空
```

### 显示所有已保存探索的默认部分

```
Copied!1
2
3
4
5
6
7
configuration:
  homePage:
    columns:
      - sections:
          - contents:
              type: savedExplorations  # 内容的类型设定为已保存的探索
              savedExplorations: {}    # 已保存的探索，这里是一个空字典，意味着目前没有保存任何探索
```

### 默认部分显示所有重要Object类型

```
Copied!1
2
3
4
5
6
7
configuration:
  homePage:
    columns:
      - sections:
          - contents:
              type: objectTypes
              objectTypes: {}  # 这里定义了一个空的对象类型映射，可能需要在此处指定具体的对象类型
```

### 默认部分显示特定对象类型

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
configuration:
  homePage:
    columns:
      - sections:
          - contents:
              type: objectTypes  # 指定类型为objectTypes
              objectTypes:
                objectTypes:
                  - objectTypeRid: ri.ontology.main.object-type.14014a36-91d6-45b7-a288-bda5f2881568  # 对象类型的唯一标识符
                  - objectTypeRid: ri.ontology.main.object-type.e5a5adea-cfa4-4a80-808b-3dbbe7e0bc4b  # 另一对象类型的唯一标识符
```

### 默认部分显示特定Objects

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
configuration:
  homePage:
    columns:
      - sections:
          - contents:
              type: objects  # 定义内容的类型为对象
              objects:
                objects:
                  - objectRid: ri.phonograph2-objects.main.object.17474c05-bfa3-4477-adc8-9c98e65b0269  # 对象的唯一标识符
                  - objectRid: ri.phonograph2-objects.main.object.048f39e4-10af-48be-9736-d24191242732  # 另一个对象的唯一标识符
```

此段 YAML 配置文件定义了主页的结构，其中包含一个内容类型为"objects"的部分。每个对象通过objectRid唯一标识符进行引用。

### 自定义部分与模块项 - Workshop模块

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
configuration:
  homePage:
    columns:
      - sections:
          - title: null
            description: null
            contents:
              type: custom
              custom:
                items:
                  - type: module
                    module:
                      displayMetadata: {}  # 显示元数据，当前为空
                      moduleRid: ri.workshop.main.module.525ab70b-d24b-42f4-ad25-a407f0273b83  # 模块的唯一标识符（资源 ID）
                      parameterValues: {}  # 模块的参数值，当前为空
```

### 自定义部分与模块项 - Workshop模块与模块接口变量

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
configuration:
  homePage:
    columns:
      - sections:
          - title: null
            description: null
            contents:
              type: custom
              custom:
                items:
                  - type: module
                    module:
                      displayMetadata: {}
                      moduleRid: ri.workshop.main.module.525ab70b-d24b-42f4-ad25-a407f0273b83
                      parameterValues:
                        variable.status:
                            type: string
                            string:
                                string: Open # 变量“status”的值为字符串类型，内容为“Open”
```

此YAML配置文件定义了一个主页配置，包含多个列和部分。在给定的部分中，内容类型为自定义，具体项为一个模块，其中包含一个参数“status”，其值为字符串“Open”。
要将模块接口变量传递给工作室模块，请将其添加到parameterValues映射中，并加上variable.前缀。在上述示例中，具有外部IDstatus的模块接口字符串变量以值Open传递给工作室模块。

### 带有模块项的自定义部分 - Object View模块 - Object View

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
configuration:
  homePage:
    columns:
      - sections:
          - title: null
            description: null
            contents:
              type: custom
              custom:
                items:
                  - type: module
                    module:
                      displayMetadata: {}
                      moduleRid: ri.carbon..core-module.object-view  # 模块标识符，引用了一个对象查看模块
                      parameterValues:
                        objectRid:
                            type: object
                            object:
                                objectRid: ri.phonograph2-objects.main.object.ab863bd7-c82c-482f-9218-9ba1df79bd3c  # 对象标识符，指定了要查看的具体对象
```

该代码片段是一个 YAML 配置文件的一部分，定义了主页的布局和模块配置。moduleRid和objectRid分别指定了模块和对象的唯一标识符。

### 自定义部分与模块项 - Object Explorer 模块 - 对象集

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
configuration:
  homePage:
    columns:
      - sections:
          - title: null
            description: null
            contents:
              type: custom
              custom:
                items:
                  - type: module
                    module:
                      displayMetadata: {}
                      moduleRid: ri.carbon..core-module.exploration
                      parameterValues:
                        objectSetRid:
                            type: string
                            string:
                                # 指定对象集合的唯一标识符（RID）
                                string: ri.object-set.main.versioned-object-set.36824ec3-3746-4d74-9e96-5094b8c8630e
```

在这段代码中，我们配置了一个主页，主页的某个部分包含一个自定义模块。这个模块中关键的部分是objectSetRid，它用来指定一个对象集合的唯一标识符（RID）。moduleRid指定了模块的类型，这里是一个探索模块。parameterValues包含该模块所需的参数值。

### 具有Object类型项的自定义部分

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
configuration:
  homePage:
    columns:
      - sections:
          - title: null # 标题为空
            description: null # 描述为空
            contents:
              type: custom # 自定义类型
              custom:
                items:
                  - type: objectType # 项目类型
                    objectType:
                      objectTypeRid: ri.ontology.main.object-type.14014a36-91d6-45b7-a288-bda5f2881568 # 对象类型的唯一标识符
```

此配置文件可能用于定义主页的布局和内容，其中包括一个自定义对象类型的项。

### 包含Object项的自定义部分

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
configuration:
  homePage:
    columns:
      - sections:
          - title: null
            description: null
            contents:
              type: custom
              custom:
                items:
                  - type: object
                    object:
                      objectRid: ri.phonograph2-objects.main.object.17474c05-bfa3-4477-adc8-9c98e65b0269
                      # objectRid 是一个唯一标识符，用于引用特定对象
```

### 带有资源项的自定义部分

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
configuration:
  homePage:
    columns:
      - sections:
          - title: null
            description: null
            contents:
              type: custom
              custom:
                items:
                  - type: compassResource
                    compassResource:
                      displayMetadata:
                        title: Fusion Sheet # 显示的标题为“Fusion Sheet”
                        description: For spreadsheet use cases # 描述信息为“用于电子表格的用例”
                      targetResource:
                        resourceRid: ri.fusion.main.document.01eaf763-c721-4557-b368-42be112e40a3 # 目标资源的ID
```

这个YAML配置文件定义了一个主页配置，其中包括一个自定义的内容项。该内容项的类型为compassResource，显示的标题为“Fusion Sheet”，描述为“用于电子表格的用例”，并且指向一个特定的资源ID。

### 使用Palantir应用程序项的自定义部分

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
configuration:
  homePage:
    columns:
      - sections:
          - title: null
            description: null
            contents:
              type: custom
              custom:
                items:
                  - type: foundryApplication
                    foundryApplication:
                      displayMetadata: {}
                      workspaceApplicationName: contour-app  # 工作区应用名称为 contour-app
                      relativeUrl: null  # 相对URL为null
```

上述YAML配置文件片段定义了一个首页配置，其中包含一个自定义类型的内容项。该项是一个工作区应用，名为contour-app，相对URL未设置（为null）。
