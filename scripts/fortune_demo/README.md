# 财富广场注册域 demo（试验性质）

> 状态：机制验证原型。合成样本 + 演示口径；**非交付物**。

## 跑法
1. 造样：/opt/anaconda3/bin/python3 scripts/fortune_demo/build_sample.py
2. 服务：cd scripts/fortune_demo && set -a; . ../../.env; set +a; /opt/anaconda3/bin/python3 -m uvicorn server:app --host 127.0.0.1 --port 8900
3. ChatBI 壳（展示层 Demo 主入口）：http://127.0.0.1:8900/chat —— 对话流式 + 证据面板（决策过程/结论依据/返回数据）+ 历史回放
4. 分析页（旧，三面板）：http://127.0.0.1:8900/
5. CLI：/opt/anaconda3/bin/python3 scripts/fortune_demo/semantic_layer.py

## 真假边界（诚实声明）
- **假**：数据（合成样本，按字典字段结构造，分布参数为演示假设）；口径裁决号（演示占位）。
- **真**：决策链路——规则路由、SQL 编译、SQLite 执行、校验器（含同源交叉验证）全部真实运行。
- 价值验收（更快/更深/答案对）必须接内网真数据才算数（路线第②步）。

## 待办（已归口 docs/BACKLOG.md · A 财富广场线，此处不重复维护）
- [ ] **证据链落库**：每次查询的 trace JSON（request_id + 全步输入输出）落审计库，可回放可导出——现仅在响应内返回
- [ ] **真数据接入**：合成样本 → 内网 DWD/DWS 真数据（脱敏通道），价值验收以真数据为准
- [ ] （已完成 2026-09-08）路由 mock → 真 DeepSeek
