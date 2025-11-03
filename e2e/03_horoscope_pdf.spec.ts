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
    // Aller à la page horoscope
    await page.goto('/app/horoscope');

    // Remplir le formulaire natal
    await page.fill('input[name="date"]', '1990-01-01');
    await page.fill('input[name="time"]', '12:00');
    await page.fill('input[name="latitude"]', '48.8566');
    await page.fill('input[name="longitude"]', '2.3522');
    await page.fill('input[name="timezone"]', 'Europe/Paris');
    await page.fill('input[name="name"]', 'Test Chart');

    // Soumettre
    await page.click('button[type="submit"]');

    // Attendre que le thème natal soit créé (message de succès ou affichage)
    await expect(
      page
        .locator('text=créé')
        .or(page.locator('text=succès'))
        .or(page.locator('[data-testid="natal-success"]'))
    ).toBeVisible({ timeout: 10000 });

    // Attendre que Today soit chargé
    await expect(
      page
        .locator('text=Horoscope')
        .or(page.locator('[data-testid="today-content"]'))
    ).toBeVisible({ timeout: 5000 });

    // Vérifier que le contenu Today est présent
    const todayContent = page
      .locator('[data-testid="today-content"]')
      .or(page.locator('text=/Horoscope today/i'));

    await expect(todayContent).toBeVisible();

    // Intercepter la requête PDF et retourner un blob PDF simulé
    await page.route('**/v1/horoscope/pdf/natal/*', async (route) => {
      const pdfContent = '%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\nxref\n0 1\ntrailer\n<<\n/Size 1\n/Root 1 0 R\n>>\nstartxref\n9\n%%EOF';
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
      page
        .locator('button:has-text("Exporter PDF")')
        .or(page.locator('button:has-text("PDF")'))
        .or(page.locator('[data-testid="export-pdf-button"]'))
        .click(),
    ]);

    // Vérifier que le téléchargement a eu lieu
    expect(download.suggestedFilename()).toContain('.pdf');
    const path = await download.path();
    expect(path).toBeTruthy();
  });
});

