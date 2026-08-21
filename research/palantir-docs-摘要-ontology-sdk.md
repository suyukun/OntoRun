# Palantir 文档精读摘要（A 栏：机制事实）

> 编制：Rose ｜ 日期：2026-08-21 ｜ 来源：Palantir Foundry 官方中文文档（AIP 机器翻译）
> 用途：S2 复核输入包的 A 栏（客观机制事实），B 栏（对 OntoRun 的启示）留白给复核模型

## ontology-sdk 模块
- **OSDK**：开发环境直接访问 Ontology 的 SDK，支持 TS/Python/Java，其余语言可导 OpenAPI 生成；只为应用所选实体子集生成类型/函数，叠加用户数据权限。
- **查询机制**：对象 get()/fetch() 按主键取单个；page(page_size, page_token) 分页带 next_page_token；iterate() 自动翻页拉全量。
- **过滤**：按属性类型 startsWith/containsAnyTerm(fuzzy)/containsAllTerms/lt/gt/lte/gte/eq/isNull；布尔组合 Java $not/$and/$or、Python ~/&/|。
- **聚合**：approximateDistinct（近似去重）/count/数值 avg/max/min/sum；groupBy exact(maxGroupCount)/fixedWidth/range/日期时间分桶（秒/分/时/天/周/月/季/年）；响应含 excludedItems。
- **动作**：apply() 单条返回 validation(VALID/INVALID + 提交标准 + 参数级约束) 与 edits；applyBatch() 批量返回 edits 不返回验证；ReturnEditsMode ALL/NONE。
- **函数(FoO)**：Java client.ontology().queries().<q>().execute()；TS client(q).executeFunction()，可返回 ObjectSet。
- **认证**：用户权限=授权码 OAuth；应用权限=客户端凭据 OAuth + 服务用户；密钥仅创建时可见一次。
- **权限生效**：应用角色 Viewer(只读)/Editor/Owner；资源访问范围随添加资源自动纳入。
- **限制**：Phonograph(OSV1) 上限 10,000 结果（ObjectsExceededLimit）；pageSize 上限 10,000 且首页决定后续页；Python SDK 限 3.9-3.11。
- **来源**：research/palantir_foundry_docs/palantir_docs/ontology-sdk/（18 文件全读）
