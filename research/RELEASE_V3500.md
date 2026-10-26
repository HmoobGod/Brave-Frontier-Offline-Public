# v35.00 — Original Story Dialogue Line Navigator

Baseline: verified green v34.00 Build #234, commit e89aa6679bb14f5979bb75d3397708f61875a1d0.

The quest reader's twenty original 2022 Global dungeon event scripts preserve 405 archived MSGDRAW frames. The new optional read-only **GO TO LINE** control lets players navigate directly to any page of an unlocked dialogue (for example Karl → Seria in Morgan) without tapping NEXT dozens of times.

The navigator invokes existing reader Prev/Next events, preserving v28 speaker selection, v29 source expression art, v27 recovered backgrounds, v34 source-relative stage position, and scene unlock gates. It pauses the opt-in v33 timed playback before seeking and never reads or writes save/localStorage data or modifies battle rewards. No extra quests unlock. Navigated pages are not persisted between app launches.

The native renderer's pixel transform, event choreography, camera moves, voice and timeline durations remain unknown. Do not claim these visual presentations reproduce original runtime faithfully.

Android remains org.bravefrontier.offline with development debug signer, no INTERNET permission and bf_global_offline_demo_v7 saved progress. Chromium integration test plus packaged APK regression are required for promotion.
