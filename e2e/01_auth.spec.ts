import { test, expect } from '@playwright/test';

/**
 * Scénario E2E 1: signup → login → dashboard
 * Teste le parcours complet d'authentification
 */
test.describe('Authentication flow', () => {
  test('devrait permettre signup → login → dashboard', async ({ page }) => {
    // Aller à la page signup
    await page.goto('/signup');

    // Remplir le formulaire signup
    await page.fill('input[type="email"]', 'e2e-test@example.com');
    await page.fill('input[name="password"]', 'password123');
    await page.fill('input[name="confirmPassword"]', 'password123');

    // Soumettre
    await page.click('button[type="submit"]');

    // Attendre redirection vers login
    await page.waitForURL('**/login', { timeout: 5000 });

    // Remplir le formulaire login
    await page.fill('input[type="email"]', 'e2e-test@example.com');
    await page.fill('input[type="password"]', 'password123');

    // Soumettre
    await page.click('button[type="submit"]');

    // Attendre redirection vers dashboard
    await page.waitForURL('**/app/dashboard', { timeout: 5000 });

    // Vérifier que le dashboard est affiché
    await expect(page.locator('text=Dashboard')).toBeVisible();
    await expect(page.locator('text=PlanBanner').or(page.locator('[data-testid="plan-banner"]'))).toBeVisible();

    // Sauvegarder l'état pour les tests suivants
    await page.context().storageState({ path: 'e2e/.auth/user.json' });
  });
});

