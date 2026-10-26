# Brave Frontier Offline — first-APK signing and save safety

## What changed

- All GitHub Actions debug APKs built after this update use one persistent **development-only** signing identity. It is stored as a base64-encoded PKCS12 key in this private repository and decoded during CI. This key is **not suitable for production distribution**. Do not release a store build signed with it.
- CI uses `versionCode = 1000 + github.run_number`; the older first APK used versionCode 15.
- Android WebView receives lifecycle pause/resume calls. Android 15+ insets include keyboard and display cutout; the background is set explicitly.
- Bundled v0.13.1 demo HTML has an idempotent build-time quarantine-deduplication patch. The original source file is preserved in Git; `patch_bf_save_quarantine.py` applies the tested change before Gradle packages assets (CI and local direct Gradle builds).
- `test_bf_v0131.py` covers corrupt-save recovery, quarantine deduplication, support BB, Auto Battle, and mid-burst restart, in **headless Chrome only**.

## Important: first APK compatibility

GitHub build #3 was signed with an ephemeral debug keystore. The private key for that first build was **not persisted**, so the new stable development signing key probably has a different signing certificate. **Even though the new APK's versionCode is higher, Android will refuse an in-place upgrade across different signatures.**

**Before attempting to replace the first APK, open it and use `Download Save File` to export your `.json` save.** Keep the file outside the app. After confirming the backup exists, uninstall the old app if Android refuses the update, install the new debug APK, and use `Import Save File`.

Future builds signed with the *same preserved development key* should support in-place updates (provided the version code increases). This statement requires device verification. Never rotate the development key without a backup/migration plan.

## Device checks still needed

1. First launch: no white/black screen; all content visible above system bars.
2. Attack, offensive BB, support BB and Auto Battle.
3. Quest clear, force-stop immediately (under 2 s), reopen; separately test after waiting 15 s. Report missing recent progress; onPause alone doesn't prove localStorage durability.
4. Download a save to a user-chosen location, reimport it, and verify values.
5. Open the save-code keyboard and inspect bottom padding; cancel both file pickers.
6. Test upgrading the first APK; if a signing mismatch occurs, export a save then uninstall/reinstall.

No Android installation, update, or gameplay verification is claimed from CI success alone.
