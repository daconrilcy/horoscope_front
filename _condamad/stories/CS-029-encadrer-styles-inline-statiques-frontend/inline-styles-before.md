<!-- Baseline des styles inline TSX avant politique CS-029. -->

# Inline Styles Before

Baseline source:

```powershell
rg -n "style=" frontend\src -g "*.tsx"
```

Exemples statiques audites:

- `frontend/src/layouts/SettingsLayout.tsx`
- `frontend/src/features/astrologers/components/AstrologerCard.tsx`
- `frontend/src/components/settings/DeleteAccountModal.tsx`
