import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

test("rebuilt workspace loads with the intended hierarchy", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("heading", { level: 1 })).toContainText(
    "Give surplus inventory"
  );
  await expect(
    page.getByRole("navigation", { name: "Workspace sections" })
  ).toBeVisible();
  await expect(page.getByText("Hard gates before scoring.")).toBeVisible();
  await expect(page.getByLabel("Inventory workbook")).toBeAttached();
  await expect(page.getByRole("button", { name: "Analyze Inventory" })).toBeVisible();
});

test("phase navigation is keyboard reachable", async ({ page }) => {
  await page.goto("/");

  const configure = page.getByRole("link", { name: /01 Configure/ });
  await configure.focus();
  await expect(configure).toBeFocused();

  const outline = await configure.evaluate((element) => {
    const style = getComputedStyle(element);
    return {
      style: style.outlineStyle,
      width: style.outlineWidth,
    };
  });

  expect(outline.style).not.toBe("none");
  expect(outline.width).not.toBe("0px");

  await configure.press("Enter");
  await expect(page.locator("#decision-context")).toBeInViewport();
});

test("required workbook is enforced before analysis", async ({ page }) => {
  await page.goto("/");

  const analyze = page.getByRole("button", { name: "Analyze Inventory" });
  await analyze.click();

  const file = page.locator("#inventory-file");
  const valid = await file.evaluate((element) => element.checkValidity());
  expect(valid).toBe(false);
  await expect(page.locator("#results")).toHaveClass(/hidden/);
});

test("desktop layout has no horizontal page overflow", async ({ page }) => {
  await page.goto("/");

  const overflow = await page.evaluate(() => ({
    scrollWidth: document.documentElement.scrollWidth,
    clientWidth: document.documentElement.clientWidth,
  }));

  expect(overflow.scrollWidth).toBeLessThanOrEqual(overflow.clientWidth + 1);
});

test("mobile layout keeps the primary action reachable", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");

  await expect(page.getByRole("button", { name: "Analyze Inventory" })).toBeVisible();

  const overflow = await page.evaluate(() => ({
    scrollWidth: document.documentElement.scrollWidth,
    clientWidth: document.documentElement.clientWidth,
  }));

  expect(overflow.scrollWidth).toBeLessThanOrEqual(overflow.clientWidth + 1);
});

test("automated accessibility scan has no serious or critical violations", async ({ page }) => {
  await page.goto("/");

  const results = await new AxeBuilder({ page }).analyze();
  const blocking = results.violations.filter((violation) =>
    ["serious", "critical"].includes(violation.impact)
  );

  expect(blocking).toEqual([]);
});
