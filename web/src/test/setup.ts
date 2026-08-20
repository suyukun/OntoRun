import '@testing-library/jest-dom/vitest';
// 初始化 i18n 全局单例（react-i18next 的 useTranslation 在无 Provider 时使用全局实例）
import '../i18n';

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
const origGetComputedStyle = window.getComputedStyle;
window.getComputedStyle = (elt: Element, pseudoElt?: string | null) => {
  const style = origGetComputedStyle(elt, pseudoElt);
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
