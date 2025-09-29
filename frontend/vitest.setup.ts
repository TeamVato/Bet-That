import { expect, afterEach } from "vitest";
import * as matchers from "@testing-library/jest-dom/matchers";
import "whatwg-fetch";
import { cleanup } from "@testing-library/react";

afterEach(() => {
  cleanup();
});

expect.extend(matchers);
