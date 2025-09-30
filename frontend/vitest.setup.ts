import { expect, afterEach } from "vitest";
import * as matchers from "@testing-library/jest-dom/matchers";
import "whatwg-fetch";
import { cleanup } from "@testing-library/react";

// Extend Vitest's expect with jest-dom matchers
expect.extend(matchers);

afterEach(() => {
  cleanup();
});
