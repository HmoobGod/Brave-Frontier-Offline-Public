# v163 — Actual old/new browser save downgrade regression

This checkpoint **does not award Gems or change production gameplay**. It makes a precise upgrade/downgrade risk executable rather than relying only on comments or schema inspection.

## Test fixture

In Chromium with mocked storage, load two different repository HTML versions:

1. The CI-prepared v161+ game HTML, which contains the source-approved 22-finales pending Gem evidence and canonical v7 save extensions.
2. The checked-in unpatched game HTML from the **same repository revision** (`git show HEAD:app/src/main/assets/index.html`), representing the **pre-v160 parser**. This is not claimed to be the owner's exact installed v124 APK.

The current game completes quest finale #12, writing its real quest-clear counter, v160 legacy ledger and v161 pending first-clear marker together to the existing `bf_global_offline_demo_v7` key.

The earlier parser imports the JSON, preserves the clear counter, drops the unknown v160/v161 metadata and saves back to the same v7 key. The current parser then reimports that downgraded save; it must recover a historical legacy clear but **not re-create a pending first-clear marker** or award a Gem on a replay.

Finally, importing the **original untouched JSON backup** from before downgrade restores the original pending marker, proving why a separate exported save is necessary before an old-APK rollback.

## Explicit limits and policy

- CI reproduces **parser-level** downgrade/reupgrade behavior in browser. It does not replace a signed Android update/downgrade or device-save durability test.
- No local live storage, Android signing, APK package, currency wallet, purchase path, or player state is modified by the new test.
- Owners should **export and safeguard a save JSON before any downgrade**. Older versions can silently erase metadata they do not understand on their next save. Current automatic rotating backups should not be assumed to survive an uninstall.
- The original 2022 currency enum and old-account reimbursement policy remain unresolved. Live Gem payouts stay disabled.
- CI gate: exact v163 feature-head success, verified v162 merged-main build, guarded PR merge, then fresh merged-main success.

## Follow-up

Before enabling Gems, test the exact owner v124 APK/save on a physical Android device if requested, provide a non-destructive export path for any older-APK downgrade, prove initial wallet/accounting and native 2022 payout semantics, and lock the one-time claim rules for older completed quests.
