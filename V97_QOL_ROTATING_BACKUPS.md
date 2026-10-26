# Brave Frontier Global Offline — v97.00 QoL Backup Checkpoint

Base: verified public main v96 commit bb6b1d3dec9cfe39f12c922d948e4334b3fbf7e2; GitHub Actions Build #10 success.

## Scope
First opt-in-compatible QoL foundation for later quest repeat/squad/battle improvements:
- Automatically retain the three most recent **different, valid JSON v7** active saves in app-local WebView storage.
- Never replace, migrate or remove the main active save key, \`bf_global_offline_demo_v7\`.
- Reject damaged/incomplete and oversized snapshots (512 KiB cap).
- Pause auto backups through an independent QoL checkbox; keep existing snapshots.
- Explicit **Export a Backup** uses the existing Android Storage Access Framework save-file picker. Never auto-export to public storage and never auto-restore over progress.
- One small panel under the quest screen. Automatic checks every 12 seconds when visible, on page hide, and when switching away.
- Isolated storage: \`bf_global_offline_qol_rotating_backups_v97\` and \`bf_global_offline_qol_backups_enabled_v97\`.

## Safety and limitations
A backup in app-local storage **does not survive uninstall or clearing app data**. Export a backup JSON outside the app for durable recovery. Local storage quota failure will silently skip a new snapshot and leave active progress untouched. Native Android UI/device import/export and complete gameplay still require on-device verification.
Original combat, quest balance, rewards, package ID, signing secret, P schema v7 and existing save recovery logic are unchanged.

## Requested QoL backlog (after original gameplay stability)
- Auto-repeat cleared quests
- Expanded battle speed controls
- Skip lengthy battle animations
- Advanced Smart Auto Battle
- Saved squad presets
- Unit favorites and locking
- Evolution material tracking
- Automatic rotating save backups **v97 implementation**
- Detailed battle information
- Skip previously viewed dialogue

No other QoL item is claimed implemented by v97.
