# CS-042 CSS fallbacks after

## Result

- Global fallback count after selected shared batch: 117.
- Reduction: 45 fallback occurrences removed from the original 165-entry executable contract.
- Registry and executable allowlist are synchronized after reduction.

## Current scan

`	ext
frontend/src\App.css:1949:  color: var(--error, #ff6b6b);
frontend/src\App.css:2467:  border-color: var(--success, #4ade80);
frontend/src\App.css:2468:  background: var(--success, #4ade80);
frontend/src\App.css:2815:  gap: var(--space-3, 0.75rem);
frontend/src\App.css:2816:  padding: var(--space-3, 0.75rem) var(--space-4, 1rem);
frontend/src\App.css:2819:  border-radius: var(--radius-lg, 12px);
frontend/src\App.css:2820:  margin-bottom: var(--space-4, 1rem);
frontend/src\App.css:2870:  gap: var(--space-6, 1.5rem);
frontend/src\App.css:2878:  margin-bottom: var(--space-2, 0.5rem);
frontend/src\App.css:2884:  gap: var(--space-3, 0.75rem);
frontend/src\App.css:2891:  gap: var(--space-2, 0.5rem);
frontend/src\App.css:2892:  padding: var(--space-3, 0.75rem) var(--space-4, 1rem);
frontend/src\App.css:2895:  border-radius: var(--radius-lg, 12px);
frontend/src\App.css:2897:  transition: all var(--duration-normal, 200ms) ease;
frontend/src\App.css:2931:  padding: var(--space-4, 1rem);
frontend/src\App.css:2934:  border-radius: var(--radius-lg, 12px);
frontend/src\App.css:3422:  background: var(--success, #4ade80);
frontend/src\App.css:3423:  border-color: var(--success, #4ade80);
frontend/src\App.css:3596:  width: calc(var(--usage-progress, 0) * 1%);
frontend/src\styles\glass.css:4:  backdrop-filter: blur(var(--surface-glass-blur, 14px));
frontend/src\styles\glass.css:5:  -webkit-backdrop-filter: blur(var(--surface-glass-blur, 14px));
frontend/src\styles\utilities.css:76:  backdrop-filter: blur(var(--surface-glass-blur, 14px));
frontend/src\styles\utilities.css:77:  -webkit-backdrop-filter: blur(var(--surface-glass-blur, 14px));
frontend/src\pages\BirthProfilePage.css:29:  border-bottom: 1px solid var(--border-color, #eee);
frontend/src\pages\BirthProfilePage.css:35:  color: var(--text-secondary, #666);
frontend/src\pages\BirthProfilePage.css:53:  background-color: var(--bg-secondary, #f9f9f9);
frontend/src\pages\BirthProfilePage.css:61:  background-color: var(--bg-button-secondary, #eee);
frontend/src\pages\BirthProfilePage.css:62:  color: var(--text-button-secondary, #333);
frontend/src\pages\BirthProfilePage.css:63:  border: 1px solid var(--border-color, #ccc);
frontend/src\pages\BirthProfilePage.css:71:  background-color: var(--bg-button-secondary-hover, #ddd);
frontend/src\pages\HelpPage.css:856:  color: var(--settings-text-body, var(--text-2));
frontend/src\pages\HelpPage.css:863:  color: var(--settings-text-heading, var(--text-1));
frontend/src\pages\HelpPage.css:971:  color: var(--settings-text-muted, var(--text-2));
frontend/src\pages\HelpPage.css:1005:  color: var(--settings-text-body, var(--text-2));
frontend/src\pages\HelpPage.css:1214:  color: var(--settings-text-muted, var(--text-2));
frontend/src\pages\HelpPage.css:1247:  color: var(--settings-text-muted, var(--text-2));
frontend/src\pages\HelpPage.css:1259:  color: var(--settings-text-body, var(--text-2));
frontend/src\pages\HelpPage.css:1383:  color: var(--settings-text-muted, var(--text-2));
frontend/src\pages\HelpPage.css:1389:  color: var(--settings-text-body, var(--text-2));
frontend/src\pages\HelpPage.css:1455:  color: var(--settings-text-muted, var(--text-2));
frontend/src\pages\HelpPage.css:1545:  color: var(--settings-text-body, var(--text-2));
frontend/src\pages\admin\AdminEntitlementsPage.css:44:  background: var(--glass-heavy, #1a1a1a);
frontend/src\pages\NatalChartPage.css:60:  color: var(--premium-text-meta, var(--text-faint));
frontend/src\pages\NatalChartPage.css:72:  color: var(--premium-text-strong, var(--text-strong));
frontend/src\pages\NatalChartPage.css:86:  color: var(--premium-text-main, var(--text-main));
frontend/src\pages\NatalChartPage.css:93:  border: 1px solid var(--premium-glass-border-strong, rgba(255, 255, 255, 0.58));
frontend/src\pages\NatalChartPage.css:95:  color: var(--premium-accent-purple-strong, var(--primary-strong));
frontend/src\pages\NatalChartPage.css:117:  color: var(--premium-text-muted, var(--text-muted));
frontend/src\pages\NatalChartPage.css:134:  background: var(--premium-glass-surface-1, rgba(255, 255, 255, 0.45));
frontend/src\pages\NatalChartPage.css:137:  border: 1px solid var(--premium-glass-border, rgba(255, 255, 255, 0.5));
frontend/src\pages\NatalChartPage.css:138:  border-radius: var(--premium-radius-card, 24px);
frontend/src\pages\NatalChartPage.css:140:  box-shadow: var(--premium-shadow-card, 0 10px 30px rgba(0,0,0,0.05));
frontend/src\pages\NatalChartPage.css:146:  box-shadow: var(--premium-shadow-focus, 0 15px 45px rgba(0,0,0,0.08));
frontend/src\pages\NatalChartPage.css:153:  color: var(--premium-text-strong, var(--text-strong));
frontend/src\pages\NatalChartPage.css:218:  color: var(--premium-text-meta, var(--text-faint));
frontend/src\pages\NatalChartPage.css:230:  color: var(--premium-accent-purple-strong, var(--primary-strong));
frontend/src\pages\NatalChartPage.css:244:  color: var(--premium-text-main, var(--text-main));
frontend/src\pages\NatalChartPage.css:259:  color: var(--premium-text-main, var(--text-main));
frontend/src\pages\NatalChartPage.css:261:  border-bottom: 1px solid var(--premium-glass-border-soft, rgba(255, 255, 255, 0.2));
frontend/src\pages\NatalChartPage.css:296:  color: var(--premium-text-strong, var(--text-strong));
frontend/src\pages\NatalChartPage.css:302:  color: var(--premium-accent-purple-strong, var(--primary-strong));
frontend/src\pages\NatalChartPage.css:317:  color: var(--premium-text-main, var(--text-main));
frontend/src\pages\NatalChartPage.css:328:  color: var(--premium-text-main, var(--text-main));
frontend/src\pages\NatalChartPage.css:337:  color: var(--premium-text-meta, var(--text-faint));
frontend/src\pages\NatalChartPage.css:343:  color: var(--premium-text-main, var(--text-main));
frontend/src\pages\NatalChartPage.css:349:  background: var(--premium-glass-surface-2, rgba(255, 255, 255, 0.35));
frontend/src\pages\NatalChartPage.css:350:  border: 1px solid var(--premium-glass-border-soft, rgba(255, 255, 255, 0.3));
frontend/src\pages\NatalChartPage.css:351:  border-radius: var(--premium-radius-card, 24px);
frontend/src\pages\NatalChartPage.css:357:  background: var(--premium-glass-surface-1, rgba(255, 255, 255, 0.45));
frontend/src\pages\NatalChartPage.css:358:  box-shadow: var(--premium-shadow-focus, 0 15px 45px rgba(0,0,0,0.08));
frontend/src\pages\NatalChartPage.css:480:  color: var(--premium-accent-purple-strong, var(--primary-strong));
frontend/src\pages\NatalChartPage.css:491:  color: var(--premium-text-strong, var(--text-strong));
frontend/src\pages\NatalChartPage.css:498:  color: var(--premium-text-main, var(--text-main));
frontend/src\pages\NatalChartPage.css:522:  color: var(--premium-text-meta, var(--text-faint));
frontend/src\pages\NatalChartPage.css:529:  color: var(--premium-text-strong, var(--text-strong));
frontend/src\pages\admin\AdminPromptsPage.css:1114:  background: color-mix(in srgb, var(--color-accent, var(--color-primary)) 14%, transparent);
frontend/src\features\chat\components\ChatWindow.css:84:  border-radius: var(--premium-radius-pill, 999px);
frontend/src\pages\settings\Settings.css:533:  border: 1px solid var(--settings-purple-border, rgba(134, 108, 208, 0.28));
frontend/src\pages\settings\Settings.css:534:  color: var(--settings-purple, #866cd0);
frontend/src\pages\settings\Settings.css:1052:  width: calc(var(--usage-progress, 0) * 1%);
frontend/src\components\NatalInterpretation.css:6:  border-top: 1px solid var(--premium-glass-border-soft, rgba(255, 255, 255, 0.2));
frontend/src\components\NatalInterpretation.css:96:  border-radius: var(--premium-radius-pill, 999px);
frontend/src\components\NatalInterpretation.css:139:  border-radius: var(--premium-radius-pill, 999px);
frontend/src\components\NatalInterpretation.css:1032:  padding: var(--space-3, 0.75rem) var(--space-4, 1rem);
frontend/src\components\NatalInterpretation.css:1048:  font-size: var(--font-size-sm, 0.875rem);
frontend/src\components\layout\Sidebar.css:58:  gap: var(--space-1, 0.25rem);
frontend/src\components\layout\Sidebar.css:59:  padding: var(--space-4, 1rem) 0;
frontend/src\components\layout\Sidebar.css:65:  gap: var(--space-3, 0.75rem);
frontend/src\components\layout\Sidebar.css:66:  padding: var(--space-3, 0.75rem);
frontend/src\components\layout\Sidebar.css:92:  padding: var(--space-3, 0.75rem);
frontend/src\components\layout\Sidebar.css:98:  border-radius: var(--radius-md, 0.5rem);
frontend/src\components\layout\Header.css:5:  padding: 0 var(--space-4, 1rem);
frontend/src\components\layout\Header.css:21:  gap: var(--space-3, 0.75rem);
frontend/src\components\layout\Header.css:34:  padding: var(--space-2, 0.5rem);
frontend/src\components\layout\Header.css:35:  border-radius: var(--radius-md, 0.5rem);
frontend/src\components\layout\Header.css:58:  gap: var(--space-3, 0.75rem);
frontend/src\components\layout\Header.css:62:  padding-left: var(--space-2, 0.5rem);
frontend/src\components\layout\Header.css:93:  gap: var(--space-3, 0.75rem);
frontend/src\components\layout\Header.css:111:    padding: 0 var(--space-3, 0.75rem);
frontend/src\components\layout\Header.css:115:    gap: var(--space-2, 0.5rem);
frontend/src\pages\landing\sections\TestimonialsSection.css:170:.case-study-column--after .case-study-label { color: var(--success, #2ecc71); }
frontend/src\components\SignUpForm.css:74:  color: var(--danger, #ff6b81);
frontend/src\components\prediction\CategoryGrid.css:30:  margin: var(--space-1, 0.25rem) 0;
frontend/src\components\prediction\PeriodCard.css:136:    color: var(--color-text-muted, rgba(30, 27, 46, 0.45));
frontend/src\components\prediction\PeriodCard.css:202:    background: var(--color-error, #ff6b81);
frontend/src\components\prediction\PeriodCard.css:224:    color: var(--color-text-muted, rgba(30, 27, 46, 0.55));
frontend/src\components\prediction\PeriodCard.css:231:    color: var(--color-text-secondary, rgba(30, 27, 46, 0.72));
frontend/src\components\prediction\PeriodCard.css:259:    color: var(--color-text-muted, rgba(30, 27, 46, 0.35));
frontend/src\components\prediction\PeriodCard.css:267:    color: var(--color-text-muted, rgba(30, 27, 46, 0.5));
frontend/src\components\prediction\KeyPointCard.css:9:  box-shadow: var(--shadow-hero-card, 0 4px 20px rgba(44, 28, 100, 0.15));
frontend/src\components\prediction\KeyPointCard.css:49:  color: var(--color-hero-ink, var(--color-text-primary));
frontend/src\components\prediction\KeyPointCard.css:68:  background: linear-gradient(90deg, var(--color-primary), var(--color-hero-ink-accent, var(--color-primary)));
frontend/src\components\prediction\DayPredictionCard.css:4:  margin-top: var(--space-6, 1.5rem);
frontend/src\components\prediction\DayPredictionCard.css:28:  margin-top: var(--space-6, 1.5rem);
frontend/src\components\prediction\DayPredictionCard.css:29:  padding: var(--space-4, 1rem);
frontend/src\components\prediction\DayPredictionCard.css:41:  margin: 0 0 var(--space-2, 0.5rem) 0;
frontend/src\components\prediction\DayPredictionCard.css:53:  margin: var(--space-1, 0.25rem) 0 0 0;
`

## Guard evidence

- 
pm run test -- css-fallback design-system: covered by combined target run and PASS.
