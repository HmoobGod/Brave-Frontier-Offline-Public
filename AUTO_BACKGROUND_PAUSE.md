# Auto Battle pauses when the game page is hidden

When the page receives a hidden visibility signal, Auto turns off and its pending
timer is cancelled. An already running round finishes through the existing
executor. Returning to the page leaves Auto off; the player can enable it again.
The scheduler also rejects hidden-page calls and delayed timer callbacks.

This is offline reconstruction lifecycle behavior, not a restored native Global
combat rule. It changes no action selection, damage, gauge, quest reward, save
schema, signing or Android permissions. It does not cancel the current round or
roll back legitimately completed actions/rewards.

The existing v41 runtime check invokes a synthetic visibility regression that
uses real Auto scheduling and real combat rounds with surviving enemies. It
covers default and Smart Auto, pending cancellation, delayed event delivery,
in-flight completion, foreground staying paused and explicit manual resumption.
It also checks interruption of the existing repeat-quest controller using mocked
result/replay metadata, while running the real Auto scheduler and round executor.
Full synthetic player and storage state must remain unchanged. The existing v41
APK check compares the generated lifecycle handler and both scheduler guards.
No new workflow rules or triggers.

Browser tests simulate the visibility signal; physical Android background/resume
delivery remains a separate device acceptance requirement. Fresh GitHub Android
CI and independent exact-head review are required before integration.
