'use strict';
// look.js — screenshots for the LOOK stage (module-review.md stage 4, ui-loop.md): every page of a module at
// 1280px and 390px, signed in as the demo user whose role reaches it. Reads a JSON list of shots:
//   [{ "page": "Tax_Overview", "user": "invoicing.manager", "menu": ["Configuration", "Taxes"] },
//    { "page": "Tax_NewEdit", "user": "invoicing.manager", "menu": ["Configuration", "Taxes"], "openRow": 1 }]
// openRow: click row N of the first data grid / list view on the menu page (opens the NewEdit page).
// click: a widget name (mx-name-*) to click after landing (e.g. a New button).
// url: the page's route (its Url), opened directly instead of through the menu.
// rowText: open the row of the first data grid that shows this text (instead of openRow).
// Usage: node tests/e2e/look.js <shots.json> <outDir>
// Prints one line per shot: page, size, title read off the page, console errors, Mendix error dialog text.
const fs = require('fs');
const { chromium } = require('playwright');
const BASE = process.env.APP_URL || 'http://127.0.0.1:8080';
const PASSWORD = 'Erpv1-Demo-2026!';
const [shotsFile, outDir] = process.argv.slice(2);
const shots = JSON.parse(fs.readFileSync(shotsFile, 'utf8'));
fs.mkdirSync(outDir, { recursive: true });

async function login(page, user) {
  await page.goto(BASE + '/login.html');
  await page.fill('#usernameInput', user);
  await page.fill('#passwordInput', PASSWORD);
  await page.click('#loginButton');
  await page.waitForSelector('.mx-page', { timeout: 30000 });
  // a heavy home page (Invoice_Overview: four grids) still renders after .mx-page appears; navigating before it settles
  // lands back on the home page (LOOK 2026-10-16d)
  await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {});
  await page.waitForTimeout(4000);   // the approvals-inbox home (purchase.manager) re-renders after the network settles
}

async function nav(page, menu) {
  const [group, item] = menu;
  if (await page.locator('.region-sidebar .mx-navigationtree').isVisible().catch(() => false)) {
    const groupLi = page.locator('.mx-navigationtree li', { has: page.locator(':scope > a', { hasText: group }) }).first();
    const leaf = groupLi.locator('li a', { hasText: item }).first();
    if (!(await leaf.isVisible().catch(() => false))) {
      await groupLi.locator(':scope > a').first().click();
      await page.waitForTimeout(300);
    }
    await leaf.click();
    return;
  }
  // phone: the rail is hidden; the same menu is a menu bar in the top bar (themesource/core main.scss)
  await page.locator('.phone-menu .mx-navbar-item > a', { hasText: group }).first().click();
  await page.waitForTimeout(300);
  await page.locator('.phone-menu .mx-navbar-subitem a', { hasText: item }).first().click();
}

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.PW_CHROMIUM || undefined });
  let failures = 0;
  for (const s of shots) {
    for (const width of [1280, 390]) {
      const ctx = await browser.newContext({ viewport: { width, height: width === 390 ? 844 : 900 } });
      const page = await ctx.newPage();
      const errors = [];
      page.on('console', m => { if (m.type() === 'error') errors.push(m.text().slice(0, 160)); });
      try {
        await login(page, s.user);
        errors.length = 0; // the login page itself logs a 401 before a session exists: not page errors
        // url: open a page by its route (a page with Url) when the menu leaf is unreliable to click (collapsed groups)
        if (s.url) await page.goto(BASE + '/p/' + s.url); else if (s.menu) await nav(page, s.menu);
        await page.waitForTimeout(1200);
        if (s.rowText) {   // open the grid row that shows this text (a specific record, not the newest)
          await page.locator('.mx-name-gridMain [role="row"]', { hasText: s.rowText }).first().locator('[role="gridcell"]').nth(2).click();
          await page.waitForTimeout(1500);
        } else if (s.openRow) {
          const row = page.locator('.mx-name-gridMain [role="row"], .mx-name-gridMain .tr').nth(s.openRow);
          const lv = page.locator('.mx-listview-item').nth(s.openRow - 1);
          // a cell, not the row's centre: a multi-select grid (Invoice_Overview) opens rows from their cells
          const cell = row.locator('[role="gridcell"]').nth(2);
          if (await row.count()) await ((await cell.count()) ? cell : row).click(); else await lv.click();
          await page.waitForTimeout(1500);
        }
        if (s.click) { await page.click('.mx-name-' + s.click); await page.waitForTimeout(1500); }
        const h1 = (await page.locator('h1').first().textContent().catch(() => '')) || '';
        const dialog = (await page.locator('.mx-dialog-body, .alert-danger').first().textContent().catch(() => '')) || '';
        const file = `${outDir}/${s.module ? s.module + '.' : ''}${s.page}-${width}.png`;
        await page.screenshot({ path: file, fullPage: true });
        const pageErrors = errors.slice(); // before sign-out, which itself triggers a 401 on the closed session
        const out = page.locator('.mx-name-btnSignOut');
        if (await out.count()) { await out.first().click({ force: true }).catch(() => {}); await page.waitForTimeout(500); }
        console.log(`${s.page}\t${width}\th1="${h1.trim().slice(0, 50)}"\tconsoleErrors=${pageErrors.length}${pageErrors.length ? " [" + pageErrors.join(" | ") + "]" : ""}${dialog ? '\tDIALOG="' + dialog.trim().slice(0, 120) + '"' : ''}\t${file}`);
      } catch (e) {
        failures++;
        console.log(`${s.page}\t${width}\tFAULT ${e.message.split('\n')[0]}`);
      }
      await ctx.close();
    }
  }
  await browser.close();
  process.exit(failures ? 1 : 0);
})();
