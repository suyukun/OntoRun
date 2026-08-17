import '@testing-library/jest-dom/vitest';

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
