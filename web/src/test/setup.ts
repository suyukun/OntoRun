import '@testing-library/jest-dom/vitest';
// 初始化 i18n 全局单例（react-i18next 的 useTranslation 在无 Provider 时使用全局实例）
import '../i18n';

// act() 环境：React 19 仅在 IS_REACT_ACT_ENVIRONMENT === true 时开启 act 语义与"未包 act"告警。
// RTL 在 render/fireEvent/waitFor 前后已自行开关该标志，这里显式声明一次作为正确基线
// （vitest+jsdom 下应为 true，保证 act 生效；测试必须 await 异步更新，见 riskData 快照用例）。
(globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;

// Mock window.matchMedia for Ant Design (jsdom doesn't support it)
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  }),
});

// Mock scrollIntoView (jsdom doesn't support it)
Element.prototype.scrollIntoView = () => {};

// Mock ResizeObserver (jsdom 无实现；ReactFlow 等依赖)
class ResizeObserverMock {
  observe() {}
  unobserve() {}
  disconnect() {}
}
(globalThis as typeof globalThis & { ResizeObserver: unknown }).ResizeObserver = ResizeObserverMock;

// Mock getComputedStyle for Ant Design
// 注意：jsdom 不支持伪元素，传入 pseudoElt 会打 "Not implemented" stderr 噪音；
// 统一忽略伪元素参数，用 Proxy 兜底所有未实现属性。
const origGetComputedStyle = window.getComputedStyle;
window.getComputedStyle = (elt: Element) => {
  const style = origGetComputedStyle(elt);
  // Return a CSSStyleDeclaration-like object that handles all properties
  return new Proxy(style, {
    get(target, prop) {
      if (prop in target) {
        return Reflect.get(target, prop);
      }
      return '';
    },
  });
};
