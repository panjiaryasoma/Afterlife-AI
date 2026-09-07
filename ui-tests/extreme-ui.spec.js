import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

test("extreme workspace loads with core landmarks", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("heading", { level: 1 })).toContainText(
    "Give surplus inventory"
  );
  await expect(page.getByRole("navigation", { name: "Workspace navigation" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Design Lab" })).toBeVisible();
  await expect(page.getByText("Hard gates before scoring")).toBeVisible();
});

test("design lab state is keyboard reachable and URL synced", async ({ page }) => {
  await page.goto("/");

  const toggle = page.getByRole("button", { name: "Design Lab" });
  await toggle.focus();
  await expect(toggle).toBeFocused();
  await toggle.press("Enter");

  const panel = page.getByRole("region", { name: "Design Lab" });
  await expect(panel).toBeVisible();

  await page.getByRole("button", { name: "Editorial" }).click();
  await expect(page.locator("body")).toHaveAttribute("data-lab-mode", "editorial");
  await expect(page).toHaveURL(/view=editorial/);

  const density = page.getByLabel("Density");
  await density.fill("8");
  await expect(page).toHaveURL(/density=8/);
});

test("workspace keeps a visible focus treatment", async ({ page }) => {
  await page.goto("/");

  const firstRailLink = page.getByRole("link", { name: "Mission brief" });
  await firstRailLink.focus();
  await expect(firstRailLink).toBeFocused();

  const outlineStyle = await firstRailLink.evaluate((element) => {
    const style = getComputedStyle(element);
    return {
      outlineStyle: style.outlineStyle,
      outlineWidth: style.outlineWidth,
    };
  });

  expect(outlineStyle.outlineStyle).not.toBe("none");
  expect(outlineStyle.outlineWidth).not.toBe("0px");
});

test("layout does not create horizontal page overflow", async ({ page }) => {
  await page.goto("/");

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
