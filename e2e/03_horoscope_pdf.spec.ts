import { test, expect } from '@playwright/test';

/**
 * Scénario E2E 3: créer natal → today → export PDF
 * Teste le parcours complet horoscope avec téléchargement PDF
 */
test.describe('Horoscope flow', () => {
  // Utiliser l'état d'authentification sauvegardé
  test.use({ storageState: 'e2e/.auth/user.json' });

  test('devrait permettre créer natal → today → export PDF', async ({
    page,
  }) => {
    const chartId = 'chart_e2e_1234';

    // Mock backend endpoints pour stabiliser le flow
    await page.route('**/v1/horoscope/natal', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          chart_id: chartId,
          created_at: new Date().toISOString(),
        }),
      });
    });

    await page.route(`**/v1/horoscope/today/${chartId}`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          content: 'Horoscope du jour (mock)',
          generated_at: new Date().toISOString(),
        }),
      });
    });

    await page.route(
      `**/v1/horoscope/today/premium/${chartId}`,
      async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            content: 'Horoscope premium (mock)',
            premium_insights: 'Insights premium mock',
            generated_at: new Date().toISOString(),
          }),
        });
      }
    );

    // Aller à la page horoscope
    await page.goto('/app/horoscope');

    // Remplir le formulaire natal (selectors alignés avec ids réels)
    await page.fill('#date', '1990-01-01');
    await page.fill('#time', '12:00');
    await page.fill('#latitude', '48.8566');
    await page.fill('#longitude', '2.3522');
    // timezone est en lecture seule et déjà renseigné
    await page.fill('#location', 'Test Chart');

    // Soumettre
    await page.click('button[type="submit"]');

    // Attendre que l'action d'export soit disponible
    const exportButtonLocator = page
      .getByRole('button', { name: /Exporter PDF/i })
      .or(page.getByRole('button', { name: /PDF/i }))
      .or(page.locator('[data-testid="export-pdf-button"]'));

    await expect(exportButtonLocator).toBeVisible({ timeout: 10000 });

    // Intercepter la requête PDF et retourner un blob PDF simulé
    await page.route('**/v1/horoscope/pdf/natal/*', async (route) => {
      const pdfContent =
        '%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\nxref\n0 1\ntrailer\n<<\n/Size 1\n/Root 1 0 R\n>>\nstartxref\n9\n%%EOF';
      const pdfBuffer = Buffer.from(pdfContent);
      await route.fulfill({
        status: 200,
        contentType: 'application/pdf',
        body: pdfBuffer,
        headers: {
          'Content-Disposition': 'attachment; filename="natal-test.pdf"',
        },
      });
    });

    // Attendre le téléchargement du PDF
    const [download] = await Promise.all([
      page.waitForEvent('download'),
      exportButtonLocator.click(),
    ]);

    // Vérifier que le téléchargement a eu lieu
    expect(download.suggestedFilename()).toContain('.pdf');
    const path = await download.path();
    expect(path).toBeTruthy();
  });
});
