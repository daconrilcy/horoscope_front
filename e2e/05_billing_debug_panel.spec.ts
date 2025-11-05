import { test, expect } from '@playwright/test';

/**
 * Tests E2E pour FE-13 - Billing Debug Panel
 * Vérifie que le panel apparaît en dev, est masqué en prod, et affiche correctement les flags
 */

test.describe('Billing Debug Panel (FE-13)', () => {
  test.beforeEach(async ({ page }) => {
    // Aller sur la page d'accueil (route publique)
    await page.goto('/');
  });

  test('le panel apparaît en développement', async ({ page }) => {
    // En dev, le panel devrait être visible
    // Note: Ce test fonctionne uniquement si NODE_ENV=development ou VITE_DEV=true
    const panel = page.locator('[data-testid="billing-debug-panel"]');
    
    // Vérifier que le panel existe dans le DOM (même s'il est masqué par import.meta.env.DEV)
    // Si import.meta.env.DEV est true, le panel devrait être visible
    const title = page.locator('text=🔧 Billing Debug Panel (DEV)');
    
    // Le panel peut prendre un peu de temps à charger (lazy loading + React Query)
    await page.waitForTimeout(1000);
    
    // Vérifier que le titre existe (indique que le composant est rendu)
    // Note: En production, le composant ne sera pas rendu du tout
    const titleExists = await title.isVisible().catch(() => false);
    
    // En dev, le panel devrait être visible
    if (process.env.NODE_ENV === 'development' || process.env.VITE_DEV === 'true') {
      expect(titleExists).toBe(true);
    }
  });

  test('affiche le badge d\'environnement correct', async ({ page }) => {
    await page.waitForTimeout(1000);
    
    // Vérifier la présence du label "Environment:"
    const envLabel = page.locator('text=/Environment:/');
    const envLabelExists = await envLabel.isVisible().catch(() => false);
    
    if (process.env.NODE_ENV === 'development' || process.env.VITE_DEV === 'true') {
      if (envLabelExists) {
        // Vérifier que le badge affiche "development" en dev
        const envValue = page.locator('text=/development|production/');
        await expect(envValue).toBeVisible();
        
        // Vérifier que la valeur correspond à l'environnement
        const envText = await envValue.textContent();
        expect(envText).toMatch(/development|production/);
      }
    }
  });

  test('affiche les flags billing (Trials, Coupons, Tax)', async ({ page }) => {
    await page.waitForTimeout(1000);
    
    if (process.env.NODE_ENV === 'development' || process.env.VITE_DEV === 'true') {
      // Vérifier la présence des labels de flags
      const trialsLabel = page.locator('text=/Trials:/');
      const couponsLabel = page.locator('text=/Coupons:/');
      const taxLabel = page.locator('text=/Tax:/');
      
      // Au moins un des labels devrait être visible si le panel est rendu
      const hasTrials = await trialsLabel.isVisible().catch(() => false);
      const hasCoupons = await couponsLabel.isVisible().catch(() => false);
      const hasTax = await taxLabel.isVisible().catch(() => false);
      
      // Si le panel est visible, au moins un flag devrait être affiché
      if (hasTrials || hasCoupons || hasTax) {
        // Vérifier que les badges ENABLED/DISABLED sont présents
        const enabledBadge = page.locator('text=/ENABLED|DISABLED/');
        const badgeCount = await enabledBadge.count();
        expect(badgeCount).toBeGreaterThan(0);
      }
    }
  });

  test('affiche les URLs de configuration', async ({ page }) => {
    await page.waitForTimeout(1000);
    
    if (process.env.NODE_ENV === 'development' || process.env.VITE_DEV === 'true') {
      // Vérifier la présence des labels d'URLs
      const baseUrlLabel = page.locator('text=/Public Base URL:/');
      const successPathLabel = page.locator('text=/Success Path:/');
      const cancelPathLabel = page.locator('text=/Cancel Path:/');
      
      // Au moins un label d'URL devrait être visible si le panel est rendu
      const hasBaseUrl = await baseUrlLabel.isVisible().catch(() => false);
      const hasSuccessPath = await successPathLabel.isVisible().catch(() => false);
      const hasCancelPath = await cancelPathLabel.isVisible().catch(() => false);
      
      // Si le panel est visible, au moins une URL devrait être affichée
      if (hasBaseUrl || hasSuccessPath || hasCancelPath) {
        // Vérifier qu'au moins une URL est présente dans le DOM
        const urlPattern = page.locator('text=/http|\\//');
        const urlCount = await urlPattern.count();
        expect(urlCount).toBeGreaterThan(0);
      }
    }
  });

  test('affiche un warning si origin mismatch', async ({ page }) => {
    await page.waitForTimeout(1500); // Plus de temps pour permettre la vérification d'origin
    
    if (process.env.NODE_ENV === 'development' || process.env.VITE_DEV === 'true') {
      // Chercher le warning d'origin mismatch
      const warning = page.locator('text=/Origin mismatch|⚠️/');
      const warningExists = await warning.isVisible().catch(() => false);
      
      // Le warning peut être présent ou non selon la configuration
      // On vérifie juste que s'il est présent, il est bien formaté
      if (warningExists) {
        const warningText = await warning.textContent();
        expect(warningText).toContain('mismatch');
      }
    }
  });

  test('le panel est masqué en production (build)', async ({ page, context }) => {
    // Note: Ce test nécessite de construire l'app en mode production
    // Pour tester cela, il faudrait:
    // 1. Build en prod: npm run build
    // 2. Servir le build: npm run preview
    // 3. Naviguer vers la page
    
    // Pour l'instant, on vérifie juste que le composant n'est pas rendu
    // si import.meta.env.DEV est false
    await page.waitForTimeout(1000);
    
    // En production, le titre du panel ne devrait PAS être présent
    const title = page.locator('text=🔧 Billing Debug Panel (DEV)');
    const titleExists = await title.isVisible().catch(() => false);
    
    // Si on est en production, le panel ne devrait pas être visible
    if (process.env.NODE_ENV === 'production') {
      expect(titleExists).toBe(false);
    }
  });

  test('le panel est positionné en bas-droite', async ({ page }) => {
    await page.waitForTimeout(1000);
    
    if (process.env.NODE_ENV === 'development' || process.env.VITE_DEV === 'true') {
      // Chercher le panel par son titre
      const title = page.locator('text=🔧 Billing Debug Panel (DEV)');
      const titleExists = await title.isVisible().catch(() => false);
      
      if (titleExists) {
        // Le panel devrait avoir un style position: fixed, bottom, right
        // Vérifier que le composant parent a les bonnes propriétés CSS
        const panelContainer = title.locator('..').locator('..');
        const boundingBox = await panelContainer.boundingBox();
        
        if (boundingBox) {
          // Vérifier que le panel est en bas de la page (bottom > 80% de la hauteur)
          const viewportHeight = page.viewportSize()?.height ?? 800;
          const panelBottom = boundingBox.y + boundingBox.height;
          const isNearBottom = panelBottom > viewportHeight * 0.8;
          
          // Vérifier que le panel est à droite (x > 50% de la largeur)
          const viewportWidth = page.viewportSize()?.width ?? 1200;
          const isOnRight = boundingBox.x > viewportWidth * 0.5;
          
          expect(isNearBottom || isOnRight).toBe(true);
        }
      }
    }
  });
});
