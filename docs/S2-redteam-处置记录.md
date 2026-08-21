# S2 red-team 处置记录（2026-08-21）

> 独立对抗复核（docs/red-team-p2p3-review.md，commit 2db9b9a）23 项发现的处置闭环。

## 处置状态
| 级别 | 发现数 | 已修 | 说明 |
|---|---|---|---|
| P1 高风险 | 4 | 4 ✅ | 读权限 fail-open / link 旁路 / approve 门 / 门禁测试+impact |
| P2 中风险 | 9 | 9 ✅ | 哈希链断链 / time_range / R2 自洽 / C4 死锁 / auto_precision / 原子性 / M8 / medium |
| P3 建议 | 10 | 部分 | 大函数拆分排期；口径漂移已注；naming 0.9 语义待架构确认 |

## 修复 commits
- 047c0d3 + 9bce51f：P1-1/P1-2/P2-1/P2-2（读权限 fail-closed + link 目标 decide + 哈希链单调 + time_range 拒答）+ P3 门禁测试 16+1 + calibrate 修复
- 508614c：P3 管道 8 项（approve 门 + impact.py + pipeline.py + R2 + auto_precision + 原子 review/publish + M8 + medium）+ 门禁测试 26

## 验证
- 增量 120 passed（p3/p15/p2 三测试文件）+ ruff 全绿
- 阶段末全量 pytest：验证中

## 待 Jack 拍板（修复暴露的语义决策）
1. **4 个 planned 对象注册**（P2 R2 遗留，⚠️ schema 变更）
2. **新对象自动入注册表闭环**（red-team P2-4）：C4 要求已注册 vs publish 拒绝重复互斥——拍板「C4 未注册 object → 进待补录队列」或「新对象前移 P1a 注册流程」
3. **naming 0.9 自动过「仍过审」语义**（P3-5）：auto-approve 与「审=人专属」张力
4. **大函数拆分**（contract.py 883 行等）：排期做
