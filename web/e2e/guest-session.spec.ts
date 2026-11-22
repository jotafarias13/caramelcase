import { expect, test } from "@playwright/test";
import en from "../src/i18n/en.json" with { type: "json" };
import ptBR from "../src/i18n/pt-BR.json" with { type: "json" };

/**
 * The spec's end-to-end path, in each project's language, with every
 * feature flag off: a guest opens the landing page, goes through
 * onboarding, finishes a session and sees the summary, then opens Home,
 * Profile and Settings. On the way, each number is explained once.
 *
 * It runs against the real API and database, so it does not know the
 * correct keys: it takes the first option every time. Texts come from the
 * translation files, so the test reads the screens as a student would.
 */

function oneOf(...texts: string[]): RegExp {
  const escaped = texts.map((text) =>
    text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"),
  );
  return new RegExp(`^(${escaped.join("|")})$`);
}

test("a guest opens the landing page, finishes a session and sees the summary", async ({
  page,
  request,
}, testInfo) => {
  const copy = testInfo.project.use.locale?.startsWith("en") ? en : ptBR;

  // V1 is the app with every flag off.
  const config = await (await request.get("/api/v1/config")).json();
  expect(Object.values(config.flags)).not.toContain(true);

  // A one-time hint, and the button that closes it and lets the next show.
  const hint = page.getByRole("dialog", { name: copy.explain.label });
  const gotIt = page.getByRole("button", { name: copy.explain.got_it });
  /** The start of an explanation, up to its first number. */
  const start = (text: string) => text.split("{{")[0];

  await test.step("the landing page", async () => {
    await page.goto("/");
    await expect(
      page.getByRole("heading", { level: 1, name: copy.landing.title }),
    ).toBeVisible();
    await page
      .getByRole("link", { name: copy.common.lets_practice })
      .first()
      .click();
  });

  await test.step("onboarding", async () => {
    const title = (text: string) =>
      expect(page.getByRole("heading", { level: 1, name: text })).toBeVisible();
    const next = () =>
      page.getByRole("button", { name: copy.common.continue }).click();

    await title(copy.onboarding.language_title);
    await next();
    await title(copy.onboarding.study_title);
    await page.getByLabel(copy.onboarding.university).fill("UFRN");
    await page.getByLabel(copy.onboarding.course).fill("Ciência da Computação");
    await next();
    await title(copy.onboarding.subject_title);
    await next();
    await title(copy.onboarding.goal_title);
    await page.getByRole("button", { name: copy.common.lets_practice }).click();
  });

  await test.step("ten questions", async () => {
    await expect(page).toHaveURL(/\/session\/[^/]+$/);
    const options = page.getByRole("radiogroup", {
      name: copy.session.options,
    });
    const result = page.getByRole("heading", {
      level: 2,
      name: oneOf(copy.feedback.correct_title, copy.feedback.wrong_title),
    });
    for (let question = 1; question <= 10; question++) {
      await options.getByRole("radio").first().click();
      await page.getByRole("button", { name: copy.session.check }).click();
      await expect(result).toBeVisible();
      await page.getByRole("button", { name: copy.common.continue }).click();
    }
  });

  await test.step("the summary", async () => {
    await expect(page).toHaveURL(/\/session\/[^/]+\/summary$/);
    // A guest's first summary offers to save the progress.
    const offer = page.getByRole("dialog", { name: copy.summary.save_title });
    await expect(offer).toBeVisible();
    await offer.getByRole("button", { name: copy.summary.save_later }).click();
    await expect(
      page.getByRole("heading", {
        level: 1,
        name: oneOf(copy.summary.title_gain, copy.summary.title_loss),
      }),
    ).toBeVisible();
    await expect(
      page.getByText(copy.summary.correct_of.replace("{{total}}", "10")),
    ).toBeVisible();
    // With the offer gone, XP and the rating are explained, one at a time.
    for (const text of [copy.explain.xp, copy.explain.rating]) {
      await expect(hint).toContainText(start(text));
      await gotIt.click();
    }
    await expect(hint).toHaveCount(0);
  });

  await test.step("Home, Profile and Settings", async () => {
    await page.getByRole("button", { name: copy.common.back_to_home }).click();
    await expect(page).toHaveURL(/\/home$/);
    await expect(
      page.getByRole("heading", {
        level: 1,
        name: copy.home.greeting_no_name,
      }),
    ).toBeVisible();
    await expect(page.getByText(copy.home.topics_note)).toBeVisible();
    for (const text of [
      copy.explain.streak,
      copy.explain.topics,
      copy.explain.subject,
    ]) {
      await expect(hint).toContainText(start(text));
      await gotIt.click();
    }
    await expect(hint).toHaveCount(0);

    const nav = page.getByRole("navigation", { name: copy.nav.main });
    await nav.getByRole("link", { name: copy.nav.profile }).click();
    await expect(
      page.getByRole("heading", { level: 1, name: copy.profile.title }),
    ).toBeVisible();
    await expect(page.getByText(copy.profile.mastery_by_topic)).toBeVisible();

    await nav.getByRole("link", { name: copy.nav.settings }).click();
    await expect(
      page.getByRole("heading", { level: 1, name: copy.settings.title }),
    ).toBeVisible();
    // The reminders flag is off: its switch is not there.
    await expect(page.getByText(copy.settings.daily_reminder)).toHaveCount(0);

    // Back on Home, nothing is explained a second time.
    await nav.getByRole("link", { name: copy.nav.home }).click();
    await expect(page.getByText(copy.home.topics_note)).toBeVisible();
    await expect(hint).toHaveCount(0);
  });
});
