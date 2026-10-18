const { test, expect } = require('@playwright/test');

// Hosted smoke test for the public demo (live-demo-deployment 4.1). Point BASE_URL at the public app:
//   BASE_URL=https://retina-app-lilac.vercel.app npx playwright test tests/frontend/live-demo.spec.js --project frontend
// Works against any demo-mode build (the browser test DB or a demo-mode API). Each run starts with a fresh browser.

async function startEmergencyCase(page, hn) {
  await page.goto('/');
  await expect(page.getByRole('status').filter({ hasText: 'Demo: synthetic patients' })).toBeVisible();
  await page.getByRole('button', { name: 'Continue as guest (GP)' }).click();
  await page.getByRole('link', { name: 'New case' }).click();
  const pick = page.getByLabel('Choose a patient (HN)');
  await pick.selectOption(await pick.locator('option', { hasText: hn }).getAttribute('value'));
  await page.getByRole('button', { name: 'Open' }).click();

  await page.getByLabel(/Emergency: sudden vision loss/).check();
  await page.getByRole('button', { name: 'Continue' }).click();
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
}

test('guest GP runs a cached RAO photo to its Emergency triage card', async ({ page }) => {
  await startEmergencyCase(page, 'HN-0005');
  await page.getByRole('button', { name: /Cached: RAO 1/ }).click();
  await page.getByRole('button', { name: 'Analyse photo' }).click();
  const card = page.getByRole('region').filter({ has: page.locator('#triage-h') }); // the triage card
  await expect(card).toBeVisible({ timeout: 15_000 });
  await expect(card.getByRole('listitem').first()).toBeVisible(); // its next action
  await expect(page.getByRole('status').filter({ hasText: 'Demo: synthetic patients' })).toBeVisible();
});

test('an unknown upload gets the demo-photo message', async ({ page }) => {
  await startEmergencyCase(page, 'HN-0006');
  const png = Buffer.from('89504e470d0a1a0a' + '00'.repeat(32), 'hex'); // PNG signature, not one of the demo photos
  await page.locator('#photo').setInputFiles({ name: 'mine.png', mimeType: 'image/png', buffer: png });
  await page.getByRole('button', { name: 'Analyse photo' }).click();
  await expect(page.getByText('This demo accepts only the sample photos below.')).toBeVisible();
});
