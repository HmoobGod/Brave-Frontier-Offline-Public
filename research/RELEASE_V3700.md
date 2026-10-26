# v37.00 — Optional Full-Screen Original Story Theater

Baseline: v36.00 composited original archived cutscene stage (requires verified v36 Android build before promotion).

Adds a one-tap, **opt-in full-screen story reader** for supported unlocked 2022 Global archived dialogue. The panel expands to a viewport-covering mobile reading surface, while preserving the existing source script text, actor expression frames, recovered dungeon JPG backdrops, scene placement metadata, v33 timed playback, v35 line navigation, and all original quest unlock gates. Players can exit using a visible 44px touch target, Escape, closing the reader, or switching to another navigation tab.

This presentation is a reconstruction and not an assertion of recovered original native UI timing, stage pixel coordinates or animation curves. The mode exists only in active UI state; it writes no localStorage/save data and never alters quest clears, enemies, drops or rewards.

Tests require Android package/signing/save v7 stability and browser full-screen enter/exit, keyboard escape and story navigation while focused.
