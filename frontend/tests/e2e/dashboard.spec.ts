import { test, expect } from "@playwright/test";

test.describe("Dashboard cross-browser smoke test", () => {
  test("renders beta dashboard without console errors", async ({
    page,
    browserName,
  }) => {
    const consoleErrors: string[] = [];
    const failedRequests: string[] = [];
    page.on("console", (message) => {
      if (message.type() === "error") {
        consoleErrors.push(message.text());
      }
    });
    page.on("requestfailed", (request) => {
      failedRequests.push(
        `${request.url()} :: ${request.failure()?.errorText}`,
      );
    });

    await page.goto("/");
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(500);

    expect(consoleErrors, consoleErrors.join("\n")).toHaveLength(0);
    expect(failedRequests, failedRequests.join("\n")).toHaveLength(0);

    await expect(page.getByText("Beta Mode - View Only")).toBeVisible();
    await expect(
      page.getByRole("heading", { level: 1, name: "Current Edges" }),
    ).toBeVisible();
    await expect(page.getByRole("button", { name: /refresh/i })).toBeVisible();

    const totalEdgesCard = page
      .locator('div:has(> p:has-text("Total Edges"))')
      .first();
    await expect(totalEdgesCard.locator("p").nth(1)).toHaveText("14");

    await expect(
      page.getByRole("heading", { level: 3, name: "Aaron Rodgers" }),
    ).toBeVisible();

    // Responsive spot-check: ensure cards remain visible on smaller viewports
    if (browserName.includes("mobile")) {
      await expect(page.getByText("View Only")).toBeVisible();
    }
  });
});
