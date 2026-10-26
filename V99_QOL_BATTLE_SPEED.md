# Brave Frontier Global Offline — v99.00 QoL Battle Speed

Parent: isolated v98 cleared-quest repeat branch; v97 backups already verified and merged.

- Existing native battle speeds remain 1×, 2× (default), 3×, and 5×. Optional 8× and 12× choices added to the original speed selector, which already feeds roundSpeed and only changes next-round presentation.
- Optional **skip long battle animations** is OFF by default. When enabled, a separate optional wrapper caps the existing presentation wait at 40 ms for original-style archive battles. This retains asynchronous frame/epoch checks rather than replacing battle commands.
- Changes to animation-skip state are rejected while a round is busy.
- All QoL choices use separate local preferences, not original save key bf_global_offline_demo_v7 or P.version.
- No modifications to hit counts, damage, status ailments, enemy behavior, rewards, Energy, quest clears or gameplay balance; latest signed APK and full Android gameplay testing are still required before release.
- Test includes normal versus rapid waits, training-mode exclusion, mid-round toggle rejection, original speed preservation and v7 save immutability.

Remaining: Advanced Auto Battle, live squad presets, favorites/locking, improved materials tracking, detailed battle info, and previously-read dialogue skip.
