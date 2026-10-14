'use strict';
// 00-skeleton.journey.js — walking-skeleton journey (walking-skeleton.md row 5).
// Log in as sales.user → menu Contacts → New → fill Name/Email → Save → the row is in the grid,
// then the data rung asserts the row by OQL (run by the caller, see tests/e2e/run-skeleton.sh).
// Usage: node tests/e2e/journeys/00-skeleton.journey.js <name> [menuCaption]
const { chromium } = require('playwright');
const BASE = process.env.APP_URL || 'http://127.0.0.1:8080';
const NAME = process.argv[2];
const MENU = process.argv[3] || 'Contacts';
const SHOT = process.env.SHOT || '';
(async () => {
  const browser = await chromium.launch({ executablePath: process.env.PW_CHROMIUM || undefined });
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  const fail = async (msg) => { console.log('FAIL ' + msg); await browser.close(); process.exit(1); };
  try {
    await page.goto(BASE + '/login.html');
    await page.fill('#usernameInput', 'sales.user');
    await page.fill('#passwordInput', 'Erpv1-Demo-2026!');
    await page.click('#loginButton');
    await page.waitForSelector('.mx-navigationtree', { timeout: 30000 });
    const group = page.locator('.mx-navigationtree a', { hasText: MENU }).first();
    if (!(await group.count())) return fail(`menu item "${MENU}" not found`);
    await group.click();
    // a group expands; click the leaf item with the same caption if the group did not navigate
    await page.waitForTimeout(500);
    if (!(await page.locator('.mx-name-gridPartners').count())) {
      await page.locator('.mx-navigationtree a', { hasText: MENU }).last().click();
    }
    await page.waitForSelector('.mx-name-gridPartners', { timeout: 20000 });
    await page.click('.mx-name-btnNew');
    await page.waitForSelector('.mx-name-txtName input', { timeout: 20000 });
    await page.fill('.mx-name-txtName input', NAME);
    await page.fill('.mx-name-txtEmail input', 'skeleton@example.com');
    await page.click('.mx-name-btnSave');
    await page.waitForSelector('.mx-name-gridPartners', { timeout: 20000 });
    await page.waitForSelector(`.mx-name-gridPartners >> text=${NAME}`, { timeout: 20000 });
    if (SHOT) await page.screenshot({ path: SHOT, fullPage: true });
    console.log('PASS row visible in grid: ' + NAME);
  } catch (e) { return fail(e.message.split('\n')[0]); }
  await browser.close();
})();
