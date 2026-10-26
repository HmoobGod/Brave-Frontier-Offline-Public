# v0.13.1 safety regression report

- 12 focused Chromium checks passed; zero uncaught JavaScript errors.
- Canvas context balanced: 921 saves / 921 restores in measured test.
- Separate end-to-end three-wave Auto Battle passed with saved rewards.
- Save v7 schema retained, migration from v6 verified.
- Corrupt-save quarantine / recovery and export verified with actual browser download.
- Support BB healing and zero enemy damage verified.
- Mid-BB epoch cancellation, triple execute and overkill log verified.
- Android layout and native picker are NOT compiled or Android-device tested.
