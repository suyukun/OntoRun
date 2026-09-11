import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    // M1 遗留③ flaky 整改（T503 实证）：8 并发 worker 下 antd 重页面首个用例的
    // 渲染预热会顶穿 vitest 默认 5s testTimeout——search.test.tsx 基线连跑 3/3
    // 报 "Test timed out in 5000ms"（solo 全绿），故障面是测试级超时不是
    // findBy 轮询。放大到 10s 后全量连跑 3 次稳定全绿，保留并行速度。
    testTimeout: 10000,
  },
});
