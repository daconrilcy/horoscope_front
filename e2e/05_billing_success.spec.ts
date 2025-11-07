import { test, expect } from '@playwright/test';

/**
 * Scénario E2E 5: Billing success page avec validation session_id
 * Teste le parcours de redirection post-Checkout vers /billing/success
 */
test.describe('Billing success page', () => {
  // Utiliser l'état d'authentification sauvegardé
  test.use({ storageState: 'e2e/.auth/user.json' });

  test('devrait valider session_id et afficher succès', async ({ page }) => {
    const mockSessionId = 'cs_test_1234567890';
    const mockSessionData = {
      status: 'paid',
      session_id: mockSessionId,
      plan: 'plus',
    };

    // Intercepter la requête de vérification de session
    await page.route(
      `**/v1/billing/checkout/session?session_id=${mockSessionId}`,
      (route) => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(mockSessionData),
        });
      }
    );

    // Naviguer directement vers la page success avec session_id
    await page.goto(`/billing/success?session_id=${mockSessionId}`);

    // Attendre que la validation soit terminée (le loader peut être éphémère)
    await expect(page.locator('text=Paiement réussi !')).toBeVisible({
      timeout: 5000,
    });

    // Vérifier le message de succès
    await expect(
      page.locator('text=Votre abonnement a été activé avec succès')
    ).toBeVisible();

    // Vérifier que le plan est affiché
    await expect(page.locator('text=Plan :')).toBeVisible();
    await expect(page.locator('text=plus')).toBeVisible();

    // Vérifier le bouton vers le dashboard
    const dashboardLink = page.locator(
      'a:has-text("Accéder au tableau de bord")'
    );
    await expect(dashboardLink).toBeVisible();
    await expect(dashboardLink).toHaveAttribute('href', '/app/dashboard');
  });

  test('devrait afficher erreur si session_id manquant', async ({ page }) => {
    // Naviguer vers la page success sans session_id
    await page.goto('/billing/success');

    // Vérifier que la page affiche une erreur
    await expect(page.locator('text=Erreur')).toBeVisible({ timeout: 2000 });
    await expect(
      page.locator("text=Aucun identifiant de session trouvé dans l'URL")
    ).toBeVisible();

    // Vérifier le bouton de retour au dashboard
    const dashboardLink = page.locator(
      'a:has-text("Retour au tableau de bord")'
    );
    await expect(dashboardLink).toBeVisible();
  });

  test('devrait afficher erreur si session introuvable (404)', async ({
    page,
  }) => {
    const mockSessionId = 'cs_test_invalid';

    // Intercepter la requête avec erreur 404
    await page.route(
      `**/v1/billing/checkout/session?session_id=${mockSessionId}`,
      (route) => {
        route.fulfill({
          status: 404,
          contentType: 'application/json',
          body: JSON.stringify({
            message: 'Session introuvable',
          }),
        });
      }
    );

    // Naviguer vers la page success avec session_id invalide
    await page.goto(`/billing/success?session_id=${mockSessionId}`);

    // Attendre que l'erreur soit affichée
    await expect(page.locator('text=Erreur de validation')).toBeVisible({
      timeout: 5000,
    });

    await expect(
      page.locator('text=Session introuvable ou expirée')
    ).toBeVisible();

    // Vérifier le bouton de retry
    const retryButton = page.locator('button:has-text("Réessayer")');
    await expect(retryButton).toBeVisible();
  });

  test("devrait permettre retry en cas d'erreur", async ({ page }) => {
    const mockSessionId = 'cs_test_retry';
    let callCount = 0;

    // Intercepter la requête : première fois erreur, deuxième fois succès
    await page.route(
      `**/v1/billing/checkout/session?session_id=${mockSessionId}`,
      (route) => {
        callCount++;
        if (callCount === 1) {
          // Premier appel : erreur 500
          route.fulfill({
            status: 500,
            contentType: 'application/json',
            body: JSON.stringify({
              message: 'Erreur serveur',
            }),
          });
        } else {
          // Deuxième appel : succès
          route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              status: 'paid',
              session_id: mockSessionId,
              plan: 'plus',
            }),
          });
        }
      }
    );

    // Naviguer vers la page success
    await page.goto(`/billing/success?session_id=${mockSessionId}`);

    // Attendre l'erreur initiale
    await expect(page.locator('text=Erreur de validation')).toBeVisible({
      timeout: 5000,
    });

    // Cliquer sur le bouton de retry
    const retryButton = page.locator('button:has-text("Réessayer")');
    await expect(retryButton).toBeVisible();
    await retryButton.click();

    // Attendre que le succès soit affiché après retry
    await expect(page.locator('text=Paiement réussi !')).toBeVisible({
      timeout: 5000,
    });
  });

  test('devrait afficher message si statut unpaid', async ({ page }) => {
    const mockSessionId = 'cs_test_unpaid';
    const mockSessionData = {
      status: 'unpaid',
      session_id: mockSessionId,
    };

    // Intercepter la requête avec statut unpaid
    await page.route(
      `**/v1/billing/checkout/session?session_id=${mockSessionId}`,
      (route) => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(mockSessionData),
        });
      }
    );

    // Naviguer vers la page success
    await page.goto(`/billing/success?session_id=${mockSessionId}`);

    // Attendre le message unpaid
    await expect(page.locator('text=Paiement non finalisé')).toBeVisible({
      timeout: 5000,
    });

    await expect(
      page.locator("text=Le paiement n'a pas été finalisé")
    ).toBeVisible();
  });

  test('devrait afficher message si statut expired', async ({ page }) => {
    const mockSessionId = 'cs_test_expired';
    const mockSessionData = {
      status: 'expired',
      session_id: mockSessionId,
    };

    // Intercepter la requête avec statut expired
    await page.route(
      `**/v1/billing/checkout/session?session_id=${mockSessionId}`,
      (route) => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(mockSessionData),
        });
      }
    );

    // Naviguer vers la page success
    await page.goto(`/billing/success?session_id=${mockSessionId}`);

    // Attendre le message expired
    await expect(page.locator('text=Paiement non finalisé')).toBeVisible({
      timeout: 5000,
    });

    await expect(
      page.locator('text=La session de paiement a expiré')
    ).toBeVisible();
  });
});
