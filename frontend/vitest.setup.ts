import "@testing-library/jest-dom/vitest";

// jsdom does not implement scrollIntoView; stub it for components that call it.
if (!Element.prototype.scrollIntoView) {
  Element.prototype.scrollIntoView = () => {};
}
