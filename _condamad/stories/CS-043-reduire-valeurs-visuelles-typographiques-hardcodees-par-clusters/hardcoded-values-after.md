# CS-043 hardcoded values after

## Result

- Migrated literals in selected cluster to existing semantic tokens/classes:
  - Button.css danger text now uses ar(--color-text-on-astro).
  - Settings.css feedback/delete action colors use existing admin/status tokens.
  - Static visual TSX literals moved to CSS classes and spacing tokens.
- No new token namespace or typography role was introduced.

## Remaining literals in selected files

Reason: existing page/component-specific visual vocabulary outside this bounded cluster remains documented debt for future batches.
Exit: migrate in a later cluster when a clear token mapping exists.

`	ext
frontend/src/components/ui/Form/Form.css:5:  margin: 0;
frontend/src/components/ui/Form/Form.css:6:  padding: 0;
frontend/src/components/ui/Button/Button.css:7:  border-radius: var(--radius-full);
frontend/src/components/ui/Button/Button.css:12:  font-weight: var(--font-weight-semibold);
frontend/src/components/ui/Button/Button.css:37:  box-shadow: var(--shadow-cta);
frontend/src/components/ui/Button/Button.css:66:  background: rgba(255, 255, 255, 0.05);
frontend/src/components/ui/Button/Button.css:80:  padding: var(--space-2) var(--space-4);
frontend/src/components/ui/Button/Button.css:81:  font-size: var(--font-size-sm);
frontend/src/components/ui/Button/Button.css:85:  padding: var(--space-3) var(--space-6);
frontend/src/components/ui/Button/Button.css:86:  font-size: var(--font-size-md);
frontend/src/components/ui/Button/Button.css:90:  padding: var(--space-4) var(--space-8);
frontend/src/components/ui/Button/Button.css:91:  font-size: var(--font-size-lg);
frontend/src/components/ui/Button/Button.css:112:  border-radius: 50%;
frontend/src/pages/settings/Settings.css:3:  --settings-purple: #866cd0;
frontend/src/pages/settings/Settings.css:5:  --settings-purple-soft: rgba(134, 108, 208, 0.12);
frontend/src/pages/settings/Settings.css:6:  --settings-purple-border: rgba(134, 108, 208, 0.28);
frontend/src/pages/settings/Settings.css:7:  --settings-gold: #d59a39;
frontend/src/pages/settings/Settings.css:9:  --settings-gold-soft: rgba(213, 154, 57, 0.16);
frontend/src/pages/settings/Settings.css:10:  --settings-gold-border: rgba(213, 154, 57, 0.28);
frontend/src/pages/settings/Settings.css:13:  --settings-card-surface: rgba(255, 255, 255, 0.62);
frontend/src/pages/settings/Settings.css:14:  --settings-card-surface-strong: rgba(255, 255, 255, 0.76);
frontend/src/pages/settings/Settings.css:15:  --settings-card-border: rgba(205, 217, 240, 0.72);
frontend/src/pages/settings/Settings.css:16:  --settings-card-shadow: 0 22px 60px rgba(132, 150, 190, 0.16);
frontend/src/pages/settings/Settings.css:17:  --settings-card-shadow-soft: 0 16px 42px rgba(132, 150, 190, 0.12);
frontend/src/pages/settings/Settings.css:20:  --settings-text-heading: #24334d;
frontend/src/pages/settings/Settings.css:21:  --settings-text-body: #4f5f78;
frontend/src/pages/settings/Settings.css:22:  --settings-text-muted: #7f8da4;
frontend/src/pages/settings/Settings.css:27:  margin: 0 auto;
frontend/src/pages/settings/Settings.css:28:  padding: 24px 24px 96px;
frontend/src/pages/settings/Settings.css:35:  padding: 0 !important;
frontend/src/pages/settings/Settings.css:36:  margin: 0 !important;
frontend/src/pages/settings/Settings.css:41:  padding: 0 !important;
frontend/src/pages/settings/Settings.css:54:    radial-gradient(circle at 10% 16%, rgba(171, 148, 255, 0.34) 0%, transparent 28%),
frontend/src/pages/settings/Settings.css:55:    radial-gradient(circle at 80% 12%, rgba(190, 170, 255, 0.22) 0%, transparent 26%),
frontend/src/pages/settings/Settings.css:56:    radial-gradient(circle at 55% 80%, rgba(241, 218, 168, 0.20) 0%, transparent 30%),
frontend/src/pages/settings/Settings.css:57:    linear-gradient(180deg, #fdfcff 0%, #f7f4ff 48%, #f0f5ff 100%);
frontend/src/pages/settings/Settings.css:70:  border-radius: 26px;
frontend/src/pages/settings/Settings.css:72:  box-shadow: var(--settings-card-shadow);
frontend/src/pages/settings/Settings.css:75:  padding: 28px 32px;
frontend/src/pages/settings/Settings.css:86:  box-shadow: var(--settings-card-shadow-soft);
frontend/src/pages/settings/Settings.css:87:  border-radius: 22px;
frontend/src/pages/settings/Settings.css:88:  padding: 22px 26px;
frontend/src/pages/settings/Settings.css:115:  background: linear-gradient(180deg, rgba(229, 224, 255, 0.86) 0%, rgba(218, 210, 255, 0.72) 100%);
frontend/src/pages/settings/Settings.css:117:  border-radius: 22px;
frontend/src/pages/settings/Settings.css:118:  box-shadow: var(--settings-card-shadow-soft);
frontend/src/pages/settings/Settings.css:122:  margin: 0 0 18px;
frontend/src/pages/settings/Settings.css:125:  font-size: clamp(1.6rem, 2.2vw, 2rem);
frontend/src/pages/settings/Settings.css:127:  line-height: 1.05;
frontend/src/pages/settings/Settings.css:128:  font-weight: 600;
frontend/src/pages/settings/Settings.css:136:  font-size: 1.2rem;
frontend/src/pages/settings/Settings.css:153:  border-radius: var(--radius-full);
frontend/src/pages/settings/Settings.css:154:  background: linear-gradient(90deg, var(--settings-purple) 0%, rgba(134, 108, 208, 0.4) 100%);
frontend/src/pages/settings/Settings.css:159:  margin: -4px 0 18px;
frontend/src/pages/settings/Settings.css:161:  font-size: 14px;
frontend/src/pages/settings/Settings.css:162:  line-height: 1.6;
frontend/src/pages/settings/Settings.css:166:  margin: -6px 0 18px;
frontend/src/pages/settings/Settings.css:168:  font-size: 14px;
frontend/src/pages/settings/Settings.css:169:  line-height: 1.6;
frontend/src/pages/settings/Settings.css:177:  padding: 28px;
frontend/src/pages/settings/Settings.css:178:  border-radius: 28px;
frontend/src/pages/settings/Settings.css:180:    radial-gradient(circle at top right, rgba(213, 154, 57, 0.18) 0%, rgba(213, 154, 57, 0) 32%),
frontend/src/pages/settings/Settings.css:181:    radial-gradient(circle at 18% 18%, rgba(134, 108, 208, 0.16) 0%, rgba(134, 108, 208, 0) 28%),
frontend/src/pages/settings/Settings.css:182:    linear-gradient(180deg, rgba(255, 255, 255, 0.86) 0%, rgba(246, 241, 255, 0.72) 100%);
frontend/src/pages/settings/Settings.css:183:  border: 1px solid rgba(205, 217, 240, 0.82);
frontend/src/pages/settings/Settings.css:184:  box-shadow:
frontend/src/pages/settings/Settings.css:185:    0 24px 58px rgba(132, 150, 190, 0.14),
frontend/src/pages/settings/Settings.css:186:    inset 0 1px 0 rgba(255, 255, 255, 0.5);
frontend/src/pages/settings/Settings.css:205:  font-size: var(--type-page-title-size);
frontend/src/pages/settings/Settings.css:206:  font-weight: var(--type-page-title-weight);
frontend/src/pages/settings/Settings.css:207:  line-height: var(--type-page-title-line-height);
frontend/src/pages/settings/Settings.css:214:  padding: 0.42rem 0.82rem;
frontend/src/pages/settings/Settings.css:215:  border-radius: var(--radius-full);
frontend/src/pages/settings/Settings.css:216:  background: rgba(134, 108, 208, 0.1);
frontend/src/pages/settings/Settings.css:217:  border: 1px solid rgba(134, 108, 208, 0.18);
frontend/src/pages/settings/Settings.css:219:  font-size: 0.72rem;
frontend/src/pages/settings/Settings.css:220:  font-weight: 700;
frontend/src/pages/settings/Settings.css:221:  letter-spacing: 0.12em;
frontend/src/pages/settings/Settings.css:226:  margin: 8px 0 0;
frontend/src/pages/settings/Settings.css:229:  font-size: clamp(2rem, 3.2vw, 2.8rem);
frontend/src/pages/settings/Settings.css:230:  line-height: 1;
frontend/src/pages/settings/Settings.css:231:  letter-spacing: -0.05em;
frontend/src/pages/settings/Settings.css:235:  margin: 0;
frontend/src/pages/settings/Settings.css:237:  font-size: 0.82rem;
frontend/src/pages/settings/Settings.css:238:  font-weight: 700;
frontend/src/pages/settings/Settings.css:239:  letter-spacing: 0.12em;
frontend/src/pages/settings/Settings.css:244:  margin: 0;
frontend/src/pages/settings/Settings.css:247:  font-size: 0.98rem;
frontend/src/pages/settings/Settings.css:248:  line-height: 1.64;
frontend/src/pages/settings/Settings.css:255:  margin: 0;
frontend/src/pages/settings/Settings.css:256:  padding: 0;
frontend/src/pages/settings/Settings.css:265:  font-size: 0.92rem;
frontend/src/pages/settings/Settings.css:266:  line-height: 1.5;
frontend/src/pages/settings/Settings.css:280:  padding: 22px 20px;
frontend/src/pages/settings/Settings.css:281:  border-radius: 22px;
frontend/src/pages/settings/Settings.css:283:    radial-gradient(circle at top right, rgba(213, 154, 57, 0.16) 0%, rgba(213, 154, 57, 0) 42%),
frontend/src/pages/settings/Settings.css:284:    linear-gradient(180deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 250, 243, 0.8) 100%);
frontend/src/pages/settings/Settings.css:285:  border: 1px solid rgba(223, 208, 185, 0.9);
frontend/src/pages/settings/Settings.css:286:  box-shadow:
frontend/src/pages/settings/Settings.css:287:    0 20px 42px rgba(132, 150, 190, 0.12),
frontend/src/pages/settings/Settings.css:288:    inset 0 1px 0 rgba(255, 255, 255, 0.52);
frontend/src/pages/settings/Settings.css:294:  font-size: 0.72rem;
frontend/src/pages/settings/Settings.css:295:  font-weight: 700;
frontend/src/pages/settings/Settings.css:296:  letter-spacing: 0.08em;
frontend/src/pages/settings/Settings.css:301:  margin: 0;
frontend/src/pages/settings/Settings.css:303:  font-size: 0.94rem;
frontend/src/pages/settings/Settings.css:304:  line-height: 1.58;
frontend/src/pages/settings/Settings.css:305:  font-weight: 600;
frontend/src/pages/settings/Settings.css:324:  padding: 18px 18px 20px;
frontend/src/pages/settings/Settings.css:325:  border-radius: 20px;
frontend/src/pages/settings/Settings.css:327:    linear-gradient(180deg, rgba(255, 255, 255, 0.78) 0%, rgba(255, 255, 255, 0.62) 100%);
frontend/src/pages/settings/Settings.css:328:  border: 1px solid rgba(205, 217, 240, 0.78);
frontend/src/pages/settings/Settings.css:329:  box-shadow: 0 14px 32px rgba(132, 150, 190, 0.08);
frontend/src/pages/settings/Settings.css:334:  font-size: 0.96rem;
frontend/src/pages/settings/Settings.css:335:  line-height: 1.45;
frontend/src/pages/settings/Settings.css:336:  font-weight: 700;
frontend/src/pages/settings/Settings.css:350:  margin: 0;
frontend/src/pages/settings/Settings.css:352:  font-size: 0.92rem;
frontend/src/pages/settings/Settings.css:353:  line-height: 1.6;
frontend/src/pages/settings/Settings.css:367:  padding: 0 20px;
frontend/src/pages/settings/Settings.css:368:  border-radius: var(--radius-full);
frontend/src/pages/settings/Settings.css:370:  border: 1px solid rgba(197, 211, 233, 0.86);
frontend/src/pages/settings/Settings.css:372:  background: rgba(255, 255, 255, 0.68);
frontend/src/pages/settings/Settings.css:374:  box-shadow: 0 10px 24px rgba(132, 150, 190, 0.10);
frontend/src/pages/settings/Settings.css:377:  font-size: 14px;
frontend/src/pages/settings/Settings.css:378:  font-weight: 600;
frontend/src/pages/settings/Settings.css:390:  border-color: rgba(163, 143, 220, 0.88);
frontend/src/pages/settings/Settings.css:391:  background: rgba(255, 255, 255, 0.82);
frontend/src/pages/settings/Settings.css:392:  box-shadow: 0 14px 28px rgba(132, 150, 190, 0.14);
frontend/src/pages/settings/Settings.css:398:  color: #fff;
frontend/src/pages/settings/Settings.css:399:  box-shadow: 0 10px 28px rgba(134, 108, 208, 0.28);
frontend/src/pages/settings/Settings.css:403:  background: #7460bb;
frontend/src/pages/settings/Settings.css:404:  border-color: #7460bb;
frontend/src/pages/settings/Settings.css:405:  color: #fff;
frontend/src/pages/settings/Settings.css:410:  background: rgba(195, 206, 225, 0.72);
frontend/src/pages/settings/Settings.css:412:  margin: 24px 0;
frontend/src/pages/settings/Settings.css:429:  padding: 18px 16px;
frontend/src/pages/settings/Settings.css:430:  border-radius: 18px;
frontend/src/pages/settings/Settings.css:444:  border-color: rgba(163, 143, 220, 0.64);
frontend/src/pages/settings/Settings.css:445:  background: rgba(255, 255, 255, 0.78);
frontend/src/pages/settings/Settings.css:446:  box-shadow: 0 12px 32px rgba(134, 108, 208, 0.10);
frontend/src/pages/settings/Settings.css:454:  box-shadow: 0 14px 38px rgba(134, 108, 208, 0.16);
frontend/src/pages/settings/Settings.css:461:  border-radius: 50%;
frontend/src/pages/settings/Settings.css:465:  box-shadow: 0 6px 18px rgba(111, 135, 166, 0.16);
frontend/src/pages/settings/Settings.css:472:  border-radius: 50%;
frontend/src/pages/settings/Settings.css:473:  background: linear-gradient(180deg, rgba(241, 237, 255, 0.96) 0%, rgba(221, 212, 250, 0.94) 100%);
frontend/src/pages/settings/Settings.css:479:  font-size: 22px;
frontend/src/pages/settings/Settings.css:484:  font-size: 14px;
frontend/src/pages/settings/Settings.css:485:  font-weight: 600;
frontend/src/pages/settings/Settings.css:486:  line-height: 1.3;
frontend/src/pages/settings/Settings.css:491:  font-size: 12px;
frontend/src/pages/settings/Settings.css:492:  line-height: 1.3;
frontend/src/pages/settings/Settings.css:500:  padding: 3px 10px;
frontend/src/pages/settings/Settings.css:501:  border-radius: var(--radius-full);
frontend/src/pages/settings/Settings.css:503:  color: #fff;
frontend/src/pages/settings/Settings.css:504:  font-size: 11px;
frontend/src/pages/settings/Settings.css:505:  font-weight: 700;
frontend/src/pages/settings/Settings.css:506:  letter-spacing: 0.04em;
frontend/src/pages/settings/Settings.css:514:  padding: 5px 12px;
frontend/src/pages/settings/Settings.css:515:  border-radius: var(--radius-full);
frontend/src/pages/settings/Settings.css:516:  background: rgba(255, 255, 255, 0.84);
frontend/src/pages/settings/Settings.css:519:  font-size: 12px;
frontend/src/pages/settings/Settings.css:520:  font-weight: 700;
frontend/src/pages/settings/Settings.css:521:  letter-spacing: 0.04em;
frontend/src/pages/settings/Settings.css:530:  padding: 8px 16px;
frontend/src/pages/settings/Settings.css:531:  border-radius: var(--radius-full);
frontend/src/pages/settings/Settings.css:532:  background: rgba(255, 255, 255, 0.84);
frontend/src/pages/settings/Settings.css:533:  border: 1px solid var(--settings-purple-border, rgba(134, 108, 208, 0.28));
frontend/src/pages/settings/Settings.css:534:  color: var(--settings-purple, #866cd0);
frontend/src/pages/settings/Settings.css:535:  font-size: 13px;
frontend/src/pages/settings/Settings.css:536:  font-weight: 700;
frontend/src/pages/settings/Settings.css:537:  letter-spacing: 0.04em;
frontend/src/pages/settings/Settings.css:538:  box-shadow: 0 8px 20px rgba(134, 108, 208, 0.10);
frontend/src/pages/settings/Settings.css:548:  background: rgba(255, 255, 255, 0.5);
frontend/src/pages/settings/Settings.css:563:  margin: 20px 0;
frontend/src/pages/settings/Settings.css:572:  padding: 26px 24px;
frontend/src/pages/settings/Settings.css:573:  border-radius: 26px;
frontend/src/pages/settings/Settings.css:574:  border: 1px solid rgba(205, 217, 240, 0.82);
frontend/src/pages/settings/Settings.css:576:    linear-gradient(180deg, rgba(255, 255, 255, 0.8) 0%, rgba(250, 247, 255, 0.62) 100%);
frontend/src/pages/settings/Settings.css:578:  box-shadow:
frontend/src/pages/settings/Settings.css:579:    0 20px 44px rgba(132, 150, 190, 0.12),
frontend/src/pages/settings/Settings.css:580:    inset 0 1px 0 rgba(255, 255, 255, 0.5);
frontend/src/pages/settings/Settings.css:594:  outline: 2px solid rgba(134, 108, 208, 0.5);
frontend/src/pages/settings/Settings.css:609:  border-color: rgba(255, 255, 255, 0.4);
frontend/src/pages/settings/Settings.css:616:  border-radius: inherit;
frontend/src/pages/settings/Settings.css:617:  border: 1px solid rgba(255, 255, 255, 0.34);
frontend/src/pages/settings/Settings.css:628:  border-radius: 50%;
frontend/src/pages/settings/Settings.css:629:  background: radial-gradient(circle, rgba(134, 108, 208, 0.16) 0%, rgba(134, 108, 208, 0) 72%);
frontend/src/pages/settings/Settings.css:635:  border-color: rgba(134, 108, 208, 0.32);
frontend/src/pages/settings/Settings.css:636:  box-shadow:
frontend/src/pages/settings/Settings.css:637:    0 26px 52px rgba(132, 150, 190, 0.16),
frontend/src/pages/settings/Settings.css:638:    inset 0 1px 0 rgba(255, 255, 255, 0.54);
frontend/src/pages/settings/Settings.css:643:  border: 1px solid rgba(213, 154, 57, 0.56);
frontend/src/pages/settings/Settings.css:645:    radial-gradient(circle at top right, rgba(213, 154, 57, 0.22) 0%, rgba(213, 154, 57, 0) 34%),
frontend/src/pages/settings/Settings.css:646:    linear-gradient(180deg, rgba(255, 250, 243, 0.96) 0%, rgba(255, 247, 233, 0.88) 100%);
frontend/src/pages/settings/Settings.css:647:  box-shadow:
frontend/src/pages/settings/Settings.css:648:    0 30px 64px rgba(132, 150, 190, 0.16),
frontend/src/pages/settings/Settings.css:649:    0 0 0 1px rgba(213, 154, 57, 0.18);
frontend/src/pages/settings/Settings.css:655:    radial-gradient(circle at top center, rgba(134, 108, 208, 0.18) 0%, rgba(134, 108, 208, 0) 42%),
frontend/src/pages/settings/Settings.css:656:    linear-gradient(180deg, rgba(255, 255, 255, 0.88) 0%, rgba(248, 244, 255, 0.72) 100%);
frontend/src/pages/settings/Settings.css:661:    radial-gradient(circle at top right, rgba(213, 154, 57, 0.28) 0%, rgba(213, 154, 57, 0) 42%),
frontend/src/pages/settings/Settings.css:662:    linear-gradient(180deg, rgba(255, 252, 247, 0.92) 0%, rgba(255, 246, 233, 0.78) 100%);
frontend/src/pages/settings/Settings.css:663:  border-color: rgba(223, 190, 143, 0.86);
frontend/src/pages/settings/Settings.css:683:  font-size: 0.78rem;
frontend/src/pages/settings/Settings.css:684:  font-weight: 700;
frontend/src/pages/settings/Settings.css:685:  letter-spacing: 0.12em;
frontend/src/pages/settings/Settings.css:701:  font-size: clamp(1.55rem, 2vw, 1.9rem);
frontend/src/pages/settings/Settings.css:702:  font-weight: 800;
frontend/src/pages/settings/Settings.css:703:  margin: 0;
frontend/src/pages/settings/Settings.css:704:  line-height: 1;
frontend/src/pages/settings/Settings.css:705:  letter-spacing: -0.05em;
frontend/src/pages/settings/Settings.css:710:  font-size: clamp(2.3rem, 4vw, 3.2rem);
frontend/src/pages/settings/Settings.css:711:  font-weight: 700;
frontend/src/pages/settings/Settings.css:712:  line-height: 0.98;
frontend/src/pages/settings/Settings.css:713:  text-shadow: 0 10px 22px rgba(255, 255, 255, 0.32);
frontend/src/pages/settings/Settings.css:717:  margin: 0;
frontend/src/pages/settings/Settings.css:719:  font-size: 0.96rem;
frontend/src/pages/settings/Settings.css:720:  line-height: 1.58;
frontend/src/pages/settings/Settings.css:726:  margin: 0;
frontend/src/pages/settings/Settings.css:727:  padding: 0;
frontend/src/pages/settings/Settings.css:736:  font-size: 0.92rem;
frontend/src/pages/settings/Settings.css:737:  line-height: 1.48;
frontend/src/pages/settings/Settings.css:748:  font-size: 13px;
frontend/src/pages/settings/Settings.css:749:  font-weight: 700;
frontend/src/pages/settings/Settings.css:750:  line-height: 1.45;
frontend/src/pages/settings/Settings.css:756:  font-size: 13px;
frontend/src/pages/settings/Settings.css:757:  font-weight: 600;
frontend/src/pages/settings/Settings.css:761:  color: #79521a;
frontend/src/pages/settings/Settings.css:762:  font-size: 13px;
frontend/src/pages/settings/Settings.css:763:  font-weight: 600;
frontend/src/pages/settings/Settings.css:764:  line-height: 1.5;
frontend/src/pages/settings/Settings.css:776:  padding: 6px 12px;
frontend/src/pages/settings/Settings.css:777:  border-radius: var(--radius-full);
frontend/src/pages/settings/Settings.css:778:  background: linear-gradient(180deg, #f6d28a 0%, #ebb25a 100%);
frontend/src/pages/settings/Settings.css:779:  box-shadow: 0 8px 22px rgba(214, 154, 57, 0.18);
frontend/src/pages/settings/Settings.css:780:  color: #79521a;
frontend/src/pages/settings/Settings.css:781:  font-size: 12px;
frontend/src/pages/settings/Settings.css:782:  font-weight: 700;
frontend/src/pages/settings/Settings.css:787:  background: rgba(255, 255, 255, 0.56);
frontend/src/pages/settings/Settings.css:788:  border: 1px solid rgba(205, 217, 240, 0.72);
frontend/src/pages/settings/Settings.css:789:  box-shadow: 0 10px 22px rgba(132, 150, 190, 0.08);
frontend/src/pages/settings/Settings.css:812:  padding: 14px 16px;
frontend/src/pages/settings/Settings.css:813:  border-radius: 18px;
frontend/src/pages/settings/Settings.css:814:  border: 1px solid rgba(205, 217, 240, 0.72);
frontend/src/pages/settings/Settings.css:815:  background: rgba(255, 255, 255, 0.76);
frontend/src/pages/settings/Settings.css:816:  box-shadow: 0 14px 32px rgba(132, 150, 190, 0.08);
frontend/src/pages/settings/Settings.css:818:  font-size: 14px;
frontend/src/pages/settings/Settings.css:819:  line-height: 1.55;
frontend/src/pages/settings/Settings.css:823:  border-color: rgba(192, 57, 43, 0.26);
frontend/src/pages/settings/Settings.css:824:  background: linear-gradient(180deg, rgba(255, 245, 244, 0.9) 0%, rgba(255, 250, 249, 0.76) 100%);
frontend/src/pages/settings/Settings.css:825:  color: #a53a2c;
frontend/src/pages/settings/Settings.css:829:  border-color: rgba(58, 143, 94, 0.24);
frontend/src/pages/settings/Settings.css:830:  background: linear-gradient(180deg, rgba(244, 255, 248, 0.92) 0%, rgba(249, 255, 251, 0.8) 100%);
frontend/src/pages/settings/Settings.css:831:  color: #347650;
frontend/src/pages/settings/Settings.css:835:  border-color: rgba(134, 108, 208, 0.22);
frontend/src/pages/settings/Settings.css:836:  background: linear-gradient(180deg, rgba(248, 245, 255, 0.92) 0%, rgba(252, 250, 255, 0.8) 100%);
frontend/src/pages/settings/Settings.css:846:  padding: 22px 24px;
frontend/src/pages/settings/Settings.css:847:  border-radius: 24px;
frontend/src/pages/settings/Settings.css:849:    linear-gradient(180deg, rgba(255, 255, 255, 0.84) 0%, rgba(247, 243, 255, 0.68) 100%);
frontend/src/pages/settings/Settings.css:850:  border: 1px solid rgba(205, 217, 240, 0.82);
frontend/src/pages/settings/Settings.css:851:  box-shadow: 0 18px 40px rgba(132, 150, 190, 0.08);
frontend/src/pages/settings/Settings.css:860:  margin: 0;
frontend/src/pages/settings/Settings.css:862:  font-size: 1rem;
frontend/src/pages/settings/Settings.css:863:  line-height: 1.62;
frontend/src/pages/settings/Settings.css:864:  font-weight: 600;
frontend/src/pages/settings/Settings.css:869:  font-size: 13px;
frontend/src/pages/settings/Settings.css:889:  border-top: 1px solid rgba(195, 206, 225, 0.72);
frontend/src/pages/settings/Settings.css:907:  margin: 0;
frontend/src/pages/settings/Settings.css:909:  font-size: 14px;
frontend/src/pages/settings/Settings.css:910:  line-height: 1.6;
frontend/src/pages/settings/Settings.css:914:  margin: 0;
frontend/src/pages/settings/Settings.css:917:  font-size: 14px;
frontend/src/pages/settings/Settings.css:918:  line-height: 1.7;
frontend/src/pages/settings/Settings.css:929:  padding: 24px 26px;
frontend/src/pages/settings/Settings.css:930:  border-radius: 26px;
frontend/src/pages/settings/Settings.css:932:    linear-gradient(180deg, rgba(245, 241, 255, 0.74) 0%, rgba(236, 230, 252, 0.58) 100%);
frontend/src/pages/settings/Settings.css:933:  border: 1px solid rgba(163, 143, 220, 0.24);
frontend/src/pages/settings/Settings.css:934:  box-shadow:
frontend/src/pages/settings/Settings.css:935:    0 18px 38px rgba(132, 150, 190, 0.09),
frontend/src/pages/settings/Settings.css:936:    inset 0 1px 0 rgba(255, 255, 255, 0.46);
frontend/src/pages/settings/Settings.css:940:  margin: 0 0 8px;
frontend/src/pages/settings/Settings.css:942:  font-size: 16px;
frontend/src/pages/settings/Settings.css:943:  font-weight: 700;
frontend/src/pages/settings/Settings.css:947:  margin: 0 0 16px;
frontend/src/pages/settings/Settings.css:949:  font-size: 14px;
frontend/src/pages/settings/Settings.css:950:  line-height: 1.6;
frontend/src/pages/settings/Settings.css:954:  margin: 0 0 16px;
frontend/src/pages/settings/Settings.css:956:  font-size: 13px;
frontend/src/pages/settings/Settings.css:957:  line-height: 1.6;
frontend/src/pages/settings/Settings.css:967:  border-radius: 22px;
frontend/src/pages/settings/Settings.css:968:  box-shadow: var(--settings-card-shadow);
frontend/src/pages/settings/Settings.css:983:  padding: 22px 24px;
frontend/src/pages/settings/Settings.css:994:  background: rgba(195, 206, 225, 0.9);
frontend/src/pages/settings/Settings.css:999:  font-size: 11px;
frontend/src/pages/settings/Settings.css:1000:  font-weight: 700;
frontend/src/pages/settings/Settings.css:1002:  letter-spacing: 0.06em;
frontend/src/pages/settings/Settings.css:1015:  box-shadow: 0 12px 28px rgba(134, 108, 208, 0.14);
frontend/src/pages/settings/Settings.css:1025:  padding: 0.34rem 0.76rem;
frontend/src/pages/settings/Settings.css:1026:  border-radius: var(--radius-full);
frontend/src/pages/settings/Settings.css:1027:  background: rgba(255, 255, 255, 0.68);
frontend/src/pages/settings/Settings.css:1028:  border: 1px solid rgba(255, 255, 255, 0.74);
frontend/src/pages/settings/Settings.css:1030:  font-size: 0.72rem;
frontend/src/pages/settings/Settings.css:1031:  font-weight: 700;
frontend/src/pages/settings/Settings.css:1032:  letter-spacing: 0.08em;
frontend/src/pages/settings/Settings.css:1037:  font-size: 1rem;
frontend/src/pages/settings/Settings.css:1038:  line-height: 1.45;
frontend/src/pages/settings/Settings.css:1044:  border-radius: var(--radius-full);
frontend/src/pages/settings/Settings.css:1045:  background: rgba(195, 206, 225, 0.5);
frontend/src/pages/settings/Settings.css:1053:  border-radius: var(--radius-full);
frontend/src/pages/settings/Settings.css:1054:  background: linear-gradient(90deg, var(--settings-purple) 0%, rgba(134, 108, 208, 0.7) 100%);
frontend/src/pages/settings/Settings.css:1070:  margin: 0;
frontend/src/pages/settings/Settings.css:1087:  border-top: 1px solid rgba(195, 206, 225, 0.72);
frontend/src/pages/settings/Settings.css:1098:  margin: 0;
frontend/src/pages/settings/Settings.css:1100:  font-size: 15px;
frontend/src/pages/settings/Settings.css:1101:  font-weight: 700;
frontend/src/pages/settings/Settings.css:1106:  font-size: 14px;
frontend/src/pages/settings/Settings.css:1107:  font-weight: 700;
frontend/src/pages/settings/Settings.css:1112:  margin: 0;
frontend/src/pages/settings/Settings.css:1114:  font-size: 12px;
frontend/src/pages/settings/Settings.css:1115:  line-height: 1.4;
frontend/src/pages/settings/Settings.css:1124:  border-radius: var(--radius-full);
frontend/src/pages/settings/Settings.css:1126:  background: rgba(195, 206, 225, 0.45);
frontend/src/pages/settings/Settings.css:1130:  background: rgba(195, 206, 225, 0.45);
frontend/src/pages/settings/Settings.css:1131:  border-radius: var(--radius-full);
frontend/src/pages/settings/Settings.css:1135:  border-radius: var(--radius-full);
frontend/src/pages/settings/Settings.css:1136:  background: linear-gradient(90deg, rgba(134, 108, 208, 0.92) 0%, rgba(213, 154, 57, 0.72) 100%);
frontend/src/pages/settings/Settings.css:1140:  border-radius: var(--radius-full);
frontend/src/pages/settings/Settings.css:1141:  background: linear-gradient(90deg, rgba(134, 108, 208, 0.92) 0%, rgba(213, 154, 57, 0.72) 100%);
frontend/src/pages/settings/Settings.css:1147:  font-size: 13px;
frontend/src/pages/settings/Settings.css:1165:    padding: 16px 16px 80px;
frontend/src/pages/settings/Settings.css:1177:    padding: 22px;
frontend/src/pages/settings/Settings.css:1207:    padding: 22px;
frontend/src/pages/settings/Settings.css:1237:    font-size: 13px;
frontend/src/pages/settings/Settings.css:1238:    padding: 0 14px;
frontend/src/pages/settings/Settings.css:1247:  padding: 0;
frontend/src/pages/settings/Settings.css:1248:  margin: -1px;
`

## Guard evidence

- 
pm run test -- design-system theme-tokens: covered by combined target run and PASS.
