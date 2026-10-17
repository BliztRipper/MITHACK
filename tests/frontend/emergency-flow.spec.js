const { test, expect } = require('@playwright/test');

// Needs IRIS + API + web running and a seeded store. Credentials: E2E_USER / E2E_PASS (a GP login).
// Optional E2E_HN picks the patient (default HN-0005). Each run creates a fresh case.
const { E2E_USER, E2E_PASS, E2E_HN = 'HN-0005' } = process.env;

test('GP: emergency case with cached RAO image, override-sign, final report', async ({ page }) => {
  test.skip(!E2E_USER || !E2E_PASS, 'set E2E_USER and E2E_PASS');
  await page.goto('/');
  await page.getByLabel('Username').fill(E2E_USER);
  await page.getByLabel('Password').fill(E2E_PASS);
  await page.getByRole('button', { name: 'Sign in' }).click();

  await page.getByRole('link', { name: 'New case' }).click();
  await page.getByLabel('Search name or HN').fill(E2E_HN);
  await page.getByRole('button', { name: 'Search' }).click();
  await page.getByRole('row').filter({ hasText: E2E_HN }).getByRole('link').click();

  await page.getByLabel(/Emergency: sudden vision loss/).check();
  await page.getByRole('button', { name: 'Continue' }).click();

  // consent step: record it unless already on file from an earlier run
  const record = page.getByRole('button', { name: 'Record consent and continue' });
  await expect(record.or(page.getByText(/Consent on file/))).toBeVisible();
  if (await record.isVisible()) {
    await page.getByLabel('Care use (required)').check();
    await page.getByLabel(/Right to withdraw explained/).check();
    await record.click();
    await expect(page.getByText(/Consent on file/)).toBeVisible();
  }
  await page.getByRole('button', { name: 'Continue' }).click();

  await page.getByLabel('Hours since onset of vision loss').fill('3');
  await page.getByRole('group', { name: /Sudden, painless, one eye/ }).getByLabel('Yes').check();
  await page.getByRole('group', { name: /GCA symptoms/ }).getByLabel('No').check();
  await page.getByRole('button', { name: 'Continue' }).click();

  await page.getByRole('button', { name: 'Cached: RAO example (RFMiD 716)' }).click();
  await page.getByRole('button', { name: 'Analyse photo' }).click();

  // no trained CRAO model exists: the heatmap layer is in its explicit "no model" state, triage escalates
  await expect(page).toHaveURL(/\/cases\//, { timeout: 120_000 });
  await expect(page.getByText('No model loaded. Probability not available. Case routed to ESCALATE.')).toBeVisible();
  await expect(page.getByRole('switch', { name: /Model attention \(heatmap\)/ })).toBeDisabled();
  await expect(page.getByText('Heatmap not available for this case.')).toBeVisible();
  await expect(page.getByText('PRELIMINARY').first()).toBeVisible();

  await page.getByRole('button', { name: 'Sign result' }).click();
  const dlg = page.getByRole('dialog');
  await dlg.getByLabel('Override with my finding').check();
  await dlg.getByLabel('Finding (required)').fill('E2E override finding');
  await dlg.getByLabel('clinical findings disagree').check();
  await dlg.getByLabel('No, not CRAO').check();
  await dlg.getByRole('button', { name: 'Sign as final' }).click();

  await expect(page.getByText(/FINAL · signed by/)).toBeVisible();
  await expect(page.getByText('PRELIMINARY')).toHaveCount(0);
});
