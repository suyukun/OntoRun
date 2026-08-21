# OntoRun S2 P2/P3 独立 Red-team 审查报告

> 审查者：独立 red-team（对抗性复核）｜ 日期：2026-08-21
> 范围：P2 ChatBI 读侧（src/des/metrics.py、metrics_materialize.py、contract.py、src/runtime/permissions.py）+ P3 映射治理（src/builder/mapping/{review,publish,calibrate,annotate}.py）+ 设计文档 P2/P3/P1.5
> 方法：全量读代码 + 针对性冒烟脚本（/tmp/smoke*.py）复现关键发现；只审查不改代码；未跑全量 pytest
> 结论先行：**P0 阻断 = 0 项；P1 高风险 = 4 项；P2 中风险 = 9 项；P3 建议 = 10 项**（详见文末 Top 3）

---

## 〇、审查基线（防止"自圆其说"）

- 设计与交付口径核对：P2 完成记录（docs/S2-P2-ChatBI闭环完成记录.md）**如实声明**了 3 项待办：head-to-head 实验未跑、读侧权限 API 接线留 P4、4 个本体对象注册待 Jack 拍板——本报告不重复批评这 3 项"已声明待办"，但对其中**直接违背设计门禁语义**的部分单独成项（见 P1-1）。
- P3 设计（docs/P3-映射治理设计_v0.1.md §0.1/§5）声明了 4 件交付物 + 门禁测试集，实际落地的只有 review/publish/calibrate 三个模块，**管道编排与影响分析未交付、门禁测试集完全缺失**（见 P1-4）。
- 已复现发现的冒烟脚本：`/tmp/smoke1.py`（哈希链）、`/tmp/smoke2.py`+3.py（校准/审核）、`/tmp/smoke4.py`（发布）、`/tmp/smoke5.py`（C4 死锁）、`/tmp/smoke6.py`（time_range 忽略）、`/tmp/smoke7.py`（权限下未注册对象）。

---

## 一、P1 高风险（4 项）

### P1-1 读侧权限仅在库层面实现为"可选参数"，全代码无任何调用方接线；缺省 fail-open（绕过条件 = 不传 ctx 即跳过）

- **位置**：src/des/contract.py:511（`permission_ctx: PermissionContext | None = None`）、:595-597（`if ctx is None: return None`）；全 src 无一处构造 ContractExecutor 时传 permission_ctx（grep 证实）。
- **问题描述**：设计 P2 §3.3 将"契约执行器前置调 decide(read) + 属性级 visible_attributes"列为 P2 读侧闭环内容；实现把权限做成"缺省 None = 无校验"的可选开关，且**当前不存在任何接入点**（无 FastAPI 路由、无 Agent 层接线）。这等于读侧权限是死代码：只要将来在 API/Agent 层按库默认构造执行器（或忘了传 ctx），权限即整体静默关闭。完成记录自认"读侧权限 API 接线留 P4"（docs/S2-P2-ChatBI闭环完成记录.md:29），与设计 §3.3 的 P2 口径冲突。
- **证据**：`test_permission_no_ctx_compat`（tests/test_p2_chatbi.py:637-651）显式把"无 ctx 照常执行"固化为预期行为；grep `permission_ctx` 仅出现于 contract.py 定义处，无调用点。
- **风险**：默认 fail-open 的权限体系在"忘记接线"时无任何失败信号——安全的程序应 fail-closed。
- **修复建议**：① 构造执行器的唯一入口（未来 API 层）强制要求 PermissionContext（不传即拒绝初始化或默认走 deny）；② 把"是否启用权限"写入可见的配置/启动检查（self_check 检查）而不是参数缺省；③ 若 P4 才接线，至少在 P2 阶段提供一个"默认 deny"的 ctx 工厂并写文档告警。

### P1-2 link_traversal 目标对象读权限完全未检（真实绕过，已复现）

- **位置**：src/des/contract.py:543-549（只对 source 对象 obj.name 做 `_assert_fields_visible`）、:696-699（`_build_items` 对 link 目标 `SELECT * FROM {target.source_table}` 直读，无 decide）。
- **问题描述**：v0.1 路径带 link_traversal 时，目标对象（如 Material.codes → Code）的整表数据被无条件读出并返回 `codes` 数组，**不经过目标对象的 decide(read)**。若目标对象配置了 deny/无策略（fail-closed 应拒绝），仍会返回数据。
- **证据**（已复现，/tmp/smoke2.py）：Material 对象级 read allow、Code 无任何策略，执行 DQ01_CONTRACT（含 link material.codes）成功返回 1200 条 + 每条的 codes 数组（code_space/value）。
- **风险**：属性级/对象级读权限可被 link_traversal 系统性旁路；被 deny 的敏感对象（如财务、客户）只要被注册成某个允许对象的 link 目标即泄数据。
- **修复建议**：`_build_items` 前对 target 对象执行 `decide(subject, target.object_type, "read")`；link 返回列（fk_field、code_space/value 等）同样过 visible_attributes 过滤；fail-closed 拒答。补测试：link 目标被 deny 时契约必须拒答。

### P1-3 P3 审核/发布 approve 权限门完全缺失（设计 §2.1/§4.1 明确要求，未实现）

- **位置**：src/builder/mapping/review.py:94-183（import_decisions/_apply_decision 无任何 decide 调用）、src/builder/mapping/publish.py:221-270（publish_approved 无任何 decide 调用）。
- **问题描述**：设计 P3 §2.1"批准即权限接线：人工审核动作前先 decide(subject=reviewer, resource=该候选 target 对象, operation='approve')……P3 至少走纯函数 decide 校验 human——agent 不可审，V9 兜底"；§4.1 发布亦属治理动作。实现里 review CLI 的 `--reviewer` 是任意字符串（默认 'cli'），审核痕迹 actor 硬编码 'human'（review.py:46），**既没有 decide(approve) 校验也没有 V9 human 兜底**；publish_approved 同样无门。
- **证据**（已复现，/tmp/smoke3.py、/tmp/smoke4.py）：`import_decisions(..., reviewer="suspicious_agent")` 直接 accept 成功并把 corrected_target=`NOT_A_VALID_TARGET` 写入 target；publish_approved 在无任何 approve 策略下发布成功（无 decide 调用）。此外 corrected_target **未经任何 C4/格式/注册表校验**即落库（review.py:186-198）。
- **风险**：任何能执行 CLI 的主体（含被 prompt-injection 的 agent 进程、自动化管线）可无痕批准/发布映射并注册对象，V9"审=人专属"防线在 P3 交付中实际不存在。
- **修复建议**：① import 每个 accept/reject/conflict 前调 `decide(subject=human, target 对象, 'approve')`，denied 即记失败；② reviewer 参数必须能解析为 PermissionSubject(human, ...)，agent 一律拒；③ corrected_target 写入前做 target 格式 + C4 注册表校验（attribute 须为已注册对象字段 / object 须为合法对象名）；④ publish_approved 在发布每个候选前复核 approve 权限与 human 审核来源。

### P1-4 P3 门禁测试集整体缺失；映射变更影响分析（C2 硬要求）与管道编排未交付

- **位置**：tests/ 下无 `test_p3_mapping_governance.py`（glob 证实）；src/ 下无 impact.py/`analyze_change`/`run_mapping_pipeline`/PipelineReport（grep 证实）。
- **问题描述**：设计 P3 §5 列出的门禁测试（test_gt_load_and_validate / test_recall_metrics / test_calibrate_thresholds / test_review_cli_export_import / test_approved_to_registry / test_change_impact_analysis）**一条都没有**；design §4.3 的"映射变更影响分析"（C2「必有映射变更影响分析」，P3 门禁 test_change_impact_analysis 依赖它）与 §1.1 的管道编排（PipelineReport/skipped_c4）也未实现。review/publish/calibrate 三个新模块零测试。
- **证据**：设计 P3 §4.3 "新增 `src/builder/mapping/impact.py`：`analyze_change(candidate) -> MappingChangeReport`"；§5 门禁表；实际 src/builder/mapping/ 下仅 annotate/review/publish/calibrate 等既有/新增文件。
- **风险**：C2（映射变更影响分析）是拍板共识，缺实现意味着"改映射不知影响哪些指标/契约/审计"，治理闭环缺关键一环；三个新模块无测试 = 无门禁兜底，P3 交付不可验收。
- **修复建议**：按设计 §4.3 实现 impact.py 并落 test_change_impact_analysis；补齐 P3 门禁测试（tmp_path 双库，遵守铁律①）；把 annotate_mapping_candidates 的 C4 静默跳过改为"计数 + 返回 skipped_c4"（对齐 PipelineReport 语义，见 P2-5）。

---

## 二、P2 中风险（9 项）

### P2-1 审计哈希链在"同毫秒连续追加"下 ~50% 概率自断链（verify_integrity 误报），已复现

- **位置**：src/runtime/audit.py:25-34（new_ulid 时间戳前缀 + 80 位随机）、:203-208（append 取 `ORDER BY audit_id DESC LIMIT 1` 作 prev）、:261-263（verify 按 `ORDER BY audit_id ASC` 重算）。
- **问题描述**：链序按 audit_id 字典序，但 append 只保证"追加时刻最新"（取当前最大 audit_id 作 prev）。同毫秒两次追加时，后生成的 ULID 随机部分有 ~50% 概率**字典序更小** → 追加序与 verify 链序相反 → verify 把正常追加报为 broken。
- **证据**（已复现，/tmp/smoke1.py）：构造同一毫秒前缀、随机部分逆序的两条顺序追加记录，`verify_integrity()` 返回 `ok=False`、两条均 broken。
- **风险**：审计"篡改必检出"的核心承诺失效——正常高频追加（动作引擎/P2 契约审计）会随机产生"假 broken"，使运维无法区分真篡改与正常乱序；同时若调用方显式传 audit_id 可系统性制造断链。
- **修复建议**：链序与追加序统一：① append 前对已存在最大 audit_id 做"若新 id 更小则重新生成/或把新 id 强制递增到 > 当前最大"；② 或 verify 用 ts 序 + audit_id 联合排序并记录物理追加序（增加 `seq` 自增列最稳）；③ 补同毫秒并发/乱序测试。

### P2-2 v0.1 非 metric 契约的 time_range 被静默忽略（返回错误数据范围），已复现

- **位置**：src/des/contract.py:386-394（validate_contract 非 metric 分支不校验 time_range）、:541-573（execute 非 metric 分支不应用 time_range）。
- **问题描述**：contract.py 文档与设计 §3.1 声明"time_range 可与 dimension_filters 并存 / 非 metric 契约绑定对象唯一 date 字段"，但实现既不校验也不应用——`time_range` 是顶层白名单键（CONTRACT_KEYS 含它），传了校验也通过，执行却完全忽略。
- **证据**（已复现，/tmp/smoke6.py）：Material + material_type=ROH + `time_range {from:2026-01-01,to:2026-01-31}`，validate 通过，count=1592（全周期 ROH 数），created_date 实际范围 2025-01~2026-12，time_range 未生效。
- **风险**：ChatBI 用户问"近 30 天"拿到全量数据却以为已过滤——**静默错误答案**比拒答更危险。
- **修复建议**：非 metric 路径要么实现（绑定对象唯一 date 字段 + 参数化过滤），要么在校验期拒答（fail-closed）"非 metric 契约不支持 time_range"，杜绝静默忽略；补测试。

### P2-3 C4 reconcile 两侧同源 SQL，检不出"语义性口径错误"；设计 R2 跨指标自洽（物化层）未落地

- **位置**：src/des/metrics_materialize.py:306-314（materialize_metrics 用同一 sql 建表 + reconcile）、:219-239（_reconcile_one 两侧跑同一 sql）。
- **问题描述**：reconcile 用**同一个 derive_metric_sql** 同时算"物化表"和"源库直算"，只证明"物化 = 自查询"，不证明"自查询 = 正确口径"。若 join 键、GROUP BY、口径（如错误 join 造成行放大/金额翻倍）在 SQL 生成里系统性出错，两侧同错、reconcile 照样全绿。设计 §2.3 R2 本以"跨指标自洽（C1 账面 vs C3 流水净变，物化层 diff=0）"作为第二道防线，但**R2 在代码与测试中均不存在**（仅数据层 D10 存在于 test_des_p1b_data.py:267，非物化层）。
- **证据**：materialize_metrics 中 `sql = derive_metric_sql(...)` 后既用于 CTAS 又传给 `_reconcile_one(con, metric, sql)`；tests 无 R2 断言。设计 §2.3 R2 列为门禁。
- **风险**：指标口径错误可静默通过 C4，直达查询侧。
- **修复建议**：① 物化层实现 R2（C1/C3 同地点 diff=0，基于 metrics.db 物化表）；② reconcile 增加对"物化表行数与 metric_meta.row_count 一致"的断言；③ 至少在测试里用一条"已知错误 join 的指标"证明 reconcile 能/不能检出，把边界写进规格。

### P2-4 P3"新增对象入注册表"与 C4 前置校验自相矛盾：新对象无法经自动管道产生 approved（Vendor/InventoryLocation/FinanceEntry 被静默丢弃）

- **位置**：src/builder/mapping/annotate.py:194-204（create 时 object target 必须已注册，否则 TargetNotRegisteredError）、:494-498（annotate_mapping_candidates 静默 `continue` 丢弃）；src/builder/mapping/publish.py:185-202（_publish_object 又要 register_object_type 新增对象）。
- **问题描述**：C4 要求候选 target 必须是"已注册对象"（机验⑤），但 publish 的职责是"注册新对象"。于是自动管道里，针对未注册对象（P2 planned 的 Vendor/InventoryLocation/FinanceEntry）的 DES 语义候选全部被 C4 静默丢弃，永远到不了 approved → publish 要么命中"已注册拒绝重复"，要么从未收到新对象。唯一能造出"新对象 approved"的路是 review CLI 手动 accept（transition 不重验 target，绕过 C4）——自动闭环形同虚设。
- **证据**（已复现，/tmp/smoke5.py）：`annotate_mapping_candidates` 输入 Customer（已注册）与 Vendor（未注册）两个 object 候选，只有 Customer 落表，Vendor 被 C4 静默跳过。
- **修复建议**：明确"新对象注册"的入口与 C4 语义——要么 C4 对 object 候选改为"未注册即进 draft 待补录队列 + PipelineReport.skipped_c4 显式计数"（对齐设计 §1.1），要么把新对象注册前移到 P1a 范式注册流程，两者取一并在文档中消除矛盾；顺带把 annotate 的静默丢弃改为显式返回 skipped。

### P2-5 阈值校准 auto_precision 定义缺陷：只统计 GT 键，非 GT 自动错批完全不计数（防错批扩散失效），已复现

- **位置**：src/builder/mapping/calibrate.py:139-152（auto_precision 只遍历 GT 键，auto 候选只取该 GT 键下的）。
- **问题描述**：设计 §3.3 用 auto_precision"防自动错批扩散"；实现把分母限定为"含 ≥1 个 score≥high 候选的 GT 键"，非 GT 字段/键上的自动错批候选（score 0.99 的垃圾映射）一概不计入。管道在 GT 之外的 1000 个字段上自动错批 900 个，auto_precision 仍 1.0。
- **证据**（已复现，/tmp/smoke3.py）：GT 1 条命中 + 50 个非 GT 键 0.99 分错批候选在场，`auto_precision(0.9)=1.0`。
- **风险**：校准报告对"自动化误批"给出假乐观数字，误导阈值决策（C2 核心目标失效）。
- **修复建议**：auto_precision 分母改为"全部 auto_approved 候选"（含非 GT 键），命中真值才计 TP；GT 覆盖之外自动过候选应显式列入报告"unvalidated auto-approved"。

### P2-6 review import 非原子（改 target / 状态流转 / 审计三笔独立事务）；corrected_target 无校验

- **位置**：src/builder/mapping/review.py:158-168（accept 流程：_update_target 一个连接 + transition 一个连接 + _audit_review 一个连接，各自 commit）、:186-198（_update_target 无任何 target 校验）。
- **问题描述**：设计 §2.3"逐候选原子，失败不静默"；实现中"改完即入注册表"的 3 个副作用不在同一事务：_update_target 已 commit 后若 transition/audit 失败，候选停留在"target 已改但状态未 approved"的中间态；audit 失败则"已 approved 但无 source='review' 审计"。批次级更非原子（逐行独立提交，设计允许，但行内应原子）。corrected_target 直接 UPDATE 落库，无 C4/格式校验（与 P1-3 ③ 同源）。
- **修复建议**：把"改 target + 流转 + 落 history + 落 audit"包进 Store 单连接单事务（store.ontology_conn() 一次 begin/commit）；corrected_target 校验复用 C4；补失败注入测试。

### P2-7 publish 注册/血缘/审计非同一事务；self_check 只报告不阻断（设计"0 error 才接受"未兑现）

- **位置**：src/builder/mapping/publish.py:193-202（先 registry.register_object_type 改内存，后 mapping_repo.create 用独立连接，再 _audit_publish）；:264-269（self_check 结果仅写入 report，不阻止/回滚）。
- **问题描述**：设计 §4.2"注册写在同一 Store 事务内先落 mappings 血缘表、再注册 Registry（内存）"；实现顺序相反（先内存注册、后独立连接写血缘），血缘写失败则 Registry 多一个无血缘对象；§4.1"发布后自检 0 error 才接受"被实现为"报告里给个 ok 标志"，self_check 报错对象仍保留在 Registry 中。
- **修复建议**：血缘先落、注册后置、同事务；self_check 有 error 时回滚本批注册（或明确"自检仅报告"并去掉"才接受"措辞）；补血缘失败/自检失败测试。

### P2-8 指标注册表输入白名单缺口：transform 函数名/维度名/度量名未校验，存在纵深防御性 SQL 注入面

- **位置**：src/des/metrics.py:354-372（transform 仅查"是字符串"，维度/度量 name 无命名校验）、src/des/metrics_materialize.py:95-108（_split_transform/_transform_expr 把 transform 的 func+args 直接拼进 SQL）、:167-180（dimension name 作列别名、measure.name 作列名）。
- **问题描述**：设计宣称"物化 SQL 表/字段全为常量、无注入面"，但 transform 函数名与参数、dimension/measure 的 name 都来自 metrics.yaml 且未白名单校验。若 metrics 注册表将来成为外部/半可信输入（P5 工作台编辑指标），`transform: "evil(1); DROP TABLE x--"` 可直接注入 derive_metric_sql。当前 15 条内置指标无风险（配置可信），属纵深防御缺口。
- **修复建议**：M 系列校验新增 M8：transform 函数名 ∈ 白名单（substr 等，用 DATE_TRANSFORM_FUNCS 语义统一）、参数为数字/纯逗号分隔；dimension/measure name 须匹配 `^[a-z][a-z0-9_]*$`（复用 metric_id 正则）。

### P2-9 校准网格 medium 阈值对目标函数无影响，输出 medium 是摆设

- **位置**：src/builder/mapping/calibrate.py:184-199（auto_coverage/auto_precision 只依赖 high；full_recall 与阈值无关；选优只比 auto_coverage）。
- **问题描述**：同一 high 下所有 medium 的(auto_coverage, full_recall, auto_precision)完全相同，"最优"实际只由 high 决定，medium 取迭代首个（最小）即胜出。校准报告的"建议 medium"无任何统计依据。
- **修复建议**：要么让 medium 进入某一口径（如 auto 队列负载、中档进队列占比），要么从选优逻辑中移除 medium、只校准 high，并在报告注明。

---

## 三、P3 建议（10 项）

1. **代码规模超规**（项目规范：文件 ≤800 行 / 函数 <50 行）：contract.py 883 行超标；函数超限：materialize_metrics 81、validate_contract 72、decide 64、_structure_violations 64、validate_policy 58、_validate_metric_block 52 行（AST 实测）。建议拆分并补注释，便于后续安全审查。
2. **口径漂移：publish 审计 source='publish'**（publish.py:29）vs 设计 §2.2"入注册表发布 source='review'"。store.py AUDIT_SOURCES 已含 'publish'（store.py:43），功能不炸，但与设计不一致（证据链归类漂移）。
3. **口径漂移：校准网格范围** [0.70,0.95]×[0.40,0.70]（calibrate.py:27-31）vs 设计 §3.3 [0.60,1.00]×[0.35,0.85]。设计注释已标"可参数化"，但应回写设计或说明取舍。
4. **口径漂移："改完即入注册表"在 review.py 为占位**（review.py:108 `"published_to_registry": 0  # 占位`），设计 §2.1 要求 accept+corrected 立即 registry_write.apply_approved；现状靠事后 publish_approved 阶段承接，行为与设计不同（完成记录未声明此偏移）。
5. **口径漂移（待验证）：naming 适配器 score=0.9 在 0.9 阈值边界上被自动 approve**（annotate.py:49,91-95 + adapt_naming_attributes:404），而 P1.5 设计 §3.5 对 naming 写的是"0.9（规则确定性高，仍过审）"——若"仍过审"指仍须过审，则实现与设计相反（待架构确认语义）。
6. **metric 物化结果 measure 列不受属性级 deny 约束**：contract.py:644-645（_filter_metric_rows 保留所有非对象字段列）。当前 15 指标 measure 名与对象字段无碰撞、无实际泄漏，但语义上"属性级读控制可被注册指标聚合绕过"需在文档中明示边界。
7. **对象 api_name 无查重**：publish._to_snake（publish.py:45-51）+ registry.register_object_type（registry.py:50-53）只按 name 去重；不同 name 可坍缩出相同 api_name，contract._resolve_type 按 name|api_name 解析出现歧义。self_check 未查 api_name 唯一。
8. **decide() read 分支对未注册对象无 KeyError 兜底**（permissions.py:215 `registry.object_type(object_type).model`）：策略对象在运行期被卸载/未加载时，decide 直接抛 KeyError 而非 fail-closed 拒绝（edge；正常写路径 V1 已挡）。
9. **V5 结果护栏上限锚定 MARA 行数**（contract.py:581-584）：所有对象/指标共用 MARA 派生上限，与查询对象规模无关——demo 可接受，但作为通用护栏语义应改为按查询对象 row_count 派生。
10. **其他小项**：① `in` 操作符值数量无上限（潜在资源面，本地契约场景可接受）；② audit.append 允许调用方显式传 audit_id（无单调性约束，放大 P2-1）；③ annotate_mapping_candidates 的 C4 静默跳过不计数不报告（对齐 P2-4）；④ publish_approved 按 score 降序处理候选，link 依赖的端点对象若分数更低会在本批报错需重跑（已用 error 显式记录，可接受但建议按依赖拓扑排序）。

---

## 四、测试盲区汇总（现有门禁未覆盖的高风险路径）

| 盲区 | 现状 | 关联发现 |
|---|---|---|
| P3 门禁测试（review/publish/calibrate/GT/impact） | tests/ 下无 test_p3_mapping_governance.py | P1-4 |
| 哈希链同毫秒/并发乱序 | test_p15_governance.py 只测顺序追加 | P2-1 |
| link_traversal 目标对象权限 | test_p2_chatbi.py 权限测试均不含 link | P1-2 |
| v0.1 非 metric time_range | 无测试（现行为 = 静默忽略） | P2-2 |
| R2 物化层跨指标自洽（C1 vs C3） | 仅数据层 D10，物化层无 | P2-3 |
| publish/review/calibrate 任何用例 | 三个新模块零测试 | P1-4/P2-5~7 |
| head-to-head 30 问 + 靶值断言 | 完成记录自认待办；无 harness | —（已声明） |
| P2 性能门禁（P95≤100ms、加速比≥10×） | 仅一个 500ms 宽松冒烟（test_p2_chatbi.py:739） | — |

---

## 五、总体结论

**不可接受作为"治理闭环"定稿交付。** 判定依据：
- **P2 读侧**：物化/契约执行/版本守卫/T3 这套"机器可验"链路质量尚可（参数化到位、M1-M7/V1-V5 校验扎实、reconcile 逐行比数值无"只比数量"漏洞、join 键从配置派生态正确）；但**读侧权限在本阶段是未接线的死代码 + link_traversal 存在可复现的旁路**，且 v0.1 time_range 静默忽略会产出"看着过滤了其实没过滤"的错误答案。
- **P3 映射治理**：审核/发布/校准三件套本身可跑，但**最关键的治理语义（approve 权限门、影响分析、门禁测试、新对象入注册表闭环）缺失或自相矛盾**——这恰是 P3 的立项理由（C2 治理闭环），不能因"CLI 先行为主"而豁免。
- **WORM 审计**：设计精巧（触发器+哈希链+镜像），但哈希链同毫秒断链是真实缺陷，动摇"正常追加链恒绿"的机器可验承诺。

**Top 3 优先修**（按安全与核心承诺排序）：
1. **P1-1 + P1-2（读侧权限）**：给契约执行器唯一入口强制 fail-closed 的权限上下文；link_traversal 目标对象纳入 decide + visible_attributes 过滤。安全不可拖到 P4。
2. **P1-3（approve 权限门）**：review import 与 publish_approved 必须接 decide(operation='approve', human-only) + corrected_target 校验。这是 P3 立项核心（V9 人专属审）。
3. **P2-1（哈希链同毫秒断链）**：统一追加序与链序（增 seq 或强制 id 单调），否则 verify_integrity 在正常高频追加下会随机误报，审计保证失去意义。

> 说明：本报告所有"已复现"项均附冒烟脚本（/tmp/smoke*.py）与输出；未复现仅基于静态阅读的项已标注原因。"待验证"项（P3-5 naming 语义等）标注以待架构确认，不据此定罪。
